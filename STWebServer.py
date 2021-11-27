#Copyright (C) 2021 Andrew Palardy
#See LICENSE file for complete license terms
#WebServer class
#This file manages the web interface and web api endpoints
import cv2
import numpy as np
from datetime import datetime
import json
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os.path
import logging


#Web Server glass
class STWebServer():
    def __init__(self,WebConfig,Objs):
        #Store objects for use in the handler
        self.Objs = Objs
        print("WEB: Config is ",WebConfig)
        #Get configuration fields
        self.Host = WebConfig.get('host','')
        self.Port = WebConfig.get('port',8080)

        #Start webserver task
        self.Task = threading.Thread(target=self.task,name="Webserver")
        self.Task.start()

    #Separate thread to run webserver
    def task(self):
        #Store server so it can be used by request handler
        server = self
        #Request Handling class
        class STWebServerHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                print("Path is",self.path)
                #If the request starts with API, call the api endpoint
                if(self.path.startswith('/api/')):
                    #Strip prefix
                    self.path = self.path.replace("/api/","")
                    self.do_api()
                #Otherwise, it must be a static element, so call the static handler
                else:
                    self.do_static()

            #Function to return a string result
            def return_string(self,data):
                self.wfile.write(bytes(data,"utf-8"))
                return

            #Function to return the index page
            def do_index(self):
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
                self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
                self.wfile.write(bytes("<body>", "utf-8"))
                self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
                self.wfile.write(bytes("<table>","utf-8"))
                #Print information about each camera
                for camera in server.Objs['CamCd']:
                    self.wfile.write(bytes("<h2>"+camera.Name+"</h2>","utf-8"))
                    self.wfile.write(bytes("<p>Status:<br>"+json.dumps(camera.CStatus)+"</p>","utf-8"))
                    #self.wfile.write(bytes("<table>","utf-8"))
                    #self.wfile.write(bytes("<tr>"+json.dumps(server.Objs)+"</p","utf-8"))
                    #self.wfile.write(bytes("</table>","utf-8"))
                self.wfile.write(bytes("</body></html>", "utf-8"))

            #Function to return a static file
            def do_static(self):
                #Strip the path of all ..'s so people don't try and escape
                self.path = self.path.replace("..","")

                #Add Add the path of the current file + 'static'
                root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
                
                #If the path is empty, add the index file
                if self.path == '/':
                    filename = root + '/index.html'
                else:
                    filename = root + self.path

                #Determine if file does or does not exist
                if(not os.path.exists(filename)):
                    #Return an error
                    self.do_error()
                    return

                #Determine file type
                self.send_response(200)
                if filename.endswith('.css'):
                    self.send_header('Content-type', 'text/css')
                elif filename.endswith('.json'):
                    self.send_header('Content-type', 'application/json')
                elif filename.endswith('.js'):
                    self.send_header('Content-type', 'application/javascript')
                elif filename.endswith('.ico'):
                    self.send_header('Content-type', 'image/x-icon')
                elif filename.endswith('.png'):
                    self.send_header('Content-type', 'image/png')
                else:
                    self.send_header('Content-type', 'text/html')
                self.end_headers()

                #Open file as binary and return as binary
                with open(filename, 'rb') as fh:
                    data = fh.read()
                    self.wfile.write(data)


            #Function to return an API endpoint
            def do_api(self):
                #Camera endpoint (single camera detection status)
                if(self.path.startswith('camera/')):
                    self.do_api_camera()
                #Camera Still endpoint
                elif(self.path.startswith('camerastill/')):
                    self.do_api_camerastill()
                #Cameras endpoint (array of camera statuses)
                elif(self.path.startswith('cameras')):
                    self.do_api_cameras()
                #Box List endpoint
                elif(self.path.startswith('boxes')):
                    self.do_api_boxes()
                #Other
                else:
                    self.do_error()

            #Function to return an error in HTML form
            def do_error(self):
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.return_string("<html><body>Not Found</body></html>")

            #Function to handle the cameras endpoint (array of camera statuses)
            def do_api_cameras(self):
                self.send_response(200)
                self.send_header('Content-type','application/json')
                self.end_headers()
                RtnData = []
                for Cam in server.Objs['CamCd']:
                    RtnData.append(Cam.CStatus)
                #JSON-ify the result
                self.return_string(json.dumps(RtnData))

            #Function to handle the camera endpoint (array of detections for one camera)
            def do_api_camera(self):
                #Strip the API endpoint so we can identify the camera name
                self.path = self.path.replace('camera/','')
                print("WEB: Identifying camera by name",self.path)
                #Check which camera it is
                RtnData = None
                for Cam in server.Objs['CamCd']:
                    if self.path.startswith(Cam.Name):
                        #Camera is valid, but results are not
                        if Cam.Results is None:
                            RtnData = {'Length':0}\
                        #Results are valid
                        else:
                            RtnData = {'Length':len(Cam.Results),'Results':Cam.Results}
                #If none, path wasn't found
                if RtnData is None:
                    self.do_error()
                    return
                #Otherwise, JSON-ify it
                self.send_response(200)
                self.send_header('Content-type','application/json')
                self.end_headers()      
                self.return_string(json.dumps(RtnData))    

            #Function to return a JPEG of the latest image from a camera
            def do_api_camerastill(self):
                 #Strip the API endpoint so we can identify the camera name
                self.path = self.path.replace('camerastill/','')
                print("WEB: Identifying camera by name for still",self.path)
                #Check which camera it is
                RtnData = None
                ImgFound = False
                for Cam in server.Objs['CamCd']:
                    if self.path.startswith(Cam.Name):
                        #Camera is correct
                        ImgFound = True
                        #Camera is correct and image is valid, convert image to bytes
                        if Cam.ImageColor is not None:
                            ImSuccess,RtnData = cv2.imencode(".jpeg",Cam.ImageColor)
                            if not ImSuccess:
                                RtnData = None

                #If ImgFound is false, return error
                if ImgFound == False:
                    self.do_error()
                    return
                #If RtnData is none, then the image was found to be invalid
                elif RtnData is None:
                    #Return 503 error if camera is offline
                    self.send_response(503)
                    self.end_headers()
                    return
                #Otherwise, return binary data
                self.send_response(200)
                self.send_header('Content-type','image/jpeg')
                self.end_headers()      
                self.wfile.write(RtnData.tobytes())   


            #Custom log_message which does absolutely nothing to stop logging all the requests
            def log_message(self, format, *args):
                return       

        print("WEB: Starting task")
        
        #Create server
        self.Server = HTTPServer((self.Host,self.Port),STWebServerHandler)

        #Run forever
        self.Server.serve_forever()

        #Finished running the webserver
        print("WEB: Stopped webserver")

    #Stop the webserver
    def stop(self):
        self.Server.server_close()