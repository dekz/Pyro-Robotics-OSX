# A bare brain

from pyrobot.brain import Brain

class SimpleBrain(Brain):
   # Only method you must define is the step method:

   def setup(self):
      # create any vars you need here
      pass

   def destroy(self):
      # if you need to del or destroy items, do it here
      pass

   def step(self):
      #self.robot.move(0, -.2) # negative is to the right!
      print "IR : ----------------------------"
      print "Min distance:", min([s.distance() for s in self.robot.range["all"]])
      print "Max distance:", max([s.distance() for s in self.robot.range["all"]])

# -------------------------------------------------------
# This is the interface for calling from the gui.
# Takes one param (the engine), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain("SimpleBrain", engine)
      
