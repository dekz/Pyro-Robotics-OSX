# A bare robot and brain

from pyrobot.robot.simple import *

class bareEngine:
   def __init__(self):
      self.status = 1
      self.robot = SimpleRobot()

   def step(self):
      print "step!"

   def run(self, list = []):
      while self.status == 1:
         self.step()

def init():
   return bareEngine()
      
