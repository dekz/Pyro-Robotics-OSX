# A bare brain

from pyrobot.brain import Brain
from time import sleep
from pyrobot.vision.cblob import blob
from pyrobot.vision.cblob import bitmap_from_V4LGrabber
from pyrobot.camera.v4l import *

class SimpleBrain(Brain):

   def setup(self, **args):
      self.cwidth = 96
      self.cheight = 64
      self.camera = V4LGrabber(self.cwidth, self.cheight, channel = 0)
      self.nStep = 0
      
   # Only method you have to define is the step method:

   def step(self):
      self.camera.update()
      print "%d: updated..." % (self.nStep)
      bmp = bitmap_from_V4LGrabber(self.camera, blob.FILTER_RED, 0.5)
      blob.Bitmap_write_to_pgm(bmp, "bmplast.pgm", 1)
      print "got bitmap..."
      data = blob.Blobdata_init(bmp)
      print "got blobdata..."
      bigred = 0
      for i in range(data.nblobs):
         if blob.blob_at(data.bloblist, i).mass > \
                blob.blob_at(data.bloblist, bigred).mass:
            bigred = i
      print "got largest..."
      pos = blob.blob_at(data.bloblist,bigred).cm_x
      scalepos = (self.cwidth/2 - pos)/self.cwidth
      print "%f\t%f" % (pos, scalepos)
      self.nStep = self.nStep + 1
      if min([s.distance() for s in self.robot.range["front"]]) > .4:
         print "Turning..."
         self.move(.1, scalepos*2)
         print "Turned"
      else:
         print "Stopping..."
         self.move(0, 0)
         print "Stopped"
      

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (an engine), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain('SimpleBrain', engine)
      
