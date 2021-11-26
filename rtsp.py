import cv2
import numpy as np
from CountsPerSec import CountsPerSec
from datetime import datetime
from apriltag import apriltag
from paho.mqtt import client as mqtt_client
import json
import random

#Draw function
def display(im, detections, color):
    for detect in detections:
        #print("ID: ",detect['id'])
        hull = detect['lb-rb-rt-lt']

        n = len(hull)

        # Draw the convext hull
        for j in range(0,n):
            p1 = tuple([int(cell) for cell in hull[j]])
            p2 = tuple([int(cell) for cell in hull[(j+1)%n]])
            cv2.line(im, p1, p2, color, 3)


print("About to open videocapture")

url = "rtsp://admin:KeyHole7@keyhole7.palnet.net:554/cam/realmonitor?channel=1&subtype=00"
url = "rtsp://10.0.69.2:554/11"
vcap = cv2.VideoCapture(url,cv2.CAP_FFMPEG)
cps  = CountsPerSec().start()
targetFR = 1.0
tlast = datetime.now()
detector = apriltag("tag36h11")

#Open MQTT broker
broker = 'telstar.palnet.net'
port = 1883
client_id = f'python-mqtt-{random.randint(0, 1000)}'
# username = 'emqx'
# password = 'public'
client = mqtt_client.Client(client_id)
#client.username_pw_set(username, password)
#client.on_connect = on_connect
client.connect(broker, port)

while(1):
    ret,imagecolor = vcap.read()
    if ret == False:
        print("bad frame")
        continue
    #Capture dt
    tnow = datetime.now()
    dt = (tnow - tlast).total_seconds()
    #If it hasn't been enough time, skip
    if(dt < 1/targetFR):
        continue
    #Store tlast for next dt calc
    tlast = tnow
    #Convert to grayscale
    imgray = cv2.cvtColor(imagecolor,cv2.COLOR_BGR2GRAY)
    #Process image
    tdetect = datetime.now()
    detections = detector.detect(imgray)
    #Time it takes to process
    proctime = (datetime.now() - tdetect).total_seconds()
    #Draw on image
    display(imagecolor,detections,(255,0,0))
    imsmall = cv2.resize(imagecolor,(960,540))
    cv2.imshow('VIDEO',imsmall)
    #Parse stuff for MQTT
    for detect in detections:
        #print("Detection: ",detect)
        topic = "storagetags/cam1/"+str(detect['id'])
        payload = {
            'x': detect['center'][0],
            'y': detect['center'][1],
            'hamming': detect['hamming'],
            'time': tnow.strftime("%Y-%m-%d-%H:%M:%S")}
        payloadstr = json.dumps(payload)
        client.publish(topic,payloadstr)

    #Total time it took including OpenCV operations
    totime = (datetime.now() - tnow).total_seconds()
    cps.increment()
    print("framerate is ",cps.countsPerSec(), "proctime is ",proctime, "totime is ",totime)
    if cv2.waitKey(1) >= 0:
        break

vcap.release()
cv2.destroyAllWindows()