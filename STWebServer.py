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
                return

            #Function to return an API endpoint
            def do_api(self):
                return

            #Function to return an error
            def do_error(self):
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.return_string("<html><body>Not Found</body></html>")

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