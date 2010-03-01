""" This is the FSM for the scavenger hunt, AAAI 2006. """

from pyrobot.brain.behaviors import State, FSMBrain
from pyrobot.simulators.pysim import *
import random, time

def avg(vector):
   """ Computes average of a vector of numbers. Works on all types of numbers. """
   return sum(vector)/float(len(vector))
      
class Start(State):
   """ Start state. Just an initialization state. """
   def setup(self):
      # turn on the devices, if not already on
      if not self.robot.hasA("frequency"):
         self.startDevice("Frequency")
      self.robot.frequency[0].setSampleTime(0.1)
      if not self.robot.hasA("camera"):
         self.startDevice("V4LCamera")
         self.startDevice("FourwayRot2")
      # clear the filters:
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[1].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      self.robot.camera[4].active = 0 # don't need this one
      # make some aliases:
      self.brain.frontCamera = self.robot.camera[2]
      self.brain.backCamera = self.robot.camera[1]
      self.brain.downCamera = self.robot.camera[3]
      # Back camera -----------------------------------------------
      self.brain.backCamera.addFilter("rotate",) # rotate it coz it is upside down!
      # filters:
      self.brain.backCamera.addFilter("match",140,135,78,)
      self.brain.backCamera.addFilter("match",240,234,172,)
      self.brain.backCamera.addFilter("match",186,182,119,)
      self.brain.backCamera.addFilter("blobify",0,255,255,0,1,1,1,)
      self.brain.backCamera.minBlob = 100
      # Front camera ----------------------------------------------
      # filters:
      self.brain.frontCamera.addFilter("match",155,149,85,)
      self.brain.frontCamera.addFilter("match",184,194,117,)
      self.brain.frontCamera.addFilter("match",217,243,170,)
      self.brain.frontCamera.addFilter("match",131,132,54,)
      self.brain.frontCamera.addFilter("match",255,255,219,)
      self.brain.frontCamera.addFilter("blobify",0,255,255,0,1,1,1,)
      self.brain.frontCamera.minBlob = 100      
   def step(self):
      # watch some vars:
      self.engine.gui.watch("brain.activeState.name")
      self.engine.gui.watch("brain.states['MaintainHeight'].distance")
      self.engine.gui.watch("brain.states['MaintainHeight'].old_amt")
      print "Here we go!"
      # start two states:
      self.goto("MaintainHeight")
      self.goto("Search")

class MaintainHeight(State):
   """ Maintains the height of the ballon. """
   def setup(self):
      self.targetDistance = 0.6 # meters
      self.distances = [0]*10
      self.distance = self.targetDistance # current height, start off about here
      self.pgain = 1.0
      self.igain = 0.0
      self.dgain = 0.0
      self.step_count = 0
      self.integral = 0.0
      self.old_diff = 0.0
      self.old_amt = 0.0
      self.deriv = 0.0
      self.pulseTime = 0.5
      self.dutyCycle = .3
      print "MaintainHeight:"
      print "  sleep between:", self.robot.frequency[0].asyncSleep
      print "  sampleTime:", self.robot.frequency[0].sampleTime
      sampleCount = 0
      print "  sample starting..."
      while sampleCount < len(self.distances):
         distance, freq, value, total, best, bestValue = self.robot.frequency[0].results
         if bestValue/total <= 0.15:
            self.distances[sampleCount] = distance
            sampleCount += 1
         time.sleep(.1)
      print "  sample done!"
         
   def step(self):
      distance, freq, value, total, best, bestValue = self.robot.frequency[0].results
      if bestValue/total <= 0.15:
         #bad data! what to do?
         return
      else:
         self.distance = distance
         #data must be good
         self.distances[self.step_count % len(self.distances)] = distance
         self.step_count += 1
         #proportional
         diff = self.targetDistance - distance
         #integral
         self.integral += diff
         #derivative
         self.deriv = diff - self.old_diff
         #correction amount
         amount = (self.integral*self.igain) + (self.deriv*self.dgain) + (diff*self.pgain)
         # get rid of "flat spot" where no signal will be sent:
         if((amount >= 0) and (amount <= 19)):
            amount += 19
         elif((amount < 0) and (amount >= -19)):
            amount -= 19
         amount = max(min(amount, 1.0), -1.0)
         self.old_amt = amount
         self.robot.moveZ(amount)
         time.sleep(.2)
         self.robot.moveZ(0) 
         time.sleep(.2)
         self.old_diff = diff

class Search(State): # looking through forward camera to find a fiducial
   def onGoto(self, args = []):
      self.trackFrontCount = 0
      self.trackBackCount = 0
      
   def step(self):
      # looks in the front, back, and down cameras for items of interest
      backResults  = self.brain.backCamera.filterResults[:] # copy results
      frontResults = self.brain.frontCamera.filterResults[:] # copy results
      backBlob = [data for data in backResults if type(data) == tuple][0][0] # get blob data
      frontBlob = [data for data in frontResults if type(data) == tuple][0][0] # get blob data
      # x1, y1, x2, x2, matches
      print frontBlob[4], backBlob[4]
      if frontBlob[4] > backBlob[4]:
         if frontBlob[4] > self.brain.frontCamera.minBlob:
            self.trackFrontCount += 1
            if self.trackFrontCount > 5:
               print "Track front"
               self.goto("Track", "front")
               return
      else:
         if backBlob[4] > self.brain.backCamera.minBlob:
            self.trackBackCount += 1
            if self.trackBackCount > 5:
               print "Track back"
               self.goto("Track", "back")
               return
      print "Still searching..."
      # we are still searching. let's rotate!
      rand = random.random()
      if rand < .33:
         self.robot.rotate(.2)
      elif rand < .66:
         self.robot.rotate(-.2)
      else:
         pass # don't move
      # burst fan
      time.sleep(.2)
      self.robot.rotate(0) # stop moving
      time.sleep(.5)

class Track(State):
   def onGoto(self, camera):
      self.trackCamera = camera
      
   def step(self):
      # if centered enough
      # go forward
      # if off a little
      # maybe turn a little
      time.sleep(5)
      # if we lose sight of it for too long
      self.goto("Search")

def INIT(engine): # passes in engine, if you need it
   brain = FSMBrain("Blimpy", engine)
   # add a few states:
   brain.add(Start(1))
   brain.add(MaintainHeight()) # will always be on after Start
   brain.add(Search())
   brain.add(Track())
   return brain

