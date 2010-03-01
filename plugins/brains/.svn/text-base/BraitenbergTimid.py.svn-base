"""
Braitenberg Timid

If an obstacle is within 1 robot unit of the robot, then the closer it
is on the left side the faster the left motor moves, and the closer it
is on the right side the faster the right motor moves.  Each motor is
also given a small positive constant value.  Together, this causes the
robot to be able to navigate a maze, if there is is an open path.
When the robot encounters a dead end, it cannot turn around.  Try this
with the LongHall world.

"""

from pyrobot.brain import Brain, avg

class Vehicle(Brain):
   def setup(self):
      self.robot.range.units = "ROBOTS"
      self.constant = 0.1
   def step(self):
      left  = min([s.value for s in self.robot.range["front-left"]])
      right = min([s.value for s in self.robot.range["front-right"]])
      leftSpeed = self.constant
      rightSpeed = self.constant
      if left < 1.0-self.constant and left < right:
         leftSpeed = 1.0 - left
      if right < 1.0-self.constant and right < left:
         rightSpeed = 1.0 - right
      print "leftSpeed, rightSpeed:", leftSpeed, rightSpeed
      self.motors(leftSpeed,  rightSpeed) 

def INIT(engine):
   if engine.robot.type not in ['K-Team', 'Pyrobot']:
      raise "Robot should have light sensors!"
   return Vehicle('Braitenberg2a', engine)
      
