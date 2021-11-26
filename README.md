## Storage Tags
This project tracks objects in storage (physical storage!), by using fiducial markers ('tags') on the boxes and cameras to identify the location.

See [this blog post](https://www.apalrd.net/projects/2021/storage_tracker/) for more information.

### Dependencies
This project requires the following dependencies:
* [AprilTag](https://github.com/aprilrobotics/apriltag) - You must install this according to their instructions. Make sure the python bindings are available. 
* Python modules: opencv-contrib-python, paho-mqtt, pyyaml