# A Behavior-based control system

from pyrobot.brain.fuzzy import *
from pyrobot.brain.behaviors import *
import math, time

class Avoid (Behavior):
    """Avoid Class"""
    def setup(self): # called when created
        """setup method"""
        self.lasttime = time.time()
        self.count = 0

    def direction(self, dir):
        """ computes opposite direction given an angle"""
        if dir < 0.0:
            return 0.3
        else:
            return -0.3

    def update(self):
        if self.count == 50:
            currtime = time.time()
            self.count = 0
            self.lasttime =  time.time()
        else:
            self.count += 1
        close_dist, angle = min( [(s.distance(), s.angle(unit="radians")) for s in self.robot.range["front-all"]])
        max_sensitive = self.robot.range.getMaxvalue() * 0.8
        self.IF(Fuzzy(0.1, max_sensitive) << close_dist, 'translate', 0.0, "TooClose")
        self.IF(Fuzzy(0.1, max_sensitive) >> close_dist, 'translate', 0.3, "Ok")
        self.IF(Fuzzy(0.1, max_sensitive) << close_dist, 'rotate', self.direction(angle), "TooClose")
        self.IF(Fuzzy(0.1, max_sensitive) >> close_dist, 'rotate', 0.0, "Ok")

class TurnAround(State):
    def update(self):
        if min([s.distance() for s in self.robot.range["front-all"]]) < 1.0:
            self.move(0, .2)
        else:
            self.goto("state1")

class state1 (State):
    """ sample state """
    def setup(self):
        self.add(Avoid(1, {'translate': .3, 'rotate': .3}))
        print "initialized state", self.name
    def update(self):
        if min([s.distance() for s in self.robot.range["front-all"]]) < 1: 
            self.goto("TurnAround")

def INIT(engine): # passes in robot, if you need it
    brain = BehaviorBasedBrain({'translate' : engine.robot.translate, \
                                'rotate' : engine.robot.rotate, \
                                'update' : engine.robot.update }, engine)
    # add a few states:
    brain.add(state1()) # non active
    brain.add(TurnAround()) # non active

    # activate a state:
    brain.activate('state1') # could have made it active in constructor
    return brain
