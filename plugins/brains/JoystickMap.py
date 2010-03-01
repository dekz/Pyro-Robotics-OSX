from pyrobot.brain import *
from pyrobot.tools.joystick import Joystick
import pyrobot.system.share as share
from pyrobot.map.lps import LPS
from pyrobot.map.gps import GPS
import thread

class Map(Brain):
   def setup(self):
      # We want our map to measure in MM, so we first store our current unit of measure
      units = self.robot.range.units
      # We then reset our measurements to MMs
      self.robot.range.units = 'MM'
      # Calculate the maximum range of our sensors
      rangeMaxMM = self.robot.range.getMaxvalue()
      sizeMM = rangeMaxMM * 3 + (self.robot.radius / 1000.0) # in MMs
      # Reset our unit of measure
      self.robot.range.units = units
      # Now, we create our Local Perceptual Space window - this will hold our local map
      # Map will be 20px by 20px and will represent a height and width of sizeMM (total sensor range)
      self.lps = LPS( 40, 40,
                      widthMM = sizeMM,
                      heightMM = sizeMM)
      # Then create our Global Perceptual Space window - this will hold our global map
      # This map will be 500px by 500px and will represent an area N times the size of our maximum range
      self.gps = GPS( cols=300, rows=300,
                      heightMM = sizeMM * 5, widthMM = sizeMM * 5)
      self.joystick = Joystick(share.gui)
      self.need_redraw = False
      self.lock = thread.allocate_lock()
      
   def step(self):
      if not self.lock.acquire(False):
         return
      #print "Stepping...",
      # First we clear out all our old LPS data
      self.lps.reset()
      # Next we update our LPS with current 'range' sensor readings
      self.lps.sensorHits(self.robot, 'range')
      # Now redraw our LPS window - the LPS redraw can be improve performance
      
      # Then update our GPS with the new information in the LPS
      self.gps.updateFromLPS(self.lps, self.robot)
      # Finally, we redraw the GPS window
      
      self.need_redraw = True
      self.move(self.joystick.translate, self.joystick.rotate)
      self.lock.release()
      #print "done stepping!"
      
   def redraw(self):
      if (not self.lock.acquire(False)):
         return
      #print "Redrawing...",
      if self.need_redraw:
         self.lps.redraw(drawLabels=False)
         self.gps.update()
         self.gps.redraw()
         self.need_redraw = False
      self.lock.release()
      #print "done redrawing!"
       
   def destroy(self):
      # Make sure we close down cleanly
      self.lps.destroy()
      self.gps.destroy()
      self.joystick.destroy()
       
def INIT(engine):
   return Map("Mapping Brain", engine)
