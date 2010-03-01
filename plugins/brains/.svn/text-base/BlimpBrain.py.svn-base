from pyrobot.brain import Brain
import time

def avg(mem):
   return sum(mem)/len(mem)


class BlimpBrain(Brain):
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
      if not self.robot.hasA("frequency"):
         self.startDevice("Frequency")
      self.robot.frequency[0].setSampleTime(0.1)
      print "sleep between:", self.robot.frequency[0].asyncSleep
      print "sampleTime:", self.robot.frequency[0].sampleTime
      for i in range(10):
         distance, freq, value, total, best, bestValue = self.robot.frequency[0].results
         self.mem[i] = distance
         time.sleep(.1)
         
   def step(self):
      distance, freq, value, total, best, bestValue = self.robot.frequency[0].results
      av = avg(self.mem)
      print abs(distance - av)
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
         self.robot.moveZ(0)
         time.sleep(.2)
         #time.sleep(self.dutyCycle * self.pulseTime)
         #self.robot.moveZ(0.0)
         #time.sleep(self.pulseTime * (1-self.dutyCycle))
         self.old_diff = diff


def INIT(engine):
   return BlimpBrain("BlimpBrain", engine)
      
