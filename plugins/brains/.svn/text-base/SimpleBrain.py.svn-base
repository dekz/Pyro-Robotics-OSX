# A bare brain

from pyrobot.brain import Brain
from time import sleep

class SimpleBrain(Brain):

   def setup(self, **args):
      print "Loading arg: '%s'" % args.get('my_arg')
      # initialize your vars here!
      
   # Only method you have to define is the step method:

   def step(self):
      # do something here!
      # self.robot.move(translate, rotate)
      print "running..."
      #sleep(1)

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (an engine), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain('SimpleBrain', engine, my_arg = "testing")
      
