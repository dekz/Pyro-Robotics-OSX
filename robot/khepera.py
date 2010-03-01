"""
Defines KheperaRobot, a subclass of robot.

(c) 2005, PyrobRobotics.org. Licenced under the GNU GPL.
"""

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision: 2429 $"

from pyrobot.system.share import config
from pyrobot.robot import *
from pyrobot.robot.device import *
from pyrobot.system.serial import *
import pyrobot.gui.console as console
import string, array, math 
import threading
from pyrobot.geometry import PITIMES180, PIOVER180, DEG90RADS, COSDEG90RADS, SINDEG90RADS

class IRSensor(Device):
    def __init__(self, dev, type = "ir"):
        Device.__init__(self, type)
        self._dev = dev
        self.arc = 15.0 * PIOVER180 # radians
        self.units    = "ROBOTS" # current report units
        self.radius = dev.radius # universally in METERS
        # ox, oy, oz in METERS as well
        # ----------------------------------------------
        # natural units (not alterable):
        self.rawunits = "CM"
        self.maxvalueraw = 6.0 # in rawunits
        # ----------------------------------------------
        self.count = 8
        self.groups = {'all': range(8),
                       'front' : (2, 3), 
                       'front-left' : (0, 1), 
                       'front-right' : (4, 5),
                       'front-all' : (1, 2, 3, 4),
                       'left' : (0, ), 
                       'right' : (5, ), 
                       'left-front' : (0, ), 
                       'right-front' : (5, ), 
                       'left-back' : (7, ), 
                       'right-back' : (6, ), 
                       'back-left' : (7, ), 
                       'back-right' : (6, ), 
                       'back-all' : (6, 7), 
                       'back' : (6, 7)} 
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
            return (1023 - self._dev.rawData['ir'][pos])/1023.0 * 6.0
        except:
            return 0

class LightSensor(IRSensor):
    def __init__(self, dev):
        IRSensor.__init__(self, dev, "light")
        # now, just overwrite those differences
        self.units = "SCALED"
        self.rawunits = "RAW"
        self.maxvalueraw = 511
        self.arc = 0 # no meaning for light sensor
    def _getVal(self, pos):
        try:
            data = int(self.maxvalueraw - self._dev.rawData['light'][pos])
        except:
            data = 0
        return data

class KheperaRobot(Robot):
    def __init__(self,
                 port = None,
                 simulator = 0,
                 rate = None,
                 subtype = "Khepera"):
        # simulator = 0 makes it real
        Robot.__init__(self) # robot constructor
        self.lock = threading.Lock()
        self.buffer = ''
        self.debug = 0
        self.pause = 0.1 # for hemisson to keep from swamping the wireless
        if simulator == 1:
            raise AttributeError, "simulator no longer supported"
        else:
            if subtype == "Khepera":
                if port == None:
                    try:
                        port = config.get('khepera', 'port')
                    except:
                        pass
                if port == None:
                    port = "/dev/ttyS0"
                if rate == None:
                    rate = 38400
            else:
                if port == None:
                    try:
                        port = config.get('hemisson', 'port')
                    except:
                        pass
                if port == None:
                    port = "/dev/rfcomm0"
                if rate == None:
                    rate = 115200
            print "K-Team opening port", port, "..."
            self.sc = Serial(port, baudrate=rate) #, xonxoff=0, rtscts=0)
            self.sc.setTimeout(0)
            self.sc.readlines() # to clear out the line
        self.stallTolerance = 0.25
        self.stallHistoryPos = 0
        self.stallHistorySize = 5
        self.stallHistory = [0] * self.stallHistorySize
        self.lastTranslate = 0
        self.lastRotate = 0
        self.currSpeed = [0, 0]
        # This could go as high as 127, but I am keeping it small
        # to be on the same scale as larger robots. -DSB
        self.translateFactor = 12
        self.rotateFactor = 12
        self.dataTypes = {'n': 'ir',
                          'h' : 'position',
                          'o' : 'light',
                          'k' : 'stall',
                          'e' : 'speed',
                          'b' : 'version',
                          'j' : 'extensionDevices',
                          't1b'  : 'gripper software',
                          't1f'  : 'gripper resistivity',
                          't1g'  : 'gripper beam state',
                          't1h1' : 'gripper arm position',
                          't1h0' : 'gripper state',
                          't1j'  : 'gripper jumpers'
                          }
        self.rawData = {}
        self.rawData['position'] = [0] * 3
        self.rawData['ir'] = [0] * 6
        self.rawData['light'] = [0] * 6
        self.rawData['stall'] = [0] * 6
        self.subtype = subtype
        if subtype == "Hemisson":
            self.radius = .06 #meters
            self.builtinDevices = ['ir', 'light', 'audio']
            self._newline = "\r"
        elif subtype == "Khepera":
            self.radius = .03 #meters
            self.builtinDevices = ['ir', 'light', 'gripper']
            self._newline = "\n"
        else:
            raise TypeError, "invalid K-Team subtype: '%s'" % subtype
        self.startDevice("ir")
        self.range = self.ir[0]
        self.startDevice("light")
        if subtype == "Khepera":
            self.sendMsg('H') # position
        else:
            self.rawData["position"] = 0, 0
            self.sendMsg('B') # version
            self.sendMsg('j') # extensionDevices
        self.x = 0.0
        self.y = 0.0
        self.thr = 0.0
        self.th = 0.0
        try:
            self.w0 = self.rawData['position'][0]
            self.w1 = self.rawData['position'][1]
        except:
            raise "KTeamConnectionError"
        self.type = "K-Team"
        self.port = port
        self.simulated = simulator
        # ----- Updatable things:
        self.stall = self.isStall()
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.th = 0.0
        self.thr = 0.0
        self.supportedFeatures.append( "odometry" )
        self.supportedFeatures.append( "continuous-movement" )
        self.supportedFeatures.append( "range-sensor" )
	self.update() 
        print "Done loading K-Team robot."

    def startDeviceBuiltin(self, item):
        if item == "ir":
            return {"ir": IRSensor(self)}
        elif item == "light":
            return {"light": LightSensor(self)}
        elif item == "gripper":
            return {"gripper": KheperaGripper(self)}
        else:
            raise AttributeError, "K-Team robot does not support device '%s'" % item

    def disconnect(self):
        self.stop()

    def sendMsg(self, msg):
        self.lock.acquire()
        self.sc.writeline(msg, self._newline)
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
                            if self.debug: print "K-Team turret packet error:", rawdata
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
                            if self.debug: print "K-Team packet error:", rawdata

    def update(self):
        Robot.update(self)
        if self.subtype == "Khepera":
            self.sendMsg('N') #, 'ir')     # proximity
            self.sendMsg('O') #, 'light')  # ambient light
            self.sendMsg('H') #, 'position')
            self.sendMsg('E') #, 'speed')
            self.sendMsg('K') #, 'stall')  # motor status, used by isStall
            gripper = self.hasA('gripper')
            if gripper:
                #self.sendMsg('T,1,H,0')  # gripper state
                #self.sendMsg('T,1,H,1')  # arm position
                self.sendMsg('T,1,G')    # gripper beam state
                self.sendMsg('T,1,F')    # gripper resistivity                
        elif self.subtype == "Hemisson":
            self.sendMsg('N') #, 'ir')     # proximity
            self.sendMsg('O') #, 'light')  # ambient light
        while self.sc.inWaiting(): self.readData()
        """
        The 'K' message returns 6 numbers dealing with the status of the
        motors.  The 3rd and 6th are error codes representing the left and
        right motors, respectively.  The represent the difference
        between the desired speed and the actual speed.
        """
        # ----------- start compute stall
        self.stallHistory[self.stallHistoryPos] = 0
        try:
            if self.currSpeed[0] != 0:
                err = abs(float(self.rawData['stall'][2])/float(self.currSpeed[0]) - 1)
                if err < .25:
                    self.stallHistory[self.stallHistoryPos] = 1
            if self.currSpeed[1] != 0:
                err = abs(float(self.rawData['stall'][5])/float(self.currSpeed[1]) - 1)
                if err < .25:
                    self.stallHistory[self.stallHistoryPos] = 1
        except:
            pass
        # ----------- end compute stall
        self.stallHistoryPos = (self.stallHistoryPos + 1) % self.stallHistorySize
        self.stall = self.isStall()
        self.deadReckon()
        
    def deadReckon(self):
        """
        Called after each little update in position.
        Based on code from Adam R. Bockrath
        http://www.dcs.qmul.ac.uk/~adamb/
        """
        # get wheel positions:
        try:
            w0 = self.rawData['position'][0]
            w1 = self.rawData['position'][1]
        except:
            return
        if w0 == self.w0 and w1 == self.w1:
            # no difference to compute
            return
        # get diff:
        delta_w0 = (w0 - self.w0) # in ticks
        delta_w1 = (w1 - self.w1) # in ticks
        # get diff / diameter of wheel base, in ticks:
        delta_thr   = (delta_w1 - delta_w0) / 644.5
        # average diff (dist):
        delta_dist = (delta_w0 + delta_w1) / 2.0
        # compute change in x, y:
        delta_x = delta_dist * math.cos(self.thr + delta_thr/2.0)
        delta_y = delta_dist * math.sin(self.thr + delta_thr/2.0)
        if delta_thr != 0:
            delta_x *= 2.0 * math.sin(delta_thr/2.0) / delta_thr
            delta_y *= 2.0 * math.sin(delta_thr/2.0) / delta_thr
        # update everything:
        # FIX: I think that this needs to be subtracted for our th?
        self.thr += delta_thr
        # keep thr in range 0 - 2pi:
        while (self.thr > 2.0 * math.pi):
            self.thr -= (2.0 * math.pi)
        while (self.thr < 0):
            self.thr += (2.0 * math.pi)
        # save old values:
        self.w0 = w0
        self.w1 = w1
        self.x += (delta_x * .08) # convert ticks to mm
        self.y += (delta_y * .08) # convert ticks to mm
        self.th = self.thr * (180.0 / math.pi)

    def isStall(self, dev = 0):
        stalls = float(reduce(lambda x, y: x + y, self.stallHistory))
        # if greater than % of last history is stall, then stall
        return (stalls / self.stallHistorySize) > 0.5

    def move(self, trans, rotate):
        self.lastTranslate = trans
        self.lastRotate = rotate
        # FIX: do min/max here
        self.adjustSpeed()

    def adjustSpeed(dev):
        # This will send new motor commands based on the
        # robot's lastTranslate and lastRotate settings.
        # Khepera has differential drive, so compute each
        # side motor commands:
        left  = int((dev.lastTranslate * dev.translateFactor - \
                     dev.lastRotate * dev.rotateFactor))
        right  = int((dev.lastTranslate * dev.translateFactor + \
                      dev.lastRotate * dev.rotateFactor))
        # FIX: add acceleration, and assume that adjustSpeed
        # is being continuously called.
        dev.currSpeed = [left, right]
        dev.sendMsg('D,%i,%i' % (left, right))
        
    def translate(dev, value):
        dev.lastTranslate = value
        dev.adjustSpeed()
    
    def rotate(dev, value):
        dev.lastRotate = value
        dev.adjustSpeed()
    
class KheperaGripper(GripperDevice):
    def __init__(self, robot, type = "gripper"):
        GripperDevice.__init__(self, type)
        self.robot = robot
        self.robot.sendMsg('T,1,B')    # gripper software version
        self.robot.sendMsg('T,1,J')    # gripper jumpers
        self.lowestArmPosition = 255
        self.highestArmPosition = 165
        self.liftUpPosition = 175
        self.putDownPosition = 240
        self.startDevice()

    # preGet methods
    def getGripState(self):
        r = self.resistance()
        if r > 20:
            return 'closed'
        else:
            return 'open'

    def getArmPosition(self):
        return self.robot.rawData['gripper arm position'][0]

    def resistance(self):
        return self.robot.rawData['gripper resistivity'][0]

    def getSoftwareVersion(self):
        version, revision = self.robot.rawData['gripper software'][0:2]
        return version + 0.1 * revision

    def isLiftMaxed(self):
        return self.getArmPosition() == self.highestArmPosition

    # postSet methods

    def setArmPosition(self, angle):
        if angle > self.lowestArmPosition:
            angle = self.lowestArmPosition
        elif angle < self.highestArmPosition:
            angle = self.highestArmPosition
        self.robot.sendMsg('T,1,E,' + str(angle))

    # previous name was gripClose
    def close(self):
        self.robot.sendMsg('T,1,D,1')

    # previous name was gripOpen
    def open(self):
        self.robot.sendMsg('T,1,D,0')

    # previous name was liftUp
    def up(self):
        self.setArmPosition(self.liftUpPosition)

    # previous name was liftDown
    def down(self):
        self.setArmPosition(self.putDownPosition)

    # previous name was gripperStore
    def store(self):
        self.close()
        self.up()

    # previous name was gripperDeploy
    def deploy(self):
        self.down()
        self.open()

    # previous name was gripperHalt
    def halt(self):
        return self.stop()

    def getBreakBeam(self, which = None):
        # ignore which, because khepera has only one beam
        beamState = self.robot.rawData['gripper beam state'][0]
        if beamState < 100:
            return 0
        else:
            return 1

    def isClosed(self):
        return int(self.getGripState() == 'closed')

    def isOpened(self):
        return int(self.getGripState() == 'open')


if __name__ == '__main__':
    x = KheperaRobot()
    x.update()
    x.GetMin()
