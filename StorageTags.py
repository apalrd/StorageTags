#Copyright (C) 2021 Andrew Palardy
#See LICENSE file for complete license terms
#Main file of StorageTags
from STMqttClient import STMqttClient
from STCameraDecoder import STCameraDecoder
import time
import yaml

def Main():
    #Open the configuration yaml file
    CFname = "config.yml"
    print("MAIN: Opening configuration file ",CFname)
    CFile = open(CFname,'r')
    Config = yaml.safe_load(CFile)
    print("CONFIG: Entire configuration structure is ",Config)


    #If MQTT section is not none, start MQTT
    ConfigMQTT = Config.get('mqtt')
    MqttCl = None
    if ConfigMQTT is not None:
        MqttCl = STMqttClient(ConfigMQTT)
    else:
        print("CONFIG: MQTT not defined, not starting module")

    #For each entry in the Cameras array, start the camera
    ConfigCams = Config.get('cameras')
    CamCd = []
    if ConfigCams is not None:
        print("CONFIG: Creating",len(ConfigCams),"Cameras")
        for Cam in ConfigCams:
            CamCd.append(STCameraDecoder(Cam,MqttCl))
    else:
        print("CONFIG: No cameras defined, not starting module")

    #MainLoop
    while(1):
        try:
            time.sleep(10)
        except:
            break

    #Send stop command to other threads
    if MqttCl is not None:
        MqttCl.stop()
    for Cam in CamCd:
        if Cam is not None:
            Cam.stop()

#Entry point
if __name__ == "__main__": 
    Main() 
