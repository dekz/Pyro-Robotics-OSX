# Some core/stock behaviors

from pyrobot.brain.behaviors import *
from math import sqrt

class StopBehavior (Behavior):
    def init(self):
        self.Effects('translate', 1) 
        self.Effects('rotate', 1)

    def update(self):
        self.IF(1, 'translate', 0)
        self.IF(1, 'rotate', 0)

class ForwardBehavior (Behavior):
    def init(self):
        self.Effects('translate', 1) 

    def update(self):
        self.IF(1, 'translate', 1)

class BackwardBehavior (Behavior):
    def init(self):
        self.Effects('translate', 1) 

    def update(self):
        self.IF(1, 'translate', -1)

class TurnLeftBehavior (Behavior):
    def init(self):
        self.Effects('rotate', 1)

    def update(self):
        self.IF(1, 'rotate', 1)        

class TurnRightBehavior (Behavior):
    def init(self):
        self.Effects('rotate', 1)

    def update(self):
        self.IF(1, 'rotate', -1)        

class StraightBehavior (Behavior):
    def init(self): # called when created
        self.Effects('translate', .1) 
        self.Effects('rotate', .1) 

    def update(self):
        self.IF(1, 'translate', .2) 
        self.IF(1, 'rotate', 0)

