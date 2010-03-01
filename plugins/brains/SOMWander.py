# A Behavior-based system

from pyrobot.brain.fuzzy import *
from pyrobot.brain.behaviors import *
from pyrobot.brain.behaviors.core import *  
from pyrobot.brain.som import *

import math
from random import random
import time
import struct

class DriveIt (Behavior):
    def init(self): # called when created
        self.Effects('translate', .3) 
        self.Effects('rotate', 1)
        self.behaviorEngine.som_translate = 0
        self.behaviorEngine.som_rotate = 0

    def update(self):
        self.IF(1, 'translate', self.behaviorEngine.som_translate)
        self.IF(1, 'rotate', self.behaviorEngine.som_rotate)
        print "Setting Translate = ", self.behaviorEngine.som_translate
        print "Setting Rotate = ", self.behaviorEngine.som_rotate

class state1 (State):
    def init(self):
        self.add(DriveIt(1))
        print "initialized state", self.name

    def onActivate(self):
        self.count = 0

    def update(self):
        print "State 1"
        if self.count == 0:
            self.goto("state2")
        else:
            self.count += 1

class state2 (State):
    def init(self):
        self.add(StopBehavior(1))
        print "initialized state", self.name

    def update(self):
        print "State 2"
        # save the current readings
        self.behaviorEngine.history[1]['speed'] = self.behaviorEngine.robot.senseData['speed']
        self.behaviorEngine.history[1]['ir'] = self.behaviorEngine.robot.senseData['ir']
        self.goto("state3")

class state3 (State):
    def init(self):
        print "initialized state", self.name
        self.som = SOM("/home/dblank/html/som/som.cod")
        #self.som = SOM("/home/dblank/html/som/mot.cod")
        self.count = 0

    def onActivate(self):
        self.count += 1

    def p5toVec(self, filename, vec, x):
        fp = open(filename, "r")
        line1 = fp.readline()
        line2 = fp.readline()
        line3 = fp.readline()
        c = fp.read(1)
        while (c):
            vec[x] = (float(struct.unpack('h', c + '\x00')[0]) / 255.0)
            x += 1
            c = fp.read(1)

    def update(self):
        print "State 3"
        self.behaviorEngine.camera.snap("/tmp/temp.pgm")

        sensorVec = {}
        sv = 0
        # make vector from inputs
        sensorVec[sv] = self.behaviorEngine.history[2]['translate']
        sv += 1
        sensorVec[sv] = self.behaviorEngine.history[2]['rotate'] 
        sv += 1
        sensorVec[sv] = self.behaviorEngine.history[2]['speed'][0] 
        sv += 1
        sensorVec[sv] = self.behaviorEngine.history[2]['speed'][1] 
        sv += 1
        for s in self.behaviorEngine.history[2]['ir']:
            sensorVec[sv] = int(s)
            sv += 1

        self.p5toVec("/tmp/temp.pgm", sensorVec, sv)
        #self.p5toVec("/home/dblank/html/som/data/snap-1.pgm", sensorVec, sv)

        # find closest model vector
        outVec = self.som.findModel(sensorVec)

        print "translate =", outVec[0]
        print "rotate =", outVec[1]

        print "set translate to=", outVec[0] * float(self.som.max_translate - self.som.min_translate) + self.som.min_translate

        print "set rotate to=", outVec[1] * float(self.som.max_rotate - self.som.min_rotate) + self.som.min_rotate

        self.behaviorEngine.som_translate = outVec[0] * float(self.som.max_translate - self.som.min_translate) + self.som.min_translate
        self.behaviorEngine.som_rotate = outVec[1] * float(self.som.max_rotate - self.som.min_rotate) + self.som.min_rotate
        # go!
        self.goto("state1")

def INIT(engine): # passes in robot, if you need it
    brain = BehaviorBasedBrain({'translate' : engine.robot.translate, \
                                'rotate' : engine.robot.rotate, \
                                'update' : engine.robot.update }, engine)
    # add a few states:
    brain.add(state1()) # non active
    brain.add(state2()) # non active
    brain.add(state3()) # non active

    # activate a state:
    brain.activate('state1') # could have made it active in constructor
    brain.init()

    import pyrobot.camera
    brain.camera = pyrobot.camera.Camera()

    return brain
