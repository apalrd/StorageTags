#Copyright (C) 2021 Andrew Palardy
#See LICENSE file for complete license terms
#Main file of StorageTags
from STMqttClient import STMqttClient
from STCameraDecoder import STCameraDecoder
from STWebServer import STWebServer
import time
import yaml

def Main():
    #Objects cache
    Objs = {}
    #Open the configuration yaml file
    CFname = "config.yml"
    print("MAIN: Opening configuration file ",CFname)
    CFile = open(CFname,'r')
    Config = yaml.safe_load(CFile)
    print("CONFIG: Entire configuration structure is ",Config)


    #If MQTT section is not none, start MQTT
    ConfigMQTT = Config.get('mqtt')
    Objs['MqttCl'] = None
    if ConfigMQTT is not None:
        print("CONFIG: Creating MQTT")
        Objs['MqttCl'] = STMqttClient(ConfigMQTT)
    else:
        print("CONFIG: MQTT not defined, not starting module")

    #For each entry in the Cameras array, start the camera
    ConfigCams = Config.get('cameras')
    Objs['CamCd'] = []
    if ConfigCams is not None:
        print("CONFIG: Creating",len(ConfigCams),"Cameras")
        for Cam in ConfigCams:
            Objs['CamCd'].append(STCameraDecoder(Cam,Objs['MqttCl']))
    else:
        print("CONFIG: No cameras defined, not starting module")

    #If web is defined, start the webserver
    ConfigWeb = Config.get('web')
    Objs['Web'] = None
    if ConfigWeb is not None:
        print("CONFIG: Creating Webserver")
        Objs['Web'] = STWebServer(ConfigWeb,Objs)
    else:
        print("CONFIG: Web not defined, not starting module")

    #MainLoop
    while(1):
        try:
            time.sleep(10)
        except:
            break

    #Send stop command to other threads
    if Objs['MqttCl'] is not None:
        Objs['MqttCl'].stop()
    for Cam in Objs['CamCd']:
        if Cam is not None:
            Cam.stop()
    if Objs['Web'] is not None:
        Objs['Web'].stop()

#Entry point
if __name__ == "__main__": 
    Main() 
