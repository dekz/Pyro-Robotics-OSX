
"""

Braitenberg vehicle


"""

from pyrobot.brain import Brain, avg

import math
import types

#squashing function
def logsig(x):
   if (type(x) is types.IntType) or (type(x) is types.FloatType):
      y = 1/(1+math.exp(-x))
   else: # list type
      y = [1/(1+math.exp(-xi)) for xi in x]
   return y


class Vehicle(Brain):
   def setup(self):
      self.slope = 8
      self.rotSpeedFactor = 3

   def step(self):
      self.stepHateRed()

   def stepHateRed(self):
      #self.robot.light[0]  represents the pair of light sensors
      leftLightSensor = self.robot.light[0]["left"][0]
      rLeft,gLeft,bLeft = leftLightSensor.rgb
      rightLightSensor = self.robot.light[0]["right"][0]
      rRight,gRight,bRight = rightLightSensor.rgb
      leftSpeed = logsig(self.slope*(rRight/255.0 -0.8))
      rightSpeed = logsig(self.slope*(rLeft/255.0 -0.8))
      #print "rLeft:", rLeft, "rRight:", rRight
      print "rightSpeed-leftSpeed:", rightSpeed-leftSpeed
      #print "rLeft:", rLeft, "rRight:", rRight
      totalLightValue = leftLightSensor.value+rightLightSensor.value
      weightedRotationSpeed =  self.rotSpeedFactor *(rightSpeed-leftSpeed)
      print "lin,rot speeds = ", totalLightValue, weightedRotationSpeed
      self.move(totalLightValue,weightedRotationSpeed )
      #self.motors(leftSpeed,  rightSpeed)


def INIT(engine):
   if engine.robot.type not in ['K-Team', 'Pyrobot']:
      raise "Robot should have light sensors!"
   return Vehicle('Braitenberg2a', engine)
      

## + + + + + + + +  CODE CEMETARY  + + + + + + + +
##
##      leftSpeed = rRight/255.0
##      rightSpeed = rLeft/255.0

##      rMean = (rLeft+rRight)*0.5;
##      leftSpeed = (rRight-rMean)/255.0 +0.1
##      rightSpeed = (rLeft-rMean)/255.0 +0.1
