""" Assumes that a camera[0] already exists """

from pyrobot.camera.fourway import FourwayCamera
from pyrobot.system.share import ask

def INIT(robot):
    if len(robot.camera) == 1:
        index = 0
    elif len(robot.camera) > 1:
        retval = ask("Please enter the index number of the camera to split 2 ways",
                     (("Index", "0"),))
        
        index = int(retval["Index"])
    else:
        raise AttributeError, "you need a camera already loaded"
    baseCamera = robot.camera[index]
    cameras = [0] * 2
    for i in range(2):
        cameras[i] = FourwayCamera(baseCamera, 2, i)
    return [{"camera": cameras[0]},
            {"camera": cameras[1]} ]
