from pyrobot.camera import Camera, CBuffer # base class
from pyrobot.camera.fourway.fourway import Fourway
from pyrobot.vision.cvision import VisionSystem

class FourwayCamera(Camera):
   """
   """
   def __init__(self, camera, splits, quad, rot = 0):
      """
      Can split a camera 2 or 4 ways.
      """
      self._camera = camera
      self._splits = splits
      self._quad   = quad
      self._dev = Fourway( self._camera._dev, splits, quad, rot)
      self.vision = VisionSystem()
      self._dev.setRGB(camera.rgb[0], camera.rgb[1], camera.rgb[2])
      self.rgb = camera.rgb
      self.format = camera.format
      self.vision.registerCameraDevice(self._dev)
      self._cbuf = self.vision.getMMap()
      ## -------------------------------------------------
      Camera.__init__(self, self._dev.getWidth(), self._dev.getHeight(), self._dev.getDepth(),
                      "Quad #%d" % quad)
      self.data = CBuffer(self._cbuf)

   def update(self):
      if not self.active: return
      self._dev.updateMMap()
      self.processAll()

if __name__ == "__main__":
   from pyrobot.camera.fake import FakeCamera
   cam = FakeCamera(pattern = "../../vision/tutorial/test-?.ppm", start = 0,
                    stop = 11, interval = 1, visionSystem = VisionSystem())
   cam.update()
   cam.makeWindow()
   cam.updateWindow()
   cameras = [0] * 4
   for i in range(4):
      cameras[i] = FourwayCamera(cam, 4, i)
      cameras[i].update()
      cameras[i].makeWindow()
      cameras[i].updateWindow()
