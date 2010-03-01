from pyrobot.camera.blob import BlobCamera
from pyrobot.vision.cvision import VisionSystem

def INIT(robot):
    return {"camera": BlobCamera(robot, visionSystem = VisionSystem())}
