"""
Braitenberg Vehicle4
The motors' dependency on the sensors can be some non-linear function,
such as a gaussian or a step function.  When two light sources are
present and the step function is used, this vehicle will circle the
the two lights, slowing down when it approaches them. 
"""

from pyrobot.brain import Brain
from math import *

def gaussian(x, a=1.0, b=0.5, c=0.4):
    """
    The height is determined by a.
    The peak is centered at b.
    The width is determined by c.
    """
    v = (x-b)**2
    return a*e**(-v/c**2)

def step(x):
   if x<0.2 or x>0.8:
      return 0.1
   if x<0.4 or x>0.6:
      return 0.7
   else:
      return 1.0

class Vehicle(Brain):
   def setup(self):
      self.robot.light[0].units = "SCALED"
   def step(self):
      leftSpeed = step(max([s.value for s in self.robot.light[0]["right"]]))
      rightSpeed = step(max([s.value for s in self.robot.light[0]["left"]]))
      print "leftSpeed, rightSpeed:", leftSpeed, rightSpeed
      self.motors(leftSpeed,  rightSpeed) 

def INIT(engine):
   if engine.robot.type not in ['K-Team', 'Pyrobot']:
      raise "Robot should have light sensors!"
   return Vehicle('Braitenberg', engine)
      
