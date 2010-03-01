from pyrobot.camera import Camera, CBuffer
from pyrobot.camera.aibo.aibo import AiboCam
from math import pi, sin, cos
import threading
import time

# FIX: why does the speed of the CameraThread effect the main
# thread? I don't know...

# Fix would like to add filter processing in this loop, but
# we would need to change the way the robot interacts with
# the filter data (lock it)

# Did I break something? the filter doesn't seem to run after every
# screen update?

class CameraThread(threading.Thread):
    """
    A camera thread class, because Aibo feeds it to us
    as fast as we can eat em!
    """
    def __init__(self, runable):
        """
        Constructor, setting initial variables
        """
        self.runable = runable
        self._stopevent = threading.Event()
        self._sleepperiod = 0.01
        threading.Thread.__init__(self, name="CameraThread")
        
    def run(self):
        """
        overload of threading.thread.run()
        main control loop
        """
        while not self._stopevent.isSet():
            self.runable._dev.updateMMap(0) # 0 = read and throw away; 1 = process
            self._stopevent.wait(self._sleepperiod)

    def join(self,timeout=None):
        """
        Stop the thread
        """
        self._stopevent.set()
        threading.Thread.join(self, timeout)

class AiboCamera(Camera):
   """
   """
   def __init__(self, robot, visionSystem = None, tcp = 1):
      """
      """
      self.robot = robot
      self.robot.setRemoteControl("Raw Cam Server", "on")
      time.sleep(1)
      self._dev = AiboCam( self.robot.host, self.robot.PORT["Raw Cam Server"], tcp)
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
      Camera.__init__(self, self.width, self.height, self.depth, "Aibo Camera View", async=1)
      self.subtype = "aibo"
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
        host = "k-8"
        PORT = {"Raw Cam Server": 10011}
        def setRemoteControl(self, *args):
            pass

    camera = AiboCamera(MyRobot(), VisionSystem())
