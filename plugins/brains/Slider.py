"""
D.S. Blank
"""

from pyrobot.brain import Brain
from pyrobot.tools.slider import Slider

class Controller(Brain):
   def setup(self):
      self.translate = Slider("Translate", -1, 1)
      # you can swap the pos and neg sides, like this:
      self.rotate = Slider("Rotate", 1, -1)
      # this helps driving, because neg is to the right

   def step(self):
      self.robot.move(self.translate.getValue(), \
                      self.rotate.getValue() ) # to the left

   def destroy(self):
      self.translate.destroy()
      self.rotate.destroy()

def INIT(engine):
   return Controller('Slider', engine)
      
