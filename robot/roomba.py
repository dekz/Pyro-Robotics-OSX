"""
Defines Roomba, a subclass of robot.

Includes code modified from IntelliBrain.py & Khepera.py
Also Includes code from the ERDOS project.

For more info. about ERDOS contact Zach Dodds(dodd@cs.hmc.edu) 
or visit http://www.cs.hmc.edu/~dodds/erdos/

(c) 2006, SUNY Potsdam. Licenced under the GNU GPL.
"""

__author__ = "James Snow <snow91@potsdam.edu>"
__version__ = "$Revision: 2495 $"

from pyrobot.system.share import config
from pyrobot.robot import *
from pyrobot.robot.device import *
from pyrobot.system.serial import *
import pyrobot.gui.console as console
import string, array, math , struct
import threading
import time

def freq2num(f):
    # 32.70 is arbitrarily zero octave
    # 32.70 = exp(VAL / 1.442695)
    # VAL = 5.03121
    octave = math.log(f) * 1.442695 - 5.03121 + 2 # make it 2 octaves higher
    octaveInt = int(round(octave, 2)) # get base octave
    if octaveInt >= octave:
        return (octaveInt * 12)
    else:
        # use computed octave differance as a percentage of octave:
        return (octaveInt * 12) + int((octave - octaveInt) * 12.0)

def bitOfByte( bit, byte ):
    """ returns a 0 or 1: the value of the 'bit' of 'byte' """
    if bit < 0 or bit > 7:
        print 'Your bit of', bit, 'is out of range (0-7)'
        print 'returning 0'
        return 0
    return ((byte >> bit) & 0x01)

def twosComplementInt1byte( byte ):
    """ returns an int of the same value of the input
        int (a byte), but interpreted in two's
        complement
        the output range should be -128 to 127
    """
    # take everything except the top bit
    topbit = bitOfByte( 7, byte )
    lowerbits = byte & 127
    if topbit == 1:
        return lowerbits - (1 << 7)
    else:
        return lowerbits

def twosComplementInt2bytes( highByte, lowByte ):
    """ returns an int which has the same value
        as the twosComplement value stored in
        the two bytes passed in

        the output range should be -32768 to 32767

        chars or ints can be input, both will be
        truncated to 8 bits
    """
    # take everything except the top bit
    topbit = bitOfByte( 7, highByte )
    lowerbits = highByte & 127
    unsignedInt = lowerbits << 8 | (lowByte & 0xFF)
    if topbit == 1:
        # with sufficient thought, I've convinced
        # myself of this... we'll see, I suppose.
        return unsignedInt - (1 << 15)
    else:
        return unsignedInt


def toTwosComplement2Bytes( value ):
    """ returns two bytes (ints) in high, low order
        whose bits form the input value when interpreted in
        two's complement
    """
    # if positive or zero, it's OK
    if value >= 0:
        eqBitVal = value
    # if it's negative, I think it is this
    else:
        eqBitVal = (1<<16) + value

    return ( (eqBitVal >> 8) & 0xFF, eqBitVal & 0xFF )

class RoombaIRDevice(Device):
    def __init__(self, robot):
        self._dev = robot
        Device.__init__(self, "ir")
        self.units    = "RAW"
        # What are the raw units?
        # Anything that you pass to rawToUnits should be in these units
        self.rawunits = "RAW"
        self.maxvalueraw = 255 # meters
        # These are fixed in meters: DO NOT CONVERT ----------------
        self.radius = self._dev.radius # meters
        # ----------------------------------------------------------
        # All of the rest of the measures are relative to units, given in rawunits:
        self.count = len(self)
        self.groups = {'wallSensor': 0,
                       'leftCliff': 1,
                       'frontLeftCliff': 2,
                       'frontRightCliff': 3,
                       'rightCliff': 4,
                       'virtualWall': 5,
                       'commIR': 6,
                       'all': range(7)}
        self.startDevice()
    def __len__(self):
        return 7
    def getSensorValue(self, pos):
        name = ['wallSensor', 'leftCliff', 'frontLeftCliff',
                'frontRightCliff', 'rightCliff', 'virtualWall',
                'commIR']
        return SensorValue(self,
                           self._dev.sensorData[name[pos]],
                           pos,
                           (0,  # x in meters
                            0,  # y
                            0,  # z
                            0,  # rads
                            0), # arc rads
                           noise=0)

class RoombaBumperDevice(Device):
    def __init__(self, robot):
        self._dev = robot
        Device.__init__(self, "bumper")
        self.units    = "RAW"
        # What are the raw units?
        # Anything that you pass to rawToUnits should be in these units
        self.rawunits = "RAW"
        self.maxvalueraw = 1.0 # meters
        # These are fixed in meters: DO NOT CONVERT ----------------
        self.radius = self._dev.radius # meters
        # ----------------------------------------------------------
        # All of the rest of the measures are relative to units, given in rawunits:
        self.count = len(self)
        self.groups = {'leftBump': 0, 'rightBump': 1, 'all': (0, 1)}
        self.startDevice()
    def __len__(self):
        return 2
    def getSensorValue(self, pos):
        name = ['leftBump', 'rightBump']
        return SensorValue(self,
                           self._dev.sensorData[name[pos]],
                           pos,
                           (0,  # x in meters
                            0,  # y
                            0,  # z
                            0,  # rads
                            0), # arc rads
                           noise=0)

class RoombaBatteryDevice(Device):
    def __init__(self, robot):
        self._dev = robot
        Device.__init__(self, "battery")
    def getTemperature(self):    
    	return self._dev.sensorData['temperature']
    def getCharge(self):
    	return self._dev.sensorData['charge']
    charge = property(getCharge)
    temperature = property(getTemperature)
    def addWidgets(self, window):
        window.addData("charge", ".charge:", self.charge)
        window.addData("temp", ".temperature:", self.temperature)
    def updateWindow(self):
        self.window.updateWidget("charge", self.charge)
        self.window.updateWidget("temp", self.temperature)

class Roomba(Robot):
    def __init__(self,
                 port = None, 
                 simulator = 0,
                 rate = None,
                 subtype = "Roomba"):
        # simulator = 0 makes it real
        Robot.__init__(self) # robot constructor
        self.lock = threading.Lock()
        self.buffer = ''
        self.debug = 0
        if simulator == 1:
            raise AttributeError, "simulator no longer supported"
        else:
            if subtype == "Roomba":
                if port == None:
                    try:
                        port = config.get('Roomba', 'port')
                    except:
                        pass
                if port == None:
                    port = "/dev/rfcomm0"
                if rate == None:
                    rate = 57600
            if type(port) == str and port.lower().startswith("com"):
                portnum = int(port[3:])
                if portnum >= 10:
                    port = r'\\.\COM%d' % (portnum)
            print "Roomba opening port '%s' with baudrate %s ..." % (port, rate)
            self.sc = Serial(port, baudrate=rate) #, xonxoff=0, rtscts=0)
            self.sc.setTimeout(0.5)
            self.sc.readlines() # to clear out the line
	self.lastTranslate = 0
	self.lastRotate = 0
	self.subtype = subtype
        self.radius = .16 #meters
        self._newline = "\r"
        self.type = "Roomba"
        self.port = port
        self.simulated = simulator
        self.supportedFeatures.append( "continuous-movement" )
        self.supportedFeatures.append( "range-sensor" )
        self.sendMsg('\x80') #Start Sci
	self.sendMsg('\x82') #Give user control
	self.sendMsg('\x8E\x02') # reset sensors, useful for distance
	self.sensorData = {} # Holds all of the sensor data
	self.supportedFeatures.append( "mono-sound" )
	self.supportedFeatures.append( "visual-feedback" )
	self.builtinDevices = ["ir", "bumper", "battery"]
	for name in self.builtinDevices:
            self.startDevice(name)
	self.update() 
        print "Done loading Roomba."

    def startDeviceBuiltin(self, name, index=0):
        if name == "ir":
            return {"ir": RoombaIRDevice(self)}
        elif name == "bumper":
            return {"bumper": RoombaBumperDevice(self)}
        elif name == "battery":
            return {"battery": RoombaBatteryDevice(self)}
    def connect(self):
    	self.start()
	
    def disconnect(self):
    	self.stop()

    def sendMsg(self, msg):
	self.lock.acquire()
	self.sc.writeline(msg, self._newline)
	#time.sleep(0.05)
	self.lock.release()
    
    def readData(self):
    	while self.sc.inWaiting(): # Clear out whatever may be in buffer
		self.sc.read(size=1)
	while 1:	
	    	self.sendMsg('\x8E\x00')
		retval = self.sc.read(size=26) # Read 26 bytes
		if (retval != '') and (len(retval) == 26): # Fixes a possible crash
			break
	
	retvalInt = [ ord(c) for c in retval ] # change into ints, from chars
	
	self.interpretSensorString(retvalInt) # Handles the sensor data
	
    def interpretSensorString(self, r ):
	# byte 0: bumps and wheeldrops
	self.sensorData['casterDrop'] = bitOfByte( 4, r[0] )
	self.sensorData['leftWheelDrop'] = bitOfByte( 3, r[0] )
	self.sensorData['rightWheelDrop'] = bitOfByte( 2, r[0] )
	self.sensorData['leftBump'] = bitOfByte( 1, r[0] )
	self.sensorData['rightBump'] = bitOfByte( 0, r[0] )
    
    	# byte 1: wall sensor, the IR looking to the right
	self.sensorData['wallSensor'] = bitOfByte( 0, r[1] )
   	# byte 2: left cliff sensor
	self.sensorData['leftCliff'] = bitOfByte( 0, r[2] )
    	# byte 3: front left cliff sensor
    	self.sensorData['frontLeftCliff'] = bitOfByte( 0, r[3] )
    	# byte 4: front right cliff sensor
    	self.sensorData['frontRightCliff'] = bitOfByte( 0, r[4] )
    	# byte 5: right cliff sensor
    	self.sensorData['rightCliff'] = bitOfByte( 0, r[5] )
    	# byte 6: virtual wall detector (the separate unit)
    	self.sensorData['virtualWall'] = bitOfByte( 0, r[6] )
           
    	# byte 8: dirt detector left
    	# the dirt-detecting sensors are acoustic impact sensors
    	# basically, they hear the dirt (or don't) going by toward the back
    	# this value ranges from 0 (no dirt) to 255 (lots of dirt)
    	self.sensorData['leftDirt'] = r[8]
	
    	# byte 9: dirt detector right
    	# some roomba's don't have the right dirt detector
    	# the dirt detectors are metallic disks near the brushes
    	self.sensorData['rightDirt'] = r[9]
	        
    	# byte 11: button presses
    	self.sensorData['powerButton'] = bitOfByte( 3, r[11] )
    	self.sensorData['spotButton'] = bitOfByte( 2, r[11] )
    	self.sensorData['cleanButton'] = bitOfByte( 1, r[11] )
    	self.sensorData['maxButton'] = bitOfByte( 0, r[11] )
	
    	# bytes 12 and 13: distance
    	# the distance that roomba has traveled, in mm, since the
    	# last time this data was requested (not from a SensorFrame,
    	# but from the roomba)
    	# It will stay at the max or min (32767 or -32768) if
    	# not polled often enough, i.e., it then means "a long way"
    	# It is the sum of the two drive wheels' distances, divided by 2
    	self.sensorData['distance'] = twosComplementInt2bytes( r[12], r[13] )
    	# bytes 14 and 15: angle
    	self.sensorData['rawAngle'] = twosComplementInt2bytes( r[14], r[15] )
    	# the distance between the wheels is 258 mm
    	self.sensorData['angleInRadians'] = (2.0 * self.sensorData['rawAngle']) / 258.0
    	a = self.sensorData['angleInRadians']
    	d = self.sensorData['distance'] * 0.001
        self.x += math.cos(a) * d
        self.y += math.sin(a) * d
        self.th += self.sensorData['angleInRadians'] * 180/math.pi
        self.th %= 360
        self.thr = self.th % math.pi/180

    	# bytes 17: Communication IR 
    	self.sensorData['commIR'] = twosComplementInt1byte( r[17] )
    	# remote control signals/meaning:
    	# 129 - left
    	# 130 - forward
    	# 131 - right
    	# 132 - spot
    	# 133 - max
    	# 134 - small
    	# 135 - medium
    	# 136 - large/clean
    	# 137 - pause
    	# 138 - power
    	# 139 - arc-forward-left
    	# 140 - arc-forward-right
    	# 141 - drive stop
    	# scheduling:
    	# 142 - send all
    	# 143 - seek dock
    	# home base:
    	# 240 - reserved
    	# 248 - red buoy (on robot's right as looking at base)
    	# 244 - green buoy (on  robot's left as looking at base)
    	# 242 - force field
    	# 252 - red and green
    	# 250 - red and force field
    	# 246 - green and force field
    	# 254 - red, green, and force field
    	
        
    	# byte 21: temperature of the battery
    	# this is in degrees celsius
    	self.sensorData['temperature'] = twosComplementInt1byte( r[21] )
    
    	# bytes 22 and 23: charge of the battery in milliamp-hours
    	# this is two unsigned bytes
    	self.sensorData['charge'] = r[22] << 8 | r[23]
    
    def update(self):
        Robot.update(self)
        self.readData()

	''' Attempt at adjusting for straight travel
	if self.lastRotate == 0x8000:
		self.lastRorate = 0x7FFF;
		self.adjustSpeed()
	elif self.lastRotate == 0x7FFF:
		self.lastRotate = 0x8000;
		self.adjustSpeed()
	'''

    def beep(self, duration, frequency, frequency2=0):
        num = freq2num(frequency)
        durInt = min(int(duration * 64.0), 255) # convert to 1/64 units
        # duration is four seconds max
        # song number is 15
        # PLAY is opcode 141
        # STORESONG is opcode 140
        msg = struct.pack("BBBBBBB", 140, 15, 1, num, durInt, 141, 15)
        #print msg
        self.sendMsg(msg)
        
    def getSensor(dev, value = None):
        if value == None:
                return dev.sensorData.keys()
	elif dev.sensorData.has_key(value):
                return dev.sensorData[value]
	else:
		print "Sorry not a valid Sensor. Use %s" % dev.sensorData.keys()
		return None
    
    def setMode(dev, value):
        """ set to safe or full """
    	if value == "safe":
		dev.sendMsg('\x83')
	elif value == "full":
		dev.sendMsg('\x84')

    def setClean(dev, value):
        """ set to spot, clean, or max """
    	if value == "spot":
		dev.sendMsg('\x86')
	elif value == "clean":
		dev.sendMsg('\x87')
	elif value == "max":
		dev.sendMsg('\x88')

    def setMotor(dev, value):
        """ set to main, vac, side, or off """
    	if value == "main":
		dev.sendMsg('\x8A\x04')
	elif value == "vac":
		dev.sendMsg('\x8A\x02')
	elif value == "side":
		dev.sendMsg('\x8A\x01')
	elif value == "off":
		dev.sendMsg('\x8A\x00')
	#could also add side&vac, main&side, main&vac, all

    def setStatus(dev, value):
        """ set to sleep or wake """
    	if value == "sleep": # sends the Roomba to its dock
		dev.sendMsg('\x88') #(max clean cycle): must be in clean cycle to
		time.sleep(1)
    		dev.sendMsg('\x8F') #look for the charging station
	elif value == "wakeup":
		dev.reset()
		time.sleep(.5)
		dev.clean("max") # Roomba automatically backs out of dock
		time.sleep(8)
		dev.clean("max") # Stops cleaning cycle
		time.sleep(2)
		dev.reset()
		dev.sendMsg('\x8B\x0C\x00\x00')
    
    def move(self, trans, rotate):
	self.lastTranslate = trans
	self.lastRotate = rotate
	self.adjustSpeed()

    def translate(dev, value):
	dev.lastTranslate = value
	dev.adjustSpeed()
	    
    def rotate(dev, value):
    	dev.lastRotate = value
	dev.adjustSpeed()

    def adjustSpeed(dev):
    	if dev.lastTranslate == 0:
            if dev.lastTranslate == 0:
                    if dev.lastRotate < 0:
                            dev.sendMsg('\x89\x00\x80\xFF\xFF')
                    elif dev.lastRotate > 0:
                            dev.sendMsg('\x89\x00\x80\x00\x00')
                    else :
                            dev.sendMsg('\x89\x00\x00\x00\x00')
        else:
            vel = int(dev.lastTranslate * 500)	
            if dev.lastRotate == 0:
                    rad = 0x8000
            else:
                    rad = int(100.0/dev.lastRotate)
                    if rad > 2000:
                            rad = 2000
                    elif rad < -2000:
                            rad = -2000
            if dev.lastTranslate < 0: # backwards
                rad *= -1 # reverse the effect of turn
            velHigh = 0xFF & (vel >> 8)
            velLow = vel & 0xFF
            radHigh = 0xFF & (rad >> 8)
            radLow = rad & 0xFF
            dev.sendMsg('\x89%c%c%c%c' % (velHigh, velLow, radHigh, radLow))
	
    def reset(dev):
    	dev.sendMsg('\x80\x82')
	
    def off(dev):
    	dev.sendMsg('\x85')
	
if __name__ == '__main__':
    x = Roomba()
    x.update()
