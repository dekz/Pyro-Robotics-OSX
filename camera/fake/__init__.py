from pyrobot.camera.fake.fake import Fake # cameraDevice
from pyrobot.camera import Camera, CBuffer # base class
from pyrobot.vision.cvision import VisionSystem
import pyrobot.system as system
from pyrobot import pyrobotdir
import re, time, os

class ManualFakeCamera(Camera):
   """
   camera = ManualFakeCamera(w, h, d)

   Used when you are creating the image from Python, and wish
   to have the camera class show or manipulate the image.

   Currently only depth 3 works.

   Values in camera array are ints between 0 and 255.
   """
   def __init__(self, width, height, depth):
      self.width = width
      self.height = height
      self.depth = depth
      self._dev = Fake("", self.width, self.height, self.depth)
      self.vision = VisionSystem()
      self.vision.registerCameraDevice(self._dev)
      self._cbuf = self.vision.getMMap()
      # -------------------------------------------------
      self.rgb = (0, 1, 2) # offsets to RGB
      self.format = "RGB"
      Camera.__init__(self, self.width, self.height, self.depth,
                      "Fake Camera View")
      self.subtype = "simulated"
      self.data = CBuffer(self._cbuf)

   def blankImage(self, val=0):
      for w in range(self.width):
         for h in range(self.height):
            for d in range(self.depth):
               self.vision.setVal(w, h, d, val)

   def setGrayImage(self, array):
      """
      Will set the RGB camera image from a grayscale array (depth 1)
      assuming column major order.
      """
      for w in range(self.width):
         for h in range(self.height):
            val = array[h * self.width + w]
            for d in range(self.depth):
               self.vision.setVal(w, h, d, val)

   def setRGBImage(self, array):
      """
      Will set the RGB camera image from a RGB array (depth 3)
      assuming column major order.
      """
      for w in range(self.width):
         for h in range(self.height):
            for d in range(self.depth):
               self.vision.setVal(w, h, d, array[(w + h * self.width) * self.depth + d])

   def setRGB3Image(self, array):
      """
      Will set the RGB camera image from a RGB array (depth 3)
      assuming column major order.
      """
      for w in range(self.width):
         for h in range(self.height):
            for d in range(self.depth):
               self.vision.setVal(w, h, d, array[w][h][d])


class FakeCamera(Camera):
   """
   A fake camera.  This will emulate a camera, but instead of
   accessing the hardware, it will load a series of images from file.
   """
   def __init__(self, pattern = None,
                start = 0, stop = 19, char = "?",
                interval = 1.0, visionSystem = None, verbose = 0):
      """
      pattern is a filename with indicators on where to put digits for the
      sequence.  Absolute or relative filenames can be used.

      For example, 'image???-.ppm' would start at 'image000.ppm'
      and continue up to stop.
      
      char is the character that should be replaced in the pattern.

      interval = how often do I get new image

      As an example, to load som-0.ppm through som-19.ppm, we could call
      FakeCamera('vision/snaps/som-?.ppm', 0, 19)
      """
      if pattern == None:
         pattern = "vision/snaps/som-?.ppm"
      self.pattern = pattern
      self.stop = stop
      self.start = start
      self.current = start
      self.setUpdateInterval(interval)
      self.verbose = verbose
      self.lastUpdate = 0
      #create a matchdata object that we will store
      self.match = re.search(re.escape(char) + "+", pattern)
      #create a format string that we can use to replace the
      #replace characters
      if self.match:
         self.fstring = "%%0%dd" % len(self.match.group())
         currname = self.pattern[:self.match.start()] + \
                    self.fstring % self.current + \
                    self.pattern[self.match.end():]
      else:
         currname = self.pattern
      if system.file_exists(currname):
         self.path = ''
      elif system.file_exists( pyrobotdir() + "/" + currname):
         self.path = pyrobotdir() + "/"
      else:
         raise ValueError, "file not found: '%s'" % currname
      if self.verbose:
         print "info: reading file '%s'..." % (self.path + currname)
      self._dev = Fake(self.path + currname)
      # connect vision system: --------------------------
      if visionSystem:
         self.vision = visionSystem
         self.vision.registerCameraDevice(self._dev)
         self.width = self.vision.getWidth()
         self.height = self.vision.getHeight()
         self.depth = self.vision.getDepth()
         self._cbuf = self.vision.getMMap()
      else:
         self.vision = None
         self.width = 0
         self.height = 0
         self.depth = 0
         self._cbuf = None
      # -------------------------------------------------
      self.rgb = (0, 1, 2) # offsets to RGB
      self.format = "RGB"
      Camera.__init__(self, self.width, self.height, self.depth,
                      "Fake Camera View")
      self.subtype = "simulated"
      self.source = self.pattern
      self.data = CBuffer(self._cbuf)
      self.oldStart = None
      self.oldStop = None

   def pauseButton(self):
      self.freezeFrame()

   def playButton(self):
      self.unFreezeFrame()

   def setUpdateInterval(self, val):
      Camera.setUpdateInterval(self, val)
      self.interval = val

   def freezeFrame(self):
      if self.oldStart == None:
         self.oldStart = self.start
         self.oldStop = self.stop
         self.stop = self.current
         self.start = max(self.current - 1, 0)

   def unFreezeFrame(self):
      if self.oldStart != None:
         self.stop = self.oldStop
         self.start = self.oldStart
         self.oldStart = None
         self.oldStop = None
         
   def update(self):
      if not self.active: return
      if (self.current < self.stop):
         currentTime = time.time()
         if currentTime - self.lastUpdate > self.interval:
            if self.match:
               currname = self.pattern[:self.match.start()] + \
                          self.fstring % self.current + \
                          self.pattern[self.match.end():]
            else:
               currname = self.pattern
            if self.verbose:
               print "info: reading file '%s'..." % (self.path + currname)
            self._dev.updateMMap(self.path + currname)
            self.processAll()
            self.current += 1
            self.lastUpdate = currentTime
      else:
         self.current = self.start 

if __name__ == "__main__":
   from pyrobot.vision.cvision import VisionSystem
   camera = FakeCamera(visionSystem=VisionSystem())
   camera.update()
