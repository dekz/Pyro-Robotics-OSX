from pyrobot.camera import Camera, CBuffer
from pyrobot.camera.blob.blob import Blob
import time

class BlobCamera(Camera):
   """
   """
   def __init__(self, robot, camera = None, depth = 3, visionSystem = None):
      """
      """
      self.robot = robot
      # if no camera given, we'll try a blobfinder
      if camera == None:
         # is there a default one?
         try:
            self.blobfinder = self.robot.blobfinder[0]
         except AttributeError:
            # no,then we'll try to start one:
            self.blobfinder = self.robot.startDevice('blobfinder')
      else:
         # else, you better have supplied a name, like "blobfinder0"
         self.blobfinder = camera
      self._devBlobFinder = self.blobfinder._dev
      while self._devBlobFinder.width == 0: pass
      self.width, self.height = self._devBlobFinder.width,self._devBlobFinder.height
      self.depth = depth
      self._dev = Blob(self.width, self.height, self.depth)
      # connect vision system: --------------------------
      self.vision = visionSystem
      self.vision.registerCameraDevice(self._dev)
      self.width = self.vision.getWidth()
      self.height = self.vision.getHeight()
      self.depth = self.vision.getDepth()
      self._cbuf = self.vision.getMMap()
      # -------------------------------------------------
      self.data = CBuffer(self._cbuf)
      self.rgb = (0, 1, 2) # offsets to RGB
      self.format = "RGB"
      Camera.__init__(self, self.width, self.height, self.depth,
                      "Blob Camera View")
      self.requires = ["blobfinder"]
      self.subtype = "blob"
      self.source = "%s[%d]" % (self.blobfinder.type, self.blobfinder.index)
      self.data = CBuffer(self._cbuf)
      
   def update(self):
      if not self.active: return
      blobs = []
      for i in range(self._devBlobFinder.blobs_count):
         try:
            b = self._devBlobFinder.blobs[i]
            blobs.append((b.left, b.top, b.right, b.bottom, b.color))
         except IndexError:
            pass
      self._dev.updateMMap(blobs)
      self.processAll()
