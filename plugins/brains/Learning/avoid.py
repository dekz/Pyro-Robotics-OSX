# robot goes forward and then slows to a stop when it detects something 
  
from pyrobot.brain import Brain 
import random
  
class NNBrain(Brain): 
          
   # Give the front two sensors, decide the next move 
   def determineMove(self, sensors): 
      if sensors[2] < 0.5 or sensors[3] < 0.5:   # about to hit soon, STOP 
         print "collision imminent, stopped" 
         return(0) 
      elif sensors[2] < 0.8 or sensors[3] < 0.8:  # detecting something, SLOWDOWN 
         print "object detected" 
         return(0.1) 
      else: 
         print "clear"      # all clear, FORWARD 
         return(0.3)

   def determineTurn(self, sensors): 
      # return a value between -1 and 1 based on sensors:
      # left:
      if sensors[0] < 0.5 or sensors[1] < 0.5:
         return -1.0 # turn right
      # right:
      if sensors[4] < 0.5 or sensors[5] < 0.5:
         return 1.0 # turn left
      # front:
      if sensors[2] < 0.5 or sensors[3] < 0.5:
         return random.random() * 2.0 - 1.0
      # else don't turn
      return 0.0
     
   def step(self): 
      robot = self.getRobot()
      sensors = [x.value for x in robot.range['all']]
      translate = self.determineMove(sensors) 
      rotate = self.determineTurn(sensors) 
      print "front sensors", sensors[2], sensors[3] 
      robot.move(translate, rotate) 
        
def INIT(robot): 
   return NNBrain('NNBrain', robot) 
