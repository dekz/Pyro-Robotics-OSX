"""
Pyrobot module for interfacing with the Robocup Server.

TODO: need localize that would triangulate from flags/landmarks OR
      need someother way of dead reckoning (for x, y, th)
      need to make unique colors of lines and objects
      need to make laser sensor have more than single angle hits

(c) 2005, PyrobRobotics.org. Licenced under the GNU GPL.
"""

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision: 2023 $"

from socket import *
from pyrobot.robot import Robot
from pyrobot.robot.device import Device, SensorValue
from random import random
from time import sleep
from math import sin, cos
import threading
from pyrobot.geometry import PIOVER180, DEG90RADS, COSDEG90RADS, SINDEG90RADS

class ReadUDP(threading.Thread):
    """
    A thread class for reading UDP data.
    """
    BUF = 10000
    def __init__(self, robot):
        """
        Constructor, setting initial variables
        """
        self.robot = robot
        self._stopevent = threading.Event()
        self._sleepperiod = 0.0
        threading.Thread.__init__(self, name="ReadUDP")
        
    def run(self):
        """
        overload of threading.thread.run()
        main control loop
        """
        while not self._stopevent.isSet():
            data, addr = self.robot.socket.recvfrom(self.BUF)
            if len(data) > 0:
                self.robot.processMsg(parse(data), addr)
            self._stopevent.wait(self._sleepperiod)

    def join(self,timeout=None):
        """
        Stop the thread
        """
        self._stopevent.set()
        threading.Thread.join(self, timeout)

def makeDict(pairs):
    """ Turns list of [name, value] pairs into a dict {name: value, ...} or {name: [values], ...}"""
    dict = {}
    for item in pairs:
        if len(pairs) == 2:
            dict[item[0]] = item[1]
        else:
            dict[item[0]] = item[1:] # list of rest
    return dict

def lex(str):
    """ Simple lexical analizer for Lisp-like parser."""
    retval = []
    currentword = ""
    for ch in str:
        if ch == "(":
            if currentword:
                retval.append(currentword)
            retval.append("(")
            currentword = ""
        elif ch == ")":
            if currentword:
                retval.append(currentword)
            retval.append(")")
            currentword = ""
        elif ch == " ":
            if currentword:
                retval.append(currentword)
            currentword = ""
        elif ord(ch) == 0:
            pass
        else:
            currentword += ch
    if currentword:
        retval.append(currentword)
    return retval

def parse(str):
    """ Lisp-like parser. Takes str, returns Python list. """
    lexed = lex(str)
    stack = []
    currentlist = []
    for symbol in lexed:
        if symbol == "(":
            stack.append( currentlist )
            currentlist = []
        elif symbol == ")":
            if len(stack) == 0:
                print "too many closing parens:", str
                return []
            currentlist, temp = stack.pop(), currentlist
            currentlist.append( temp )
        else:
            if symbol.isalpha():
                currentlist.append( symbol )
            elif symbol.isdigit():
                currentlist.append( int(symbol) )
            else:
                try:
                    # doesn't get "drop_ball" above
                    # in the isalpha test
                    currentlist.append( float(symbol) )
                except:
                    if len(symbol) > 1 and symbol[0] == '"' and symbol[-1] == '"':
                        symbol = symbol[1:-1]
                    currentlist.append( symbol )
    if len(stack) != 0:
        print "missing ending paren:", str
        return []
    return currentlist[0]

class RobocupSimulationDevice(Device):
    """ A Simulation Device for the Robocup robot"""
    def __init__(self, robot):
        Device.__init__(self, "simulation")
        self.robot = robot
    def setPose(self, poseX, poseY):
        self.robot.sendMsg("(move %f %f)" % (poseX, poseY ))
            
class RobocupLaserDevice(Device):
    def __init__(self, robot):
        Device.__init__(self, "laser")
        self.robot = robot
        count = 90
        part = int(count/8)
        start = 0
        posA = part
        posB = part * 2
        posC = part * 3
        posD = part * 4
        posE = part * 5
        posF = part * 6
        posG = part * 7
        end = count
        self.groups = {'all': range(count),
                       'right': range(0, posB),
                       'left': range(posF, end),
                       'front': range(posC, posE),
                       'front-right': range(posB, posD),
                       'front-left': range(posD, posF),
                       'front-all': range(posB, posF),
                       'right-front': range(posA, posB),
                       'right-back': range(start, posA),
                       'left-front': range(posF,posG),
                       'left-back': range(posG,end),
                       'back-right': [],
                       'back-left': [],
                       'back': [],
                       'back-all': []}
        self.units    = "ROBOTS"
        self.noise    = 0.0
        self.arc      = 1.0 * PIOVER180 # in radians
        # -------------------------------------------
        self.rawunits = "METERS"
        self.maxvalueraw = 10.0
        # -------------------------------------------
        # These are fixed in meters: DO NOT CONVERT ----------------
        self.radius = 0.750 # meters
        # ----------------------------------------------------------
        self.count = count

    def __len__(self):
        return self.count
    def getSensorValue(self, pos):
        return SensorValue(self, self.values[pos], pos,
                           (0.0,
                            0.0,
                            0.03,
                            (pos - 45) * PIOVER180,
                            self.arc),
                           noise=self.noise)
    def updateDevice(self):
        self.values = [self.maxvalueraw] * self.count
        try:
            see = self.robot.see
        except:
            print "waiting for Robocup laser to come online..."
            return # not ready yet
        see.sort(lambda x,y: cmp(y[1],x[1]))
        # compute hits
        # TODO: make these hits a little wider; just one degree right now
        for item in see:
            # item is something like: [['f', 'c'], 14, 36, 0, 0]
            if len(item) >= 3: # need distance, angle
                if item[0][0] == 'f' and item[0][1] == 'l' or \
                       item[0][0] == 'f' and item[0][1] == 'b' or \
                       item[0][0] == 'f' and item[0][1] == 't' or \
                       item[0][0] == 'f' and item[0][1] == 'r':
                    pos = min(max(int(item[2]) + 45,0),89)
                    self.values[pos] = item[1]
                elif item[0][0] == 'p':
                    pos = min(max(int(item[2]) + 45,0),89)
                    self.values[ pos ] = item[1]
                elif item[0][0] == 'b':
                    pos = min(max(int(item[2]) + 45,0),89)
                    self.values[ pos ] = item[1]
                    
class RobocupRobot(Robot):
    """ A robot to interface with the Robocup simulator. """
    def __init__(self, name="TeamPyrobot", host="localhost", port=6000,
             goalie = 0):
        Robot.__init__(self)
        self.lastTranslate = 0
        self.lastRotate = 0
        self.updateNumber = 0L
        self._historyNumber = 0L
        self._lastHistory = 0
        self._historySize = 100
        self._history = [0] * self._historySize
        self.simulated = 1
        self.name = name
        self.host = host
        self.port = port
        self.continuous = 1
        self.goalie = goalie
        self.address = (self.host, self.port)
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.reader = ReadUDP(self)
        self.reader.start()
        msg = "(init %s (version 9.0)" % self.name
        if goalie:
            msg += "(goalie)"
        msg += ")" 
        self.socket.sendto(msg, self.address)
        # wait to get the real address
        while self.address[1] == self.port: pass
        self.builtinDevices = ["simulation", "laser"]
        self.startDevice("simulation")
        self.startDevice("laser")
        self.simulation[0].setPose( random() * 100 - 50,
                                    random() * 20 - 10 )
        self.range = self.laser[0]
        # default values for all robots:
        self.stall = 0
        self.x = 0.0
        self.y = 0.0
        self.th = 0.0
        self.thr = 0.0
        # Can we get these from robocup?
        self.radius = 0.75
        self.type = "Robocup"
        self.subtype = 0
        self.units = "METERS"
        #self.supportedFeatures.append( "odometry" )
        self.supportedFeatures.append( "continuous-movement" )
        self.supportedFeatures.append( "range-sensor" )
        self.localize(0, 0, 0)
        self.update()
        
    def startDeviceBuiltin(self, item):
        if item == "simulation":
            return {"simulation": RobocupSimulationDevice(self)}
        if item == "laser":
            return {"laser": RobocupLaserDevice(self)}
        else:
            raise AttributeError, "robocup robot does not support device '%s'" % item
        
    def sendMsg(self, msg, address = None):
        if address == None:
            address = self.address
        self.socket.sendto(msg + chr(0), address)

    def disconnect(self):
        self.stop()
        self.socket.close()

    def messageHandler(self, message):
        """ Write your own message handler here. """
        if message[0] == "hear":
            print "heard message:", message[1:]

    def processMsg(self, msg, addr):
        self._lastHistory = self._historyNumber % self._historySize
        if len(msg):
            self._history[self._lastHistory] = msg
            self._historyNumber += 1
            if msg[0] == "init":
                self.__dict__[msg[0]] = msg[1:]
                self.address = addr
            elif msg[0] == "server_param":
                # next is list of pairs
                self.__dict__[msg[0]] = makeDict(msg[1:])
            elif msg[0] == "player_param":
                # next is list of pairs
                self.__dict__[msg[0]] = makeDict(msg[1:])
            elif msg[0] == "player_type": # types
                # next is list of ["id" num], pairs...
                id = "%s_%d" % (msg[0], msg[1][1])
                self.__dict__[id] = makeDict(msg[2:])
            elif msg[0] == "sense_body": # time pairs...
                self.__dict__[msg[0]] = makeDict(msg[2:])
                self.__dict__["sense_body_time"] = msg[1]
            elif msg[0] == "see": # time tuples...
                self.__dict__[msg[0]] = msg[2:]
                self.__dict__["%s_time" % msg[0]] = msg[1]
            elif msg[0] == "error":
                print "Robocup error:", msg[1]
            elif msg[0] == "warning":
                print "Robocup warning:", msg[1]
            elif msg[0] == "hear": # hear time who what
                self.__dict__[msg[0]] = msg[2:]
                self.__dict__["%s_time" % msg[0]] = msg[1]
            elif msg[0] == "score": 
                self.__dict__[msg[0]] = msg[2:]
                self.__dict__["%s_time" % msg[0]] = msg[1]
            else:
                print "unhandled message in robocup.py: '%s'" % msg[0], msg
            self.messageHandler(msg)
        else:
            return

    def update(self):
        Robot.update(self)
        if self.continuous:
            self.keepGoing()
        self.updateNumber += 1

    def keepGoing(self):
        # only one per cycle!
        if self.lastTranslate and self.lastRotate:
            if self.updateNumber % 2:
                self.translate(self.lastTranslate)
            else:
                self.rotate(self.lastRotate)
        elif self.lastTranslate:
            self.translate(self.lastTranslate)
        elif self.lastRotate:
            self.rotate(self.lastRotate)
            
    def translate(self, translate_velocity):
        # robocup takes values between -100 and 100
        self.lastTranslate = translate_velocity
        val = translate_velocity * 100.0
        self.sendMsg("(dash %f)" % val)

    def rotate(self, rotate_velocity):
        # robocup takes degrees -180 180
        # but that is a lot of turning!
        # let's scale it back a bit
        # also, directions are backwards
        self.lastRotate = rotate_velocity
        val = -rotate_velocity * 20.0
        self.sendMsg("(turn %f)" % val)

    def move(self, translate_velocity, rotate_velocity):
        self.translate(translate_velocity)
        self.rotate(rotate_velocity)

