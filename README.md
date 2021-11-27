## Storage Tags
This project tracks objects in storage (physical storage!), by placing fiducial markers ('tags') on objects to be tracked, and using one or more fixed cameras to identify the location of each object

See [this blog post](https://www.apalrd.net/projects/2021/storage_tracker/) for more information.

### Current Status
The project is currently in development. Contributions are welcome, especially frontend development.

The following features currently work:
* RTSP based camera stream input and decoding using a single class of AprilTag for multiple cameras
* MQTT publishing of detections per camera


The following features are currently in development:
* API to return the same data published to MQTT over an HTTP socket
* API to return the images captured by the camera
* Web-based UI to view camera and detection status


The following features are planned but not yet started:
* Database to store box metadata, last known location, and associate boxes with AprilTag IDs
* Web UI and API endpoints for associated box data
* Web UI to view / filter boxes and determine the location
* Web UI to manage / add / delete boxes and reassociate them with new AprilTags
* Web UI to print a sheet of one or more AprilTags which are not currently in use, so they can be later associated
* MQTT publishing of box-based data in addition to camera-based data (esp. boxes currently found / not found, shelf / row / column)


### Dependencies
This project requires the following dependencies:
* [AprilTag](https://github.com/aprilrobotics/apriltag) - You must install this according to their instructions. Make sure the python bindings are available. 
* Python modules: opencv-contrib-python, paho-mqtt, pyyaml