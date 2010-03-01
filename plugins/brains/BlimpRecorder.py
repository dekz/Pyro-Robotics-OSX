from pyrobot.brain import Brain
from pyrobot.camera.v4l import V4LCamera
#from pyrobot.camera.fake import FakeCamera
from pyrobot.vision.cvision import VisionSystem
from pyrobot.camera.fourway import FourwayCamera
import time

def setupFourway(robot):
    if len(robot.camera) == 1:
        index = 0
    else:
        raise AttributeError, "you need a single camera already loaded"
    baseCamera = robot.camera[index]
    cameras = [0] * 4
    rotate = [0] * 4
    rotate[2] = 1
    for i in range(4):
        cameras[i] = FourwayCamera(baseCamera, 4, i, rotate[i])
    return [{"camera": cameras[0]},
            {"camera": cameras[1]},
            {"camera": cameras[2]},
            {"camera": cameras[3]}]

class BlimpRecorder(Brain):
    def setup(self):
        self.imageCount = 1
        if not self.robot.hasA("camera"):
            self.robot.startDevice("Frequency")
            self.robot.startDevice({"camera":
                                    V4LCamera(640,480,channel=0,
                                              visionSystem = VisionSystem())})
            self.robot.startDevice(setupFourway(self.robot))
            self.robot.camera[3].addFilter("grayScale")
      
    def step(self):
        print time.time(), self.robot.frequency[0].results
        self.robot.camera[0].vision.saveImage("cam0-%05d.pbm" % self.imageCount)
        self.imageCount += 1

def INIT(engine):
    return BlimpRecorder('BlimpRecorder', engine)
      
