""" This is the FSM of the whole maze. """

from pyrobot.brain.behaviors import State, FSMBrain
from pyrobot.simulators.pysim import *
import random, time

def f2m(feet):
   """ feet to meters """
   return 0.3048 * feet
def cm2m(cm):
   """ feet to meters """
   return  cm / 100.0
def d2r(degrees):
   """ degrees to radians """
   return PIOVER180 * degrees

def avg(mem):
   return sum(mem)/len(mem)

class Map:
   def __init__(self):
      
      # (width, height), (offset x, offset y), scale:
      self.sim = TkSimulator((523,627), (43,605), 27.229171, run = 0) 
      self.sim.wm_title("Indoor Aerial Robot Competition Map")
      # entry way:
      self.sim.addWall(f2m(17.3), f2m(0), f2m(17.3), f2m(11))
      self.sim.addWall(f2m(17.3 + 4), f2m(0), f2m(17.3 + 4), f2m(11))
      # angles:
      self.sim.addWall(f2m(17.3), f2m(11), f2m(0), f2m(21))
      self.sim.addWall(f2m(17.3 + 4), f2m(11), f2m(38.64), f2m(21))
      # sides:
      self.sim.a8000ddWall(f2m(0), f2m(21), f2m(0), f2m(21 + 45.7))
      self.sim.addWall(f2m(38.64), f2m(21), f2m(38.64), f2m(21 + 45.7 - 9.5))
      self.sim.addWall(f2m(38.64), f2m(57.13), f2m(38.64), f2m((2.1*3.94)+38.64))
      # far wall:
      self.sim.addWall(f2m(0), f2m(21 + 45.7), f2m(38.64 + 8), f2m(21 + 45.7))
      self.sim.addWall(f2m(38.64), f2m(57.13), f2m(38.64 + 8), f2m(57.13))
      # triangles:
      self.sim.addShape("polygon", (f2m( 3.74), f2m(26.79)), (f2m( 8.24), f2m(20.09)), (f2m( 8.24), f2m(33.49)), fill = "blue")
      self.sim.addShape("polygon", (f2m(12.21), f2m(20.09)), (f2m(12.21), f2m(33.49)), (f2m(17.14), f2m(26.79)), fill = "blue")
      self.sim.addShape("polygon", (f2m(25.61), f2m(20.09)), (f2m(25.61), f2m(33.49)), (f2m(20.88), f2m(26.79)), fill = "blue")
      self.sim.addShape("polygon", (f2m(29.55), f2m(20.09)), (f2m(29.55), f2m(33.49)), (f2m(34.08), f2m(26.79)), fill = "blue")
      self.sim.addShape("polygon", (f2m( 3.74), f2m(35.46)), (f2m( 3.74), f2m(48.46)), (f2m( 8.24), f2m(42.16)), fill = "blue")
      self.sim.addShape("polygon", (f2m(17.14), f2m(35.46)), (f2m(17.14), f2m(48.46)), (f2m(12.21), f2m(42.16)), fill = "blue")
      self.sim.addShape("polygon", (f2m(20.88), f2m(35.46)), (f2m(20.88), f2m(48.46)), (f2m(25.61), f2m(42.16)), fill = "blue")
      self.sim.addShape("polygon", (f2m(34.08), f2m(35.46)), (f2m(34.08), f2m(48.46)), (f2m(29.55), f2m(42.16)), fill = "blue")
      self.sim.addShape("polygon", (f2m( 3.74), f2m(57.13)), (f2m( 8.24), f2m(50.24)), (f2m( 8.24), f2m(63.04)), fill = "blue")
      self.sim.addShape("polygon", (f2m(12.21), f2m(50.24)), (f2m(12.21), f2m(63.04)), (f2m(17.14), f2m(57.13)), fill = "blue")
      self.sim.addShape("polygon", (f2m(25.61), f2m(50.24)), (f2m(25.61), f2m(63.04)), (f2m(20.88), f2m(57.13)), fill = "blue")
      self.sim.addShape("polygon", (f2m(29.55), f2m(50.24)), (f2m(29.55), f2m(63.04)), (f2m(34.08), f2m(57.13)), fill = "blue")
      ##Small Triangles
      self.sim.addShape("polygon", (f2m(3.725*3.94), f2m(17.135)), (f2m(17.14), f2m(15.36)), (f2m(17.14), f2m(18.91)), fill = "blue")
      self.sim.addShape("polygon", (f2m(5.9*3.94), f2m(17.135)), (f2m(20.88), f2m(15.36)), (f2m(20.88), f2m(18.91)), fill = "blue")
      
      self.sim.addShape("oval", (f2m(38.64 + 10), f2m(57.13 + 1)), (f2m(38.64 + 10 + 8), f2m(57.13 + 1 + 8)), fill="blue")
      self.sim.addShape("oval", (f2m(38.64 + 10 + 1), f2m(57.13 + 1 + 1)), (f2m(38.64 + 10 + 1 + 6), f2m(57.13 + 1 + 1 + 6)), fill="green")
      self.sim.addShape("oval", (f2m(38.64 + 10 + 2), f2m(57.13 + 1 + 2)), (f2m(38.64 + 10 + 2 + 4), f2m(57.13 + 1 + 2 + 4)), fill="red")
      
      # other things you can add:
      #self.sim.addShape("line", (5, 3), (6, 5), fill = "blue")
      #self.sim.addShape("polygon", (2, 3), (3, 2), (4, 3), fill = "red")
      #self.sim.addShape("oval", (5, 7), (6, 6), fill = "green")
      #self.sim.addShape("box", 5, 7, 6, 6, "purple")
      # fiducials:
      self.fiducials = {}
      self.fiducialData = [(19.306, 8,8000, 0, 1), # x, y, th, ID
                           (17.3 + 2, 2, 0, 0),
                           (3.725 * 3.94, 14.57, 60, 2), 
                           (19.306, 17.139, 0, 3),
                           (5.9*3.94, 14.57, -60, 4),
                           (1.525*3.94, 20.09, 60, 5),
                           (8.075*3.94, 20.09, -60, 9),
                           (11.032, 22.22, 0, 6),
                           (27.97, 22.22, 0, 8),
                           (2.364, 26.79, 0, 10),
                           (19.306,26.79, 0, 7),
                           (36.64, 26.79, 0, 13),
                           (11.032,32.3, 0, 11),
                           (27.97, 32.3, 0, 12),
                           (6.304,34.67, -60, 15),
                           (15.37,34.67, 60, 16),
                8000           (23.246,34.67, -60, 18),
                           (32.3,34.67, 60, 20),
                           (2.364,37.23, 0, 14),
                           (19.306,37.23, 0, 17 ),
                           (36.64,37.23, 0, 21),
                           (11.032,42.16, 0, 23),
                           (27.97,42.16, 0, 19),
                           (2.364,47.08, 0, 22),
                           (19.306,47.08, 0, 24),
                           (36.64,47.08, 0, 27),
                           (6.304,49.45, 60, 28),
                           (15.37,49.45, -60, 29),
                           (23.246,49.45, 60, 25),
                           (32.3,49.45, -60, 26),
                           (2.364,57.13, 0, 30),
                           (19.306,57.13, 0, 31),
                           (36.64,57.13, 0, 32),
                           (6.304,64.19, -90, 33),
                           (15.37,64.19, -90, 34),
                           (23.246,64.19, -90, 35),
                           (32.3,64.19, -90, 36),
                           (38.64 + 10 + 4, 57.13 + 1 + 4, -90, 37)]
      # Graph: how are places connected?
      self.graph = {0: [-1, 1, -1], # -1, means no option: left, forward, right
                    1: [2, 3, 4],
                    2: [-1, 5, 6,],
                    3: [-1, 7, -1,],
                    4: [8, 9, -1,],
                    5: [-1, -1, 10,],
                    6: [-1, 11, -1,],
                    7: [16, 17, 18,],
                    8: [-1, 12, -1,],
                    9: [13, 13, -1,],
                    10: [-1, 14, 15,],
                    11: [-1, 23, -1,],
                    12: [-1, 19, -1,],
                    13: [20, 21, -1,],
                    14: [-1, 22, -1,],
                    15: [23, -1, 29,],
                    16: [-1, -1, 23,],
                    17: [-1, 24, -1,],
                    18: [19, -1, -1,],
                    19: [25, -1, 26,],
                    20: [-1, -1, 19,],
                    21: [-1, 27, -1,],
                    22: [-1, 30, -1,],
                    23: [28, -1, 29,],
                    24: [-1, 31, -1,],
                    25: [-1, 31, 31,],
                    26: [-1, 32, -1,],
                    27: [-1, 32, -1,],
                    28: [-1, 30, -1,],
                    29: [31, 31, -1,],
                    30: [-1, -1, 33,],
                    31: [-1, -1, 35,],
                    32: [-1, -1, 37,],
                    33: [-1, 34, -1,],
                    34: [-1, 35, -1,],
                    35: [-1, 380006, -1,],
                    36: [-1, 37, -1,],
                    37: [-1, -1, -1,],}
      for fid in self.fiducialData:
         x, y, th, id = fid
         self.fiducials[id] = (x, y, th)

      # robot:
      self.sim.addRobot(60000, TkBlimp("Blimpy", f2m(17.3 + 2), f2m(2), 0.0))
      self.currentPos = None
      self.gotoID(1) # start
      self.update()

   def decide(self, dots):
      x, y, th, id = self.currentPos
      if id not in [0, 37]:
         self.drawFid(id, dots)
      options = self.graph[id]
      if options[dots - 1] == -1: # not an option!
         print "We're lost! Maybe you saw some other dots?"
         for pos in options:
            if pos != -1:
               dots = options.index(pos) + 1
               break
         print "I'm going to pick a different direction..."
      self.gotoID(options[dots - 1])

   def drawFid(self, id, dots):
      x, y, th = self.fiducials[id]
      self.addFiducial(x, y, th, dots)

   def gotoID(self, id): # start it off!
      x, y, th = self.fiducials[id]
      if self.currentPos != None:
         self.sim.addShape("line", (f2m(self.currentPos[0]), f2m(self.currentPos[1])), (f2m(x), f2m(y)), fill = "purple")
      self.moveTo(x, y, th)
      self.currentPos = x, y, th, id

   def drawAllFiducials(self):
      for fid in self.fiducialData:
         x, y, th, id = fid
         self.drawFid(id)

   def move(self, x, y, z = 0):
      self.sim.robots[0].move(x, y)
      self.update()

   def moveTo(self, x, y, th):
      self.sim.robots[0]._gx = f2m(x)
      self.sim.robots[0]._gy = f2m(y)
      self.sim.robots[0]._ga = d2r(th)
      self.update()

   def addFiducial(self, x, y, th, dots = 0):
      size = 2.75 # meters
      si = size / 2.0
      s = size / 4.0
      e = size / 8.0
      t = s * .3
      xm = f2m(x)
      ym = f2m(y)
      thr = d2r(th)
      cos_a90 = math.cos(thr)
      sin_a90 = math.sin(thr)
      x1, y1 = (xm + f2m(si) * cos_a90 - 0 * sin_a90), (ym + f2m(si) * sin_a90 + 0 * cos_a90)
      x2, y2 = (xm - f2m(si) * cos_a90 - 0 * sin_a90), (ym - f2m(si) * sin_a90 + 0 * cos_a90)
      self.sim.addShape("line", (x1, y1), (x2, y2), fill="black") # long line
      # forks:
      px1, py1 = (xm + f2m(si) * cos_a90 - f2m(s) * sin_a90), (ym + f2m(si) * sin_a90 + f2m(s) * cos_a90)
      px2, py2 = (xm - f2m(si) * cos_a90 - f2m(s) * sin_a90), (ym - f2m(si) * sin_a90 + f2m(s) * cos_a90)
      self.sim.addShape("line", (x1, y1), (px1, py1), fill="black")
      self.sim.addShape("line", (x2, y2), (px2, py2), fill="black")
      # dots:
      if dots in (1, 3):
         x, y = (xm + f2m(0) * cos_a90 - f2m(e) * sin_a90), (ym + f2m(0) * sin_a90 + f2m(e) * cos_a90)
         self.sim.addShape("oval", (x - f2m(t), y - f2m(t)), (x + f2m(t), y + f2m(t)), fill="red")
      if dots in (2, 3):
         x, y = (xm - f2m(s) * cos_a90 - f2m(e) * sin_a90), (ym - f2m(s) * sin_a90 + f2m(e) * cos_a90)
         self.sim.addShape("oval", (x - f2m(t), y - f2m(t)), (x + f2m(t), y + f2m(t)), fill="red")
         x, y = (xm + f2m(s) * cos_a90 - f2m(e) * sin_a90), (ym + f2m(s) * sin_a90 + f2m(e) * cos_a90)
         self.sim.addShape("oval", (x - f2m(t), y - f2m(t)), (x + f2m(t), y + f2m(t)), fill="red")
      
   def update(self):
      self.sim.step(run=0)
      self.sim.update()

class Start(State):
   def setup(self):
      if not self.robot.hasA("frequency"):
         self.startDevice("Frequency")
      self.robot.frequency[0].setSampleTime(0.1)
      if not self.robot.hasA("camera"):
         self.startDevice("V4LCamera")
         #self.startDevice("BlimpMovie")
         #self.startDevice("BlimpCameraHallway")
         self.startDevice("FourwayRot2")
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[1].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      self.robot.camera[4].active = 0
      self.robot.camera[1].addFilter("rotate",) # backview
        
   def step(self):
      self.engine.gui.makeWindows()
      self.robot.camera[4].setVisible(0)
      self.robot.camera[0].setVisible(0)
      print "Here we go!"
      self.goto("MaintainHeight")
      self.goto("ReadFiducial")

class MaintainHeight(State):
   def setup(self):
      self.targetDistance = 1.0 # meters
      self.mem = [0]*10
      self.step_count = 0
      self.cont_count = 0
      self.old_amt = 0
      self.igain = 0.0
      self.pgain = 0.75
      self.dgain = 0.25
      self.integral = 0.0
      self.old_diff = 0.0
      self.deriv = 0.0
      self.pulseTime = 0.5
      self.dutyCycle = .3
      print "sleep between:", self.robot.frequency[0].asyncSleep
      print "sampleTime:", self.robot.frequency[0].sampleTime
      for i in range(10):
         distance, freq, value, total, best, bestValue = self.robot.frequency[0].results
         self.mem[i] = distance
         time.sleep(.1)
         
   def step(self):
      distance, freq, value, total, best, bestValue = self.robot.frequency[0].results
      av = avg(self.mem)
      #print abs(distance - av)
      if(abs(distance - av) > 1):
         self.cont_count += 1
         if(self.cont_count > 20):
            for i in range(10):
               distance, freq, value, total, best, bestValue = self.robot.frequency[0].results
         return
      else:
         self.cont_count = 0
         self.mem[self.step_count%10] = distance
         self.step_count += 1
         #proportional
         diff = self.targetDistance - distance
         #print diff
         #integral
         self.integral += diff
         #derivative
         self.deriv = diff - self.old_diff
         #correction amount
         amount = (self.integral * self.igain + diff + (self.deriv*self.dgain)) * self.pgain
         if((amount >= 0) and (amount <= 19)):
            amount += 19
         elif((amount < 0) and (amount >= -19)):
            amount -= 19
         amount = max(min(amount, 1.0), -1.0)
         #print distance, amount, diff, self.pgain, self.igain, self.dgain
         self.old_amt = amount
         self.robot.moveZ(amount)
         time.sleep(.2)
         self.robot.moveZ(0) # ok, robot will do this automatically
         time.sleep(.2)
         #time.sleep(self.dutyCycle * self.pulseTime)
         #self.robot.moveZ(0.0)
         #time.sleep(self.pulseTime * (1-self.dutyCycle))
         self.old_diff = diff

class Search(State): # looking through forward camera to find a fiducial
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      self.robot.camera[3].addFilter("match", 245, 193, 188, 25) #front view look for red
      self.robot.camera[3].addFilter("superColor", 0) #front view look for red
      self.robot.camera[3].addFilter("blobify", 0) #front view look for red
      self.robot.camera[2].addFilter("match", 158, 110, 99, 25) #front view look for red
      self.robot.camera[2].addFilter("superColor", 0) #front view look for red
      self.robot.camera[2].addFilter("blobify", 0) #front view look for red
      self.h1 = self.robot.camera[2].height
      self.h1L = self.h1/3
      self.counter = 0
      
   def step(self):
      self.counter += 1
      x1, y1, x2, y2, matches = self.robot.camera[2].filterResults[2][0]
      if matches > 100: # FIX: box is big enough?
         self.goto('GotoBullseye')
         return
      if matches > 50: # FIX: box is big enough?
         self.goto('Advance2Fid')
         return
      x1, y1, x2, y2, matches = self.robot.camera[3].filterResults[2][0]
      if matches > 20:
         self.goto('Advance2Fid')
         return
      if random.random() < .3:
         if self.brain.robotControl:
            self.robot.move(.2, 0) # turn to the right
            time.sleep(6)
            self.robot.move(0, 0)
      if random.random() < .3:
         if self.brain.robotControl:
            self.robot.move(0, -.2) # turn to the right
            time.sleep(.1)
            self.robot.move(0, 0)
            time.sleep(.3)
      elif self.counter > 100:
         self.counter = 0
         if self.brain.robotControl:
            self.robot.move(.5,0) # go forward
            time.sleep(1)
            self.robot.move(0,0)

class Advance2Fid(State): # move towards Fiducial
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      if self.brain.robotControl:
         self.robot.move(1,0)
         time.sleep(1)
         self.robot.move(0,0)
   def step(self):
      self.goto('OrientFiducial')

class OrientFiducial(State):
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      # use filters below
      self.counter = 0
        
   def step(self):
      self.counter += 1
      distance = self.robot.frequency[0].results[0]
      r1 = self.robot.camera[3].apply("grayScale")
      r2 = self.robot.camera[3].apply("orientation", distance)
      r3 = self.robot.camera[3].apply("superColor", 0)
      r4 = self.robot.camera[3].apply("blobify", 0)
      x1, y1, x2, y2, matches = r4
      if matches > 20: # FIX what is a good color?
         self.goto("ReadFiducial")
         return
      x1, y1, x2, y2, matches = self.robot.camera[3].filterResults[3][0]
      cx, cy = (x1 + x2)/2, (y1 + y2)/2
      if self.brain.robotControl:
         if cx < self.robot.camera[3].width/2: # need to turn left
            self.move(0, .2)
         else: # turn some right
            self.move(0, -.2)
         if cy < self.robot.camera[3].height/2: # need to backup
            self.move(-.2, 0)
         else: # go forward
            self.move(.2, 0)
      if self.counter > 100:
         self.goto("Search")
       
class ReadFiducial(State):
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      self.robot.camera[3].addFilter("fid",)    # downview
      self.counter = 0
      self.fidC1 = 0
      self.fidC2 = 0
      self.fidC3 = 0
        
   def step(self):
      # looking if over fiducial
      self.h3 = self.robot.camera[3].height
      #self.w3 = self.robot.camera[3].width
      self.h3U = self.h3 - (self.h3/3)
      self.h3L = self.h3 - (2*(self.h3/3))
      self.fid3x, self.fid3y, self.fid3dots = self.robot.camera[3].filterResults[0]
    
      if self.fid3y > self.h3L and self.fid3y < self.h3U:
         if self.fid3dots == 1:
            self.fidC1 += 1
         elif self.fid3dots == 2:
            self.fidC2 += 1
         elif self.fid3dots == 3:
            self.fidC3 += 1

      if self.fidC1 > 5 or self.fidC2 > 5 or self.fidC3 > 5:
         maxval = max(self.fidC1, self.fidC2, self.fidC3)
         if maxval == self.fidC1:
            self.brain.map.decide(1)
            self.goto('Advance2ft1')
         elif maxval == self.fidC2:
            self.brain.map.decide(2)
            self.goto('Advance2ft2')
         elif maxval == self.fidC3:
            self.brain.map.decide(3)
            self.goto('Advance2ft3')
         self.FFcounter = 0
         return
         
      if self.counter > 100:
         self.goto('Search')  #### put returns after gotos
      else:
         self.counter +=1

class Advance2ft1(State):
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      if self.brain.robotControl:
         self.robot.move(0,0) # stop
         self.robot.move(.2,0) # go forward 2 ft
         time.sleep(6)
         self.robot.move(0,0)
         self.robot.move(0,.2) # turn left
         time.sleep(2)
         self.robot.move(0,-.2) # stop turning
         time.sleep(.2)
         self.robot.move(.2,0) # go forward a few feet
         time.sleep(6)
         self.robot.move(0,0) # stop
   def step(self):
      self.goto('Search')

class Advance2ft2(State):
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      if self.brain.robotControl:
         self.robot.move(0,0) # stop
         self.robot.move(.2,0) # go forward 2 ft
         time.sleep(6)
         self.robot.move(0,0) # stop
         time.sleep(1)
         self.robot.move(.2,0) # go forward a few feet
         time.sleep(6)
         self.robot.move(0,0) # stop
   def step(self):
      self.goto('Search')

class Advance2ft3(State):
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      if self.brain.robotControl:
         self.robot.move(0,0) # stop
         self.robot.move(.2,0) # go forward 2 ft
         time.sleep(6)
         self.robot.move(0,0)
         self.robot.move(0,-.2) # turn left
         time.sleep(2)
         self.robot.move(0,.2) # stop turning
         time.sleep(.2)
         self.robot.move(.2,0) # go forward a few feet
         time.sleep(6)
         self.robot.move(0,0) # stop
   def step(self):
      self.goto('Search')
        
class Done(State):
   def onActivate(self):
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
   def step(self):
      print "We're done! Look through window!"
      if self.brain.robotControl:
         self.robot.move(0,0)

class GotoBullseye(State):
   def onActivate(self): # method called when activated or gotoed
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      self.robot.camera[3].addFilter("match", 245, 193, 188, 25) #front view look for red
      self.robot.camera[3].addFilter("superColor", 0) #front view look for red
      self.robot.camera[3].addFilter("blobify", 0) #front view look for red
      self.robot.camera[2].addFilter("match", 158, 110, 99, 25) #front view look for red
      self.robot.camera[2].addFilter("superColor", 0) #front view look for red
      self.robot.camera[2].addFilter("blobify", 0) #front view look for red
      self.counter = 0
      self.lost = 0

   def step(self):
      self.counter += 1
      if self.robot.camera[3].filterResults[2][0][4] > 20: # matches ///
         self.goto("HoverBullseye")
         return
      x1, y1, x2, y2, matches = self.robot.camera[3].filterResults[2][0]
      cx, cy = (x1 + x2)/2, (y1 + y2)/2
      if matches == 0:
         self.lost += 1
      if self.lost > 20:
         self.goto("Search")
         return
      if self.brain.robotControl:
         if cx < self.robot.camera[3].width/2: # need to turn left
            self.move(0, .2)
         else: # turn some right
            self.move(0, -.2)
         if cy < self.robot.camera[3].height/2: # need to backup
            self.move(-.2, 0)
         else: # go forward
            self.move(.2, 0)
      if self.counter > 100:
         self.goto('Search')  #### put returns after gotos


class HoverBullseye(State):
   def onActivate(self): # method called when activated or gotoed
      self.robot.camera[0].clearCallbackList()
      self.robot.camera[2].clearCallbackList()
      self.robot.camera[3].clearCallbackList()
      self.robot.camera[3].addFilter("match", 245, 193, 188, 25) #front view look for red
      self.robot.camera[3].addFilter("superColor", 0) #front view look for red
      self.robot.camera[3].addFilter("blobify", 0) #front view look for red
      self.startTime = time.time()
      self.lost = 0
    
   def step(self):
      if time.time() - self.startTime > 15:
         self.goto('Done')
      else:
         x1, y1, x2, y2, matches = self.robot.camera[3].filterResults[2][0]
         cx, cy = (x1 + x2)/2, (y1 + y2)/2
         if matches == 0:
            self.lost += 1
         if self.lost > 10:
            self.goto('Search')            
         if self.brain.robotControl:
            if cx < self.robot.camera[3].width/2: # need to turn left
               self.move(0, .2)
            else: # turn some right
               self.move(0, -.2)
            if cy < self.robot.camera[3].height/2: # need to backup
               self.move(-.2, 0)
            else: # go forward
               self.move(.2, 0)

class MyBrain(FSMBrain):
   def setup(self):
      self.map = Map()
      self.robotControl = 0
   def destroy(self):
      self.map.destroy()

def INIT(engine): # passes in engine, if you need it
   brain = MyBrain("Blimpy", engine)
   # add a few states:
   brain.add(Start(1))
   brain.add(MaintainHeight()) # will always be on after Start
   brain.add(Search())
   brain.add(Advance2Fid())
   brain.add(OrientFiducial())
   brain.add(ReadFiducial())
   brain.add(Advance2ft1())
   brain.add(Advance2ft2())
   brain.add(Advance2ft3())
   brain.add(Done())
   brain.add(GotoBullseye())
   brain.add(HoverBullseye())
   return brain

if __name__ == "__main__":
   map = Map()
