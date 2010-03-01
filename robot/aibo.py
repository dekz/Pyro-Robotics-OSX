"""
Aibo client commands for talking to the Tekkotsu servers
from Python.

(c) 2005, PyrobRobotics.org. Licenced under the GNU GPL.
"""

__author__ = "Ioana Butoi, Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision: 2428 $"

from pyrobot.robot import Robot
from pyrobot.robot.device import Device
from socket import *
import struct, time, sys, threading

def makeControlCommand(control, amt):
    # HEAD: control is tilt 't', pan 'p', or roll 'r'
    # WALK: control is forward 'f', strafe 's', and rotate 'r'
    return struct.pack('<bf', ord(control), amt) 

class Listener:
    """
    A class for talking to ports on Aibo. If you want to read the data off
    in the background, give this thread to ListenerThread, below.
    """
    def __init__(self, port, host, protocol = "TCP"):
        self.port = port
        self.host = host
        self.protocol = protocol
        self.runConnect()
        #self.s.settimeout(0.1)

    def runConnect(self):
        print >> sys.stderr, "[",self.port,"] connecting ...",
        try:
            if self.protocol == "UDP":
                self.s = socket(AF_INET, SOCK_DGRAM) # udp socket
            elif self.protocol == "TCP":
                self.s = socket(AF_INET, SOCK_STREAM) # tcp socket
            done = 0
            while not done:
                try:
                    self.s.connect((self.host,self.port)) # connect to server
                    done = 1
                except KeyboardInterrupt:
                    print >> sys.stderr, "aborted!"
                    return
                except:
                    print >> sys.stderr, ".",
            print >> sys.stderr, "connected!"
        except IOError, e:
            print e
        if self.protocol == "UDP":
            self.s.send("connection request")
            self.s.settimeout(0.5)
            self.s.receive()
            self.s.settimeout(0)

    def readUntil(self, stop = "\n"):
        retval = ""
        ch = self.s.recvfrom(1)[0]
        while ch != stop:
            retval += struct.unpack('c', ch)[0]
            ch = self.s.recvfrom(1)[0]
        return retval

    def read(self, bytes = 4, format = 'l', all=False):
        data = ""
        for i in range(bytes):
            data += self.s.recvfrom(1)[0]
        if all:
            return struct.unpack(format, data)
        else:
            return struct.unpack(format, data)[0]

    def write(self, message):
        retval = self.s.send(message)
        return retval
        
class ListenerThread(threading.Thread):
    """
    A thread class, for ports where Aibo feeds it to us
    as fast as we can eat em!
    """
    def __init__(self, listener, callback):
        """
        Constructor, setting initial variables
        """
        self.listener = listener
        self.callback = callback
        self._stopevent = threading.Event()
        self._sleepperiod = 0.001
        threading.Thread.__init__(self, name="ListenerThread")
        
    def run(self):
        """
        overload of threading.thread.run()
        main control loop
        """
        while not self._stopevent.isSet():
            self.callback(self.listener)
            self._stopevent.wait(self._sleepperiod)

    def join(self,timeout=None):
        """
        Stop the thread
        """
        self._stopevent.set()
        threading.Thread.join(self, timeout)

class AiboHeadDevice(Device):
    """
    Class for moving the Aibo Head unit as a Pan-Tilt-Zoom-Nod device.
    Does not implement zoom.
    """
    def __init__(self, robot):
        Device.__init__(self, "ptz")
        self.robot = robot
        # Turn on head remote control if off:
        self.robot.setRemoteControl("Head Remote Control", "on")
        time.sleep(1) # pause for a second
        self.dev   = Listener(self.robot.PORT["Head Remote Control"],
                              self.robot.host)
        self.supports = ["pan", "tilt", "roll"]
        self.pose = [0, 0, 0, 0]

    def init(self):
        self.center()

    def setPose(self, *args):
        pan, tilt, zoom, roll = 0, 0, 0, 0
        if len(args) == 3:
            pan, tilt, zoom = args[0], args[1], args[2]
        elif len(args) == 4:
            pan, tilt, zoom, roll = args[0], args[1], args[2], args[3]
        elif len(args[0]) == 3:
            pan, tilt, zoom = args[0][0], args[0][1], args[0][2]
        elif len(args[0]) == 4:
            pan, tilt, zoom, roll = args[0][0], args[0][1], args[0][2], args[0][3]
        else:
            raise AttributeError, "setPose takes pan, tilt, zoom (ignored)[, and roll]"
        self.pan( pan )
        self.tilt( tilt )
        self.zoom( zoom )
        self.roll( roll )
        return "ok"

    def zoom(self, amt):
        return "ok"

    def tilt(self, amt):
        # tilt: 0 to -1 (straight ahead to down)
        # see HeadPointListener.java
        if amt > 0:
            amt = 0
        if amt < -1:
            amt = -1
        self.dev.write( makeControlCommand('t', amt))
        self.pose[1] = amt
        return "ok"

    def pan(self, amt):
        # pan: -1 to 1 (right to left)
        # see HeadPointListener.java
        if amt > 1:
            amt = 1
        if amt < -1:
            amt = -1
        self.dev.write( makeControlCommand('p', amt)) 
        self.pose[0] = amt
        return "ok"

    def roll(self, amt):
        # roll: 0 to 1 (straight ahead, to up (stretched))
        if amt < 0:
            amt = 0
        if amt > 1:
            amt = 1
        self.dev.write( makeControlCommand('r', amt))
        self.pose[3] = amt
        return "ok"

    def center(self):
        return self.setPose(0, 0, 0, 0)

    def addWidgets(self, window):
        p, t, z, r = self.pose
        window.addCommand("pan", "Pan!", str(p), lambda p: self.pan(float(p)))
        window.addCommand("tilt", "Tilt!", str(t), lambda t: self.tilt(float(t)))
        window.addCommand("zoom", "Zoom!", str(z), lambda z: self.zoom(float(z)))
        window.addCommand("roll", "Roll!", str(r), lambda r: self.roll(float(r)))


class AiboRobot(Robot):
    """
    Class for an Aibo robot in Pyrobot. 
    """
    # pyrobot/camera/aibo/__init__.py references this:
    PORT = {"Head Remote Control": 10052,
            "Walk Remote Control": 10050, 
            "EStop Remote Control": 10053,
            "World State Serializer": 10031,
            "Raw Cam Server": 10011,
            "Seg Cam Server": 10012,
            "Main Control": 10020,
            "Joint Writer": 10051
            }
    def __init__(self, host):
        Robot.__init__(self)
        self.host = host
        #---------------------------------------------------
        self.main_control     = Listener(self.PORT["Main Control"],
                                         self.host) 
        self.main_control.s.send("!reset\n") # reset menu
        # --------------------------------------------------
        # Throttle the sending of data from the Aibo; we can't handle much faster than
        # 10 bits of data a second. Make this lower if you can (these are ms pauses):
        self.setAiboConfig("vision.rawcam_interval", 50)
        #self.setAiboConfig("vision.rle_interval", 50)
        #self.setAiboConfig("vision.worldState_interval", 50)
        # --------------------------------------------------
        self.setRemoteControl("Walk Remote Control", "on")
        self.setRemoteControl("EStop Remote Control", "on")
        self.setRemoteControl("World State Serializer", "on")
        self.setRemoteControl("Raw Cam Server", "off")
        self.setRemoteControl("Aibo 3D", "on")
        time.sleep(1) # let the servers get going...
        self.walk_control     = Listener(self.PORT["Walk Remote Control"],
                                         self.host)
        self.estop_control    = Listener(self.PORT["EStop Remote Control"],
                                         self.host) # stop control
        #wsjoints_port   =10031 # world state read sensors
        #wspids_port     =10032 # world state read pids        
        self.sensor_socket    = Listener(self.PORT["World State Serializer"],
                                         self.host) # sensors
        self.joint_socket    = Listener(self.PORT["Joint Writer"],
                                        self.host) # joints
        self.sensor_thread    = ListenerThread(self.sensor_socket, self.readWorldState)
        self.sensor_thread.start()
        #self.pid_socket       = Listener(10032, self.host) # sensors
        time.sleep(1) # let all of the servers get going...
        self.estop_control.s.send("start\n") # send "stop\n" to emergency stop the robot
        time.sleep(1) # let all of the servers get going...
        self.builtinDevices = ["ptz"]
        # start up some devices:
        self.startDevice("ptz")
        #self.startDevice("camera", visible=1)

        # Commands available on main_control (port 10020):
        # '!refresh' - redisplays the current control (handy on first connecting,
        #               or when other output has scrolled it off the screen)
        # '!reset' - return to the root control
        # '!next' - calls doNextItem() of the current control
        # '!prev' - calls doPrevItem() of the current control
        # '!select' - calls doSelect() of the current control
        # '!cancel' - calls doCancel() of the current control
        # '!msg text' - broadcasts text as a TextMsgEvent
        # '!root text ...' - calls takeInput(text) on the root control
        # '!hello' - responds with 'hello\ncount\n' where count is the number of times
        #            '!hello' has been sent.  Good for detecting first connection after
        #            boot vs. a reconnect.
        # '!hilight [n1 [n2 [...]]]' - hilights zero, one, or more items in the menu
        # '!input text' - calls takeInput(text) on the currently hilighted control(s)
        # '!set section.key=value' - will be sent to Config::setValue(section,key,value)
        #  any text not beginning with ! - sent to takeInput() of the current control

    def setAiboConfig(self, item, state):
        self.main_control.s.send("!set %s=%s\n" % (item, state))

    def setRemoteControl(self, item, state):
        # "Walk Remote Control"
        # could also use "!root "TekkotsuMon" %(item)", but that toggles
        if state == "off":
            item = "#" + item
        self.main_control.s.send("!select \"%s\"\n" % item)

        # Main menu:
        # 0 Mode Switch - Contains the "major" apps, mutually exclusive selection
        # 1 Background Behaviors - Background daemons and monitors
        # 2 TekkotsuMon: Servers for GUIs
        # 3 Status Reports: Displays info about the runtime environment on the console
        # 4 File Access: Access/load files on the memory stick
        # 5 Walk Edit: Edit the walk parameters
        # 6 Posture Editor: Allows you to load, save, and numerically edit the posture
        # 7 Vision Pipeline: Start/Stop stages of the vision pipeline
        # 8 Shutdown?: Confirms decision to reboot or shut down
        # 9 Help: Recurses through the menu, prints name and description of each item

        # Option 2 from Main Menu, TekkotsuMon menu:
        # 0 RawCamServer: Forwards images from camera, port 10011
        # 1 SegCamServer: Forwards segmented images from camera, port 10012
        # 2 Head Remote Control: Listens to head control commands, port 10052
        # 3 Walk Remote Control: Listens to walk control commands, port 10050
        # 4 View WMVars: Brings up the WatchableMemory GUI on port 10061
        # 5 Watchable Memory Monitor: Bidirectional control communication, port 10061
        # 6 Aibo 3D: Listens to aibo3d control commands coming in from port 10051
        # 7 World State Serializer: Sends sensor information to port 10031
        #                           and current pid values to port 10032
        # 8 EStop Remote Control

    def readWorldState(self, socket):
        """ Used as a callback in ListenerThread for sockets that produce data fast for us to read. """
        # read sensor/pid states:
        self.ws_timestamp = socket.read(4, "l")
        # ---
        numPIDJoints = socket.read(4, "l")
        self.numPIDJoints = numPIDJoints # ERS7: 18
        self.positionRaw = socket.read(numPIDJoints * 4,
                                       "<%df" % numPIDJoints,all=1)
        # ---
        numSensors = socket.read(4, "l") # ERS7: 8
        self.numSensors = numSensors
        self.sensorRaw = socket.read(numSensors * 4,
                                     "<%df" % numSensors,all=1)
        # ---
        numButtons = socket.read(4, "l") # ERS7: 6
        self.numButtons = numButtons
        self.buttonRaw = socket.read(numButtons * 4,
                                     "<%df" % numButtons,all=1)
        # --- same number as PID joints:             # ERS7: 18
        self.dutyCycleRaw = socket.read(numPIDJoints * 4,
                                        "<%df" % numPIDJoints,all=1)
                
    def getJoint(self, query):
        """ Get position, dutyCycle of joint by name """
        legOffset = 0
        numLegs = 4
        jointsPerLeg = 3
        numLegJoints = numLegs*jointsPerLeg
        headOffset = legOffset+numLegJoints
        numHeadJoints = 3
        tailOffset = headOffset + numHeadJoints
        numTailJoints = 2
        mouthOffset = tailOffset + numTailJoints
        jointDict = query.split()
        pos = 0
        check = 0 #used to check if the joint request is correct
        normalize = 1.0 # need to normalize joint position because of setPose
        if "leg" in jointDict:
            if len(jointDict) == 4:
                pos += legOffset
                check +=1
                if "front" in jointDict:
                    pos +=0
                    check +=1
                elif "back" in jointDict:
                    pos += numLegs/2*jointsPerLeg
                    check +=1
                if "left" in jointDict:
                    pos +=0
                    check +=1
                elif "right" in jointDict:
                    pos += jointsPerLeg
                    check +=1
                if "rotator" in jointDict:
                    pos +=0
                    check +=1
                    normalize = 2.4
                elif "elevator" in jointDict:
                    pos +=1
                    check +=1
                    normalize = 1.6
                elif "knee" in jointDict:
                    pos +=2
                    check +=1
                    normalize = 2.3
                if check !=4:
                    raise AttributeError, "incorrect joint request"
            else:
                raise AttributeError, "incorrect joint request"
        elif "head" in jointDict:
            if len(jointDict) ==2:
                pos += headOffset
                check +=1
                if "tilt" in jointDict:
                    pos +=0
                    check +=1
                elif "pan" in jointDict:
                    pos +=1
                    check +=1
                elif "roll" in jointDict:
                    pos +=2
                    check +=1
                elif "nod" in jointDict:
                    pos +=2
                    check +=1
                if check !=2:
                    raise AttributeError, "incorrect joint request"
            else:
                raise AttributeError, "incorrect joint request"
        elif "tail" in jointDict:
            if len(jointDict) == 2:
                pos += tailOffset
                check +=1
                if "tilt" in jointDict:
                    pos +=0
                    check +=1
                elif "pan" in jointDict:
                    pos +=1
                    check +=1
                if check != 2:
                    raise AttributeError, "incorrect joint request"
            else:
                raise AttributeError, "incorrect joint request"
        elif "mouth" in jointDict:
                if len(jointDict) == 1:
                    pos += mouthOffset
                    normalize = -1.0
                else:
                    raise AttributeError, "incorrect joint request"

        else:
            raise AttributeError, "no such joint"
        return self.positionRaw[pos]/normalize, self.dutyCycleRaw[pos]
    def getButton(self, query):
        """ Get value of button by name """
        pos = 0
        check = 0
        btnDict = query.split()
        if "chin" in btnDict:
            if len(btnDict) == 1:
                pos = 4
            else:
                raise AttributeError, "incorrect button request"
        elif "head" in btnDict:
            if len(btnDict) == 1:
                pos = 5
            else:
                raise AttributeError, "incorrect button request"    
        elif "body" in btnDict:
            if len(btnDict) == 2:
                pos +=6
                check +=1
                if "front" in btnDict:
                    pos +=0
                    check+=1
                elif "middle" in btnDict:
                    pos +=1
                    check += 1
                elif "rear" in btnDict:
                    pos +=2
                    check +=1
                if check !=2:
                    raise AttributeError, "incorrect button request"
            else:
                raise AttributeError, "incorrect button request"  
        elif "wireless" in btnDict:
            if len(btnDict) == 1:
                pos = 9
            else:
                raise AttributeError, "incorrect button request"
        elif "paw" in btnDict:
            if len(btnDict) == 3:
                pos +=0
                check +=1
                if "front" in btnDict:
                    pos +=0
                    check +=1
                elif "back" in btnDict:
                    pos +=2
                    check += 1
                if "left" in btnDict:
                    pos +=0
                    check +=1
                elif "right" in btnDict:
                    pos +=1
                    check +=1
                if check !=3:
                    raise AttributeError, "incorrect button request"
            else:
                raise AttributeError, "no such button"
        return self.buttonRaw[pos]

    def getSensor(self, query):
        """ Get the sensor value """
        pos = 0
        check =0
        sensDict = query.split()
        if "ir" in sensDict:
            if len(sensDict) == 2:
                pos +=0
                check +=1
                if "near" in sensDict:
                    # in mm 50-500
                    pos +=0
                    check +=1
                elif "far" in sensDict:
                    # in mm 200-1500
                    pos +=1
                    check += 1
                elif "chest" in sensDict:
                    # in mm 100-900
                    pos +=2
                    check += 1
                if check !=2:
                    raise AttributeError , "incorrect sensor request"
            else:
                raise AttributeError , "incorrect sensor request"
        elif "accel" in sensDict:
            if len(sensDict) == 2:
                pos +=3
                check +=1
                if "front-back" in sensDict:
                    pos +=0
                    check+=1
                elif "right-left" in sensDict:
                    pos +=1
                    check += 1
                elif "up-down" in sensDict:
                    pos +=2
                    check += 1
                if check !=2:
                    raise AttributeError , "incorrect sensor request"
            else:
                raise AttributeError , "incorrect sensor request"
        elif "power" in sensDict:
            if len(sensDict) == 2:
                pos +=6
                check += 1
                if "remaining" in sensDict:
                    pos +=0
                    check +=1
                elif "thermo" in sensDict:
                    pos +=1
                    check +=1
                elif "capacity" in sensDict:
                    pos +=2
                    check +=1
                elif "voltage" in sensDict:
                    pos +=3
                    check +=1
                elif "current" in sensDict:
                    pos +=4
                    check += 1
                if check !=2:
                    raise AttributeError , "incorrect sensor request"
            else:
                raise AttributeError , "incorrect sensor request"
        else:
                raise AttributeError , "no such sensor"
        return self.sensorRaw[pos]

    def startDeviceBuiltin(self, item):
        if item == "ptz":
            return {"ptz": AiboHeadDevice(self)}
        elif item == "camera":
            return self.startDevice("AiboCamera")

    def connect(self):
        self.estop_control.s.send("start\n")

    def disconnect(self):
        self.estop_control.s.send("stop\n")

    def rotate(self, amount):
        self.walk_control.write( makeControlCommand('r', amount)) 

    def translate(self, amount):
        self.walk_control.write( makeControlCommand('f', amount)) 

    def strafe(self, amount):
        # strafe (side-to-side) -1 to 1 :(right to left)
        self.walk_control.write( makeControlCommand('s', amount)) 
        
    def move(self, translate, rotate):
        # forward: -1 to 1 (backward to forward)
        # rotate: -1 to 1 (right to left)
        self.walk_control.write( makeControlCommand('f', translate)) 
        self.walk_control.write( makeControlCommand('r', rotate))

    def destroy(self):
        self.setRemoteControl("Raw Cam Server", "off")
        self.sensor_thread.join()
        Robot.destroy(self)

    def playSound(self, file):
        """
        AiboRobot.playSound(FILENAME) takes one of the following filenames
        (WAV is optional):
        
        3BARKS.WAV, 3YIPS.WAV, BARKHIGH.WAV, BARKLOW.WAV, BARKMED.WAV
        BARKREAL.WAV, CAMERA.WAV, CATCRY.WAV, CATYOWL.WAV, CRASH.WAV
        CUTEY.WAV, DONKEY.WAV, FART.WAV, GLASS.WAV, GROWL.WAV
        GROWL2.WAV, GRRR.WAV, HOWL.WAV, MEW.WAV, PING.WAV, ROAR.WAV
        SKID.WAV, SNIFF.WAV, TICK.WAV, TOC.WAV, WHIIP.WAV, WHIMPER.WAV
        WHOOP.WAV, YAP.WAV, YIPPER.WAV
        """
        file = file.upper();
        if (not file.endswith(".WAV")):
            file +=".WAV"
        self.main_control.s.send("!select \"%s\"\n" % "Play Sound")
        self.main_control.s.send("!select \"%s\"\n" % file) #select file

    def runMotion(self, file):
        file = file.upper()
        if (not file.endswith(".MOT")):
            file +=".MOT"
        self.main_control.s.send("!select \"%s\"\n" % "Run Motion Sequence")
        self.main_control.s.send("!select \"%s\"\n" % file)
        
    def setWalk(self, file):
        """
        AiboRobot.setWalk(FILENAME) - takes one of the following filenames:
        
        PACE.PRM, TIGER.PRM, WALK.PRM (crawl)
        """
        file = file.upper();
        if (not file.endswith(".PRM")):
            file +=".PRM"
        self.walk_control.s.close()
        self.main_control.s.send("!select \"%s\"\n" % "Load Walk") # forces files to be read
        self.main_control.s.send("!select \"%s\"\n" % file) # select file
        self.main_control.s.send("!select \"%s\"\n" % "#WalkControllerBehavior") # turn off
        self.main_control.s.send("!select \"%s\"\n" % "-WalkControllerBehavior") # turn on
        # If you change the walk, then you have to reconnect
        # back onto the walk server
        time.sleep(2)
        self.walk_control     = Listener(self.PORT["Walk Remote Control"],
                                         self.host) # walk command

    def setPose(self, joint, amtx, amty=None, amtz=None):
        """ Set the position of a joint """
        # all values passed in are between -1.0 and 1.0
        if amtx < -1.0:
            amtx = -1.0
        elif amtx > 1.0:
            amtx =  1.0
        if amty !=None:
            if amty < -1.0:
                amty = -1.0
            elif amty > 1.0:
                amty = 1.0
        if amtz !=None:
            if amtz < -1.0:
                amtz = -1.0
            elif amtz > 1.0:
                amtz = 1.0
            
        if (amtx>=-1.0 and amtx<=1.0) and \
           ((amty==None) or ( amty>=-1.0 and amty<=1.0)) and \
           ((amtz==None) or ( amtz>=-1.0 and amtz<=1.0)):
            self.update()
            l = list(self.positionRaw)
            jointDict = joint.split()
            check = 0
            if "mouth" in jointDict:
                # original: 0.0(closed) and -1.0(open)
                # pyrobot: 0.0(closed) and 1.0(open)
                if len(jointDict) == 1:
                    if amtx < 0:
                        amtx = 0
                    l[17] = -amtx
                else:
                    raise AttributeError, "incorrect joint name"    
            elif "tail" in jointDict:
                if len(jointDict) == 1:
                    l[16] = amtx; #pan
                    l[15] = amty; #tilt
                elif len(jointDict) == 2:
                    if "pan" in jointDict:
                        l[16] = amtx;
                    elif "tilt" in jointDict:
                        l[15] = amtx;
                    else:
                        raise AttributeError, "incorrect joint name"     
                else:
                    raise AttributeError, "incorrect joint name"    
            elif "leg" in jointDict:
                # back rotator original: -2.4(fwd) to 2.2 (bwd)
                #   pyrobot: -1.0(fwd) to 1.0(bwd) where 0 is straight
                # front rotator, original: -2.2(bwd) to 2.4(fwd)
                #   pyrobot: -1.0(bwd) to 1.0(fwd) where 0 is straight down
                # elevator, original: -0.3 to 1.6 (up)
                #   pyrobot: -1.0 to 1.0(up) where 0 is straight down
                # knee, original: -0.6 to 2.3 (contraction)
                #   pyrobot: -1.0 to 1.0(contraction)
                if len(jointDict) == 3 or len(jointDict) == 4:
                    check +=1
                    offset = 0
                    if "front" in jointDict:
                        offset = 0
                        check += 1
                    elif "back" in jointDict:
                        offset = 6
                        check += 1
                    if "left" in jointDict:
                        offset +=0
                        check += 1
                    elif "right" in jointDict:
                        offset +=3
                        check += 1
                    if check == 3:
                        if len(jointDict) == check:
                            amtx = amtx*2.4
                            if amtx >2.2:
                                amtx = 2.2
                            amty = amty*1.6
                            if amty<-0.3:
                                amty = -0.3
                            amtz = amtz*2.3
                            if amtz < -0.6:
                                amtx = -0.6
                            l[offset] = amtx #rotator
                            l[offset+1] = amty #elevator
                            l[offset+2] = amtz #knee
                        else:
                            if "rotator" in jointDict:
                                offset +=0
                                check +=1
                                amtx = amtx*2.4
                                if amtx >2.2:
                                    amtx = 2.2
                            elif "elevator" in jointDict:
                                offset +=1
                                check +=1
                                amtx = amtx*1.6
                                if amtx<-0.3:
                                    amtx = -0.3
                            elif "knee" in jointDict:
                                offset +=2
                                check +=1
                                amtx = amtx*2.3
                                if amtx < -0.6:
                                    amtx = -0.6
                            if check !=4:
                                raise AttributeError, "incorrect joint name"
                            l[offset] = amtx
                    
                    else:
                        raise AttributeError, "incorrect joint name"
                else:
                    raise AttributeError, "incorrect joint name"
            else:
                raise AttributeError, "no such joint"  
            self.joint_socket.write(struct.pack("<18f",*l))
            self.update()
        else:
            raise AttributeError, "values out of range -1.0, 1.0"

    def getPose(self, joint):
        jointDict = joint.split()
        res = {}
        if "tilt" in jointDict:
            val = self.getJoint("head tilt")[0]
            res["tilt"]=val/1.32
        if "pan" in jointDict:
            val = self.getJoint("head pan")[0]
            if val < 0:
                res["pan"] = val/1.49
            else:
                res["pan"] = val/1.54
        if "roll" in jointDict:
            val = self.getJoint("head roll")[0]
            res["roll"] = val/0.71
        return res
   
# Aibo 3D: Listens to aibo3d control commands coming in from port 10051
# World State Serializer: Sends sensor information to port 10031 and
# current pid values to port 10032
