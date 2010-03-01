# A Neural Network Brain
# D.S. Blank

from pyrobot.brain import Brain
from pyrobot.brain.conx import *
from pyrobot.gui.plot.scatter import Scatter
import pyrobot.system.share as share

class NNPredict(Brain):
   def setup(self):
      """ Create the network. """
      self.sensorCount = self.robot.range.count
      self.net = Network()
      self.net.addThreeLayers(self.sensorCount, 16, 2)
      self.net.initialize()
      self.net.setVerbosity(0)
      self.net.setEpsilon(0.5)
      self.net.setMomentum(.1)
      self.net.setLearning(1)
      self.trans = 0
      self.rotate = 0
      self.counter = 0
      self.maxvalue = self.robot.range.getMaxvalue()
      self.new = [self.scale(s.distance()) for s in self.robot.range["all"]]
      self.plot = Scatter(app=share.gui, linecount=2, connectPoints=0,
                          xEnd=10.0, yEnd=1.0, legend=["Trained", "Test"],
                          title="NN Generalization", width=400,
                          xLabel = "Distance to wall",
                          yLabel = "Speed")
      self.plot.addLine(0, .5, 10, .5, color = "green")
      self.min = 0.0
      self.robot.range._noise = [0.0] * self.robot.range.count
      #self.fp = open("train.dat", "w")
      
   def destroy(self):
      self.plot.destroy()
      
   def scale(self, val):
      return (val / self.maxvalue)           

   def teacher(self):
      # set targets   
      target_trans  = 1.0
      target_rotate = 0.5
      self.min = min([s.distance() for s in self.robot.range.span(20, -20)])
      if self.min < 3:
         target_trans = 0.5
      elif self.min < 4:
         target_trans = 0.65
      elif self.min < 5:
         target_trans = 0.8
      elif self.min < 6:
         target_trans = 0.95
      return [target_trans, target_rotate]

   def step(self):
      target = self.teacher()
      old = self.new 
      self.new = [self.scale(s.distance()) for s in self.robot.range["all"]]
      # results
      if self.net.learning:
         e, c, t, p = self.net.step(input=old, output=target)
         if self.counter % 10 == 0:
            print "error = %.2f" % e
         self.trans, self.rotate = target
         #self.fp.write(" ".join(map(lambda f: str(f), old)) +
         #              (" %f %f\n" % (target[0], target[1])))
      else:
         old = self.new + [self.trans, self.rotate] 
         self.net.step(input=old, output=target)
         self.trans, self.rotate = self.net['output'].activation
         if self.counter % 10 == 0:
            print self.trans, self.rotate
      colors= ["red", "blue"]
      self.plot.addPoint(self.min, self.trans, int(not self.net.learning),
                         color=colors[int(not self.net.learning)])
      self.robot.move((self.trans - .5)/2.0, (self.rotate - .5)/2.0)
      self.counter += 1

def INIT(engine):
   return NNPredict('NNPredict', engine)
      
