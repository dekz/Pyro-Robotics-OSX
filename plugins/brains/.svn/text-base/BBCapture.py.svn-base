# A Behavior-based system

from pyrobot.brain.fuzzy import *
from pyrobot.brain.behaviors import *
from pyrobot.brain.behaviors.core import *  # Stop

import math
from random import random
import time

class Avoid (Behavior):
    def setup(self): # called when created
        self.Effects('translate', .1) 
        self.Effects('rotate', .1)
        self.lasttime = time.mktime(time.localtime())
        self.count = 0

    def direction(self, value):
        if value < 0:
            return -1
        else:
            return 1

    def update(self):
        FTOLERANCE = 1.0
        LTOLERANCE = 1.0
        RTOLERANCE = 1.0
        
        # Normally :
        #self.IF(1, 'translate', .2) 
        #self.IF(1, 'rotate', 0)
        
        left = min([s.distance() for s in self.robot.range["left"]])
        front = min([s.distance() for s in self.robot.range["front"]])
        right = min([s.distance() for s in self.robot.range["right"]])
        
        if (left < LTOLERANCE and right < RTOLERANCE):
            #self.move(0, .2)
            self.IF(1, 'rotate', .2)
            self.IF(1, 'translate', 0)
            #sleep(.5)
        elif (left < LTOLERANCE):
            #self.move(0, -.2)
            self.IF(1, 'rotate', -.2)
            self.IF(1, 'translate', 0)
        elif (right < RTOLERANCE):
            #self.move(0, .2)
            self.IF(1, 'rotate', .2)
            self.IF(1, 'translate', 0)
        elif (front < FTOLERANCE):
            if random() < .5:
                #self.move(0, .2)
                self.IF(1, 'rotate', .2)
                self.IF(1, 'translate', 0)
            else:
                #self.move(0, .2)
                self.IF(1, 'rotate', .2)
                self.IF(1, 'translate', 0)
        else:
            #self.move(.2, 0)
            self.IF(1, 'translate', .2)
            self.IF(1, 'rotate', 0)

class state1 (State):
    def setup(self):
        self.add(Avoid(1))
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
    def setup(self):
        self.add(StopBehavior(1))
        print "initialized state", self.name

    def update(self):
        print "State 2"
        self.goto("state3")

class state3 (State):
    def setup(self):
        print "initialized state", self.name
        self.count = 0

    def onActivate(self):
        self.count += 1

    def update(self):
        print "State 3"
        self.engine.camera.snap("som4/snap-%d.pgm" % self.count) # can name the file right here
        # save IR, motors
        fp = open("som4/snap-%d.dat" % self.count, "w")
        fp.write("translate=%f\n" % self.engine.history[2]['translate'])
        fp.write("rotate=%f\nspeed=" % self.engine.history[2]['rotate'])
        for s in self.engine.history[2]['speed']:
            fp.write("%d " % s)
        fp.write("\nir=")
        for s in self.engine.history[2]['ir']:
            fp.write("%d " % s)
        fp.write("\n")
        fp.close()
        self.goto("state1")

def INIT(engine): # passes in engine, if you need it
    assert (engine.robot.requires("range-sensor") and
            engine.robot.requires("continuous-movement"))
    brain = BehaviorBasedBrain({'translate' : engine.robot.translate, \
                                'rotate' : engine.robot.rotate, \
                                'update' : engine.robot.update }, engine)
    # add a few states:
    brain.add(state1()) # non active
    brain.add(state2()) # non active
    brain.add(state3()) # non active

    # activate a state:
    brain.activate('state1') # could have made it active in constructor

    brain.startService("camera")

    return brain

