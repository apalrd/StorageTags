from MqttClient import MqttClient
from CameraDecoder import CameraDecoder
import time

data = {
    'broker':'telstar.palnet.net',
    'port':1883,
}
cl = MqttClient(data)

# Create CameraDecoder
cconfig = {
    'url':'rtsp://10.0.69.2:554/11',
    'name':'Lab Camera',
    'framerate':1.0,
    'tag':'tag36h11'
}
cd = CameraDecoder(cconfig,cl)

while(1):
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        break
cl.stop()
cd.stop()
