# A bare brain

from pyrobot.brain import Brain

class SimpleBrain(Brain):
   # Only method you have to define is the step method:

   def step(self):
      TOLERANCE = 1.0

      left = min([s.distance() for s in self.robot.range["left"]])
      right = min([s.distance() for s in self.robot.range["right"]])
      front = min([s.distance() for s in self.robot.range["front"]])

      #print "left", left, "front", front, "right", right

      if (left < TOLERANCE and right < TOLERANCE):
         self.robot.move(0, .2)
      elif (right < TOLERANCE):
         self.robot.move(0, .2)
      elif (left < TOLERANCE):
         self.robot.move(0, -.2)
      elif (front < TOLERANCE): 
         self.robot.move(0, .2) # arbitrarily turn one way
      else:
         self.robot.move(.2, 0)

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (the robot), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain('SimpleBrain', engine)
      
