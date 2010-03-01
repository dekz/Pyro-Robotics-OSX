from pyrobot.camera.fake import FakeCamera
from pyrobot.vision.cvision import VisionSystem

def INIT(robot):
    return {"camera": FakeCamera(pattern = "vision/blimp/hall-?.pbm",
                                 start = 1,
                                 stop = 9,
                                 interval = 1,
                                 visionSystem = VisionSystem())}
