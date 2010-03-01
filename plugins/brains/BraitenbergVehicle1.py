"""
Braitenberg Vehicle1
The more light sensed the faster the robot moves.
"""

from pyrobot.brain import Brain

class Vehicle(Brain):
   def setup(self):
      self.robot.light[0].units = "SCALED"
   def step(self):
      leftSpeed = max([s.value for s in self.robot.light[0]["left"]])
      rightSpeed = max([s.value for s in self.robot.light[0]["right"]])
      speed = (leftSpeed + rightSpeed)/2.0
      print "speed:", speed
      self.motors(speed,  speed) 

def INIT(engine):
   if engine.robot.type not in ['K-Team', 'Pyrobot']:
      raise "Robot should have light sensors!"
   return Vehicle('Braitenberg', engine)
      
