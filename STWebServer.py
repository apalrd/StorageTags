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

#Request Handling class
class STWebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

#Web Server glass
class STWebServer():
    def __init__(self,WebConfig):
        print("WEB: Config is ",WebConfig)