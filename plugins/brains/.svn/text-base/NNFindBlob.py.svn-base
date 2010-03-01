# Brain used in conjunction with GAFindBlobNN.py to create a robot
# that chases after red objects.

# Network inputs: 8
# 4 virtual sonar sensors and 4 pieces of color blob info.
# Sonar values are the minimums of four groups:
# back, front-left, front-right, and front.

# The color blob info consists of the range to closest blob,
# and 3 nodes which code for direction of the closest blob:
# 100=left, 010=center, 001=right, and 000=none.
# All inputs are scaled between 0 and 1.

# Network outputs: 2
# Translate and rotate.

from pyrobot.brain import Brain
from pyrobot.brain.conx import *
from time import *

# The robot will get translate and rotate values in the range [-0.5,0.5],
# but the neural network will generate outputs in the range [0,1].
def toNetworkUnits(val):
   return (val + 0.5)

def toRobotUnits(val):
   return (val - 0.5)

class NNBrain(Brain):
   def setup(self, **args):
      self.net = Network()
      self.net.addThreeLayers(8,6,2)
      self.net.setLearning(0)
      if not self.robot.hasA("camera"):
         # Assume Stage, which uses the BlobCamera:
         self.robot.startDevice("BlobCamera")
         self.robot.camera[0].addFilter("match", 255, 0, 0)
         self.robot.camera[0].addFilter("blobify",0,255,255,0,1,1,1,)
      self.robot.range.units = "meters"
      self.robot.range.setMaxvalue(4.5) # about as far as sonar can see in room
      self.robot.range.units = "scaled"
      self.counter = 0
      self.currentInputs = [0] * 8

   def getBlobInfo(self, (x1, y1, x2, y2, pixels)):
      blobLeft, blobCenter, blobRight = (0.0, 0.0, 0.0)
      if (x1, y1, x2, y2) == (0.0, 0.0, 0.0, 0.0):
         return 0.0, blobLeft, blobCenter, blobRight
      # how close is the blob? how much of the view does it occupy?
      blobRange = (y2 - y1) / float(self.robot.camera[0].height)
      # where is the blob in the image?
      center = (x2 + x1) / 2.0
      # is it in the left third of view?
      if center < self.robot.camera[0].width/3.0: # left third
         blobLeft = 1.0
      # right third?
      elif center > 2.0 * self.robot.camera[0].width/3.0: # right third
         blobRight = 1.0
      # must be in center
      else:
         blobCenter = 1.0
      return blobRange, blobLeft, blobCenter, blobRight

   def getInputs(self):
      # get minimum values for each area:
      back =  min([s.distance() for s in self.robot.range["back"]])
      left  = min([s.distance() for s in self.robot.range["front-left"]])
      front = min([s.distance() for s in self.robot.range["front"]])
      right = min([s.distance() for s in self.robot.range["front-right"]])
      blobList = self.robot.camera[0].filterResults[1]
      if blobList  != []:
         blobRange, blobLeft, blobCenter, blobRight  = self.getBlobInfo(blobList[0]) # biggest blob
      self.currentInputs = [back, left, front, right, blobRange, blobLeft, blobCenter, blobRight]
      self.net['input'].copyActivations(self.currentInputs)

   def getOutputs(self):
      translate = toRobotUnits(self.net['output'].activation[0])
      rotate = toRobotUnits(self.net['output'].activation[1])
      return translate, rotate

   def step(self):
      print "adapter is stepping"
      self.robot.update()
      self.getInputs()
      self.net.propagate()
      translate, rotate = self.getOutputs()
      self.move(translate, rotate)
      self.counter += 1

def INIT(engine):
   return NNBrain('NNBrain', engine)
