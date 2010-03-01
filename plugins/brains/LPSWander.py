# A bare brain with a Local Perceptual View

from pyrobot.brain import Brain
from random import random
from time import sleep
from pyrobot.map.lps import LPS
from pyrobot.map.gps import GPS
from pyrobot.tools.joystick import Joystick

class SimpleBrain(Brain):
   def setup(self):
      # create the Local Perceptiual Space window
      units = self.robot.range.units
      self.robot.range.units = 'MM'
      sizeMM = self.robot.range.getMaxvalue() * 3 + \
               self.robot.radius
      self.robot.range.units = units
      self.lps = LPS( 20, 20,
                      widthMM = sizeMM,
                      heightMM = sizeMM)
      self.gps = GPS(400, 300, widthMM = sizeMM * 5, heightMM = sizeMM * 5)
      self.stick = Joystick()
   
   def destroy(self):
      self.lps.destroy()
      self.gps.destroy()
      self.stick.destroy()
   
   def step(self):
      robot = self.robot
      self.lps.reset() # reset counts
      self.lps.sensorHits(robot, 'range')
      self.lps.redraw()
      self.gps.updateFromLPS(self.lps, robot)
      self.gps.redraw()
      self.robot.move( self.stick.translate, self.stick.rotate)
   
# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (the robot), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain('SimpleBrain', engine)
      
