# A Pyro bare brain template

from pyrobot.brain import Brain

class MyBrain(Brain):
   def setup(self):
      # Called during construction
      # initialize your vars here
      pass
      
   # Only method you have to define is the step method:

   def step(self):
      # Called many times a second
      # [s.value for s in self.robot.range["all"]]
      translate, rotate = 0.5, 0.0
      self.robot.move(translate, rotate)

def INIT(engine):
   return MyBrain('MyBrain', engine)
      
