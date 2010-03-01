# Communication Protocol for talking with the SC-8000
# serial to buddybox RC controller
# D.S. Blank, Bryn Mawr College

from pyrobot.system.serial import Serial
from pyrobot.robot import Robot

def bitmask(*args):
    retval = 0
    for i in args:
        retval |= (1 << (i - 1))
    return retval

def bytes(num):
    hi = num >> 8 
    lo = num & 0x00FF
    return hi, lo

class BlimpRobot(Robot):
    def __init__(self,
                 name = "Blimp",
                 serialPort = "/dev/ttyUSB0"):
        Robot.__init__(self) # robot constructor
        self.channels = 4
        self.debug = 0
        self.name = name
        self.simulated = 0
        self.serialPort = serialPort
        self.port = Serial(serialPort, baudrate=9600)
        #self.port = open("debug.txt", "w")
        self.lastCommand = {}
        offPositions = {}
        for i in range(1, self.channels + 1): # init to zeros
            self.lastCommand[i] = 0
            offPositions[i] = 15000
        # send commands to all be neutral (15000):
        self.sendCommands(offPositions)
        # default values for all robots:
        self.stall = 0
        self.x = 0.0
        self.y = 0.0
        self.th = 0.0
        self.thr = 0.0
        # Can we get these from player?
        self.radius = 1.00
        self.type = "Blimp"
        self.subtype = 0
        self.units = "METERS"
        self.localize(0.0, 0.0, 0.0)
        self.update()

    def sendCommands(self, channelDict):
        # first, remove any that are duplicates of what has already been sent:
        if self.debug: print "        commands:", channelDict
        #remove = []
        #for channel in channelDict:
        #    if self.lastCommand[channel] == channelDict[channel]:
        #        remove.append(channel)
        #    else:
        #        # record what will be the last command sent
        #        self.lastCommand[channel] = channelDict[channel]
        ## delete the nums (can't do it above, in loop):
        #for num in remove:
        #    del channelDict[num]
        # next, construct the packets, if there is one:
        if len(channelDict) == 0: return {}
        if self.debug: print "reduced commands:", channelDict
        retval = []
        retval.append(ord('~'))
        retval.append(ord('~'))
        orderedChannels = channelDict.keys()
        orderedChannels.sort()
        retval.append(bitmask(*orderedChannels))
        binaryMask = bitmask() # list digital bits here, 1 = light
        retval.append(ord(str(binaryMask)))
        for i in orderedChannels:
            num = channelDict[i]
            hi, lo = bytes(num)
            retval.append(hi)
            retval.append(lo)
        self.port.write( "".join(map(chr, retval)) )
        #self.port.flush()
        if self.debug: print "write:", retval
        return channelDict

    def translate(self, amt):
        power = 10000 + int(((amt + 1) / 2.0) * 10000)
        self.sendCommands({3: power})

    def rotate(self, amt):
        # motor 1 positive: left
        # motor 4 positive: right
        power1 = 10000 + int(((amt + 1) / 2.0) * 10000)
        power4 = 10000 + int(((-amt + 1) / 2.0) * 10000)
        self.sendCommands({1: power1, 4: power4})

    def move(self, t_amt = 0, r_amt = 0, h_amt = 0):
        t_power = 10000 + int(((t_amt + 1) / 2.0) * 10000)
        r_power1 = 10000 + int(((r_amt + 1) / 2.0) * 10000)
        r_power4 = 10000 + int(((-r_amt + 1) / 2.0) * 10000)
        h_power = 10000 + int(((-h_amt + 1) / 2.0) * 10000)
        self.sendCommands({1: r_power1, 2: h_power, 3: t_power, 4: r_power4})

    def moveZ(self, height):
        power = 10000 + int(((-height + 1) / 2.0) * 10000)
        self.sendCommands({2: power})

    def stop(self):
        self.move(0, 0, 0)
        
