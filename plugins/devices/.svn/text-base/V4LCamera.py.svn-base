from pyrobot.camera.v4l import V4LCamera
from pyrobot.vision.cvision import VisionSystem
from pyrobot.system.share import ask

def INIT(robot):
    retval = ask("Please enter the parameters for the Video4Linux Camera",
                 (("Device", "/dev/video0"),
                  ("Width", "160"),
                  ("Height", "120"),
                  ("Channel", "0"),                  
                  ))
    if retval["ok"]:
        return {"camera" : V4LCamera( int(retval["Width"]), 
                                      int(retval["Height"]), 
                                      device = retval["Device"],
                                      channel = int(retval["Channel"]), 
                                      visionSystem = VisionSystem())}
    else:
        raise "Cancelled!"
