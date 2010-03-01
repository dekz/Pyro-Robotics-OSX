from pyrobot.brain import Brain
from pyrobot.tools import joystick
from time import sleep

class JoystickControl(Brain):

   def setup(self):
      self.stick = joystick.Joystick()

   def step(self):
      self.robot.move( self.stick.translate,
                            self.stick.rotate )

   def destroy(self):
      self.stick.destroy()

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (an engine), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return JoystickControl('JoystickControl', engine)
      
