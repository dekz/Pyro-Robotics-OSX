# A Pyrobot brain to clean up two rooms
# After Russell and Norvig AIMA

from pyrobot.brain import Brain

class CleanUp(Brain):
      
   def step(self):
      if self.robot.status == "dirty":
         self.robot.move("suck")
      elif self.robot.location == "A":
         self.robot.move("right")
      elif self.robot.location == "B":
         self.robot.move("left")

def INIT(engine):
   return CleanUp('AIMA', engine)
      
