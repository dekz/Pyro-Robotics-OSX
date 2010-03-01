# A bare brain

from pyrobot.brain import Brain

class SimpleBrain(Brain):
   # Only method you have to define is the step method:

   def setup(self):
      # create any vars you need here
      print "Setup!"
      pass
   
   def step(self):
      #self.robot.move(0, -.2) # negative is to the right!
      pass

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (the robot), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain("SimpleBrain", engine)
      
