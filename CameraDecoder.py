#CameraDecoder class
import cv2
import numpy as np
from datetime import datetime
from apriltag import apriltag
from paho.mqtt import client as mqtt_client
import json
import random

class CameraDecoder():
    #Create camera decoder with a config dictionary
    def __init__(self, CamConfig, MqttClient):
        #MQTT Client class
        self.MqttClient = MqttClient
        #URL of camera
        self.URL = CamConfig.get('url')
        #Name of camera
        self.Name = CamConfig.get('name')
        #Tags array for camera
        self.Tags = CamConfig.get('tags')
        #Framerate, default 1.0
        self.Framerate = CamConfig.get('framerate',1.0)

        #Make sure that none of the configuration is invalid
        if(self.Name is None):
            print("Error: Camera Unnamed has no name")
            return
        if(self.URL is None):
            print("Error: Camera ",self.Name," has invalid URL")
            return
        if(self.Tags is None):
            print("Error: Camera ",self.Name," has undefined tag list")
            return


    #Task function
    def task(self, CamConfig):


    #Function to terminate
    def stop(self)