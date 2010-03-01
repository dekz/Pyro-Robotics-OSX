from pyrobot.camera.fake import FakeCamera
from pyrobot.vision.cvision import VisionSystem

def INIT(robot):
    return {"camera": FakeCamera(pattern = "vision/stereo/stereo-??.ppm",
                                 start = 1,
                                 stop = 7,
                                 visionSystem = VisionSystem())}
