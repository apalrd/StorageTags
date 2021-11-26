#Copyright (C) 2021 Andrew Palardy
#See LICENSE file for complete license terms
#MqttClient class
#Implements management code for Paho MQTT client
from paho.mqtt import client as mqtt_client
import json
import threading

class STMqttClient():
    #Create camera decoder with a config dictionary
    def __init__(self, MqttConfig):
        #Address of broker
        self.Broker = MqttConfig.get('broker')
        #Port of broker
        self.Port = MqttConfig.get('port',1883)
        #Prefix
        self.Prefix = MqttConfig.get('prefix','storagetags')
        #client ID
        self.ClientID = MqttConfig.get('client_id','StorageTags')
        #Uname and password
        self.Uname = MqttConfig.get('username')
        self.Pword = MqttConfig.get('password')

        #Make sure that none of the configuration is invalid
        if(self.Broker is None):
            print("MQTT: Error: MQTT broker address is invalid")
            return

        #Start the broker
        self.Client = mqtt_client.Client(self.ClientID)

        #If Username is none, skip auth
        if(self.Uname is not None):
            if(self.Pword is None):
                print("MQTT: Error: Username is valid, but Password is None")
                print("MQTT: Not using authentication")
            else:
                self.Client.username_ps_set(self.Uname,self.Pword)
        
        #On connect function
        self.Client.on_connect = self.on_connect
        
        #Publish LWT
        self.LWTopic = self.Prefix+"/status"
        self.Client.will_set(self.LWTopic,"OFFLINE",0,True)

        #Start the broker
        self.Client.connect(self.Broker,self.Port)

        #Start a new task to deal with MQTT continuous processing
        self.Thread = threading.Thread(target=self.task,name='MQTT',args=())
        self.Thread.start()


    #Task function
    def task(self):
        print("MQTT: Started Task")
        #Call client loop forever
        self.Client.loop_forever()

    #On Connect function
    def on_connect(self,client,userdata,flags,rc):
        print("MQTT: Connected")
        #Publish status online
        self.Client.publish(self.LWTopic,"ONLINE",0,True)
        #Update subscriptions here


    #Function to terminate
    def stop(self):
        print("MQTT: Terminating")
        #Publish the disconnection message
        self.Client.publish(self.LWTopic,"OFFLINE",0,True)
        self.Client.disconnect()

    #Publish function
    def publish(self,topic,payload,qos=0,retain=True):
        #Append topic to prefix and call Paho
        self.Client.publish(self.Prefix+"/"+topic,payload,qos,retain)