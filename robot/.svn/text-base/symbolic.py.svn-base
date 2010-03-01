"""
The client robot connection programs for the PyrobotSimulator
non-symbolic robots.

(c) 2005, PyrobRobotics.org. Licenced under the GNU GPL.
"""

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision$"

import socket, threading, random, time
from pyrobot.robot import Robot
from pyrobot.robot.device import *
from pyrobot.simulators.pysim import colorMap, colorCode, colorUnCode
try:
	import cPickle as pickle
except:
	import pickle
try:
	from pyrobot.camera.fake import ManualFakeCamera
except:
	class ManualFakeCamera: pass
	# camera C++ code not built (or PIL not installed)
	print "ManualFakeCamera not loaded! Won't be able to use camera."

class PositionSimDevice(Device):
	def __init__(self, robot):
		Device.__init__(self, "position")
		self._dev = robot
		self.startDevice()
	def addWidgets(self, window):
		window.addData("x", ".x:", self._dev.x)
		window.addData("y", ".y:", self._dev.y)
		window.addData("thr", ".th (angle in radians):", self._dev.th)
		window.addData("th", ".thr (angle in degrees):", self._dev.thr)
		window.addData("stall", ".stall:", self._dev.stall)
	def updateWindow(self):
		if self.visible:
			self.window.updateWidget("x", self._dev.x)
			self.window.updateWidget("y",self._dev.y)
			self.window.updateWidget("thr", self._dev.th)
			self.window.updateWidget("th", self._dev.thr)
			self.window.updateWidget("stall",self._dev.stall)

class SimulationDevice(Device):
	def __init__(self, robot):
		Device.__init__(self, "simulation")
		self._dev = robot
		self.startDevice()
	def setPose(self, name, x = 0, y = 0, thr = 0):
		self._dev.move("a_%s_%f_%f_%f" % (name, x, y, thr))
		self._dev.localize(0,0,0)
		return "ok"
	def getPose(self, name):
		retval = self._dev.move("c_%s" % (name, ))
		return retval
	def eval(self, command):
		retval = self._dev.move("!%s" % (command,))
		return retval
	def addWidgets(self, window):
		window.addCommand("eval", "Evaluate exp!", "self.", self.onCommand)
	def onCommand(self, command):
		return self.eval(command)

class RangeSimDevice(Device):
	def __init__(self, name, index, robot, geometry, groups):
		Device.__init__(self, name)
		self._geometry = geometry
		self.groups = groups
		self.startDevice()
		self._dev = robot
		self.index = index
		self.maxvalueraw = geometry[2]
		self.rawunits = "M"
		self.units = "ROBOTS"
		self.radius = robot.radius
		self.count = len(self)
		self._noise = [0.05] * self.count
		
	def __len__(self):
		return len(self._geometry[0])

	def getSensorValue(self, pos):
		try:
			v = self._dev.__dict__["%s_%d" % (self.type, self.index)][pos]
		except:
			v = 0.0
		try:
			value = SensorValue(self, v, pos,
					    (self._geometry[0][pos][0], # x in meters
					     self._geometry[0][pos][1], # y
					     0.03,                    # z
					     self._geometry[0][pos][2], # th
					     self._geometry[1]),        # arc rads
					    noise=self._noise[pos]
					    )
		except:
			value = SensorValue(self, 0, 0,
					    (self._geometry[0][pos][0], # x in meters
					     self._geometry[0][pos][1], # y
					     0.03,                    # z
					     self._geometry[0][pos][2], # th
					     self._geometry[1]),        # arc rads
					    noise=self._noise[pos]
					    )
		return value

class LightSimDevice(RangeSimDevice):
	def __init__(self, *args, **kwargs):
		RangeSimDevice.__init__(self, *args, **kwargs)
		self.units = "SCALED"
	def _getRgb(self):
		retval = []
		for i in range(len(self)):
			retval.append( self.getSensorValue(i).rgb )
		return retval
	def getSensorValue(self, pos):
		retval = RangeSimDevice.getSensorValue(self, pos)
		if retval != None:
			retval.rgb = self._dev.move("f_%d_%d" % (self.index, pos)) # rgb
		return retval
	rgb = property(_getRgb)
	def addWidgets(self, window):
		for i in range(min(self.count, 24)):
			window.addData("%d.value" % i, "[%d].value:" % i, self[i].value)
			window.addData("%d.rgb" % i, "[%d].rgb:" % i, self[i].rgb)
	def updateWindow(self):
		if self.visible:
			for i in range(min(self.count, 24)):
				self.window.updateWidget("%d.value" % i, self[i].value)
				self.window.updateWidget("%d.rgb" % i, self[i].rgb)

class DirectionalLightSimDevice(RangeSimDevice):
	def __init__(self, *args, **kwargs):
		RangeSimDevice.__init__(self, *args, **kwargs)
		self.units = "SCALED"
	def getSensorValue(self, pos):
		retval = RangeSimDevice.getSensorValue(self, pos)
		return retval
	def addWidgets(self, window):
		for i in range(min(self.count, 24)):
			window.addData("%d.value" % i, "[%d].value:" % i, self[i].value)
	def updateWindow(self):
		if self.visible:
			for i in range(min(self.count, 24)):
				self.window.updateWidget("%d.value" % i, self[i].value)

class BulbSimDevice(Device):
	def __init__(self, robot):
		Device.__init__(self)
		self.type = "bulb"
		self._dev = robot
	def setBrightness(self, value):
		return self._dev.move("h_%f" % value)
	def addWidgets(self, window):
		b = 1.0
		window.addCommand("brightness", "Brightness!", str(b),
				  lambda b: self.setBrightness(float(b)))
		
class SpeechSimDevice(SpeechDevice, Device):
	def __init__(self, robot):
		Device.__init__(self)
		self.type = "speech"
		self._dev = robot
	def say(self, msg):
		msg = msg.replace("_", "~-")
		return self._dev.move("l_%s" % (msg,))

class PTZSimDevice(Device):
	def __init__(self, robot):
		Device.__init__(self)
		self.type = "ptz"
		self._dev = robot
	def setPose(self, p, t, z):
		return self._dev.move("j_%d_%s_%s_%s" % (0, p, t, z))
	def getPose(self):
		return self._dev.move("k_%d" % 0)
	def addWidgets(self, window):
		p, t, z = self._dev.move("k_%d" % 0)
		window.addCommand("pan", "Pan!", str(p), self.onPan)
		window.addCommand("tilt", "Tilt!", str(t), self.onTilt)
		window.addCommand("zoom", "Zoom!", str(z), self.onZoom)
	def onPan(self, command):
		return self.setPose(command, None, None)
	def onTilt(self, command):
		return self.setPose(None, command, None)
	def onZoom(self, command):
		return self.setPose(None, None, command)
	
class GripperSimDevice(GripperDevice):
	def __init__(self, robot):
		Device.__init__(self)
		self.type = "gripper"
		self._dev = robot
		self.data = [0, 0, 0, 0, 0]
		self.startDevice()
	def updateDevice(self):
		if self.active == 0: return
		newData = self._dev.move("gripper_%d" % 0)
		for i in range(len(newData)):
			self.data[i] = newData[i]
	def close(self):  return self._dev.move("z_gripper_0_close")
	def open(self):   return self._dev.move("z_gripper_0_open")
	def stop(self):   return self._dev.move("z_gripper_0_stop")
	def store(self):  return self._dev.move("z_gripper_0_store")
	def deploy(self): return self._dev.move("z_gripper_0_deploy")
	def halt(self):   return self.stop()
	# accessor values
	def getBreakBeam(self, which):
		if which == 'inner':
			return self.data[0]
		elif which == 'outer':
			return self.data[1]
		else:
			raise AttributeError, "invalid breakBeam: '%s'" % which
	def isClosed(self): return self.data[2]
	def isOpened(self): return self.data[3]
	def isMoving(self): return self.data[4]
	def isLiftMoving(self): return 0

class CameraSimDevice(ManualFakeCamera):
	def __init__(self, robot):
		self.lock = threading.Lock()
		self.robot = robot
		# fix: how to know what index?
		self.width, self.height = robot.move("g_%s_%d" % ("camera", 0))
		ManualFakeCamera.__init__(self, self.width, self.height, 3)
	def setActive(self, val):
		self.active = val
		return self.robot.move("i_%s_%d_active_%d" % ("camera", self.index, val))
	def update(self):
		if self.active == 0: return
		self.lock.acquire()
		self.data = [128 for i in range(self.height * self.width * 3)]
		self._data = self.robot.move("camera_%d" % 0)
		if len(self._data) == self.width:
			for w in range(self.width):
				(color, height) = self._data[w]
				if color == None or height == None: continue
				ccode = colorUnCode[color]
				for h in range(int(round(height))):
					for d in range(self.depth):
						self.data[(w + (self.height/2 - h) * self.width) * self.depth + d] = ccode[d]
						self.data[(w + (self.height/2 + h) * self.width) * self.depth + d] = ccode[d]
			#self.setRGBImage(self.data)
			self.vision.setImage(self.data)
			self.processAll()
		self.lock.release()

class Simbot(Robot):
	def __init__(self, simulator, port, connectionNum, startDevices=1):
		Robot.__init__(self)
		self.simulator = simulator
		self.connectionNum = connectionNum
		self.port = port
		self.init(startDevices)
	def init(self, startDevices=1):
		self.radius = self.getItem("radius")
		self.properties = self.getItem("properties")
		self.builtinDevices = self.getItem("builtinDevices")
		self.builtinDevices.append("simulation")
		self.builtinDevices.append("position")
		self.supportedFeatures = self.getItem("supportedFeatures")
		self.name = self.getItem("name")
		self.id   = self.connectionNum
		if startDevices:
			for dev in self.builtinDevices:
				d = self.startDevice(dev)
				if dev in ["sonar", "laser", "ir"]:
					self.range = d
	def move(self, message, other = None):
		if type(message) in [type(1), type(1.)] and type(other) in [type(1), type(1.)]:
			message = "m_%.2f_%.2f" % (message, other)
			other = None
		retval = None
		if other != None: return # rotate,translate command ignored
		if message == "quit" or message == "exit" or message == "end" or message == "disconnect":
			self.simulator.process(message, self.port, 0)
			return "ok"
		else:
			retval = self.simulator.process(message, self.port, 0)
		return retval
	def disconnect(self): pass
	def localize(self, x = 0, y = 0, th = 0):
		pass
	def update(self):
		for i in self.properties:
			self.__dict__[i] = self.getItem(i)
		self.updateDevices()
	def getItem(self, item):
		return self.move(item)
	def eat(self, amt):
		return self.move("e_%f" % (amt))
	def play(self, item):
		return self.move(item)
	def tell(self, item):
		return self.move(item)
	def ask(self, item):
		return self.move(item)
	def _moveDir(self, dir):
		if dir == 'L':
			self.move("left")
		elif dir == 'R':
			self.move("right")
		elif dir == 'F':
			self.move("forward")
		elif dir == 'B':
			self.move("back")
	def localize(self, x = 0, y = 0, thr = 0):
		return self.move("b_%f_%f_%f" % (x, y, thr))

	def startDeviceBuiltin(self, name, index = 0):
		if name == "simulation":
			return {"simulation": SimulationDevice(self)}
		elif name == "bulb":
			self.move("s_%s_%d" % (name, index))
			return {name: BulbSimDevice(self)}
		elif name == "ptz":
			self.move("s_%s_%d" % (name, index))
			return {name: PTZSimDevice(self)}
		elif name == "speech":
			self.move("s_%s_%d" % (name, index))
			return {name: SpeechSimDevice(self)}
		elif name == "camera":
			self.move("s_%s_%d" % (name, index))
			try:
				retval = {name: CameraSimDevice(self)}
			except:
				print "Camera device creation failed!"
				# probably no C++ ManualFakeCamera
				retval = None
			return retval
		elif name == "gripper":
			self.move("s_%s_%d" % (name, index))
			return {name: GripperSimDevice(self)}
		elif name == "position":
			return {name: PositionSimDevice(self)}
		elif name == "light":
			self.properties.append("%s_%d" % (name, index))
			self.move("s_%s_%d" % (name, index))
			geometry = self.move("g_%s_%d" % (name, index))
			groups = self.move("r_%s_%d" % (name, index))
			return {name: LightSimDevice(name, index, self, geometry, groups)}
		elif name == "directional":
			self.properties.append("%s_%d" % (name, index))
			self.move("s_%s_%d" % (name, index))
			geometry = self.move("g_%s_%d" % (name, index))
			groups = self.move("r_%s_%d" % (name, index))
			return {name: DirectionalLightSimDevice(name, index, self, geometry, groups)}
		else:
			self.properties.append("%s_%d" % (name, index))
			self.move("s_%s_%d" % (name, index))
			geometry = self.move("g_%s_%d" % (name, index))
			groups = self.move("r_%s_%d" % (name, index))
			dev = RangeSimDevice(name, index, self, geometry, groups)
			if name == "bumper":
				dev.units = "SCALED"
			return {name: dev}

	def translate(self, value):
		self.move("t_%f" % value)

	def rotate(self, value):
		self.move("o_%f" % value)

class TCPRobot(Simbot):
	"""
	A simple TCP-based socket robot for talking to PyrobotSimulator.
	"""
	BUFSIZE = 4096 # 2048 # 1024
	def __init__(self, host, port, startDevices=1):
		Robot.__init__(self)
		self.lock = threading.Lock()
		# Set the socket parameters
		self.host = host
		self.port = port
		self.addr = (host, port)
		self.type = "Pyrobot"
		# Create socket
		self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		try:
			self.socket.settimeout(1)
		except:
			print "WARN: entering deadlock zone; upgrade to Python 2.3 to avoid"
		done = 0
		while not done:
			try:
				self.socket.connect( self.addr )
				done = 1
			except:
				print "Waiting on PyrobotSimulator..."
				time.sleep(1)
		self.connectionNum = self.getItem("connectionNum:%d" % self.port)
		self.init(startDevices)

	def move(self, message, other = None):
		self.lock.acquire()
		if type(message) in [type(1), type(1.)] and type(other) in [type(1), type(1.)]:
			message = "m_%.2f_%.2f" % (message, other)
			other = None
		exp = None
		if self.socket == 0: return "not connected"
		if other != None: return # rotate,translate command ignored
		if message == "quit" or message == "exit" or message == "end" or message == "disconnect":
			self.socket.sendto(message, self.addr)
			self.socket.close()
			self.socket = 0
			self.lock.release()
			return "ok"
		else:
			self.socket.sendto(message, self.addr)
			try:
				retval, addr = self.socket.recvfrom(self.BUFSIZE)
			except:
				retval = ""
			retval = retval.strip()
			try:
				exp = pickle.loads( retval )
			except:
				exp = retval
		self.lock.release()
		return exp

	def disconnect(self):
		if self.connectionNum == 0: # the main one, let's close up!
			# Close socket
			self.getItem("quit")
		else:
			self.getItem("disconnect")


