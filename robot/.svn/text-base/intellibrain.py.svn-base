"""
Defines IntelliBrainBot, a subclass of robot.
Includes code modified from khepera.py

(c) 2006, SUNY Potsdam. Licenced under the GNU GPL.
"""

__author__ = "James Snow <snow91@potsdam.edu>"
__version__ = "$Revision$"

from pyrobot.system.share import config
from pyrobot.robot import *
from pyrobot.robot.device import *
from pyrobot.system.serial import *
import pyrobot.gui.console as console
import string, array, math 
import threading
import time
from pyrobot.geometry import PIOVER180

class IRSensor(Device):
    def __init__(self, dev, type = "ir"):
        Device.__init__(self, type)
        self._dev = dev
        self.arc = 15.0 * PIOVER180 # radians
        self.units    = "ROBOTS" # current report units
        self.radius = dev.radius # universally in METERS
        self.rawunits = "CM"
        self.maxvalueraw = 80.0 # in rawunits
        self.count = 2
        self.groups = {'all': range(2),
                       'left-front' : (1, ), 
		       'front-left' : (1, ),
                       'right-front' : (0, ),
		       'front-right' : (0, ),
                       'front' : (0, 1),
                      } 
        self.startDevice()    

    def __len__(self):
        return self.count
	
    def getSensorValue(self, pos):
        """
        Send sensor device, dist, pos, geometry (ox, oy, oz, thr, arc).
        """
        return SensorValue(self, self._getVal(pos), pos,
                           (self._ox(pos) / 1000.0, # meters
                            self._oy(pos) / 1000.0, # meters
                            20.0 / 1000.0, # meters
                            self._thr(pos),
                            self.arc),)
    def _ox(self, pos):
        # in mm
        if pos == 0:
            retval = 20.0
        elif pos == 1:
            retval = 40.0
        elif pos == 2:
            retval = 60.0
        elif pos == 3:
            retval = 60.0 
        elif pos == 4:
            retval = 40.0
        elif pos == 5:
            retval = 20.0
        elif pos == 6:
            retval = -60.0
        elif pos == 7:
            retval = -60.0
        return retval

    def _oy(self, pos):
        # in mm
        if pos == 0:
            retval = 60.0
        elif pos == 1:
            retval = 40.0
        elif pos == 2:
            retval = 20.0
        elif pos == 3:
            retval = -20.0 
        elif pos == 4:
            retval = -40.0
        elif pos == 5:
            retval = -60.0
        elif pos == 6:
            retval = -20.0
        elif pos == 7:
            retval = 20.0
        return retval

    def _thr(self, pos):
        return self._th(pos) * PIOVER180

    def _th(self, pos):
        if pos == 0:
            return 90.0
        elif pos == 1:
            return 45.0
        elif pos == 2:
            return 0.0
        elif pos == 3:
            return 0.0 
        elif pos == 4:
            return -45.0
        elif pos == 5:
            return -90.0
        elif pos == 6:
            return 180.0
        elif pos == 7:
            return 180.0
	    
    def _getVal(self, pos):
        try:
            return self._dev.rawData['ir'][pos]
        except:
            return 0

class LightSensor(IRSensor):
    def __init__(self, dev):
        IRSensor.__init__(self, dev, "light")
        # now, just overwrite those differences
        self.units = "SCALED"
        self.rawunits = "RAW"
        self.maxvalueraw = 255

    def _getVal(self, pos):
        try:
            data = int(self.maxvalueraw - self._dev.rawData['light'][pos])
        except:
            data = 0
        return data

class IntelliBrainBot(Robot):
    def __init__(self,
                 port = None,
                 simulator = 0,
                 rate = None,
                 subtype = "IntelliBrainBot"):
        # simulator = 0 makes it real
        Robot.__init__(self) # robot constructor
        self.lock = threading.Lock()
        self.buffer = ''
        self.debug = 0
        if simulator == 1:
            raise AttributeError, "simulator no longer supported"
        else:
            if subtype == "IntelliBrainBot":
                if port == None:
                    try:
                        port = config.get('IntelliBrainBot', 'port')
                    except:
                        pass
                if port == None:
                    port = "/dev/ttyUSB0"
                if rate == None:
                    rate = 38400
            print "IntelliBrain opening port", port, "..."
            self.sc = Serial(port, baudrate=rate) #, xonxoff=0, rtscts=0)
            self.sc.setTimeout(0)
            self.sc.readlines() # to clear out the line
	self.lastTranslate = 0
   	self.lastRotate = 0
	self.currSpeed = [0, 0]
        
	# This could go as high as 127, but I am keeping it small
        # to be on the same scale as larger robots. -DSB
	self.translateFactor = 9
        self.dataTypes = {'n' : 'ir',
                          'o' : 'light'
                          }
        self.rawData = {}
	self.rawData['position'] = [0] * 3
        self.rawData['ir'] = [0] * 2
        self.rawData['light'] = [0] * 2
        self.subtype = subtype
        self.radius = .06 #meters
        self.builtinDevices = ['ir', 'light']
        self._newline = "\r"

        self.startDevice("ir")
        self.range = self.ir[0]
        self.startDevice("light")

        self.rawData["position"] = 0, 0
        # self.sendMsg('B') # version
        # self.sendMsg('j') # extensionDevices

        self.x = 0.0
        self.y = 0.0
        self.thr = 0.0
        self.th = 0.0
        self.w0 = self.rawData['position'][0]
        self.w1 = self.rawData['position'][1]
        self.type = "IntelliBrain"
        self.port = port
        self.simulated = simulator
        self.supportedFeatures.append( "continuous-movement" )
        self.supportedFeatures.append( "range-sensor" )
	self.supportedFeatures.append( "light-sensor" )
	self.supportedFeatures.append( "mono-sound" )
	self.supportedFeatures.append( "visual-feedback" )
	self.update() 
        print "Done loading IntelliBrain."

    def startDeviceBuiltin(self, item):
        if item == "ir":
            return {"ir": IRSensor(self)}
        elif item == "light":
            return {"light": LightSensor(self)}
        else:
            raise AttributeError, "IntelliBrainBot does not support device '%s'" % item
	    
    def connect(self):
    	self.start()
	
    def disconnect(self):
        self.stop()

    def sendMsg(self, msg):
        self.lock.acquire()
        self.sc.writeline(msg, self._newline)
	time.sleep(0.05)
        self.lock.release()

    def readData(self):
        if self.sc.inWaiting() == 0: return
        retval = self.sc.readline() # 1 = block till we get something
        #print "DEBUG:", retval
        if len(retval) > 0:
            if retval[-1] != '\n' and retval[-1] != '\r':
                self.buffer += retval
            else:
                self.buffer += retval.strip()
                if len(self.buffer) > 0:
                    rawdata = string.split(self.buffer, ",")
                    self.buffer = ''
                    if self.debug: print "DEBUG: read:", rawdata
                    dtype, data = rawdata[0], rawdata[1:]
                    if dtype == 't':
                        if len(data) < 2:
                            self.buffer = ''
                            if self.debug: print "Turret packet error:", rawdata
                            return
                        else:
                            dtype += data[0] + data[1]
                            data = data[2:]
                    key = self.dataTypes.get(dtype, None)
                    if key != None:
                        try:
                            self.rawData[key] = map(int,data)
                        except:
                            #pass
                            if self.debug: print "Packet error:", rawdata

    def update(self):
        Robot.update(self)
        if  self.subtype == "IntelliBrainBot":
            self.sendMsg('N') #, 'ir')     # proximity
            self.sendMsg('O') #, 'light')  # ambient light
        while self.sc.inWaiting(): self.readData()
	
    def beep(dev):
    	dev.sendMsg('H,1')
    
    def led(dev, value):
    	if value == 1:
		dev.sendMsg('L,0,1')
	elif value == 2:
		dev.sendMsg('L,1,0')
	elif value == 3:
		dev.sendMsg('L,1,1')
	else:
		dev.sendMsg('L,0,0')
    
    def stop(dev):
    	dev.sendMsg('D,0,0')
	dev.sendMsg('L,0,0')
	
    def move(self, trans, rotate):
	self.lastTranslate = trans
	self.lastRotate = rotate
	self.adjustSpeed()

    def adjustSpeed(dev):
    	left  = dev.lastTranslate - dev.lastRotate
        right = dev.lastTranslate + dev.lastRotate
        maxL = abs(left)
	maxR = abs(right)

	if maxL > maxR:
		max = maxL
	else:
		max = maxR
	
	if max > 1:
		left = left/max
		right = right/max

	left = int(left * dev.translateFactor)
	right = int(right * dev.translateFactor)

	dev.sendMsg('D,%i,%i' % (left, right))

    def translate(dev, value):
	dev.lastTranslate = value
	dev.adjustSpeed()

    def rotate(dev, value):
    	dev.lastRotate = value
	dev.adjustSpeed()

if __name__ == '__main__':
    x = IntelliBrainBot()
    x.update()
