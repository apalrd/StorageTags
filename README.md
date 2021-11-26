## Storage Tags
This project tracks objects in storage (physical storage!), by placing fiducial markers ('tags') on objects to be tracked, and using one or more fixed cameras to identify the location of each object

See [this blog post](https://www.apalrd.net/projects/2021/storage_tracker/) for more information.

### Dependencies
This project requires the following dependencies:
* [AprilTag](https://github.com/aprilrobotics/apriltag) - You must install this according to their instructions. Make sure the python bindings are available. 
* Python modules: opencv-contrib-python, paho-mqtt, pyyaml