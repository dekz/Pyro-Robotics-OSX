from pyrobot.camera.fake import FakeCamera
from pyrobot.vision.cvision import VisionSystem

def INIT(robot):
    return {"camera": FakeCamera(pattern = "vision/tutorial2/?.ppm", start = 1,
                                 stop = 10, interval = 1, visionSystem = VisionSystem())}
