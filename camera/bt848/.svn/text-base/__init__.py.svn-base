from bt848 import BT848      # cameraDevice
from pyrobot.camera import Camera, CBuffer

class BT848Camera(Camera):
   """
   A Wrapper class for the C fuctions that capture data from the Camera.
   It uses the Video4linux API, and the image is kept in memory through
   an mmap.
   """
   def __init__(self, width, height, depth = 3,
                device = '/dev/bt848fg0', title = None,
                visionSystem = None):
      """
      Device should be the name of the capture device in the /dev directory.
      This is highly machine- and configuration-dependent, so make sure you
      know what works on your system
      """
      if width < 48:
         raise ValueError, "width must be greater than 48"
      if height < 48:
         raise ValueError, "height must be greater than 48"
      self.deviceFile = device
      self.handle=None
      self._cbuf=None
      try:
         self._dev = BT848(device, width, height, depth)
	 self._dev.setRGB( 2, 1, 0)
      except:
         print "bt848: grab_image failed!"
      # connect vision system: --------------------------
      self.vision = visionSystem
      self.vision.registerCameraDevice(self._dev)
      self.width = self.vision.getWidth()
      self.height = self.vision.getHeight()
      self.depth = self.vision.getDepth()
      self._cbuf = self.vision.getMMap()
      # -------------------------------------------------
      if title == None:
	 title = self.deviceFile
      self.rgb = (2, 1, 0) # offsets to BGR
      self.format = "BGR"
      Camera.__init__(self, width, height, depth, title = title)
      self.subtype = "bt848"
      self.source = device
      self.data = CBuffer(self._cbuf)

   def update(self):
      """
      Since data is mmaped to the capture card, all we have to do is call
      refresh.
      """
      if not self.active: return
      try:
         self._dev.updateMMap()
         self.processAll()
      except:
         print "bt848: updateMMap() failed"

