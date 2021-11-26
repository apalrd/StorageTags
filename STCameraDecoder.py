#Copyright (C) 2021 Andrew Palardy
#See LICENSE file for complete license terms
#CameraDecoder class
#Implements a single camera-based fiducial marker tracker
#And publishes the resulting data to both MQTT and the in-memory data store
import cv2
import numpy as np
from datetime import datetime
import time
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
        #Tag type for camera, default 36h11
        self.Tag = CamConfig.get('tag','tag36h11')
        #Framerate, default 1.0
        self.Framerate = CamConfig.get('framerate',1.0)

        #Make sure that none of the configuration is invalid
        if(self.FullName is None):
            print("Error: Camera Unnamed has no name")
            return
        if(self.URL is None):
            print("Error: Camera",self.FullName,"has invalid URL")
            return

        #Remove all spaces from Name to get internal name handle
        self.Name = self.FullName.replace(" ","")

        #Start a task for the camera
        self.Run = True
        self.Task = threading.Thread(target=self.task,name="Camera_"+self.Name,args=())
        self.Task.start()


    #Task function
    def task(self):
        print("CAM: Starting task for",self.Name)

        #Start run loop to continue with the camera on error
        while(self.Run):
            #Start video capture, catch errors
            try:
                print("CAM: Starting VideoCapture for camera",self.Name,"at address",self.URL)
                VCap = cv2.VideoCapture(self.URL,cv2.CAP_FFMPEG)

                #For each element in tags, create a Detector
                Detector = apriltag(self.Tag)
                
                #Start the decoding loop
                TimeLast = datetime.now()
                while(self.Run):
                    ret,self.ImageColor = VCap.read()
                    #If read error, terminate camera and start over
                    if ret == False:
                        #Wait 30 seconds before retrying, but abort if stop flag is also set
                        for i in range(1,30):
                            if self.Run:
                                time.sleep(1)
                        break
                    #Capture dt
                    tnow = datetime.now()
                    dt = (tnow - TimeLast).total_seconds()
                    #If it hasn't been enough time, skip
                    if(dt < 1/self.Framerate):
                        continue
                    #Store tlast for next dt calc
                    TimeLast = tnow
                    #Convert to grayscale
                    imgray = cv2.cvtColor(self.ImageColor,cv2.COLOR_BGR2GRAY)
                    #Process image with each detector
                    tdetect = datetime.now()
                    self.Detections = Detector.detect(imgray)
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
                        if self.MqttClient is not None:
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
                    if self.MqttClient is not None:
                        self.MqttClient.publish("status/"+self.Name,json.dumps(CStatus))

                #On normal loop termination, release VCap
                print("CAM: Cleaning up capture for",self.Name)
                VCap.release()

            #On exception
            except cv2.error as e:
                print("CAM: Camera",self.Name,"got exception",e)
                continue

        #End of run
        print("CAM: Terminating camera thread for",self.Name)


    #Function to terminate
    def stop(self):
        self.Run = False