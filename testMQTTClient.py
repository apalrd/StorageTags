from MqttClient import MqttClient
import time

data = {
    'broker':'telstar.palnet.net',
    'port':1883,
}
cl = MqttClient(data)

while(1):
    #cl.Client.publish("storagetracker/status","test")
    try:
        time.sleep(10)
        cl.publish("Test","TestData")
    except KeyboardInterrupt:
        break
cl.stop()
