from pyrobot.camera.v4l2 import V4L2Camera
from pyrobot.vision.cvision import VisionSystem
from pyrobot.system.share import ask

def INIT(robot):
    retval = ask("Please enter the parameters for the Video4Linux2 Camera",
                 (("Device", "/dev/video0"),
                  ("Width", "160"),
                  ("Height", "120"),
                  ("Channel", "0"),                  
                  ))
    if retval["ok"]:
        return {"camera" : V4L2Camera( int(retval["Width"]), 
                                      int(retval["Height"]), 
                                      device = retval["Device"],
                                      channel = int(retval["Channel"]), 
                                      visionSystem = VisionSystem())}
    else:
        raise "Cancelled!"
