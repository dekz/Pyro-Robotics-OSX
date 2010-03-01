from pyrobot.brain import Brain
import time
import random

class SubsumptionBehavior:
    def __init__(self):
        self.translate = 0
        self.rotate = 0
        self.flag = 0

    def move(self, translate, rotate):
        self.translate = translate
        self.rotate = rotate
        self.flag = 1
        
class SubsumptionBrain(Brain):
    def setup(self):
        self.behaviors = []

    def add(self, behavior):
        behavior.robot = self.robot
        self.behaviors.append( behavior )

    def step(self):
        b = self.updateAll()
        print "%s is in control" % self.behaviors[b].__class__.__name__
        self.robot.move(self.behaviors[b].translate,
                        self.behaviors[b].rotate)
        time.sleep(1)

    def updateAll(self):
        # for all except lowest:
        for b in range(len(self.behaviors) - 1, 0, -1):
            self.behaviors[b].flag = 0
            self.behaviors[b].update()
            # if it fired, return number:
            if self.behaviors[b].flag:
                return b
        # if none fired, return lowest:
        self.behaviors[0].update()
        return 0

# -----------------------------------------------------

class Wander(SubsumptionBehavior):
    def update(self):
        self.move( .2, random.random() * 2 - 1)

class Avoid(SubsumptionBehavior):
    def update(self):
        if min([s.distance() for s in self.robot.range["front-all"]]) < 1:
            self.move( -.2, 0)

def INIT(engine):
    subsumption = SubsumptionBrain( "SubsumptionBrain", engine )
    # add behaviors, lowest priorities first:
    subsumption.add( Wander() )
    subsumption.add( Avoid() )
    return subsumption
