from pyrobot.robot.device import Device
from pyrobot.system.share import ask

# Python interface for Canon VCC4 Pan/Tilt/Zoom device
# Jim Marshall
# Version 3/25/2009
# Based on Aria/src/ArVCC4.cpp and Aria/include/ArVCC4.h

from pyrobot.robot.device import Device
import serial, time

DELIM = chr(0x00)       # Delimeter character
DEVICEID = chr(0x30)    # Default device ID
DEVICEID_1 = chr(0x31)  # used with SETRANGE
PANSLEW = chr(0x50)     # Sets the pan slew
TILTSLEW = chr(0x51)    # Sets the tilt slew
STOP = chr(0x53)        # Stops current pan/tilt motion
INITIALIZE = chr(0x58)  # Initializes the camera
SLEWREQ = chr(0x59)     # Request pan/tilt min/max slew
ANGLEREQ = chr(0x5C)    # Request pan/tilt min/max angle
PANTILT = chr(0x62)     # Pan/tilt command
SETRANGE = chr(0x64)    # Pan/tilt min/max range assignment
PANTILTREQ = chr(0x63)  # Request pan/tilt position
INFRARED = chr(0x76)    # Controls operation of IR lighting
PRODUCTNAME = chr(0x87) # Requests the product name
LEDCONTROL = chr(0x8E)  # Controls LED status
CONTROL = chr(0x90)     # Puts camera in Control mode
POWER = chr(0xA0)       # Turns on/off power
AUTOFOCUS = chr(0xA1)   # Controls auto-focusing functions
ZOOMSTOP = chr(0xA2)    # Stops zoom motion
GAIN = chr(0xA5)        # Sets gain adjustment on camera
FOCUS = chr(0xB0)       # Manual focus adjustment
ZOOM = chr(0xB3)        # Zooms camera lens
ZOOMREQ = chr(0xB4)     # Requests max zoom position
IRCUTFILTER = chr(0xB5) # Controls the IR cut filter
DIGITALZOOM = chr(0xB7) # Controls the digital zoom amount
RESPONSE = chr(0xFE)    # Packet header for response
HEADER = chr(0xFF)      # Packet Header
FOOTER = chr(0xEF)      # Packet Footer

PACKET_HEADER = HEADER + DEVICEID + DEVICEID + DELIM

CAM_ERROR_NONE = chr(0x30)    # No error
CAM_ERROR_BUSY = chr(0x31)    # Camera busy, will not execute the command
CAM_ERROR_PARAM = chr(0x35)   # Illegal parameters to function call
CAM_ERROR_MODE = chr(0x39)    # Not in host control mode
CAM_ERROR_UNKNOWN = chr(0xFF) # Unknown error condition.  Should never happen

MIN_PAN = -98           # degrees, -875 position units is min pan assignment
MAX_PAN = 98            # degrees, 875 position units is max pan assignment
MIN_TILT = -30          # degrees, -267 position units is min tilt assignment
MAX_TILT = 88           # degrees, 790 position units is max tilt assignment
MIN_PAN_SLEW = 1        # degrees/sec, 8 positions/sec (PPS)
MAX_PAN_SLEW = 90       # degrees/sec, 800 positions/sec (PPS)
MIN_TILT_SLEW = 1       # degrees/sec, 8 position/sec (PPS)
MAX_TILT_SLEW = 69      # degrees/sec, 613 positions/sec (PPS)
MIN_ZOOM = 0
MAX_ZOOM = 1958

#-----------------------------------------------------------------------------

def panTiltPacket(pan, tilt):
    assert MIN_PAN <= pan <= MAX_PAN and MIN_TILT <= tilt <= MAX_TILT
    # convert to camera position units and encode as 8 hex bytes
    panBytes = '%04X' % int(pan / 0.1125 + 0x8000)
    tiltBytes = '%04X' % int(tilt / 0.1125 + 0x8000)
    packet = PACKET_HEADER + PANTILT + panBytes + tiltBytes + FOOTER
    return packet    

def panSlewPacket(panSlew):
    assert MIN_PAN_SLEW <= panSlew <= MAX_PAN_SLEW
    # convert to camera position units and encode as 3 hex bytes
    bytes = '%03X' % int(panSlew / 0.1125)
    packet = PACKET_HEADER + PANSLEW + bytes + FOOTER
    return packet

def tiltSlewPacket(tiltSlew):
    assert MIN_TILT_SLEW <= tiltSlew <= MAX_TILT_SLEW
    # convert to camera position units and encode as 3 hex bytes
    bytes = '%03X' % int(tiltSlew / 0.1125)
    packet = PACKET_HEADER + TILTSLEW + bytes + FOOTER
    return packet

# this is necessary because the camera defaults to a max tilt range of
# 30 instead of 88
def defaultTiltRangePacket():
    bytes = '%04X' % int(MIN_TILT / 0.1125 + 0x8000)
    bytes += '%04X' % int(MAX_TILT / 0.1125 + 0x8000)
    packet = PACKET_HEADER + SETRANGE + DEVICEID_1 + bytes + FOOTER
    return packet

def opticalZoomPacket(zoom):
    assert MIN_ZOOM <= zoom <= MAX_ZOOM
    bytes = '%04X' % int(zoom)
    packet = PACKET_HEADER + ZOOM + bytes + FOOTER
    return packet

def digitalZoomPacket(magnify):
    assert magnify in (1, 2, 4, 8)
    bytes = chr(0x30) + chr(0x30 + int(magnify))
    packet = PACKET_HEADER + DIGITALZOOM + bytes + FOOTER
    return packet

def panTiltRequestPacket():
    return PACKET_HEADER + PANTILTREQ + FOOTER

def zoomRequestPacket():
    return PACKET_HEADER + ZOOMREQ + DEVICEID + FOOTER

def controlModePacket():
    return PACKET_HEADER + CONTROL + DEVICEID + FOOTER

def powerOffPacket():
    return PACKET_HEADER + POWER + DEVICEID + FOOTER

def powerOnPacket():
    return PACKET_HEADER + POWER + DEVICEID_1 + FOOTER

def initPacket():
    return PACKET_HEADER + INITIALIZE + DEVICEID + FOOTER

def haltPanTiltPacket():
    return PACKET_HEADER + STOP + DEVICEID + FOOTER

def haltZoomPacket():
    return PACKET_HEADER + ZOOMSTOP + DEVICEID + FOOTER

def reveal(packet):
    hexcodes = ''
    for byte in packet:
        hexcodes += '0x%X ' % ord(byte)
    return hexcodes[:-1]

#-----------------------------------------------------------------------------

class CanonPTZ(Device):

    def __init__(self, portname=None, baudrate=None):
        Device.__init__(self, deviceType='ptz')
        if portname == None or baudrate == None:
            if portname == None:
                portname = '/dev/ttyS3'
            if baudrate == None:
                baudrate = 9600
            result = ask("Please enter the parameters for the Canon PTZ",
                         (("Port name", portname),
                          ("Baud rate", baudrate),
                          ))
        else:
            result = {'Port name': portname, 'Baud rate': baudrate}
        self.port = serial.Serial(result['Port name'],
                                  baudrate=result['Baud rate'])
        self._send(controlModePacket())
        self._send(initPacket())
        self._send(opticalZoomPacket(0))
        self._send(digitalZoomPacket(1))
        self._send(panSlewPacket(MAX_PAN_SLEW))
        self._send(tiltSlewPacket(MAX_TILT_SLEW))
        self._send(defaultTiltRangePacket())
        self._pan = 0
        self._tilt = 0
        self._zoom = 0
        self._magnify = 1
        self._panSpeed = MAX_PAN_SLEW
        self._tiltSpeed = MAX_TILT_SLEW
        self.supports = ['pan', 'tilt', 'zoom', 'magnify']
        print 'Canon PTZ device ready'

    def _send(self, packet):
        while True:
            #print reveal(packet)
            self.port.write(packet)
            time.sleep(0.300)
            response = self.port.read(self.port.inWaiting())
            if len(response) < 6:
                break
            elif response[3] == CAM_ERROR_BUSY:
                # camera busy, so keep trying
                continue
            elif response[3] == CAM_ERROR_NONE:
                return response
            else:
                break
        # if we get here there was an error
        print 'Error in response to:', reveal(packet)
        print 'Got %d bytes: %s' % (len(response), reveal(response))
        return None

    def waiting(self):
        print '%d bytes waiting' % self.port.inWaiting()
    
    def close(self):
        self.port.close()
        print 'Serial connection closed'

    def setPanTilt(self, pan, tilt):
        pan = max(MIN_PAN, min(pan, MAX_PAN))
        tilt = max(MIN_TILT, min(tilt, MAX_TILT))
        response = self._send(panTiltPacket(pan, tilt))
        if response is not None:
            self._pan = pan
            self._tilt = tilt

    def setPan(self, pan):
        self.setPanTilt(pan, self._tilt)

    def setTilt(self, tilt):
        self.setPanTilt(self._pan, tilt)

    def setZoom(self, zoom):
        zoom = max(MIN_ZOOM, min(zoom, MAX_ZOOM))
        response = self._send(opticalZoomPacket(zoom))
        if response is not None:
            self._zoom = zoom

    def setMagnify(self, magnify):
        if magnify not in (0, 1, 2, 4, 8):
            print 'WARNING: ignoring bad magnification level %s' % magnify
            magnify = 1
        # level 0 is interpreted as 1
        magnify = max(1, magnify)
        response = self._send(digitalZoomPacket(magnify))
        if response is not None:
            self._magnify = magnify

    def setPanSpeed(self, speed):
        speed = max(MIN_PAN_SLEW, min(speed, MAX_PAN_SLEW))
        response = self._send(panSlewPacket(speed))
        if response is not None:
            self._panSpeed = speed

    def setTiltSpeed(self, speed):
        speed = max(MIN_TILT_SLEW, min(speed, MAX_TILT_SLEW))
        response = self._send(tiltSlewPacket(speed))
        if response is not None:
            self._tiltSpeed = speed

    def incPanTilt(self, panDelta=5, tiltDelta=5):
        self.setPanTilt(self._pan + panDelta, self._tilt + tiltDelta)

    def incPan(self, delta=5):
        self.setPan(self._pan + delta)

    def incTilt(self, delta=5):
        self.setTilt(self._tilt + delta)

    def incZoom(self, delta=50):
        self.setZoom(self._zoom + delta)

    def reset(self):
        self._send(initPacket())
        self._send(defaultTiltRangePacket())
        self._pan, self._tilt = 0, 0
        self.setPanSpeed(MAX_PAN_SLEW)
        self.setTiltSpeed(MAX_TILT_SLEW)
        self.setZoom(0)
        self.setMagnify(1)

    def getSpeed(self):
        return (self._panSpeed, self._tiltSpeed)

    def getPan(self):
        return self._pan

    def getTilt(self):
        return self._tilt

    def getZoom(self):
        return self._zoom

    def getMagnify(self):
        return self._magnify

    def getPanTilt(self):
        return (self._pan, self._tilt)

    def getRealPanTilt(self):
        response = self._send(panTiltRequestPacket())
        if len(response) != 14:
            print 'Error occurred getting real pan/tilt info'
            return None
        else:
            # decode pan info
            buf = ''
            for i in range(5, 9):
                byte = ord(response[i])
                if byte < 0x40:
                    byte = byte - 0x30
                else:
                    byte = byte - ord('A') + 10
                buf += chr(byte)
            val = ord(buf[0])*0x1000 + ord(buf[1])*0x100 + ord(buf[2])*0x10 + ord(buf[3])
            pan = int((val - 0x8000) * 0.1125)
            # decode tilt info
            buf = ''
            for i in range(9, 13):
                byte = ord(response[i])
                if byte < 0x40:
                    byte = byte - 0x30
                else:
                    byte = byte - ord('A') + 10
                buf += chr(byte)
            val = ord(buf[0])*0x1000 + ord(buf[1])*0x100 + ord(buf[2])*0x10 + ord(buf[3])
            tilt = int((val - 0x8000) * 0.1125)
            return (pan, tilt)

    def getRealZoom(self):
        response = self._send(zoomRequestPacket())
        if len(response) != 10:
            print 'Error occurred getting real zoom info'
            return None
        else:
            # decode zoom info
            buf = ''
            for i in range(5, 9):
                byte = ord(response[i])
                if byte < 0x40:
                    byte = byte - 0x30
                else:
                    byte = byte - ord('A') + 10
                buf += chr(byte)
            zoom = ord(buf[0])*0x1000 + ord(buf[1])*0x100 + ord(buf[2])*0x10 + ord(buf[3])
            return zoom

    def getRealPose(self):
        pan, tilt = self.getRealPanTilt()
        zoom = self.getRealZoom()
        return (pan, tilt, zoom, self._magnify)

    def stop(self):
        self._send(haltPanTiltPacket())
        self._send(haltZoomPacket())
        self._pan, self._tilt, self._zoom, self._magnify = self.getRealPose()

    def exercise(self):
        print 'Exercising pan/tilt/zoom...'
        self.setPanTilt(MAX_PAN, MAX_TILT)
        time.sleep(4)
        self.setTilt(MIN_TILT)
        time.sleep(4)
        self.setPan(MIN_PAN)
        time.sleep(4)
        self.center()
        self.setZoom(MAX_ZOOM)
        time.sleep(4)
        self.setZoom(MIN_ZOOM)
        self.setPanTilt(MIN_PAN, MAX_TILT)
        time.sleep(4)
        self.center()

    # pyrobot support

    def init(self):
        self.reset()

    def getPose(self):
        return (self._pan, self._tilt, self._zoom, self._magnify)

    def setPose(self, *args):
        if len(args) == 4:
            pan, tilt, zoom, magnify = args
        elif len(args) == 1 and len(args[0]) == 4:
            pan, tilt, zoom, magnify = args[0]
        else:
            raise AttributeError, 'setPose takes pan, tilt, zoom, and magnify'
        self.setPanTilt(pan, tilt)
        self.setZoom(zoom)
        self.setMagnify(magnify)

    def pan(self, panVal):
        self.setPan(panVal)
        return self.getPose()

    def tilt(self, tiltVal):
        self.setTilt(tiltVal)
        return self.getPose()

    def zoom(self, zoomVal):
        self.setZoom(zoomVal)
        return self.getPose()

    def magnify(self, magnifyVal):
        self.setMagnify(magnifyVal)
        return self.getPose()

    def center(self):
        self.setPanTilt(0, 0)

    def canGetRealPanTilt(self):
        return 1

    def canGetRealZoom(self):
        return 1

    def getMaxPosPan(self):
        return MAX_PAN

    def getMaxNegPan(self):
        return MIN_PAN

    def getMaxPosTilt(self):
        return MAX_TILT

    def getMaxNegTilt(self):
        return MIN_TILT

    def getMaxZoom(self):
        return MAX_ZOOM

    def getMinZoom(self):
        return MIN_ZOOM

    def addWidgets(self, window):
        p, t, z, m = 0, 0, 0, 1
        window.addCommand("pan", "Pan", str(p), lambda p: self.pan(int(p)))
        window.addCommand("tilt", "Tilt", str(t), lambda t: self.tilt(int(t)))
        window.addCommand("zoom", "Zoom", str(z), lambda z: self.zoom(int(z)))
        window.addCommand("magnify", "Magnify", str(m), lambda m: self.magnify(int(m)))

#-----------------------------------------------------------------------------

def INIT(robot):
    return {'ptz' : CanonPTZ()}

