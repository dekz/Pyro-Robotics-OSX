from pyrobot.camera.fake import FakeCamera
from pyrobot.vision.cvision import VisionSystem

def INIT(robot):
    return {"camera": FakeCamera(pattern = "vision/tutorial/test-?.ppm", start = 0,
                                 stop = 11, interval = 1, visionSystem = VisionSystem())}
