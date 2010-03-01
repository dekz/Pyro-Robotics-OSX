"""
Engine class. This object binds together a robot, a simulator, and a brain.

This class will find, load, and start all of the parts.

Examples:

>>> e = Engine(robotfile="Test")
>>> e = Engine(robotfile="Player6665", simfile="StageSimulator",
               worldfile="everything.cfg", devices=['Test', 'BlobCamera'])
>>> e = Engine()
>>> r = Robot()
>>> e.setRobot(r)
"""

__author__ = "Douglas Blank <dblank@cs.brynmawr.edu>"
__version__= "$Revision$"

import time, sys, os
from pyrobot import pyrobotdir
import pyrobot.gui.console as console
import pyrobot.system as system
import pyrobot.system.share as share

class Engine:
   """Finds, loads, and creates the needed simulators, robots, devices, etc."""
   def __init__(self, robotfile = None, brainfile = None, simfile = None,
                pyroargs=[], config = {}, worldfile = None, devices = ['']):
      """Constructor for the Engine class."""
      self.robot = 0
      self.brain = 0
      self.gui = None
      if brainfile != None:
         self.brainfile = brainfile
      else:
         self.brainfile = ''
      if robotfile != None:
         self.robotfile = robotfile
      else:
         self.robotfile = ''
      if worldfile != None:
         self.worldfile = worldfile
      else:
         self.worldfile = ''
      if simfile != None:
         self.simfile = simfile
      else:
         self.simfile = ''
      self.args = pyroargs
      self.config = config
      if self.simfile:
         self.loadSimulator(self.simfile, self.worldfile)
         #time.sleep(2)
      if self.robotfile:
         self.loadRobot(self.robotfile)
         if devices != ['']:
            for dev in devices:
               self.robot.startDevice(dev)
      if self.brainfile:
         self.loadBrain(self.brainfile)
         #time.sleep(2)

   def reset(self):
      """Shuts down the brain, and reloads it."""
      self.pleaseStop()
      time.sleep(.1) # give it time to stop
      if self.brain is not 0:
         self.brain.pleaseQuit()
         time.sleep(.1) # give it time to stop
         #self.robot = system.loadINIT(self.robotfile, redo = 1)
         try:
            self.brain.window.destroy()
         except:
            pass
         try:
            self.brain.destroy()
         except:
            print "I was unable to properly destroy the brain"
         self.brain = system.loadINIT(self.brainfile, self, 1)

   def resetFirstAttempts(self):
      """Test method."""
      self.pleaseStop()
      if self.robotfile:
         file = self.robotfile[0:-3] # strip off .py
         #file = file.replace('/', '.')
         file = file.split('/')
         file = "pyrobot." + file[-3] + "." + file[-2] + "." + file[-1]
         print file
         exec( "reload(" + file + ")")
      if self.brainfile:
         file = self.brainfile[0:-3] # strip off .py
         #file = file.replace('/', '.')
         file = file.split('/')
         file = "pyrobot." + file[-3] + "." + file[-2] + "." + file[-1]
         print file
         exec( "reload(" + file + ")")
         #exec( "reload(" + file + ")")
         #reload(file)
         #reload(self.brainfile)

   def osRunPython(self, command):
      if os.name in ['nt', 'dos', 'os2']:
         os.system("start python " + command)
      else:
         os.system(command)

   def loadSimulator(self, file, worldfile):
      """Finds and loads the simulator."""
      import string
      options = string.split(file)
      guiflag = ''
      simulatorName = file.split('/')[-1]
      pyroPID = os.getpid()
      if simulatorName[-6:] == "Server":
         configDirName = simulatorName[:-6]
         if system.file_exists(worldfile):
            pass # leave it alone
         elif (pyrobotdir() != None and
               system.file_exists( pyrobotdir() + \
                                   '/plugins/configs/%s/%s' %
                                   (configDirName, worldfile))):
            worldfile = pyrobotdir() + \
                        '/plugins/configs/%s/%s' % (configDirName, worldfile)
         if self.config.get("pyrobot", "gui") .lower() == 'tty':
            guiflag = '-g'
         if system.file_exists(options[0]):
            os.system(file + (" %d " % pyroPID) + guiflag + " " + worldfile + " &")
         elif (pyrobotdir() != None and
               system.file_exists(pyrobotdir() + \
                                  '/plugins/simulators/' + options[0])):
            os.system(pyrobotdir() + '/plugins/simulators/' + file + \
                      (" %d " % pyroPID) + guiflag + " " + worldfile + " &")
         else:
            raise "Pyrobot Server file not found: '%s'" % file
      else:
         # Ends with "Simulator"
         simDirName = simulatorName[:-9]
         if system.file_exists(worldfile):
            pass # leave it alone
         elif (pyrobotdir() != None and
               system.file_exists( pyrobotdir() + \
                                   '/plugins/worlds/%s/%s' %
                                   (simDirName, worldfile))):
            worldfile = pyrobotdir() + \
                        '/plugins/worlds/%s/%s' % (simDirName, worldfile)
         if self.config.get("pyrobot", "gui") .lower() == 'tty':
            guiflag = '-g'
         if system.file_exists(options[0]):
            os.system(file + (" %d " % pyroPID)+ guiflag + " " + worldfile + " &")
         elif (pyrobotdir() != None and
               system.file_exists(pyrobotdir() + \
                                  '/plugins/simulators/' + options[0])):
            os.system(pyrobotdir() + '/plugins/simulators/' + file + \
                      (" %d " % pyroPID) + guiflag + " " + worldfile + " &")
         else:
            raise "Pyrobot Simulator file not found: '%s'" % file
      print "Loading.",
      sys.stdout.flush()
      wait = None
      if type(share.config) != type(0):
         wait = share.config.get("gui", "sim_start_delay")
      if wait == None:
         time.sleep(1) # default
      elif wait:
         time.sleep(float(wait)) 
      print ".",
      sys.stdout.flush()

   def loadRobot(self,file):
      """Finds and loads the robot."""
      if file[-3:] != '.py':
         file = file + '.py'
      if system.file_exists(file):
         self.robot = system.loadINIT(file)
         self.robotfile = file
      elif (pyrobotdir() != None and
            system.file_exists(pyrobotdir() + \
                               '/plugins/robots/' + file)): 
         self.robot = system.loadINIT(pyrobotdir() + \
                                      '/plugins/robots/' + file)
         self.robotfile = pyrobotdir() + '/plugins/robots/' + file
      else:
         raise "Pyrobot Robot file not found: '%s'" % file

   def setRobot(self,robot):
      """Sets the robot, after the creation of the engine."""
      self.robot = robot

   def setBrain(self,brain):
      """Sets the brain, after the creation of the engine."""
      self.brain = brain

   def loadBrain(self,file):
      """Finds and loads the brain file."""
      if self.robot is 0:
         raise 'No robot loaded when loading brain'
      if file[-3:] != '.py':
         file = file + '.py'
      if system.file_exists(file):
         try:
            self.brain.window.destroy()
         except:
            pass
         try:
            self.brain.destroy()
         except:
            pass
         self.brain = system.loadINIT(file, self)
         self.brainfile = file
      elif (pyrobotdir() != None and
            system.file_exists(pyrobotdir() + \
                               '/plugins/brains/' + file)): 
         try:
            self.brain.window.destroy()
         except:
            pass
         try:
            self.brain.destroy()
         except:
            pass
         self.brain = system.loadINIT(pyrobotdir() + \
                                      '/plugins/brains/' + file, self)
         self.brainfile = pyrobotdir() + '/plugins/brains/' + file
      else:
         raise "Pyrobot File not found: '%s'" % file

   def freeBrain(self):
      """Kills the brain."""
      if self.brain != 0:
         self.brain.pleaseQuit()
      
   def freeRobot(self):
      """Kills the robot."""
      self.freeBrain()
      if self.robot != 0:
         self.robot.disconnect()
         self.robot = 0

   def shutdown(self):
      """Shuts everything down."""
      self.freeRobot()
         
   def tryToConnect(self):
      """Tests to see if you have a brain and robot."""
      if (self.robot is 0) or (self.brain is 0):
         print "Need to have a robot and brain connected!"
         return #no go, not enough parts to make frankie go

   def pleaseRun(self, callback = 0):
      """Request to run the brain, followed by a callback."""
      if self.brain is not 0:
         self.brain.pleaseRun(callback)

   def pleaseStep(self):
      """Attempt to step the brain."""
      if self.brain is not 0:
         self.brain.pleaseStep()
         time.sleep(.5) # arbitrary time to allow it to do something
         self.robot.move(0, 0)

   def pleaseStop(self):
      """Attempt to stop the brain."""
      if self.brain is not 0:
         self.brain.pleaseStop()
      if self.robot is not 0:
         self.robot.stop()

   def _draw(self,options,renderer):
      """Method to draw the engine. Not used, currently."""
      pass # overload, if you want to draw it
      
   def destroyBrain(self):
      """Method to destroy the brain, if one."""
      if self.brain is not 0:
         try:
            self.brain.destroy()
         except:
            print "I was unable to properly destroy the brain"

   def getGUI(self):
      """Returns the gui object."""
      return self.gui
