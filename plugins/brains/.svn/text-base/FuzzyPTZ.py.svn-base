# A Fuzzy Logic PTZ Vision Tracker
# Uses Python-integrated Vision System

from pyrobot.brain.fuzzy import * 
from pyrobot.brain.behaviors import * 

class BBB(BehaviorBasedBrain):
    def destroy(self):
        print "robot=", self.robot
        self.removeDevice("ptz0")
  
class Track(Behavior): 
    def setup(self):
        # assumes that a camera device is already running!
        # we don't put it here, so that you can load whatever
        # type of camera you want: fake, blob, v4l, etc.
        self.camera = self.camera[0]
        self.camWidth = self.camera[0].width
        self.camHeight = self.camera[0].height
    def update(self):
        # match a reddish color:
        self.camera.apply("match", 144, 78, 76)
        # super color red:
        self.camera.apply("superColor", 1, -1, -1, 0, 128)
        # blobify all red:
        blob = self.camera.apply("blobify", 0, 255, 255, 0, 1, 1, 1)[0]
        # returns x1, y1, x2, y2, area
        if blob[4] > 200:
            cx = (blob[0] + blob[2]) / 2
            cy = (blob[1] + blob[3]) / 2
            self.IF(Fuzzy(0, self.camWidth ) << cx, 'pan',   5.0, "pan left") 
            self.IF(Fuzzy(0, self.camWidth ) >> cx, 'pan',  -5.0, "pan right") 
            self.IF(Fuzzy(0, self.camHeight ) << cy, 'tilt',-5.0, "tilt down") 
            self.IF(Fuzzy(0, self.camHeight ) >> cy, 'tilt', 5.0, "tilt up") 

class MyState(State): 
    def setup(self):
        self.add(Track(1, {'pan': 1, 'tilt': 1})) 

def INIT(engine):
    ptz = engine.startDevice("ptz"); 
    brain = BBB({'pan' : ptz.panRel,
                 'tilt': ptz.tiltRel,
                 'update' : engine.robot.update },
                engine) 
    brain.add(MyState(1)) # make it active
    return brain 
