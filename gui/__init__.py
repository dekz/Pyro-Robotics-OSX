""" Base GUI Class for Python Robotics. This is used for the -g tty GUI. """

import os
import sys
import signal
import time
import string
from posix import popen
from pyrobot.system.version import version as version
from pyrobot.system import help, usage, about, file_exists
from pyrobot import pyrobotdir

class TextWatcher:
   def __init__(self):
      self.list = []
   def watch(self, exp):
      self.list.append(exp)
   def unwatch(self, exp):
      self.list.remove(exp)
   def update(self, locals = None):
      if len(self.list) == 0: return
      print ("=== Pyrobot Expression Watcher: " + ("=" * 65))[:65]
      if locals == None:
         locals = globals()
      for exp in self.list:
         try:
            value = str(eval(exp, locals))
         except:
            value = "<Undefined>"
         print "   ", exp, "=>", value
      print "=" * 65

class BrainStem:
   """
   A stub used in the Pyrobot command evaluator to define "self"
   so that self.robot will work. Without this
   self is not defined. Only works when you have a robot, but
   no brain yet.
   """
   def __init__(self, robot = 0):
      self.robot = robot
   # wrappers here to talk to default robot:
   def move(self, *args):
      """Short-cut to call the robot's move method."""
      return self.robot.move(*args)
   def translate(self, *args):
      """Short-cut to call the robot's translate method."""
      return self.robot.translate(*args)
   def rotate(self, *args):
      """Short-cut to call the robot's rotate method."""
      return self.robot.rotate(*args)
   def stop(self):
      """Short-cut to call the robot's stop method."""
      return self.robot.stop()
   def startDevice(self, *args, **keywords):
      """Short-cut to call the robot's startDevice method."""
      return self.robot.startDevice(*args, **keywords)
   def removeDevice(self, *args, **keywords):
      """Short-cut to call the robot's removeDevice method."""
      return self.robot.removeDevice(*args, **keywords)
   def update(self):
      """Short-cut to call the robot's update method."""
      return self.robot.update()
   def motors(self, *args):
      """Short-cut to call the robot's motors method."""
      return self.robot.motors(*args)
   def getDevice(self, *args):
      """Short-cut to call the robot's getDevice method."""
      return self.robot.getDevice(*args)
   def hasA(self, *args):
      """Short-cut to call the robot's hasA method."""
      return self.robot.hasA(*args)
   def requires(self, *args):
      """Short-cut to call the robot's requires method."""
      return self.robot.requires(*args)
   
class gui:
   """
   This is the base class for a gui.
   """
   
   def __init__(self, name = 'abstract gui', options = {}, engine = 0):
      """
      Child classes should do initialization pertaining to the creation
      of the GUI in the constructor.
      """
      self.watcher = None
      self.triedToStop = 0
      self.alreadyCleanedUp = 0
      self.engine = engine
      self.engine.gui = self
      self.prevsighandler = signal.signal(signal.SIGINT, self.INThandler)
      self.history = []
      self.history_pointer = 0
      self.MAXHISTORY = 1000
      self.environment = {}
      self.environment["gui"] = self
      self._populateEnv()
      self.lastDir = {}
      if file_exists(os.getenv('HOME') + "/.pyrobothist"):
         fp = open(os.getenv('HOME') + "/.pyrobothist", "r")
         self.history = map( string.strip, fp.readlines())
         fp.close()
         self.history_pointer = len(self.history)

   def updateDeviceList(self, clear = 0, select = -1):
      pass
   
   def listCommandHistory(self, search = None):
      cnt = 1
      if search:
         print "Command history containing '%s':" % search
      else:
         print "Command history:"
      for line in self.history:
         if search:
            if search in line:
               print "%4d: %s" % (cnt, line)
         else:
            print "%4d: %s" % (cnt, line)
         cnt += 1

   def addCommandHistory(self, command):
      if len(self.history) > 0:
         if command != self.history[ len(self.history) - 1]:
            self.history.append(command)
      else:
            self.history.append(command)
      self.history_pointer = len(self.history)

   def run(self, command = []):
      """
      Child classes should do the beef of what they do right here.
      """
      done = 0
      print "========================================================="
      print "Pyrobot, Python Robotics, (c) 2005, D.S. Blank"
      print "http://PyroRobotics.org"
      print "Version " + version()
      print "========================================================="
      while done is not 1:
         print "pyrobot> ", 
         if len(command) > 0:
            print command[0],
            retval = command[0].strip()
            command = command[1:]
         else:
            retval = sys.stdin.readline()
         print ""
         if retval == '':
            done = 1
            continue
         done = self.processCommand(retval)

   def makeWatcher(self):
      """ Text-based watcher """
      self.watcher = TextWatcher()
      
   def watch(self, exp):
      if self.watcher == None:
         self.makeWatcher()
      self.watcher.watch(exp)

   def setCurrentConfig(self, config):
      cwd = os.getcwd()
      if self.engine.simfile:
         file = self.engine.simfile
         if pyrobotdir() + "/plugins/" in file or \
                cwd in file:
            file = file.split(os.path.sep)[-1]
         config.put("simulator", "file", file)
      if self.engine.worldfile:
         file = self.engine.worldfile
         if pyrobotdir() + "/plugins/" in file or \
                cwd in file:
            file = file.split(os.path.sep)[-1]
         config.put("world", "file", file)
      if self.engine.robotfile:
         file = self.engine.robotfile
         if pyrobotdir() + "/plugins/" in file or \
                cwd in file:
            file = file.split(os.path.sep)[-1]
         config.put("robot", "file", file)
      if self.engine.brainfile:
         file = self.engine.brainfile
         if pyrobotdir() + "/plugins/" in file or \
                cwd in file:
            file = file.split(os.path.sep)[-1]
         config.put("brain", "file", file)
      print "Ok"

   def printCommandLine(self):
      commandLine = sys.argv[0] + " "
      if self.engine.simfile:
         file = self.engine.simfile
         if pyrobotdir() + "/plugins/" in file:
            file = file.split(os.path.sep)[-1]
         commandLine += "-s %s " % file
      if self.engine.worldfile:
         file = self.engine.worldfile
         if pyrobotdir() + "/plugins/" in file:
            file = file.split(os.path.sep)[-1]
         commandLine += "-w %s " % file
      if self.engine.robotfile:
         file = self.engine.robotfile
         if pyrobotdir() + "/plugins/" in file:
            file = file.split(os.path.sep)[-1]
         commandLine += "-r %s " % file
      if self.engine.brainfile:
         file = self.engine.brainfile
         if pyrobotdir() + "/plugins/" in file:
            file = file.split(os.path.sep)[-1]
         commandLine += "-b %s " % file
      print commandLine

   def _populateEnv(self):
      if self.engine.brain:
         self.environment["self"] = self.engine.brain
      else:
         self.environment["self"] = BrainStem(self.engine.robot)
      self.environment["engine"] = self.engine
      self.environment["robot"] = self.engine.robot
      self.environment["brain"] = self.engine.brain

   def processCommand(self, retval):
      retval = retval.replace("\n", "")
      retval = retval.replace("\r", "")
      retval = retval.strip()
      if retval == "":
         return
      self.addCommandHistory(retval)
      # Macro-style substitutions here:
      if len(retval)>= 1 and retval[0] == ".":
         if len(retval) >= 2:
            if retval[1].isalpha():
               retval = "self" + retval
         else:
            retval = "self" + retval
      # Now process the command, case-like:
      if retval == "run":
         self.inform("Running in thread...")
         self.engine.pleaseRun() # pass in callback, or not
         # self.engine.pleaseRun(self.redraw) # pass in callback
      elif retval == "runtillquit":
         self.done = 0
         self.engine.pleaseRun()
         while not self.done:
            pass
         return 1
      elif retval == "step":
         self.stepEngine()
      elif retval == "info":
         print "-------------------------------------------------------------"
         print "Brain file:\t%s" % self.engine.brainfile
         print "Brain:\t\t%s" % self.engine.brain
         print "Robot:\t\t%s" % self.engine.robot
         print "World:\t\t%s" % self.engine.worldfile
         print "-------------------------------------------------------------"
      elif retval == "help":
         help()
      elif retval == "usage":
         usage()
      elif retval == "update":
         if self.engine.robot != 0:
            self.engine.robot.update()
            self.inform("Done!")
         else:
            self.inform("Define a robot first!")
      elif len(retval) >= 2 and retval[0:2] == "$$":
         os.system(retval[2:])
      elif len(retval) >= 1 and retval[0] == "$":
         pipe = popen(retval[1:])
         for line in pipe.readlines():
            print line.strip()
         pipe.close()
      elif len(retval) >= 1 and retval[0] == "!":
         if retval == "!":
            self.listCommandHistory()
         elif retval == "!!":
            self.processCommand(self.history[-2]) # -1 is !!
         elif "-" in retval:
            start, stop = retval[1:].split("-")
            start, stop = start.strip(), stop.strip()
            if start == "": # neg number
               self.processCommand(self.history[-int(stop) - 1])
            else:  
               for i in range(int(start), int(stop) + 1):
                  self.processCommand(self.history[i - 1])
         else:
            val = retval[1:]
            if val.strip().isdigit():
               self.processCommand(self.history[int(val) - 1])
            else:
               self.listCommandHistory(val)               
      elif retval == "about":
         about()
      elif retval == "reload":
         self.engine.reset()
      elif retval == "load robot":
         self.loadRobot()
      elif retval == "load brain":
         self.loadBrain()
      elif retval == "load simulator" or retval == "load server":
         print "Enter simulator or server (e.g., StageSimulator, PlayerServer)"
         self.loadSim()
      elif retval == "stop":
         self.engine.pleaseStop()
         self.inform("Stopped!")
      elif retval == "quit" or retval == "exit" or retval == "bye":
         self.done = 1
         return 1
      elif retval == "edit":
         if self.engine.brainfile != '':
            if os.getenv("EDITOR"): 
               editor = os.getenv("EDITOR")
            else:
               editor = "emacs"
            os.system("%s %s" % (editor, self.engine.brainfile))
            self.inform("Reloading...")
            self.engine.reset()
         else:
            self.inform("Need to load a brain first!")
      elif retval[:8] == "unwatch ":
         self.watcher.unwatch(retval[7:].strip())
      elif retval[:5] == "view ":
         self.objectBrowser(retval[5:])
      elif retval[:6] == "watch ":
         self._populateEnv()
         self.watch(retval[5:].strip())
      elif retval[:7] == "browse ":
         self.objectBrowser(retval[7:].strip())
      else:
         # elif len(retval) > 0 and retval[0] == "!":
         exp1 = """_retval = """ + string.strip(retval)
         _retval = "error"
         exp2 = string.strip(retval)
         # perhaps could do these once, but could change:
         self._populateEnv()
         print ">>> ",
         print retval
         try:
            _retval = eval(exp2, self.environment)
         except:
            try:
               exec exp1 in self.environment
            except:
               try:
                  exec exp2 in self.environment
               except:
                  print self.formatExceptionInfo()
               else:
                  print "Ok"
            else:
               print "Ok"
         else:
            if _retval != None:
               print _retval
      self.updateDeviceList()
      return 0

   def formatExceptionInfo(self, maxTBlevel=10):
      import sys, traceback
      cla, exc, trbk = sys.exc_info()
      print "ERROR:", cla, exc
      traceback.print_exc()
      if type(exc) == type(""):
         excName = exc   # one our fake, string exceptions
      elif type(cla) == type(""):
         excName = cla
      else:
         if "__dict__" in dir(cla) and  cla.__dict__.get("__name__") != None:
            excName = cla.__name__  # a real exception object
         else:
            excName = cla   # one our fake, string exceptions
      if "__dict__" in dir(exc) and "args" in exc.__dict__:
         excArgs = exc.__dict__["args"]
      else:
         excArgs = ("",)
      excTb = traceback.format_tb(trbk, maxTBlevel)
      # FIX: This is only the errors back four lines!
      # how do you get them before that?
      #for err in excTb:
      #   print err
      return "%s: %s %s" % (excName, excArgs[0], "in command line")

   def redraw(self):
      # FIX: this is way awkward:
      f = GenericStream()
      r = StreamRenderer(f)
      self.draw({}, r) # get data from robot, other things
      f.close()
      s = StreamTranslator(f, TTYRenderer())
      s.process()
      f.close()

   def _draw(self,options,renderer):
      """
      If the gui need draw something itself it should go here.
      """
      #render world
      #renderer.xformPush()
      renderer.color((1, 1, 1))
      renderer.rectangle((-10, -10, 0), (10, -10, 0), (10, 10, 0))
      #renderer.xformPop()
      #print "Redraw gui..."

   def makeMenu(self,name,commands):
      """ Could bind a key right here ^1, ^2, ^3..."""
      pass

   def fileloaddialog(self, type, skel, olddir = ''):
      """ Read a line from user """
      print "\n%s Filename: " % type,
      retval =  sys.stdin.readline()
      retval = retval.replace("\n", "")
      retval = retval.replace("\r", "")
      if file_exists(retval):
         return retval
      elif file_exists(olddir +"/" + retval):
         return olddir +"/" + retval
      else:
         # hope this is in the path!
         return retval

   def cleanup(self):
      if not self.alreadyCleanedUp:
         self.alreadyCleanedUp = 1
         self.done = 1
         try:
            sys.stdout = self.sysstdout
            sys.stderr = self.sysstderr
         except:
            pass
         if self.engine != 0:
            self.engine.shutdown()
         try:
            fp = open(os.getenv('HOME') + "/.pyrobothist", "w")
            line_count = min( len(self.history), self.MAXHISTORY)
            for i in range( line_count ):
               fp.write( self.history[ len(self.history) - line_count + i] +"\n" )
            fp.close()
         except:
            pass
         try:
             sys.stdout.flush()
         except IOError:
             pass
         sys.exit(1)
      else:
         os._exit(1)

   def stepEngine(self):
      self.engine.pleaseStep()
      self.inform("Step done!")

   def runEngine(self):
      self.engine.pleaseRun()
      self.inform("Running...")

   def stopEngine(self): # stop!
      self.engine.pleaseStop()
      self.inform("Stopped!")

   def stopTranslate(self):
      self.engine.robot._moveDir('ST')

   def stopRotate(self):
      self.engine.robot._moveDir('SR')

   def stepForward(self):
      self.engine.robot._moveDir('F')

   def stepBack(self):
      self.engine.robot._moveDir('B')

   def stepLeft(self):
      self.engine.robot._moveDir('L')

   def stepRight(self):
      self.engine.robot._moveDir('R')

   def resetEngine(self):
      self.engine.reset()
      
   def loadBrain(self):
      f = self.fileloaddialog("brains","*.py", self.lastDir.get("brain", ''))
      if f != '' and f != 0:
         self.lastDir["brain"] = string.join(f.split('/')[:-1],'/')
         self.freeBrain()
         self.engine.loadBrain(f)
         self._populateEnv()

   def loadDevice(self):
      f = self.fileloaddialog("devices","*.py",self.lastDir.get("devices",''))
      if f != '' and f != 0:
         self.lastDir["devices"] = string.join(f.split('/')[:-1],'/')
         if self.engine != 0 and self.engine.robot != 0:
            self.engine.robot.startDevices(f)

   def freeBrain(self):
      self.engine.pleaseStop()
      self.engine.destroyBrain()
      self.engine.freeBrain()
      self.engine.brainfile = ''

   def loadSim(self, worldfile = ''):
      pyropath = pyrobotdir()
      f = self.fileloaddialog("simulators","*",self.lastDir.get("sim", ''))
      if f != '' and f != 0:
         self.lastDir["sim"] = string.join(f.split('/')[:-1],'/')
         if worldfile == '':
            simulatorName = f.split('/')[-1]
            if simulatorName[-6:] == "Server":
               configDirName = simulatorName[:-6]
               worldfile = self.fileloaddialog("configs","*.cfg",
                                               self.lastDir.get("%s-config" % simulatorName,
                                                                "%s/plugins/configs/%s/" %
                                                                (pyropath, configDirName)))
               if worldfile == "":
                  return
               self.lastDir["%s-config" % simulatorName] = string.join(worldfile.split('/')[:-1],'/')
            else:
               # ends with "Simulator"
               simDirName = simulatorName[:-9]
               if simulatorName == "PyrobotSimulator":
                  worldfile = self.fileloaddialog("worlds","*.py",
                                                  self.lastDir.get("%s-world" % simulatorName,
                                                                   "%s/plugins/worlds/%s/" %
                                                                   (pyropath, simDirName)))
               elif simulatorName == "StageSimulator":
                  worldfile = self.fileloaddialog("worlds","*.cfg",
                                                  self.lastDir.get("%s-world" % simulatorName,
                                                                   "%s/plugins/worlds/%s/" %
                                                                   (pyropath, simDirName)))
               else:
                  worldfile = self.fileloaddialog("worlds","*.world",
                                                  self.lastDir.get("%s-world" % simulatorName,
                                                                   "%s/plugins/worlds/%s/" %
                                                                   (pyropath, simDirName)))
               if worldfile == "" or worldfile == 0:
                  return
               self.lastDir["%s-world" % simulatorName] = string.join(worldfile.split('/')[:-1],'/')
         else:
            simulatorName = worldfile
            self.lastDir["%s-world" % simulatorName] = string.join(worldfile.split('/')[:-1],'/')
         self.engine.worldfile = worldfile
         self.engine.simfile = f
         pyroPID = os.getpid()
         if os.name in ['nt', 'dos', 'os2'] :
            # FIXME: this assumes program to run is a python program; how will we know?
            # could leave out "python" and windows will ask
            print "start python %s %d %s" % (f, pyroPID, worldfile)
            os.system("start python \"%s\" \"%d\" \"%s\"" % (f, pyroPID, worldfile))
         elif os.name in ['posix']:
            os.system(f + (" %d " % pyroPID) + worldfile + " &")
         else:
            raise AttributeError, "your OS (%s) is not supported" % os.name
         
   def loadRobot(self):
      f = self.fileloaddialog("robots","*.py", self.lastDir.get("robot", ''))
      if f != '' and f != 0:
         self.lastDir["robot"] = string.join(f.split('/')[:-1],'/')
         self.freeBrain()
         self.freeRobot()
         self.engine.loadRobot(f)
         #if self.engine.robot:
         #   for device in self.engine.robot.builtinDevices:
         #      self.menuButtons["Built-in Devices"].add_command(label=device,command=lambda:self.startDevice(device))

   def freeRobot(self):
      self.freeBrain()
      self.engine.robotfile = ''
      self.engine.freeRobot()

   def INThandler(self, signum, frame):
      print "STOP ----------------------------------------------------"
      self.triedToStop += 1
      if self.triedToStop > 1:
         os.system("killall -9 pyrobot")
      self.engine.pleaseStop()
      self.cleanup()

   def inform(self, message):
      print message
      
   def filesavedialog(self, type, skel, startdir = ''):
      """ Read a line from user """
      print "\nFilename: ",
      retval =  sys.stdin.readline()
      retval = retval.replace("\n", "")
      retval = retval.replace("\r", "")
      return retval

   def newBrain(self):
      """
      Tk gui overrides this method.
      """
      pass
