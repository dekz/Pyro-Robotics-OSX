""" Needs two cameras. """

from pyrobot.camera.stereo import StereoCamera
from pyrobot.system.share import ask

def INIT(robot):
    retval = ask("Please enter the index numbers of the left and right cameras",
                 (("Left", "0"),
                  ("Right", "1"),
                  ))
    left = int(retval["Left"])
    right = int(retval["Right"])
    leftCamera = robot.camera[left]
    rightCamera = robot.camera[right]
    return {"camera": StereoCamera(leftCamera, rightCamera)}
