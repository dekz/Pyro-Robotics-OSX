from pyrobot.camera import Camera, CBuffer
from pyrobot.camera.rovio.rovio import RovioCam

class RovioCamera(Camera):
   """
   """
   def __init__(self, robot, visionSystem = None, tcp = 1):
      """
      """
      self.robot = robot
      self._dev = RovioCam(self.robot.theurl, 80, tcp)
      # connect vision system: --------------------------
      self.vision = visionSystem
      self.vision.registerCameraDevice(self._dev)
      self.width = self.vision.getWidth()
      self.height = self.vision.getHeight()
      self.depth = self.vision.getDepth()
      self._cbuf = self.vision.getMMap()
      self.data = CBuffer(self._cbuf)
      self.rgb = (0, 1, 2) # offsets to RGB
      self.format = "RGB"
      Camera.__init__(self, self.width, self.height, self.depth, "Rovio Camera View", async=1)
      self.subtype = "rovio"
      self.data = CBuffer(self._cbuf)

   def update(self):
       """
       This is called very often, or as fast as possible.
       """
       if not self.active: return
       self._dev.updateMMap(1) # read and map very often
       self.processAll() # need to process filters

if __name__ == "__main__":
    from pyrobot.vision.cvision import VisionSystem
    class MyRobot:
        theurl = "http://liquidsoapdispenser.com/rovio/treo_cam.jpg"
    camera = RovioCamera(MyRobot(), VisionSystem())
