#Copyright (C) 2021 Andrew Palardy
#See LICENSE file for complete license terms
#Main file of StorageTags
from STMqttClient import STMqttClient
from STCameraDecoder import STCameraDecoder
import time

data = {
    'broker':'telstar.palnet.net',
    'port':1883,
}
cl = STMqttClient(data)

# Create CameraDecoder
cconfig = {
    'url':'rtsp://10.0.69.2:554/11',
    'name':'Lab Camera',
    'framerate':1.0,
    'tag':'tag36h11'
}
cd = STCameraDecoder(cconfig,cl)

while(1):
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        break
cl.stop()
cd.stop()
