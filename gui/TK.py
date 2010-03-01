import Tkinter, time, sys, os, types, traceback
from pyrobot.gui import *
import pyrobot.gui.widgets.TKwidgets as TKwidgets
from pyrobot.system.version import *
from pyrobot.engine import *
from pyrobot.gui.widgets.tree import TreeWindow
from pyrobot.gui.widgets.TKwidgets.Picklist import Picklist
from pyrobot.robot.device import Device
import pyrobot.system as system
import pyrobot.system.share as share
from posixpath import exists
from pyrobot.tools.joystick import Joystick
from pyrobot import pyrobotdir

def ask(title, qlist):
   d = TKwidgets.AskDialog(share.gui, title, qlist)
   d.top.bind("<Return>", lambda event: d.OkPressed())
   ok = d.Show()
   if ok:
      retval = {"ok": 1}
      for (name, value) in qlist:
         retval[name] = d.textbox[name].get()
      d.DialogCleanup()
      return retval
   else:
      d.DialogCleanup()
      return {"ok" : 0}

if share.gui == 0:
   share.gui = Tkinter.Tk()
   share.gui.withdraw()
 
share.ask = ask

# A TK gui

class JoystickDriver(Joystick):
   def __init__(self, robot):
      self.robot = robot
      hasZ = 0
      try:
         self.robot.moveZ
         hasZ = 1
      except:
         pass
      Joystick.__init__(self, hasZ = hasZ)
   def move(self, x, y, z = None):
      if self.hasZ:
         self.robot.move(x, y, z)
      else:
         self.robot.move(x, y)

class TKgui(Tkinter.Toplevel, gui): 
   def __init__(self, engine):
      Tkinter.Toplevel.__init__(self, share.gui)
      gui.__init__(self, 'TK gui', {}, engine)
      self.name = "<tkgui>" # for checking sys.stdout.name
      self.genlist = 0
      self.frame = Tkinter.Frame(self)
      self.frame.pack(side = 'bottom', expand = "yes", anchor = "n",
                      fill = 'both')
      self.windowBrain = 0
      self.lastRun = 0
      self.lasttime = 0
      self.brainTreeWindow = None
      self.robotTreeWindow = None
      self.update_interval = 100
      self.update_interval_detail = 1.0
      self.lastButtonUpdate = 0
      self.printBuffer = []
      self.maxBufferSize = 50000 # 50k characters in buffer
                                 #set to 0 for infinite
      #store the gui structure in something nice insted of python code

      menu = [('File',[['New brain...', self.newBrain],
                       None,
                       ['Editor',self.editor],
                       ['Expression Watcher', self.makeWatcher],
                       ['Save current config as...', self.saveConfig],
                       None,
                       ['Exit',self.cleanup] 
                       ]),
              ('Window', [['Open all device windows', self.makeWindows],
                          None,
                          ['Fast Update 10/sec',self.fastUpdate],
                          ['Medium Update 3/sec',self.mediumUpdate],
                          ['Slow Update 1/sec',self.slowUpdate],
                          None,
                          ['Clear Messages', self.clearMessages],
                          ['Send Messages to Window', self.redirectToWindow],
                          ['Send Messages to Terminal', self.redirectToTerminal],
                          ]),
              ('Load',[['Server...', self.loadSim],
                       ['Robot...',self.loadRobot],
                       ['Devices...',self.loadDevice],
                       ['Brain...',self.loadBrain],
                       #['Built-in Devices', None],
                       ]),
              ('Robot',[['Joystick', self.joystick],
                        ['View', self.makeRobotTree],                         
                        None,
                        ['Forward',self.stepForward],
                        ['Back',self.stepBack],
                        ['Left',self.stepLeft],
                        ['Right',self.stepRight],
                        None,
                        ['Stop Rotate',self.stopRotate],
                        ['Stop Translate',self.stopTranslate],
                        ['Stop All',self.stopEngine],
                        None,
                        ['Unload robot', self.freeRobot],
                        None,
                        ['Update',self.update],
                        ]),
              ('Brain',[['Watch', self.openBrainWindow],
                        ['View', self.makeBrainTree], 
                        None,
                        ['Unload brain', self.freeBrain],
                        ]),
              ('Help',[['Help',self.help],
                       ['About',self.about],
                       ])
              ]
      
      self.var = Tkinter.StringVar()
      self.currentDeviceList = []      
      button1 = [('Step',self.stepEngine),
                 ('Run',self.runEngine),
                 ('Stop',self.stopEngine),
                 ('Reload Brain',self.resetEngine),
                 ]

      # create menu
      self.mBar = Tkinter.Frame(self.frame, relief=Tkinter.RAISED, borderwidth=2)
      self.mBar.pack(fill=Tkinter.X)
      self.goButtons = {}
      self.menuButtons = {}
      for entry in menu:
         self.mBar.tk_menuBar(self.makeMenu(self.mBar, entry[0], entry[1]))

      #self.menuButtons["Built-in Devices"] = Tkinter.Menubutton(self.mBar,text="Test",underline=0)

      self.frame.winfo_toplevel().title("pyrobot@%s" % os.getenv('HOSTNAME'))
      self.frame.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.cleanup)

      # create a command text area:
      self.makeCommandArea()
      # Display:
      self.loadables = [ ('button', 'Server:', self.loadSim, self.editWorld, 0), # 0 = False
                         ('button', 'Robot:', self.loadRobot, self.editRobot, self.makeRobotTree),
                         ('picklist', 'Devices:', self.loadDevice, self.editDevice, self.viewDevice), 
                         ('button', 'Brain:', self.loadBrain, self.editBrain, self.makeBrainTree), 
                        ]
      self.buttonArea = {}
      self.textArea = {}
      for item in self.loadables:
         self.makeRow(item)

      self.buttonArea["Robot:"]["state"] = 'normal'
      self.buttonArea["Server:"]["state"] = 'normal'
      ## ----------------------------------
      toolbar = Tkinter.Frame(self.frame)
      for b in button1:
         self.goButtons[b[0]] = Tkinter.Button(toolbar,text=b[0],command=b[1])
         self.goButtons[b[0]].pack(side=Tkinter.LEFT,padx=2,pady=2,fill=Tkinter.X, expand = "yes", anchor="n")
      toolbar.pack(side=Tkinter.TOP, anchor="n", fill='x', expand = "no")
      ## ----------------------------------
      self.makeRow(('status', 'Pose:', '', '', 0)) # 0 = False
      ## ----------------------------------
      self.textframe = Tkinter.Frame(self.frame)
      self.textframe.pack(side="top", expand = "yes", fill="both")
      # could get width from config
      self.status = Tkinter.Text(self.textframe, width = 60, height = 10,
                                 state='disabled',
                                 wrap='word',
                                 bg = "white")
      self.scrollbar = Tkinter.Scrollbar(self.textframe, command=self.status.yview)
      self.status.configure(yscroll=self.scrollbar.set)
      # for displaying fonts, colors, etc.: -------------------
      self.status.tag_config("red", foreground = "red")
      self.status.tag_config("black", foreground = "black")
      self.status.tag_config("green", foreground = "green")
      self.status.tag_config("blue", foreground = "blue")
      # --------------------------------------------------------
      self.scrollbar.pack(side="right", expand = "no", fill="y")
      self.status.pack(side="top", expand = "yes", fill="both")
      self.textframe.pack(side="top", fill="both")
      self.redirectToWindow()
      #self.tk_focusFollowsMouse()
      self.commandEntry.focus_force()
      self.inform("Pyrobot Version " + version() + ": Ready...")
      self.updateDeviceList(select=0)

   def freeRobot(self):
      self.updateDeviceList(clear = 1)
      gui.freeRobot(self)

   def loadDevice(self):
      gui.loadDevice(self)
      self.updateDeviceList()

   def loadRobot(self):
      gui.loadRobot(self)
      self.updateDeviceList()

   def loadBrain(self):
      gui.loadBrain(self)
      self.updateDeviceList()

   def resetEngine(self):
      gui.resetEngine(self)
      self.updateDeviceList()

   def updateDeviceList(self, clear = 0, select = -1):
      devices = []
      selDevice = None
      if not clear:
         if self.engine and self.engine.robot:
            for devType in self.engine.robot.getDevices():
               for serv in self.engine.robot.__dict__[devType]:
                  devices.append(serv.title)
            if devices != []:
               selDevice = devices[select]
      else:
         devices = [""]
         selDevice = ""
      if self.currentDeviceList != devices:
         self.currentDeviceList = devices
         self.textArea["Devices:"].setMenu(devices, selDevice)

   def editDevice(self, deviceName):
      pass # this is just selecting it from the menu

   def viewDevice(self, deviceName = None):
      deviceExp = "self.engine.robot." + self.var.get()
      try:
         dev = eval(deviceExp)
      except:
         return
      dev.makeWindow()

   def pasteCallback(self, full_id):
      self.commandEntry.insert('end', self.makeExpression(full_id))

   def execCallback(self, full_id):
      exp = self.makeExpression(full_id)
      if exp[-2:] == "()":
         help_exp = "help(%s)" % exp[:-2]
      elif exp[-2:] == "__":
         help_exp = "help(%s)" % exp
      else:
         help_exp = "help(%s.__class__)" % (exp,)
      self.processCommand(help_exp)

   def viewCallback(self, full_id):
      self.objectBrowser(self.makeExpression(full_id))

   def watchCallback(self, full_id):
      if len(full_id) == 3 and (full_id[0] == "robot" and
                                full_id[1] in self.engine.robot.devices and
                                type(full_id[2]) == type(0)):
         self.engine.robot.__dict__[ full_id[1] ][full_id[2]].makeWindow()
      else:
         self.processCommand("watch " + self.makeExpression(full_id))

   def makeExpression(self, full_id):
      self._populateEnv()
      thingStr = full_id[0]
      thing = eval(full_id[0], self.environment)
      i = 1
      while i < len(full_id):
         item = full_id[i]
         if item == "[": # array position
            pass
         elif type(item) == type("") and item[-1] == "]": # array position
            index = int(item[:-1])
            thing = thing[index]
            thingStr += "[%d]" % index
         elif item == "methods": # method
            if full_id[i+1][-2:] == "()": # method
               thingStr += ".%s%s" % (full_id[i+1][:-2], full_id[i+2:])
            else:
               thingStr += ".%s" % full_id[i+1]
            break
         elif type(thing) == type([]): # list
            thingStr += "[%s]" % item
            thing = thing[item]
         elif type(thing) == type({}): # dict
            thingStr += "[%s]" % item
            thing = thing[item]
         else:
            thingStr += ".%s" % item
            thing = thing.__dict__[item] # property
         i += 1
      return thingStr

   def getTreeContents(self, node, tree):
      self._populateEnv()
      currentName = node.full_id()[-1]
      # look up the object by path: ------------------------
      thing = eval(node.full_id()[0], self.environment)
      thingName = node.full_id()[0]
      parent = None
      position = 1
      for item in node.full_id()[1:]:
         if item == "methods": # methods
            for method in dir(thing):
               if (method[0] != "_" or method[1] == "_") and method not in thing.__dict__:
                  object = eval("thing.%s" % method)
                  if object == None:
                     tree.add_node("%s = None" % (method,), id=method, flag=0)
                  elif type(object) == type(""):
                     object = object.replace("\n", " ")
                     if len(object) > 50:
                        object = object[0:50].strip() + "..."
                     tree.add_node("%s = '%s'" % (method,object.strip()), id=method, flag=0)
                  elif type(object) in [types.FloatType, types.IntType, types.BooleanType,
                                      types.LongType, types.DictType, types.ListType, types.TupleType]:
                     tree.add_node("%s = %s" % (method,object), id=method, flag=0)
                  else:
                     docString = eval("thing.%s.__doc__" % method)
                     if docString != None:
                        docString = docString.replace("\n"," ")
                        docString = docString.strip()
                        if len(docString) > 50:
                           docString = docString[0:50].strip() + "..."
                        tree.add_node("%s(): %s" % (method,docString), id="%s()" % method, flag=0)
                     else:
                        tree.add_node("%s()" % (method,), id="%s()" % method, flag=0)                     
            return # no more things to show
         elif type(thing) == type([]): # list
            thing = thing[item]
         elif type(thing) == type({}): # dict
            thing = thing[item]
         else:
            if item in thing.__dict__:
               thing = thing.__dict__[item] # property
               thingName = item
            else:
               if item == "[":
                  if position == len(node.full_id()) - 1:
                     for i in range(len(thing)):
                        tree.add_node("[%d] - SensorValue" % i, id="%d]" % i, flag=1)
                     return
                  else:
                     pass # no need to do anything
               elif type(item) == type("") and  item[-1] == "]":
                  if position == len(node.full_id()) - 1:
                     index = int(item[:-1])
                     thing = thing[index]
                  else:
                     pass # no need?
               else:
                  return
         position += 1
      # now that you have it, see what it is: --------------
      if type(thing) == type([]): # list:
         # if a list of Devices, get them as nodes, else just as "name = value":
         if len(thing) == 0 or (len(thing) > 0 and not issubclass(type(thing[0]), Device)):
            tree.add_node("%s = %s" % (currentName, thing), id=thing, flag=0)
         else:
            for i in range(len(thing)):
               tree.add_node("%s[%d] - Device" % (currentName,i), id=i, flag=1)
         # if just strings, numbers, list them:
      else: # a complex object with parts:
         try:    iterLen = len(thing)
         except: iterLen = None
         if iterLen != None:
            tree.add_node("List [0..%d]" % (iterLen-1), id="[", flag=1)
         # first, get all of the devices, if any:
         if "devices" in thing.__dict__: # robot
            for device in thing.devices:
               tree.add_node("%s devices" % (device,), id=device, flag=1)
         # list the methods:
         tree.add_node("methods", id="methods", flag=1)
         # now, get everything else:
         dictkeys = thing.__dict__.keys()
         dictkeys.sort()
         for item in dictkeys:
            if item[0] == "_":
               pass # skip it; private
            elif type(thing.__dict__[item]) in [types.FunctionType, types.LambdaType, types.MethodType]:
               pass 
            else:
               if "devices" in thing.__dict__ and item in thing.devices: # robot
                  pass
               elif type(thing.__dict__[item]) == type({}): # dict
                  # each is a pair; list them
                  keys = thing.__dict__[item].keys()
                  keys.sort()
                  keysComma = ""
                  for key in keys:
                     if keysComma:
                        keysComma += ", '%s'" % key
                     else:
                        keysComma = "'%s'" % key
                  tree.add_node("%s = {%s}" % (item, keysComma), id=item, flag=0)
               elif type(thing.__dict__[item]) == type(''): # string
                  tree.add_node("%s = '%s'" % (item, thing.__dict__[item]), id=item, flag=0)
               else:                                        # number, other primitive
                  tree.add_node("%s = %s" % (item, thing.__dict__[item]), id=item, flag=0)

   def objectBrowser(self, objectName):
      TreeWindow(share.gui, objectName,
                 self.getTreeContents,
                 self.watchCallback,
                 self.pasteCallback,
                 self.execCallback,
                 self.viewCallback)

   def makeRobotTree(self):
      if self.engine and self.engine.robot:
         if self.robotTreeWindow:
            self.robotTreeWindow.deiconify()
            self.robotTreeWindow.tree.root.collapse()
            self.robotTreeWindow.tree.root.expand()
         else:
            self.robotTreeWindow = TreeWindow(share.gui, "robot", self.getTreeContents,
                                              self.watchCallback, self.pasteCallback,
                                              self.execCallback, self.viewCallback)
            self.robotTreeWindow.tree.root.expand()

   def makeBrainTree(self):
      if self.engine and self.engine.brain:
         if self.brainTreeWindow:
            self.brainTreeWindow.deiconify()
            self.brainTreeWindow.tree.root.collapse()
            self.brainTreeWindow.tree.root.expand()
         else:
            self.brainTreeWindow = TreeWindow(share.gui, "brain", self.getTreeContents,
                                              self.watchCallback, self.pasteCallback,
                                              self.execCallback, self.viewCallback)
            self.brainTreeWindow.tree.root.expand()

   def makeWindows(self):
      if self.engine and self.engine.robot:
         for devType in self.engine.robot.getDevices():
            for serv in self.engine.robot.__dict__[devType]:
               serv.makeWindow()
      else:
         print "Error: you need to load a robot first"

   def makeCommandArea(self):
      # ---------------------------------
      self.commandFrame = Tkinter.Frame(self.frame)
      self.commandFrame['relief'] = 'raised'
      self.commandFrame['bd']	 = '2'
      self.commandLabel = Tkinter.Label(self.commandFrame)
      self.commandLabel["text"] = "Command:"
      self.commandLabel.pack({'expand':'no', 'side':'left', 'fill':'none'})
      # create a command 
      self.commandEntry = Tkinter.Entry(self.commandFrame)
      self.commandEntry.bind('<Return>', self.CommandReturnKey)
      self.commandEntry.bind('<Tab>', self.CommandTabKey)
      self.commandEntry.bind('<Control-p>', self.CommandPreviousKey)
      self.commandEntry.bind('<Control-n>', self.CommandNextKey)
      self.commandEntry.bind('<Up>', self.CommandPreviousKey)
      self.commandEntry.bind('<Down>', self.CommandNextKey)
      self.commandEntry["relief"] = "ridge"
      self.commandEntry.pack({'expand':'yes', 'side':'bottom', 'fill':'x'})
      self.commandFrame.pack({'expand':'no', 'side':'bottom', 'fill':'x'})
      # ---------------------------------      

   def makeRow(self, item):
      type, load, loadit, editit, viewit = item
      tempframe = Tkinter.Frame(self.frame)
      if type == 'button':
         self.buttonArea[load] = Tkinter.Button(tempframe, text = load,
                                                 width = 10, command = loadit,
                                                 state='disabled')
         self.textArea[load] = Tkinter.Button(tempframe, command=editit, justify="right", state='disabled')
         if viewit:
            self.buttonArea["View " + load] = Tkinter.Button(tempframe, text = "View",
                                                 width = 10, command = viewit,
                                                 state='disabled')
            self.buttonArea["View " + load].pack(side=Tkinter.RIGHT, fill = "none", expand = "no", anchor="n")
      elif type == 'status':
         self.buttonArea[load] = Tkinter.Label(tempframe, width = 10, text = load )
         self.textArea[load] = Tkinter.Label(tempframe, justify="left")
      elif type == 'picklist':
         self.buttonArea[load] = Tkinter.Button(tempframe, text = load,
                                                 width = 10, command = loadit,
                                                 state='disabled')
         self.textArea[load] = Picklist(tempframe, self.var, "", command=editit)
         if viewit:
            self.buttonArea["View " + load] = Tkinter.Button(tempframe, text = "View",
                                                 width = 10, command = viewit,
                                                 state='disabled')
            self.buttonArea["View " + load].pack(side=Tkinter.RIGHT, fill = "none", expand = "no", anchor="n")
      self.buttonArea[load].pack(side=Tkinter.LEFT, fill = "none", expand = "no", anchor="n")
      self.textArea[load].pack(side=Tkinter.RIGHT, fill="x", expand = "yes", anchor="n")
      tempframe.pack(side = "top", anchor = "s", fill = "x")

   def redirectToWindow(self):
      # --- save old sys.stdout, sys.stderr
      self.sysstdout = sys.stdout
      sys.stdout = self # has a write() method
      self.sysstderror = sys.stderr
      sys.stderr = self # has a write() method

   def redirectToTerminal(self):
      # --- save old sys.stdout, sys.stderr
      sys.stdout = self.sysstdout
      sys.stderr = self.sysstderror

   def openBrainWindow(self):
      try:
         self.brain.window.state()
      except:
         if self.engine and self.engine.brain:
            self.engine.brain.makeWindow()

   def redrawWindowBrain(self):
      if getattr(self.engine.brain, "redraw", None) is None:
         return
      try:
         self.engine.brain.redraw()
         self.lastRun = self.engine.brain.lastRun
      except:
         print "Brain redraw exception:"
         traceback.print_exc()

   def fastUpdate(self):
      self.update_interval = 100

   def mediumUpdate(self):
      self.update_interval = 333

   def slowUpdate(self):
      self.update_interval = 1000

   def CommandPreviousKey(self, event):
      if self.history_pointer - 1 <= len(self.history) and self.history_pointer - 1 >= 0:
         self.history_pointer -= 1
         self.commandEntry.delete(0, 'end')
         self.commandEntry.insert(0, self.history[self.history_pointer])
      else:
         print 'No more commands!', chr(7)

   def CommandNextKey(self, event):
      self.commandEntry.delete(0, 'end')
      if self.history_pointer + 1 <= len(self.history) and self.history_pointer + 1 >= 0:
         self.history_pointer += 1
         if self.history_pointer <= len(self.history) - 1:
            self.commandEntry.insert(0, self.history[self.history_pointer])
      else:
         print 'No more commands!', chr(7)

   def CommandTabKey(self, event):
      from string import strip
      command = strip(self.commandEntry.get())
      # Macro-style substitutions here:
      if len(command)>= 1 and command[0] == ".":
         if len(command) >= 2:
            if command[1].isalpha():
               command = "self" + command
         else:
            command = "self" + command
      # Process the tab:
      # peel off the dot, if one:
      if len(command) > 0:
         if command[-1] == ".":
            command = command[:-1]
      # now evaluate:
      self._populateEnv()
      try:
         exec("_methods = %s.__doc__" % command) in self.environment
         methods = "   " + self.environment["_methods"]
      except:
         methods = ""
      if methods != '':
         print "Help: ----------------------------------------------------"
         print methods
      succeed = 0
      try:
         exec("_methods = dir(%s)" % command) in self.environment
         succeed = 1
      except:
         pass
      if succeed:
         methods = self.environment["_methods"]
         prettyMethods = []
         for m in methods:
            if m[0] == "_": continue
            succeed = 1
            try: exec("_methods = type(%s.%s)" % (command, m)) in self.environment
            except: succeed = 0
            if succeed and self.environment["_methods"] == types.MethodType:
               prettyMethods.append("%s()" % m)
            else:
               prettyMethods.append(m)
      else:
         prettyMethods = ["Nothing appropriate"]
      cnt = 1
      print "Completion data: -----------------------------------------"
      for item in prettyMethods:
         try:
            print "%-30s " % item,
         except:
            print item
         if cnt % 2 == 0:
            print
         cnt += 1
      self.commandEntry.focus()
      if cnt % 2 != 1:
         print
      print "----------------------------------------------------------"
      if "_methods" in self.environment: del self.environment["_methods"]
      return "break" # drops the tab from propagating

   def CommandReturnKey(self, event):
      from string import strip
      command = strip(self.commandEntry.get())
      self.commandEntry.delete(0, 'end')
      done = self.processCommand(command)
      if done:
         self.cleanup()

   def joystick(self):
      self.joywin = JoystickDriver(self.engine.robot)

   def about(self):
      #self.redirectToTerminal()
      system.about()
      #self.redirectToWindow()

   def help(self):
      #self.redirectToTerminal()
      system.help()
      system.usage()
      #self.redirectToWindow()

   def editor(self):
      import os
      if os.getenv("EDITOR"):
         os.system(os.getenv("EDITOR") + " &")
      else:
         os.system("emacs &")
   def newBrain(self):
      import os
      for i in range(1, 100):
         myfile = "~/MyBrain%d.py" % i
         if not exists(myfile):
            break
      os.system( "cp " + pyrobotdir() + ("/build/brainTemplate.py %s" % myfile))
      if os.getenv("EDITOR"):
         os.system(os.getenv("EDITOR") + " %s &" % myfile)
      else:
         os.system("emacs %s &"  % myfile)
   def editBrain(self):
      import os
      if os.getenv("EDITOR"):
         os.system(os.getenv("EDITOR") + " " + self.engine.brainfile + "&")
      else:
         os.system("emacs " + self.engine.brainfile + "&")
   def editWorld(self):
      import os
      if os.getenv("EDITOR"):
         os.system(os.getenv("EDITOR") + " " + self.engine.worldfile + "&")
      else:
         os.system("emacs " + self.engine.worldfile + "&")
   def editRobot(self):
      import os
      if os.getenv("EDITOR"):
         os.system(os.getenv("EDITOR") + " " + self.engine.robotfile + "&")
      else:
         os.system("emacs " + self.engine.robotfile + "&")
   def update(self):
      now = time.time() 
      needToUpdateState = 1
      try: needToUpdateState = self.engine.brain.needToStop
      except: pass
      if needToUpdateState:
         if type(self.engine.robot) != type(1):
            self.engine.robot.update()
      self.redrawWindowBrain()
      if self.watcher:
         self.watcher.update(self.environment)
      self.updateStatus()
      # -----------------------
      if self.engine.robot != 0:
         if self.engine.robot.stall:
            bump = "[STALL!]"
         else:
            bump = ''
         try:
            self.textArea['Pose:'].config(text = "X: %4.2f Y: %4.2f Th: %4.0f  %s"\
                                          % (self.engine.robot.x,
                                             self.engine.robot.y,
                                             self.engine.robot.th,
                                             bump))
         except:
            pass
         for deviceType in self.engine.robot.getDevices():
            for device in self.engine.robot.__dict__[deviceType]:
               if device.getVisible():
                  device.updateWindow()
      # Don't need to do the rest of this but once a second
      if now - self.lastButtonUpdate < 1:
         self.after(self.update_interval,self.update)
         return
      self.lastButtonUpdate = now
      if self.textArea['Brain:']["text"] != self.engine.brainfile:
         self.textArea['Brain:'].config(text = self.engine.brainfile)
      if self.textArea['Server:']["text"] != self.engine.worldfile:
         self.textArea['Server:'].config(text = self.engine.worldfile)
      if self.textArea['Robot:']["text"] != self.engine.robotfile:
         self.textArea['Robot:'].config(text = self.engine.robotfile)
      # enable?
      if self.textArea["Brain:"]["text"]:
         if self.textArea["Brain:"]["state"] == 'disabled':
            self.textArea["Brain:"]["state"] = 'normal'
         if self.buttonArea['View Brain:']["state"] == 'disabled':
            self.buttonArea['View Brain:']["state"] = 'normal'
      else:
         if self.textArea["Brain:"]["state"] != 'disabled':
            self.textArea["Brain:"]["state"] = 'disabled'
         if self.buttonArea['View Brain:']["state"] != 'disabled':
            self.buttonArea['View Brain:']["state"] = 'disabled'
      if self.textArea["Server:"]["text"]:
         if self.textArea["Server:"]["state"] == 'disabled':
            self.textArea["Server:"]["state"] = 'normal'
      else:
         if self.textArea["Server:"]["state"] != 'disabled':
            self.textArea["Server:"]["state"] = 'disabled'
      if self.textArea["Robot:"]["text"]:
         if self.textArea["Robot:"]["state"] == 'disabled':
            self.textArea["Robot:"]["state"] = 'normal'
         if self.buttonArea['View Robot:']["state"] == 'disabled':
            self.buttonArea['View Robot:']["state"] = 'normal'
         if self.textArea["Devices:"]["state"] == 'disabled':
            self.textArea["Devices:"]["state"] = 'normal'
      else:
         if self.textArea["Robot:"]["state"] != 'disabled':
            self.textArea["Robot:"]["state"] = 'disabled'
         if self.buttonArea['View Robot:']["state"] != 'disabled':
            self.buttonArea['View Robot:']["state"] = 'disable'
         if self.textArea["Devices:"]["state"] != 'disabled':
            self.textArea["Devices:"]["state"] = 'disabled'
      # Buttons?
      if self.textArea["Robot:"]["text"]: # have a robot!
         if self.menuButtons['Robot']["state"] == 'disabled':
            self.menuButtons['Robot']["state"] = 'normal'
         if self.buttonArea["Brain:"]["state"] == 'disabled':
            self.buttonArea["Brain:"]["state"] = 'normal'
         if self.goButtons['Reload Brain']["state"] == 'disabled':
            self.goButtons['Reload Brain']["state"] = 'normal'
         if self.buttonArea['Devices:']["state"] == 'disabled':
            self.buttonArea['Devices:']["state"] = 'normal'
      else:
         if self.menuButtons['Robot']["state"] != 'disabled':
            self.menuButtons['Robot']["state"] = 'disabled'
         #if self.menuButtons['Load']["state"] != 'disabled':
         #   self.menuButtons['Load']["state"] = 'disabled'
         if self.buttonArea["Brain:"]["state"] != 'disabled':
            self.buttonArea["Brain:"]["state"] = 'disabled'
         if self.goButtons['Reload Brain']["state"] != 'disabled':
            self.goButtons['Reload Brain']["state"] = 'disabled'
         if self.buttonArea["Devices:"]["state"] != 'disabled':
            self.buttonArea["Devices:"]["state"] = 'disabled'
      if self.textArea["Brain:"]["text"]: # have a brain!
         if self.menuButtons['Brain']["state"] == 'disabled':
            self.menuButtons['Brain']["state"] = 'normal'
         if self.goButtons['Run']["state"] == 'disabled':
            self.goButtons['Run']["state"] = 'normal'
         if self.goButtons['Step']["state"] == 'disabled':
            self.goButtons['Step']["state"] = 'normal'
         if self.goButtons['Stop']["state"] == 'disabled':
            self.goButtons['Stop']["state"] = 'normal'
         if self.goButtons['Reload Brain']["state"] == 'disabled':
            self.goButtons['Reload Brain']["state"] = 'normal'
         #if self.goButtons['View']["state"] == 'disabled':
         #   self.goButtons['View']["state"] = 'normal'
      else:
         if self.menuButtons['Brain']["state"] != 'disabled':
            self.menuButtons['Brain']["state"] = 'disabled'
         if self.goButtons['Run']["state"] != 'disabled':
            self.goButtons['Run']["state"] = 'disabled'
         if self.goButtons['Step']["state"] != 'disabled':
            self.goButtons['Step']["state"] = 'disabled'
         if self.goButtons['Stop']["state"] != 'disabled':
            self.goButtons['Stop']["state"] = 'disabled'
         if self.goButtons['Reload Brain']["state"] != 'disabled':
            self.goButtons['Reload Brain']["state"] = 'disabled'
         #if self.goButtons['View']["state"] != 'disabled':
         #   self.goButtons['View']["state"] = 'disabled'
      if self.var.get() == "":
         if self.buttonArea['View Devices:']["state"] != 'disabled':
            self.buttonArea['View Devices:']["state"] = 'disabled'
      else:
         if self.buttonArea['View Devices:']["state"] == 'disabled':
            self.buttonArea['View Devices:']["state"] = 'normal'
      self.after(self.update_interval,self.update)
      
   def run(self, command = []):
      self.done = 0
      while len(command) > 0 and self.done == 0:
         print command[0],
         retval = command[0]
         if retval:
            self.processCommand(retval)
         command = command[1:]
      if not self.done:
         self.after(self.update_interval,self.update)
         self.mainloop()

   def inform(self, message):
      self.write(message + "\n")

   def parsePrint(self, message, tag = None):
      if tag:
         self.status.insert('end', message, tag)
      else:
         if "\n" in message.strip():
            self.status.insert('end', message)
         elif len(message) > 3 and message[:3] == ">>>":
            # parse it and display it
            self.status.insert('end', message[:3]) # >>>
            self.status.insert('end', message[3:], "red")
         elif ":" in message:
            parts = message.split(":")
            self.status.insert('end', parts[0], "blue")
            for p in parts[1:]:
               self.status.insert('end', ":")
               self.status.insert('end', p)
         elif "=" in message:
            parts = message.split("=")
            self.status.insert('end', parts[0], "blue")
            for p in parts[1:]:
               self.status.insert('end', "=")
               self.status.insert('end', p)
         elif len(message) > 3 and message.strip()[:-3] == "...":
            self.status.insert('end', message, "green")
         elif len(message) > 1 and message.strip()[-1] == "!":
            self.status.insert('end', message, "red")
         else:
            self.status.insert('end', message)
      self.status.update()

   def write(self, item, tag = None):
      try:
         self.printBuffer.append(item)
      except:
         pass

   def updateStatus(self):
      try:
         origLen = len(self.printBuffer)
         for i in range(origLen):
            line = self.printBuffer.pop(0)
            self.printStatus(line)
      except:
         pass
      
   def printStatus(self, item, tag = None):
      self.status.config(state='normal')
      self.parsePrint("%s" % item, tag)
      self.status.config(state='disabled')
      self.status.see('end')
      if self.maxBufferSize:
         text = self.status.get(1.0, 'end')
         lenText = len(text)
         if lenText > self.maxBufferSize:
            self.status.config(state='normal')
            self.status.delete(1.0, float(lenText - self.maxBufferSize))
            self.status.config(state='disabled')
            self.status.see('end')
   def flush(self):
      self.status.update()

   def makeMenu(self, bar, name, commands):
      """ Assumes self.menuButtons exists """
      menu = Tkinter.Menubutton(bar,text=name,underline=0)
      self.menuButtons[name] = menu
      menu.pack(side=Tkinter.LEFT,padx="2m")
      menu.filemenu = Tkinter.Menu(menu)
      for cmd in commands:
         if cmd:
            menu.filemenu.add_command(label=cmd[0],command=cmd[1])
         else:
            menu.filemenu.add_separator()
      menu['menu'] = menu.filemenu
      return menu

   def makeWatcher(self):
      if self.watcher:
         self.watcher.deiconify()
      else:
         self.watcher = TKwidgets.Watcher(self)

   def clearMessages(self):
      self.status.config(state='normal')
      self.status.delete(1.0, 'end')
      self.status.config(state='disabled')
      self.status.see('end')

   def saveConfig(self):
      retval = self.filesavedialog("Config", "*.ini", ".", "pyrobot.ini")
      if retval:
         self.setCurrentConfig(self.engine.config)
         self.engine.config.save(retval)
         print "Config '%s' saved!" % retval

   def fileloaddialog(self, filetype, skel, startdir = ''):
      from string import replace
      import pyrobot
      from os import getcwd, getenv, chdir
      retval = ""
      cwd = getcwd()
      if startdir == '':
         chdir(pyrobot.pyrobotdir() + "/plugins/" + filetype)
      else:
         chdir(startdir)
      d = TKwidgets.LoadFileDialog(self, "Load " + filetype, skel, \
                                   pyrobot.pyrobotdir() + "/plugins/" + filetype)
      try:
         retval = d.Show()
         if retval == 1:
            doc = d.GetFileName()
            d.DialogCleanup()
            retval = doc
         else:
            d.DialogCleanup()
      except:
         print "failed!"
         # double-click bug. What should we do?
         doc = d.GetFileName()
         d.DialogCleanup()
         retval = doc
      chdir(cwd)
      return retval

   def filesavedialog(self, filetype, skel, startdir = '', default=None):
      from string import replace
      import pyrobot
      from os import getcwd, getenv, chdir
      retval = ""
      cwd = getcwd()
      if startdir == '':
         chdir(pyrobot.pyrobotdir() + "/plugins/" + filetype)
      else:
         chdir(startdir)
      d = TKwidgets.SaveFileDialog(self, "Save " + filetype, skel, defaultFilename=default)
      try:
         if d.Show() == 1:
            doc = d.GetFileName()
            d.DialogCleanup()
            retval = doc
         else:
            d.DialogCleanup()
      except:
         # double-click bug. What should we do?
         doc = d.GetFileName()
         d.DialogCleanup()
         retval = doc
      chdir(cwd)
      return retval

   def disconnectRobot(self):
      if self.engine.robot != 0:
         self.engine.robot.disconnect()
      else:
         raise ValueError, "select robot first"         

   def connectRobot(self):
      if self.engine.robot != 0:
         self.engine.robot.connect()
      else:
         raise ValueError, "select robot first"

   def enableMotors(self):
      if self.engine.robot != 0:
         self.engine.robot.enableMotors()
      else:
         raise ValueError, "select robot first"         

   def disableMotors(self):
      if self.engine.robot != 0:
         self.engine.robot.disableMotors()
      else:
         raise ValueError, "select robot first"

if __name__ == '__main__':
   root = Tkinter.Tk()
   engine = Engine()
   gui = TKgui(engine)
   gui.inform("Ready...")
