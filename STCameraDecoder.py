#Copyright (C) 2021 Andrew Palardy
#See LICENSE file for complete license terms
#CameraDecoder class
#Implements a single camera-based fiducial marker tracker
#And publishes the resulting data to both MQTT and the in-memory data store
import cv2
import numpy as np
from datetime import datetime
from apriltag import apriltag
from paho.mqtt import client as mqtt_client
import json
import random
import threading

class STCameraDecoder():
    #Create camera decoder with a config dictionary
    def __init__(self, CamConfig, MqttClient):
        #MQTT Client class
        self.MqttClient = MqttClient
        #URL of camera
        self.URL = CamConfig.get('url')
        #Name of camera
        self.FullName = CamConfig.get('name')
        #Tag type for camera
        self.Tag = CamConfig.get('tag')
        #Framerate, default 1.0
        self.Framerate = CamConfig.get('framerate',1.0)

        #Make sure that none of the configuration is invalid
        if(self.FullName is None):
            print("Error: Camera Unnamed has no name")
            return
        if(self.URL is None):
            print("Error: Camera ",self.FullName," has invalid URL")
            return
        if(self.Tag is None):
            print("Error: Camera ",self.FullName," has undefined tag")
            return

        #Remove all spaces from Name to get internal name handle
        self.Name = self.FullName.replace(" ","")

        #Start a task for the camera
        self.Run = True
        self.Task = threading.Thread(target=self.task,name="Camera_"+self.Name,args=())
        self.Task.start()


    #Task function
    def task(self):
        print("CAM: Starting task for "+self.Name)
        #Start video capture
        self.VCap = cv2.VideoCapture(self.URL,cv2.CAP_FFMPEG)

        #For each element in tags, create a Detector
        self.Detector = apriltag(self.Tag)
        
        #Start the decoding loop
        self.TimeLast = datetime.now()
        while(self.Run):
            ret,self.ImageColor = self.VCap.read()
            if ret == False:
                self.Run = False
                continue
            #Capture dt
            tnow = datetime.now()
            dt = (tnow - self.TimeLast).total_seconds()
            #If it hasn't been enough time, skip
            if(dt < 1/self.Framerate):
                continue
            #Store tlast for next dt calc
            self.TimeLast = tnow
            #Convert to grayscale
            imgray = cv2.cvtColor(self.ImageColor,cv2.COLOR_BGR2GRAY)
            #Process image with each detector
            tdetect = datetime.now()
            self.Detections = self.Detector.detect(imgray)
            #Time it takes to process
            proctime = (datetime.now() - tdetect).total_seconds()
            #Convert now into a string
            StrTime = tnow.strftime("%Y-%m-%d-%H:%M:%S")
            #Handling of each detection
            for detect in self.Detections:
                #Draw outline over image
                points = detect['lb-rb-rt-lt']
                n = len(points)
                # Draw the box outline as 4 lines
                for j in range(0,n):
                    p1 = tuple([int(cell) for cell in points[j]])
                    p2 = tuple([int(cell) for cell in points[(j+1)%n]])
                    cv2.line(self.ImageColor, p1, p2, (255,0,0), 3)

                #Create dict for the detection data to be used in the data store and MQTT
                payload = {
                    'X': detect['center'][0],
                    'Y': detect['center'][1],
                    'Hamming': detect['hamming'],
                    'Corners': tuple([tuple([cell for cell in row]) for row in detect['lb-rb-rt-lt']]),
                    'LastUpdate': StrTime,
                    'Camera': self.Name
                }

                #Topic for MQTT
                topic = self.Name+"/"+str(detect['id'])

                #Publish payload for this detection
                self.MqttClient.publish(topic,json.dumps(payload))

            #Total time it took including OpenCV operations
            totime = (datetime.now() - tnow).total_seconds()

            #Create dict for camera status data
            CStatus = {
                'FullName': self.FullName,
                'Name': self.Name,
                'FrameRateTarget':self.Framerate,
                'FrameRate':1.0/dt,
                'DetectorTime':proctime,
                'ProcessTime':totime,
                'LastUpdate':StrTime,
                'NumDetections':len(self.Detections)
            }

            #Publish status data to MQTT as well
            self.MqttClient.publish("status/"+self.Name,json.dumps(CStatus))

        #End of loop
        print("CAM: Terminating camera thread for "+self.Name)


    #Function to terminate
    def stop(self):
        self.Run = False