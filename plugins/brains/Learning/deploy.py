# Load in saved weights from offline training 
# Inputs are the two front sensor readings  
# Output is a translate value, used to control the robot  
   
from pyrobot.brain import Brain  
from pyrobot.brain.conx import *  
from time import *  
     
class NNBrain(Brain):  
   def setup(self):  
      self.n = Network()  
      self.n.addThreeLayers(8,1,2)  
      self.maxvalue = self.robot.range.getMaxvalue()
      self.doneLearning = 1  
      self.n.loadWeightsFromFile("E05M01.wts")  
      self.n.setLearning(0)  
 
   def scale(self, val):  
      return min(max(val / self.maxvalue, 0.0),1.0) 
 
   def step(self):  
      robot = self.getRobot()  
      # Set inputs  
      sensors = [x.value for x in robot.range["all"]]
      self.n.getLayer('input').copyActivations( map(self.scale, sensors) ) 
      self.n.propagate()  
      translateActual = self.n.getLayer('output').activation[0] * 2 - 1.0
      rotateActual = self.n.getLayer('output').activation[1]  * 2 - 1.0
      print "move", translateActual, rotateActual 
      robot.move(translateActual, rotateActual)  
   
def INIT(robot):  
   return NNBrain('NNBrain', robot)  
