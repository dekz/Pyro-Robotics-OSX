# A Pyro simple brain template

from pyrobot.brain import Brain
from pyrobot.brain.conx import Network
import time

class SimpleBrain(Brain):
   def setup(self):
      self.net = Network()
      self.net.addLayers(10,20,2) #ir inputs
      self.net.loadWeightsFromFile("trainedwts.wts")
      self.lastTran = 1
      
   # Only method you have to define is the step method:

   def step(self):
      x = self.robot.range.distance(unit = "SCALED")
      x.extend([self.robot.light[0][0].value, self.robot.light[0][1].value])
      output = self.net.propagate(input = x)
      self.robot.move(output[0], ((output[1]*2) - 1))
      time.sleep(1)

def INIT(engine):
   assert(engine.robot.hasA("sonar"))
   assert(engine.robot.hasA("light"))
   return SimpleBrain('SimpleBrain', engine)
      
