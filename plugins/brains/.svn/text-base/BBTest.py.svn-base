# A Behavior-based system

from pyrobot.brain.fuzzy import *
from pyrobot.brain.behaviors import *

class beh1 (Behavior):
    def setup(self): # called when created
        print "---setupializing", self.name, "..."
        self.Effects('translate', .6) # default values
        self.Effects('rotate', .6) # now we don't have to set them again

    def onActivate(self):
        pass
      
    def update(self):
        fuzz = Fuzzy(5, 100)
        print "---updating", self.name, "..."
        self.IF(Fuzzy(0, 1) >> 0, 'rotate', .96) # can set default amount
        self.IF(1.0, 'rotate', .5)
        self.IF(Fuzzy(5, 6) >> 6.5, 'rotate', .5)
        self.IF(1.0, 'translate', .5)
        print "---done updating"

class beh2 (Behavior):
    def setup(self):
        print "---setupializing", self.name, "..."
        
    def onActivate(self):
        self.Effects('translate', 0.75) # default values
        self.Effects('rotate', 0.75)

    def onDeactivate(self):
        print 'heading out...'

    def update(self):
        print "---updating", self.name, "..."
        self.Effects('rotate', .7) # change affector on fly
        self.IF(.5, 'translate', 0.1)
        self.IF(1.0, 'rotate', 0.2)
        self.IF(1.0, 'rotate', 0.4)
        print "---done updating"

class state1 (State):
    def setup(self):
        self.add(beh1(1))
        self.add(beh2(1))
        self.add(beh2(1, {}, 'beh3'))
        print "setupialized state", self.name

    def onActivate(self):
        self.count = 0

    def onDeactivate(self):
        # make motors stop FIX!
        print 'heading out of state1...'

    def update(self):
        print "Updating state1..."
        # let's count till ten and then let's change state
        self.count = self.count + 1
        if self.count == 10:
            self.goto('state_empty')
        print "Finished executing step number  ",self.count
       
class state_empty (State):
    def onActivate(self): # called when it gets activated
        self.count = 0
        print "Activating state_empty!"

    def onDeactivate(self):
        print 'heading out of state_empty...'

    def update(self):
        print "Updating Empty state"
        # let's count till 10 and then let's change state
        self.count = self.count + 1
        if self.count == 10:
            self.goto('state1') # fork states, one with args:
            self.goto('state3', self.count, self.count + 1, \
                      self.count + 2) # it's ok if it is already active
        print "Finished executing step number  ",self.count

class state3 (State):
    def setup(self):
        self.add(beh1())
        self.x = 0
        self.y = 0
        self.z = 0         

    def onGoto(self, argv): # argv is optional unless you pass vars
        if len(argv) == 3:
            print 'x =', argv[0]
            print 'y =', argv[1]
            print 'z =', argv[2]
            self.x = argv[0]
            self.y = argv[1]
            self.z = argv[2]

    def onDeactivate(self):
        print 'heading out of state3...'

    def update(self):
        print "State1 status =", self.getState('state1').status
        print "Updating State3!"

def INIT(engine): # passes in engine, if you need it
    brain = BehaviorBasedBrain({'translate' : engine.robot.translate, \
                                'rotate' : engine.robot.rotate, \
                                'update' : engine.robot.update }, engine)
    # add a few states:
    brain.add(state1()) # non active
    brain.add(state1(0, 'state2')) # not active, name
    brain.add(state_empty())
    brain.add(state3())
    # activate a state:
    brain.activate('state1') # could have made it active in constructor
    return brain

