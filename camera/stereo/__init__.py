from pyrobot.camera import Camera, CBuffer # base class
from pyrobot.camera.stereo.stereo import Stereo
from pyrobot.vision.cvision import VisionSystem

class StereoCamera(Camera):
   """
   """
   def __init__(self, leftcamera, rightcamera):
      """
      Stereo Vision.
      """
      self._leftcamera = leftcamera
      self._rightcamera = rightcamera
      self._dev = Stereo( self._leftcamera._dev, self._rightcamera._dev)
      self.vision = VisionSystem()
      self._dev.setRGB(leftcamera.rgb[0], leftcamera.rgb[1], leftcamera.rgb[2])
      self.rgb = leftcamera.rgb
      self.format = leftcamera.format
      self.vision.registerCameraDevice(self._dev)
      self._cbuf = self.vision.getMMap()
      ## -------------------------------------------------
      Camera.__init__(self, self._dev.getWidth(), self._dev.getHeight(), self._dev.getDepth(),
                      "Stereo Camera")
      self.data = CBuffer(self._cbuf)

   def update(self):
      if not self.active: return
      self._dev.updateMMap()
      self.processAll()

