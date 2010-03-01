from pyrobot.brain import Brain
import time

class BlimpBrain(Brain):
   def setup(self):
      if not self.robot.hasA("camera"):
         #self.startDevice("Frequency")
         #self.startDevice("V4LCamera0")
         self.startDevice("BlimpMovie")
         self.startDevice("FourwayRot2")
         self.robot.camera[1].addFilter("rotate",) # backview
         self.robot.camera[3].addFilter("fid")
         #self.robot.camera[3].addFilter("threshold",0,128,)
         #self.robot.camera[3].addFilter("threshold",1,128,)
         #self.robot.camera[3].addFilter("threshold",2,128,)
         #self.robot.camera[3].addFilter("threshold",11,20,)
         #self.robot.camera[3].addFilter("orientation",1.0,)

   def step(self):
      #self.robot.camera[3].apply("orientation",
      #self.robot.frequency[0].results[0])
      pass

def INIT(engine):
   return BlimpBrain("BlimpBrain", engine)
      
