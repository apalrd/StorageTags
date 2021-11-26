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

class STWebServer():