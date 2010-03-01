
from termios import *
import select
import string
import time
from threading import *

class TimeOut:
    """
    Class needed for raising a TimeOut exception
    """
    pass

class SerialConnection:
    # Indexes for termios list. 
    IFLAG = 0
    OFLAG = 1
    CFLAG = 2
    LFLAG = 3
    ISPEED = 4
    OSPEED = 5
    CC = 6

    def __init__(self, aDevice, aSpeed):
        # Open the serial interface
        self.mSerial_id = open(aDevice, "a+")
        self.mSerial_nr = self.mSerial_id.fileno()

        # Configure the serial interface
        self._setup()
        self.setSpeed(aSpeed)

        # Create Event() and Lock() objects 

        # Event object used to ensure the correct data flow from the
        # application to the robot and back
        self.mCoordinate = Event()
        self.mCoordinate.set()
        # Maximal Timeout
        self.mMaxTime = 5 # was 5

        self.mIOmutex = Lock()

    def setSpeed(self, aSpeed):
        """
        Set baud rate of the device
        """
        mode = tcgetattr(self.mSerial_nr)
        mode[self.ISPEED] = aSpeed
        mode[self.OSPEED] = aSpeed
        tcsetattr(self.mSerial_nr, TCSANOW, mode)
        
    def _setup(self):
        """
        Configure the serial device in a way that it can be used for
        the Khepera robot
        """

        mode = tcgetattr(self.mSerial_nr)
    	mode[self.IFLAG] = mode[self.IFLAG] & ~(IGNBRK    |
                                      BRKINT    |
                                      IGNPAR    |
                                      INPCK     |
                                      ISTRIP    |
                                      ICRNL     |    
                                      INLCR     |
                                      IXON|IXOFF)
	mode[self.OFLAG] = mode[self.OFLAG] & ~(OPOST)
	mode[self.CFLAG] = mode[self.CFLAG] & ~(CSIZE | PARENB)
        # CS8 = 8 Bits, CSTOPB = 1 stop bit, CRTSCTS = no hardware flow control
        # PARENB = no parity; BAUD/N/8/1 
	mode[self.CFLAG] = mode[self.CFLAG] | (CS8)
	mode[self.CFLAG] = mode[self.CFLAG] & ~(PARENB | CSTOPB | CRTSCTS)
	mode[self.LFLAG] = mode[self.LFLAG] & ~(ECHO | ICANON | IEXTEN | ISIG)
	mode[self.CC][VMIN] = 1
	mode[self.CC][VTIME] = 0
	tcsetattr(self.mSerial_nr, TCSANOW, mode)

    ########################################################################

    def fileno(self):
        """
        Return the integer representation of the device
        """
        return self.mSerial_nr

    ########################################################################

    def close(self):
        """
        Close the device
        """
        self.mSerial_id.close()

    ########################################################################

    def writeblock(self, aBlock):
        """
        Write a complete block of data to the device
        """
        
        # Check if the response for the last query has already arived
        self.mCoordinate.wait(self.mMaxTime)
        # Aquire lock for the device
        self.mIOmutex.acquire()

        if (not self.mCoordinate.isSet()):
            # We got a time out
            self.mIOmutex.release()
            raise TimeOut()

        # Clear event to show that a command has been sent an we wait
        # for a response
        self.mCoordinate.clear()

        # Write out all lines
        for vLine in aBlock:
            (vIn, vOut, vExt) = select.select([],
                                              [self.mSerial_nr],  
                                              [])
            self.mSerial_id.write(vLine)


        self.mSerial_id.flush()
        # Release lock for the device
        self.mIOmutex.release()

    ########################################################################

    def writeline(self, aData, newline = "\n"):
        """
        Write out just one line 
        """
        
        # Check if the response for the last query has already arived
        self.mCoordinate.wait(self.mMaxTime)
        # Aquire lock for the device
        self.mIOmutex.acquire()
        if (not self.mCoordinate.isSet()):
            # We got a time out
            print "sc: timeout"
            self.mIOmutex.release()
            raise TimeOut()

        # Clear event to show that a command has been sent an we wait
        # for a response
        self.mCoordinate.clear()

        (vIn, vOut, vExt) = select.select([],
                                          [self.mSerial_nr],  
                                          [])
        #  Write out the data
        self.mSerial_id.write(aData)
        self.mSerial_id.write(newline)
        self.mSerial_id.flush()

        # Release the IO-lock
        self.mIOmutex.release()

    ####################################################################

    def readline(self, aBlocking=0):
        """
        Read a line from the device, with or without blocking
        """
        if (aBlocking):
            return self._blockingReadline()
        return self._readline()

    # ------------------------------------------------------------------

    def _blockingReadline(self):
        """
        Block until we have some data at the serial interface
        """

        # Wait until we have something
        (vIn, vOut, vExt) = select.select([self.mSerial_nr],  
                                          [],
                                          [])
        # Lock the serial IO device
        self.mIOmutex.acquire()
        # Read data
        vPuffer = self.mSerial_id.readline()
        # Unlock the serial IO device
        self.mIOmutex.release()
    
        # We got a message back.
        # If we send a query from the GUI this is the answer if the
        # protocal is handled correctly.
        # Thus, a new send is allowed
        self.mCoordinate.set()
    
        # Return the data read
        return vPuffer 

    # ------------------------------------------------------------------

    def _readline(self):
        """
        Read data but do not block if nothing is available at the serial
        IO device
        """

        vPuffer = ""
        while 1:
            # Wait for data
            print "cs: wait on read"
            (vIn, vOut, vExt) = select.select([self.mSerial_nr],  
                                              [],
                                              [], 0.01)
            # Check for timeout
            if (len(vIn) == 0):
                print "sc: read timeout"
                break
            # We got data -> Lock serial IO
            self.mIOmutex.acquire()
            # Add string to the data we read in previous cylces
            vPuffer = vPuffer + self.mSerial_id.readline()
            # Unlock serial IO
            self.mIOmutex.release()

        # We got a message back.
        # If we send a query from the GUI this is the answer if the
        # protocal is handled correctly.
        # Thus, a new send is allowed
        print "cs: got message:", vPuffer
        self.mCoordinate.set()

        # Return string 
        return vPuffer 

