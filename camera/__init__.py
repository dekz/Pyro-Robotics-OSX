""" A Base Camera class """

from pyrobot.vision import PyrobotImage
from pyrobot.robot.device import Device

import Tkinter
import PIL.PpmImagePlugin
import Image, ImageTk, types, time, struct

def display(item):
   print item

def listFilter(deviceName, allArgs):
   retval = 'self.robot.%s.addFilter("%s",' % (deviceName, allArgs[0])
   if len(allArgs) > 1:
      for a in allArgs[1]:
         retval += str(a) + ","
   return retval + ")"

def makeArgList(item):
   if type(item) == type(""):
      return (item, )
   return (item[0], item[1:])

class CBuffer:
   """
   A private buffer class to transmute the CBuffer we get in data
   into something that looks like a Python list.
   """
   def __init__(self, cbuf):
      self.data = cbuf

   def __str__(self):
      return "<pyrobot.camera.CBuffer instance, %d bytes>" % len(self.data)

   def __getitem__(self, key):
      if isinstance(key, types.SliceType):
         if key.stop > len(self):
            stop = len(self)
         else:
            stop = key.stop
         return struct.unpack("B" * (stop - key.start),
                            self.data[key.start:stop])
      else:
         return struct.unpack("B", self.data[key])[0]

   def sort(self):
      pass

   def __setitem__(self, key, value):
      if isinstance(key, types.SliceType):
         if key.stop > len(self):
            stop = len(self)
         else:
            stop = key.stop
         return struct.unpack("B" * (stop - key.start),
                            self.data[key.start:stop])
      else:
         # FIX: can't do this from Python, need C function
         self.data[key] = struct.pack("B", value)

   def __len__(self):
      return len(self.data)

class Camera(PyrobotImage, Device):
   """
   A base class for Camera
   """
   def __init__(self, width, height, depth = 3, title = "Camera View", parent = None, visible = 0, async=1):
      """
      To specify the resolution of a particular camera, overload this
      constructor with one that initalizes the dimensions itself
      """
      PyrobotImage.__init__(self, width, height, depth, 0)
      self.app = 0
      self.title = title
      self.filterMode = 1
      self.callbackList = []
      self.filterResults = []
      self.callbackTextList = []
      Device.__init__(self, 'camera', async=async)
      # specific camera type will define self.rgb = (0, 1, 2) offsets
      # and self.format = "RGB", for example
      self.lastWindowUpdate = 0
      self.updateWindowInterval = 0.0 # update window once a second
      self.update() # call it once to initialize
      self.image = []
      self.data = self.data
      self.grayscale = []
      self.height = self.height
      self.width = self.width
      self.depth = self.depth
      self.filters = self.callbackTextList
      self.lastX, self.lastY = 0, 0
      # Required:
      self.startDevice()
      # make these visible by default
      if visible and self.vision:
         self.makeWindow()

   def setFilterList(self, filterList):
      """
      Filters take the form: ("name", (args))
      Example: cam.setFilterList([("superColor",1,-1,-1,0),("meanBlur",3)]) 
      """
      myList = map(makeArgList, filterList)
      self.vision.setFilterList(myList)
      # if paused, update the screen
      if not self.getActive():
         self.updateOnce()

   def popFilterList(self):
      self.vision.popFilterList()
      # if paused, update the screen
      if not self.getActive():
         self.updateOnce()

   def getFilterList(self):
      return self.vision.getFilterList()

   def loadFilters(self):
      import tkFileDialog, pickle
      fileName = tkFileDialog.askopenfilename()
      fp = open(filename, "r")
      self.clearCallbackList()
      self.callbackList.extend( pickle.load(fp) )
      fp.close()

   def saveFilters(self):
      # doesn't work on arbitrary filters
      import tkFileDialog, pickle
      fileName = tkFileDialog.asksaveasfilename()
      fp = open(fileName, "w")
      pickle.dump(self.callbackList, fp)
      fp.close()

   def getData(self):
      data = [0 for y in range(self.height * self.width * self.depth)]
      for x in range(self.width):
         for y in range(self.height):
            rgb = self.getVal(x, y)
            data[(x + y * self.width) * self.depth + 0] = rgb[self.rgb[0]]
            data[(x + y * self.width) * self.depth + 1] = rgb[self.rgb[1]]
            data[(x + y * self.width) * self.depth + 2] = rgb[self.rgb[2]]
      return data

   def stopMovie(self):
      self.vision.stopMovie()

   def continueMovie(self):
      self.vision.continueMovie()

   def startMovie(self, filename = None):
      if filename == None:
         import tkFileDialog
         filename = tkFileDialog.asksaveasfilename()
      print "starting movie with '%s'..." % filename
      self.vision.startMovie(filename)

   def saveImage(self, filename = None):
      if filename == None:
         import tkFileDialog
         filename = tkFileDialog.asksaveasfilename()
      # faster than saveToFile, as it is in C
      print "saving image to '%s'..." % filename,
      self.vision.saveImage(filename);
      print "done!"

   def saveAsTGA(self, path = "~/V4LGrab.tga"):
      """
      Save a copy of the image to disk, in TGA format (Gimp and display
      can read it).

      path is the name of the save file, and defaults to '~/V4LGrab.tga'
      """
      file = open(path, "w")
      file.write("\x00") #byte 0
      file.write("\x00") #byte 1
      if self.color:
         file.write("\x02") #type 2, uncompressed color
      else:
         file.write("\x03") #type 3, uncompressed greyscale
      file.write("\x00"*5) #Color Map (3-7); data is ignored
      file.write("\x00\x00") #X Origin
      file.write("\x00\x00") #Y Origin
      file.write("%c%c" % (self.width & 0xFF, self.width >> 8)) #Width
      file.write("%c%c" % (self.height & 0xFF, self.height >> 8)) #Height
      file.write("%c" % (self.depth*8)) #bpp
      file.write("\x20") #attributes
      file.write(self._cbuf)
      file.close

   def update(self):
      """
      Update method for getting next sequence from a video camera.
      """
      pass

   def updateOnce(self):
      oldActive = self.getActive()
      self.setActive(1)
      self.update()
      self.processAll()
      self.updateWindow()
      self.setActive(oldActive)

   def makeFilterMenu(self, data):
      menu = []
      lastCat = ""
      for line in data:
         category, subcat, args = line[0], line[1], line[2:]
         if category != lastCat:
            menu.append([category, [[subcat, lambda self=self, args=args: self.addFilter(*args)]]])
         else:
            menu[-1][1].append( [subcat, lambda self=self, args=args: self.addFilter(*args)] )
         lastCat = category
      return menu

   def setTitle(self, title):
      self.title = title
      try:
         self.window.wm_title(self.title)
      except:
         pass
   def printit(self, event):
      print "Pressed:", event

   def makeWindow(self):
      try:
         self.window.state()
         ok = 1
      except:
         ok = 0
      if ok:
         self.window.deiconify()
      else:
         import pyrobot.system.share as share
         try:
            if not share.gui:
               share.gui = Tkinter.Tk()
               share.gui.withdraw()
            self.window = Tkinter.Toplevel(share.gui)
         except:
            print "Pyrobot camera cannot make window. Check DISPLAY variable."
            self.setVisible(0)
            return
         self.window.wm_title(self.title)
         w, h = self.width, self.height
         #while w < 310:
         #   w, h = map(lambda x: x * 2, (w, h))
         self.canvas = Tkinter.Canvas(self.window, width = w, height = h)
         self.canvas.pack({'fill': 'both', 'expand': 'y', 'side': 'bottom'})
         self.canvas.bind("<Button-1>", self.processLeftClickDown)
         self.canvas.bind("<ButtonRelease-1>", self.processLeftClickUp)
         self.canvas.bind("<Button-2>", self.processMiddleClick)
         self.canvas.bind("<Button-3>", self.processRightClick)
         self.canvas.bind("<Return>", lambda event: self.updateOnce())
         self.canvas.bind("-", lambda event: self.popCallbackList())
         self.canvas.bind("=", lambda event: self.listCallbackList())
         self.canvas.bind("!", lambda event: self.clearCallbackList())
         self.canvas.bind("+", lambda event: self.toggleFilterMode())
         self.canvas.bind("<space>", self.togglePausePlay)
         self.canvas.focus_set()
         self.window.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.hideWindow)

         if self.vision:
            filterData = self.vision.getMenu()
         else:
            filterData = []

         filterList = [['List filters', self.listCallbackList, "="],
                       ['Toggle filters', self.toggleFilterMode, "+"],
                       None,
                       ['Clear filters', [["Last", self.popCallbackList, "-"],
                                          ['All', self.clearCallbackList, "*"]]],
                       None]

         filterList.extend( self.makeFilterMenu(filterData) )

         menu = [('File',[#['Load Filters...',self.loadFilters],
                          #['Save Filters...', self.saveFilters],
                          #None,
                          ['Save Image...', self.saveImage],
                          None,
                          ['Start movie...', self.startMovie],
                          ['Stop movie...', self.stopMovie],
                          ['Continue movie...', self.continueMovie],
                          None,
                          ['Close',self.hideWindow] 
                          ]),
                 ('View', [['Pause/Play', self.togglePausePlay, "<Space>"],
                           ['Update', self.updateButton, "<Enter>"],
                           None,
                           ['Fast Update (10Hz)', lambda self=self: self.setUpdateInterval(0.1)],
                           ['Medium Update (5Hz)', lambda self=self: self.setUpdateInterval(0.2)],
                           ['Normal Update (1Hz)', lambda self=self: self.setUpdateInterval(1.0)],
                           ['Slow Update (.5Hz)', lambda self=self: self.setUpdateInterval(2.0)],
                           ]),
                 ('Filter', filterList)]
         
         # create menu
         self.mBar = Tkinter.Frame(self.window, relief=Tkinter.RAISED, borderwidth=2)
         self.mBar.pack(fill=Tkinter.X, expand='n', side = "top")
         self.goButtons = {}
         self.menuButtons = {}
         for entry in menu:
            text, func, accel = None, None, None
            if len(entry) == 2:
               text, func = entry
            elif len(entry) == 3:
               text, func, accel = entry
               print accel
            self.mBar.tk_menuBar(self.makeMenu(self.mBar, text, func, accel))
      self.setVisible(1)
      self.window.aspect(self.width, self.height + 30,
                         self.width, self.height + 30)
      self.window.minsize(200, 0)
      while self.window.tk.dooneevent(2): pass

   def togglePausePlay(self, event = None):
      self.setActive(not self.active)

   def pauseButton(self):
      self.setActive(0)

   def playButton(self):
      self.setActive(1)

   def updateButton(self):
      self.updateOnce()

   def setUpdateInterval(self, val):
      self.updateWindowInterval = val

   def apply(self, command, *args):
      if type(command) == type(""):
         return self.vision.applyFilter( (command, args) )
      else:
         raise "Improper format for apply()"

   def addFilter(self, func, *args):
      """
      Add a filter to the filter list.
      Example: self.robot.camera[0].addFilter( "superColor", 3)
      """
      import inspect
      if type(func) == type(""):
         self.callbackList.append( lambda self=self, func=func, args=args: self.apply(func, *args))
         self.callbackTextList.append( listFilter( self.title, (func, args) ))
      else:
         self.callbackList.append( func )
         try:
            self.callbackTextList.append( inspect.getsource( func ))
         except:
            self.callbackTextList.append( "[User Defined Function]" )
      if not self.getActive():
         # if paused, apply it once, and update
         self.processAll()
      return len(self.callbackList) - 1

   def makeMenu(self, bar, name, commands, accel = None):
      """ Assumes self.menuButtons exists """
      menu = Tkinter.Menubutton(bar,text=name,underline=0,accelerator=accel)
      self.menuButtons[name] = menu
      menu.pack(side=Tkinter.LEFT,padx="2m")
      menu.filemenu = Tkinter.Menu(menu)
      for cmd in commands:
         if cmd == None:
            menu.filemenu.add_separator()
         elif type(cmd[1]) == type([1,]):
            newmenu = Tkinter.Menu(menu)
            for command in cmd[1]:
               if len(command) == 3:
                  text, func, accel = command
               elif len(command) == 2:
                  text, func = command
                  accel = None
               newmenu.add_command(label = text, command=func, accelerator=accel)
            menu.filemenu.add_cascade(label=cmd[0], menu=newmenu)
         else:
            if len(cmd) == 3:
               text, func, accel = cmd
            elif len(cmd) == 2:
               text, func = cmd
               accel = None
            menu.filemenu.add_command(label=text,command=func,accelerator=accel)
      menu['menu'] = menu.filemenu
      return menu

   def listCallbackList(self):
      print "Filters:"
      map(display, self.callbackTextList)

   def togglePlay(self, event):
      self.setActive(not self.getActive())

   def toggleFilterMode(self):
      self.filterMode = not self.filterMode
      if not self.getActive():
         self.updateOnce()

   def getCanvasWidth(self):
      return self.window.winfo_width() - 2

   def getCanvasHeight(self):
      return self.window.winfo_height() - 2 - 28

   def processLeftClickDown(self, event):
      x, y = event.x/float(self.getCanvasWidth()), event.y/float(self.getCanvasHeight())
      self.lastX, self.lastY = int(x * self.width), int(y * self.height)

   def processLeftClickUp(self, event):
      x, y = event.x/float(self.getCanvasWidth()), event.y/float(self.getCanvasHeight())
      x, y = int(x * self.width), int(y * self.height)
      if (x == self.lastX and y == self.lastY):
         rgb = self.vision.get(int(x), int(y))
         print 'self.robot.%s.addFilter("match", %d, %d, %d)' % (self.title, rgb[0], rgb[1], rgb[2])
         return self.addFilter("match", rgb[0], rgb[1], rgb[2])
      else:
         print 'self.robot.%s.addFilter("histogram", %d, %d, %d, %d, 8)' % (self.title, self.lastX, self.lastY, x, y)
         return self.addFilter("histogram", self.lastX, self.lastY, x, y, 8)

   def processMiddleClick(self, event):
      x, y = event.x/float(self.getCanvasWidth()), event.y/float(self.getCanvasHeight())
      x, y = int(x * self.width), int(y * self.height)
      rgb = self.vision.get(int(x), int(y))
      print 'self.robot.%s.addFilter("match", %d, %d, %d, %d, %d)' % (self.title, rgb[0], rgb[1], rgb[2], 30, 1)
      return self.addFilter("match", rgb[0], rgb[1], rgb[2], 30, 1)

   def processRightClick(self, event):
      x, y = event.x/float(self.getCanvasWidth()), event.y/float(self.getCanvasHeight())
      x, y = int(x * self.width), int(y * self.height)
      rgb = self.vision.get(int(x), int(y))
      print 'self.robot.%s.addFilter("match", %d, %d, %d, %d, %d)' % (self.title, rgb[0], rgb[1], rgb[2], 30, 2)
      return self.addFilter("match", rgb[0], rgb[1], rgb[2], 30, 2)

   def hideWindow(self):
      self.setVisible(0)
      self.window.withdraw()
      
   def getImage(self):
      return PIL.PpmImagePlugin.Image.fromstring('RGBX',
                                                 (self.width, self.height),
                                                 self._cbuf, 'raw', self.format)
   def updateWindow(self):
      if self.getVisible():
         now = time.time()
         if now - self.lastWindowUpdate < self.updateWindowInterval:
            return
         self.lastWindowUpdate = now
         self.canvas.delete("image")
         self.im = self.getImage()
         try:
            self.im = self.im.resize( (self.getCanvasWidth(),
                                       self.getCanvasHeight()) )
         except:
            print "error: could not resize window"         
         self.image = ImageTk.PhotoImage(self.im)
         try:
            self.canvas.create_image(0, 0, image = self.image,
                                     anchor=Tkinter.NW,
                                     tag="image")
         except:
            pass # just skip it
         while self.window.tk.dooneevent(2): pass

   def startDevice(self):
      self.state = "started"
      return self

   def stopDevice(self):
      self.state = "stopped"
      self.setVisible(0)
      return "Ok"

   def getDeviceData(self):
      return self.data

   def getDeviceState(self):
      return self.state

   def updateDevice(self):
      self.update()

   def delFilter(self, pos):
      self.callbackList.remove(pos)
      self.callbackTextList.remove(pos)
      if not self.getActive():
         self.updateOnce()
      return "Ok"

   def popCallbackList(self):
      if len(self.callbackList) > 0:
         self.callbackList.pop()
         self.callbackTextList.pop()
      if not self.getActive():
         self.updateOnce()
      return "Ok"

   def clearCallbackList(self):
      # callback is a function that has first param
      # as self (ie, the visionSystem object)
      while len(self.callbackList) > 0: self.callbackList.pop()
      while len(self.callbackTextList) > 0: self.callbackTextList.pop()
      if not self.getActive():
         self.updateOnce()
      return "Ok"

   def clearFilters(self):
      self.clearCallbackList()
      
   def processAll(self):
      if self.filterMode and self.vision != None:
         self.vision.applyFilterList()
         while len(self.filterResults): self.filterResults.pop()
         for filterFunc in self.callbackList:
            self.filterResults.append( filterFunc(self) )

if __name__ == '__main__':
   from pyrobot.vision.cvision import VisionSystem
   from pyrobot.camera.fake import FakeCamera
   cam = FakeCamera(visionSystem = VisionSystem())
   cam.makeWindow()
   cam.updateWindow()
   cam.window.mainloop()
