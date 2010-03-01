# A Behavior sequencing sample
# D.S. Blank

# This Pyrobot example will go (roughly) in a square

# This example has two states, "edge" that goes straight, and "turn"
# that turns 90 degrees to the left. It bounces back and forth between
# these two states.

# Note how it uses onActivate() to remember where it was when it
# started in both cases. It then moves (forward or to the left) until
# it has moved enough.

# Exercises left to reader:

# 1. this doesn't avoid obstacles; what must you do to do that?

# 2. this relies completely on odometry for localization (ie, it uses
# dead reckoning); wouldn't it be better to add some type of
# landmark-based system, if landmarks are available?

# 3. This doesn't use very sophisticated behaviors for turning or
# moving. It would be better, for example, if the turning slowed down
# when it got closer to its desired angle. How would you do that?

# 4. If you wanted to traverse a map, you would need to have a
# different state for each position in the map. You could get around
# that by using the onGoto() and Goto() methods. But you would have to
# make the next state to goto a parameter that you pass in. Why?

from pyrobot.brain.fuzzy import *
from pyrobot.brain.behaviors import *
from pyrobot.geometry import *   # import distance function
import math
from random import random

class TurnLeftBehavior (Behavior):
    def setup(self):
        self.Effects('rotate', .1)
        self.Effects('translate', .1) 

    def update(self):
        self.IF(1, 'rotate', .1)
        self.IF(1, 'translate', 0)

class StraightBehavior (Behavior):
    def setup(self): # method called when created
        self.Effects('translate', .1) 
        self.Effects('rotate', .1) 

    def update(self):
        self.IF(1, 'translate', .1) 
        self.IF(1, 'rotate', 0)

class edge (State):
    def setup(self):
        self.add(StraightBehavior(1))

    def onActivate(self): # method called when activated or gotoed
        self.startX = self.robot.x
        self.startY = self.robot.y
        
    def update(self):
        x = self.robot.x
        y = self.robot.y
        dist = distance( self.startX, self.startY, x, y) 
        #print "actual = (%f, %f) start = (%f, %f); dist = %f" \
        #      % (x, y, self.startX, self.startY, dist)
        if dist > 1.0:
            self.goto('turn')

class turn (State):
    def setup(self):
        self.count = 0
        self.add(TurnLeftBehavior(1))

    def onActivate(self):
        self.th = self.robot.th

    def update(self):
        th = self.robot.th
        #print "actual = %f start = %f" % (th, self.th)
        if angleAdd(th, - self.th) > 90: 
            self.goto('edge')

def INIT(engine): # passes in engine, if you need it
    brain = BehaviorBasedBrain({'translate' : engine.robot.translate, \
                                'rotate' : engine.robot.rotate, \
                                'update' : engine.robot.update }, engine)
    # add a few states:
    brain.add(edge(1))
    brain.add(turn())
    return brain
