from pyrobot.brain import Brain
from pyrobot.gui.plot.scatter import *
from random import random
from time import sleep
from math import sqrt, fabs, floor

from OpenGL.Tk import *

# some test data for offline work:
# a difference matrix:
data = [[0, 0.85162, 1.1705, 1.16898, 1.13626, 1.02382, 1.02108, 0.92296, 1.03327, 1.12973, 1.17869, 1.27797, 1.44365, 1.35182, 1.0667, 0.32486],
        [0, 0, 0.57832, 0.82448, 1.2327, 1.2223, 1.1779, 1.15408, 1.15861, 1.02119, 1.01911, 0.99189, 1.14645, 1.25696, 1.21544, 0.97718],
        [0, 0, 0, 0.51826, 0.96656, 1.13812, 1.1872, 1.2268, 1.22425, 1.07375, 0.95339, 0.88097, 1.04973, 1.26618, 1.24508, 1.28552],
        [0, 0, 0, 0, 0.7447, 1.01882, 1.17506, 1.21854, 1.25219, 1.16075, 1.06309, 0.86337, 0.98763, 1.1755, 1.33068, 1.23092],
        [0, 0, 0, 0, 0, 0.60992, 0.97836, 0.9507, 1.10329, 1.31973, 1.26875, 0.99859, 1.00877, 1.01182, 1.04522, 1.17952],
        [0, 0, 0, 0, 0, 0, 0.66822, 0.9757, 1.14735, 1.25217, 1.22617, 1.14443, 1.07133, 0.99356, 1.034, 1.04802],
        [0, 0, 0, 0, 0, 0, 0, 0.90886, 1.01515, 1.28035, 1.27681, 1.19291, 1.18413, 1.03972, 0.88406, 0.92036],
        [0, 0, 0, 0, 0, 0, 0, 0, 0.43665, 1.12803, 1.32311, 1.31291, 1.27895, 1.15522, 0.9602, 0.85752],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0481, 1.23462, 1.17394, 1.23808, 1.18885, 1.08355, 0.94339],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.552, 0.99686, 1.23766, 1.37767, 1.31309, 1.20307],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.63242, 1.0932, 1.38771, 1.37423, 1.28383],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.61038, 1.08169, 1.23097, 1.27565],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.67671, 1.05147, 1.44325],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.6813, 1.1955],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.93454],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

def distance(x1, y1, x2, y2):
   return sqrt( (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
   
class Relax:
   def __init__(self, num):
      self.point_x = []
      self.point_y = []
      self.num = num
      self.time = 0.0
      self.maxtime = 1000.0
      self.scatter = Scatter(title = 'The Kuipers Experiment',
                             history = [16], linecount = 1, width=400, height=300,
                             legend = ["16th Sonar Sensor"],
                             xStart=-2, xEnd = 3,
                             yStart=-2, yEnd = 3)
      for i in range(num):
         self.point_x.append(random())
         self.point_y.append(random())
      self.graph()

   def step(self, diff):
      incr = 0.1
      self.time += 1.0
      temp = .01 # 1.0 - (self.time / self.maxtime)  # .05 # need a temp schedule
      for i in range(self.num):
         # print "Relax.step", i
         rand = random()
         #print rand, temp
         if rand < temp: # go with a random choice, override ex, ey
            print "     Random!"
            ex = floor(random() * 3) - 1
            ey = floor(random() * 3) - 1
         else:
            ox = self.point_x[i] 
            oy = self.point_y[i]
            emin = 10000000
            for px in range(-1,2):
               for py in range(-1,2):
                  self.point_x[i] = ox + px * incr
                  self.point_y[i] = oy + py * incr
                  e = self.energy(diff)
                  if e < emin:
                     emin = e
                     ex = px
                     ey = py
         self.point_x[i] = ox + ex * incr
         self.point_y[i] = oy + ey * incr
      print "Min Energy:", emin, "at time", self.time
      self.graph()

   def graph(self):
      for i in range(self.num):
         ox = self.point_x[i] 
         oy = self.point_y[i]
         self.scatter.addPoint( ox, oy)

   def display(self):
      print "-------------------------------------------------------------------------"
      for i in range(self.num):
         print self.point_x[i], self.point_y[i]
      print "-------------------------------------------------------------------------"
            
   def energy(self, diff):
      e = 0
      for i in range(self.num):
         for j in range(i + 1, self.num):
            #print "Computing energy:", i, j, diff[i][j]
            d = distance(self.point_x[i], self.point_y[i], \
                         self.point_x[j], self.point_y[j]) - diff[i][j]
            e += d * d
      e /= 1.5 # largest diff?
      return e

class DevelopBrain(Brain):
   # Only method you have to define is the step method:

   def setup(self):
      self.t = 0
      self.data = []
      self.lastx = 0
      self.lasty = 0
      self.capture = 10
      self.dist_away_enough = .25
      if self.robot:
         self.state = 'capture' # initial state = 'capture', 'analyze'
      else:
         self.state = 'analyze'
      self.relax = Relax(16) # sometimes running off line: don't query robot for count

   def step(self):
      if self.state == 'capture':
         if self.t < self.capture:
            x = self.robot.x
            y = self.robot.y
            dist = distance(x, y, self.lastx, self.lasty)
            print "Distance =", dist
            if dist > self.dist_away_enough:
               print "  Capture #", self.t
               self.data.append([])
               for i in range(self.robot.sonar[0].count):
                  print ".",
                  self.data[self.t].append(self.robot.sonar[0][i].distance())
               self.lastx = self.robot.x
               self.lasty = self.robot.y
               print "Done!"
               self.t += 1
         else:
            self.robot.move(0, 0)
            self.state = 'average'
         translate = random() * 2.0 - 1
         rotate    = random() * 2.0 - 1
         self.robot.move(translate, rotate)
         sleep(1.0) # go for a bit
      elif self.state == 'average':
         self.diff = []
         for i in range(self.robot.sonar[0].count):
            self.diff.append([])
            for j in range(self.robot.sonar[0].count):
               self.diff[i].append(0)
         for t in range(self.capture):
            for i in range(self.robot.sonar[0].count):
               for j in range(i + 1, self.robot.sonar[0].count):
                  self.diff[i][j] += fabs(self.data[t][i] - self.data[t][j])
         for i in range(self.robot.sonar[0].count):
            for j in range(self.robot.sonar[0].count):
               self.diff[i][j] /= self.capture
               #print diff[i][j], 
            #print ''
         self.state = 'analyze'
      elif self.state == 'analyze':
         if self.relax.time > self.relax.maxtime:
            self.relax.display()
            self.state = 'done'
         else:
            if self.robot:
               self.relax.step(self.diff) # (data) for hardcoded
            else:
               self.relax.step(data) # (data) for hardcoded
      elif self.state == 'done':
         if self.robot:
            self.robot.disconnect()
            self.pleaseStop()
         else:
            self.pleaseQuit()
            return 0
      return 1

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (the robot), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return DevelopBrain(engine)
      
if __name__ == '__main__':
   db = DevelopBrain(0)
   while db.step():
      pass
