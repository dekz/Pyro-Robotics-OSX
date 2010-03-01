from pyrobot.robot.device import Device
import time, threading, random

class LogicDevice(Device, threading.Thread):
    def setup(self):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.data = 0
        self.start()

    def updateDevice(self):
        print "Updated started..."
        self.lock.acquire()
        # look at the shared data
        print "data:", self.data
        self.lock.release()
        print "Updated done!"
        

    def run(self):
        while self.isAlive():
            print "   Async update started..."
            time.sleep(2) # do something that takes some time
            self.lock.acquire() # acquire the lock
            self.data = random.random() # update the data
            self.lock.release() # release the lock
            print "   Async update done!"

def INIT(robot):
    return {"logic": LogicDevice()}
