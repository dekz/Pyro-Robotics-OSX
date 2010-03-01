from pyrobot.camera import Camera, CBuffer
from pyrobot.camera.robocup.robocup import Robocup
from math import pi, sin, cos
import time

PIOVER180 = pi / 180.0

class RobocupCamera(Camera):
   """
   """
   def __init__(self, robot, width=80, height=60, depth = 3, visionSystem = None):
      """
      """
      self.robot = robot
      self.width = width
      self.height = height
      self.depth = depth
      self._dev = Robocup(self.width, self.height, self.depth)
      # connect vision system: --------------------------
      self.vision = visionSystem
      self.vision.registerCameraDevice(self._dev)
      self.width = self.vision.getWidth()
      self.height = self.vision.getHeight()
      self.depth = self.vision.getDepth()
      self._cbuf = self.vision.getMMap()
      # -------------------------------------------------
      # outer boundaries: Top, Left, Right, Bottom
      # inner lines: top, left, right, bottom
      # pentalty box: 1pleft, 2pright
      # from page 31 of the Robocup Soccer Simulator manual:
      self.lines = {"top": ["lt", "ct", "rt"],
                    "left": ["lt", "glt", "gl", "glb", "lb"],
                    "bottom": ["lb", "cb", "rb"],
                    "right": ["rb", "grb", "gr", "grt", "rt"],
                    "Top": ["tl50", "tl40", "tl30", "tl20", "tl10", "t0",
                            "tr50", "tr40", "tr30", "tr20", "tr10"],
                    "Left": ["lt30", "lt20", "lt10", "l0",
                             "lb30", "lb20", "lb10"],
                    "Bottom": ["bl50", "bl40", "bl30", "bl20", "bl10", "b0",
                               "br50", "br40", "br30", "br20", "br10"],
                    "Right": ["rt30", "rt20", "rt10", "r0",
                              "rb30", "rb20", "rb10"],
                    "center": ["t0", "ct", "c", "cb", "b0"],
                    "1pleft": ["plt", "plc", "plb"],  
                    "2pright": ["prt", "prc", "prb"],
                    "a": ["plt", "lt20"], # draw pentalty box sides
                    "A": ["plb", "lb20"], # draw pentalty box sides
                    "z": ["prt", "rt20"], # draw pentalty box sides
                    "Z": ["prb", "rb20"], # draw pentalty box sides
                    }
      self.data = CBuffer(self._cbuf)
      self.rgb = (0, 1, 2) # offsets to RGB
      self.format = "RGB"
      Camera.__init__(self, self.width, self.height, self.depth,
                      "Robocup Camera View")
      self.subtype = "robocup"
      self.data = CBuffer(self._cbuf)

   def getPoint( self, distance, direction): # meters, angle off center
      row = self.height - \
            self.height * cos( direction * PIOVER180 ) * distance/100.0
      col = self.width/2.0 \
            + self.width * sin( direction * PIOVER180 ) * distance/100.0
      if row < 0 or row >= self.height:
         return None, None # off screen
      if col < 0 or col >= self.width:
         return None, None # off screen
      return [int(col), int(row)]

   def lookupLines( self, flagName ):
      retval = []
      for lineName in self.lines:
         if flagName in self.lines[lineName]:
            retval.append( lineName )
      return retval

   def update(self):
      if not self.active: return
      try:
         see = self.robot.see
      except:
         print "waiting for Robocup camera to come online..."
         return # not ready yet
      see.sort(lambda x,y: cmp(y[1],x[1]))
      objlist = []
      linePoints = {}
      for s in self.lines:
         linePoints[s] = []
      for item in see:
         # item is something like: [['f', 'c'], 14, 36, 0, 0]
         if len(item) >= 3: # otherwise, can't do much without direction
            if item[0][0] == "f" or item[0][0] == "g": # it's a flag or goal
               flagName = ""
               for ch in item[0][1:]:
                  flagName += "%s" % ch
               onLines = self.lookupLines( flagName )
               for onLine in onLines:
                  # distance, direction
                  x, y = self.getPoint( item[1], item[2])
                  if x != None and y != None:
                     linePoints[onLine].append( (x, y) )
            if item[0][0] == "p" or \
                   item[0][0] == "b" or \
                   item[0][0] == "g" or \
                   (item[0][0] == "f" and item[0][1] == "g"):
               itemName = ""
               for ch in item[0]:
                  itemName += "%s" % ch
               if x != None and y != None:
                  retval = self.getPoint(item[1],item[2])
                  objlist.append( (itemName, retval[0], retval[1]) )
      try:
         self._dev.updateMMap(linePoints, objlist)
      except TypeError:
         print "error in RobocupCamera data format: ignored"
      self.processAll() # filters
