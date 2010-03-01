from pyrobot.brain import Brain 
from time import *
import random
  
######################################################
def saveListToFile(ls, file): 
   for i in range(len(ls)): 
      file.write(str(ls[i]) + " ") 
   file.write("\n") 
######################################################
  
class CollectDataBrain(Brain): 
   
   ######################################################
   def setup(self): 
      self.counter = 0 
      self.countstopping = 0 
      self.datafile1 = open("sensors.dat", "w") 
      self.datafile2 = open("targets.dat", "w") 
      self.maxvalue = self.robot.range.getMaxvalue()
      print "max sensor value is ", self.maxvalue 
   ######################################################
 
   def determineMove(self, sensors): 
      if sensors[2] < 0.5 or sensors[3] < 0.5: 
         print "collision imminant" 
         self.countstopping = self.countstopping+1 
         return(0) 
      elif sensors[2] < 0.8 or sensors[3] < 0.8: 
         print "object detected" 
         return(0.1) 
      else: 
         print "clear" 
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

   ######################################################
   def scale(self, val): 
      return min(max(val / self.maxvalue, 0.0),1.0)
   ######################################################

   def step(self): 
      robot = self.getRobot()
      sensors = [x.value for x in robot.range['all']]
      translate = self.determineMove(sensors) 
      rotate = self.determineTurn(sensors) 
      print "front sensors", sensors[2], sensors[3] 
      if self.counter > 1000: 
         self.datafile1.close() 
         self.datafile2.close() 
         print "done collecting data" 
         robot.stop()
         self.quit()
      elif self.countstopping > 5: 
         robot.move(-0.3, 0.2) 
         sleep(0.5) 
         self.countstopping = 0 
      else: 
         print "move", self.counter, translate, rotate
         saveListToFile( map(self.scale, sensors), self.datafile1) 
         saveListToFile(map( lambda x: (x + 1)/2.0, [translate, rotate]),
                        self.datafile2) 
         robot.move(translate, rotate)
         self.counter += 1 
        
def INIT(robot): 
   return CollectDataBrain('CollectDataBrain', robot) 
