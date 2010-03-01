# A Really bad example of Goto Office
# Thou shall not emulate this style... it is not reactive!
# You should make yours based on walls, doorways, etc.
# -dsb

from pyrobot.brain.fuzzy import *
from pyrobot.brain.behaviors import *
from pyrobot.brain.behaviors.core import *  # Stop
from pyrobot.geometry import distance

import math
from random import random
import time

# A Map to the office:

#           F
#           |
#           |
#           E----------------------------------D
#                                              |
#                                              |
#                                              |
#                                              |
#                                              |
#                                              |
#                                              |
#                                              |
#                                              |
#                                              |
#                       B----------------------C
#                       |
# Start ----------------A
#

class Straight (Behavior):
    def setup(self): 
        self.Effects('translate', .1) 
        self.Effects('rotate', .1) 

    def update(self):
        self.IF(1, 'translate', .2) 
        self.IF(1, 'rotate', 0) 

class TurnLeft (Behavior):
    def setup(self):
        self.Effects('translate', .2) 
        self.Effects('rotate', .1)

    def update(self):
        self.IF(1, 'rotate', .1)
        self.IF(1, 'translate', 0) 

class TurnRight (Behavior):
    def setup(self):
        self.Effects('translate', .2) 
        self.Effects('rotate', .1)

    def update(self):
        self.IF(1, 'rotate', -.1)
        self.IF(1, 'translate', 0) 

class Start (State):
    # go straight for 8 meters
    def setup(self):
        self.add(Straight(1))

    def onActivate(self): # method called when activated or gotoed
        self.startX = self.robot.x
        self.startY = self.robot.y
        
    def update(self):
        x = self.robot.x
        y = self.robot.y
        dist = distance( self.startX, self.startY, x, y) 
        if dist > 8.0:
            self.goto('A1')

class A1 (State):
    # turn left 90 degrees
    def setup(self):
        self.count = 0
        self.add(TurnLeft(1))

    def onActivate(self):
        self.th = self.robot.th

    def update(self):
        th = self.robot.th
        if angleAdd(th, - self.th) > 90: 
            self.goto('A2')

class A2 (State):
    # go straight for 1.5 meters
    def setup(self):
        self.add(Straight(1))

    def onActivate(self): # method called when activated or gotoed
        self.startX = self.robot.x
        self.startY = self.robot.y
        
    def update(self):
        x = self.robot.x
        y = self.robot.y
        dist = distance( self.startX, self.startY, x, y) 
        if dist > 1.5:
            self.goto('B1')

class B1 (State):
    # turn right 90 degrees
    def setup(self):
        self.count = 0
        self.add(TurnRight(1))

    def onActivate(self):
        self.th = self.robot.th

    def update(self):
        th = self.robot.th
        if angleEqual(angleAdd(th, -self.th), 270):
            self.goto('B2')
            
class B2 (State):
    # go straight for 6.5 meters
    def setup(self):
        self.add(Straight(1))

    def onActivate(self): # method called when activated or gotoed
        self.startX = self.robot.x
        self.startY = self.robot.y
        
    def update(self):
        x = self.robot.x
        y = self.robot.y
        dist = distance( self.startX, self.startY, x, y) 
        if dist > 6.5:
            self.goto('C1')

class C1 (State):
    # turn left 90 degrees
    def setup(self):
        self.count = 0
        self.add(TurnLeft(1))

    def onActivate(self):
        self.th = self.robot.th

    def update(self):
        th = self.robot.th
        if angleAdd(th, - self.th) > 90: 
            self.goto('C2')

class C2 (State):
    # go straight for 8 meters
    def setup(self):
        self.add(Straight(1))

    def onActivate(self): # method called when activated or gotoed
        self.startX = self.robot.x
        self.startY = self.robot.y
        
    def update(self):
        x = self.robot.x
        y = self.robot.y
        dist = distance( self.startX, self.startY, x, y) 
        if dist > 8.0:
            self.goto('D1')

class D1 (State):
    # turn left 90 degrees
    def setup(self):
        self.count = 0
        self.add(TurnLeft(1))

    def onActivate(self):
        self.th = self.robot.th

    def update(self):
        th = self.robot.th
        if angleAdd(th, - self.th) > 90: 
            self.goto('D2')
            
class D2 (State):
    # go straight for 12 meters
    def setup(self):
        self.add(Straight(1))

    def onActivate(self): # method called when activated or gotoed
        self.startX = self.robot.x
        self.startY = self.robot.y
        
    def update(self):
        x = self.robot.x
        y = self.robot.y
        dist = distance( self.startX, self.startY, x, y) 
        if dist > 12.0:
            self.goto('E1')

class E1 (State):
    # turn right 90 degrees
    def setup(self):
        self.count = 0
        self.add(TurnRight(1))

    def onActivate(self):
        self.th = self.robot.th

    def update(self):
        th = self.robot.th
        if angleAdd(self.th, -th) < 270: 
            self.goto('E2')
            
class E2 (State):
    # go straight for 2 meters
    def setup(self):
        self.add(Straight(1))

    def onActivate(self): # method called when activated or gotoed
        self.startX = self.robot.x
        self.startY = self.robot.y
        
    def update(self):
        x = self.robot.x
        y = self.robot.y
        dist = distance( self.startX, self.startY, x, y) 
        if dist > 2.0:
            self.goto('Done')

class Done(State):
    def update(self):
        self.move(0,0)

def INIT(engine): # passes in robot, if you need it
    brain = BehaviorBasedBrain({'translate' : engine.robot.translate, \
                                'rotate' : engine.robot.rotate, \
                                'update' : engine.robot.update }, engine)
    # add a few states:
    brain.add(Start(1)) # active
    brain.add(A1()) # non active
    brain.add(A2()) # non active
    brain.add(B1()) # non active
    brain.add(B2()) # non active
    brain.add(C1()) # non active
    brain.add(C2()) # non active
    brain.add(D1()) # non active
    brain.add(D2()) # non active
    brain.add(E1()) # non active
    brain.add(E2(1)) # active
    brain.add(Done()) # non active
    return brain
