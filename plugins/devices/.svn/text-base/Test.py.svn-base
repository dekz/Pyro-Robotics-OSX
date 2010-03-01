# A Simple Device
# See TestNoBlock to see a test device that updates
# asynchronously, and quickly.

from pyrobot.robot.device import Device

class TestDevice(Device):
    def setup(self):
        self.type = "test"
        self.visible = 1
        self.specialvalue = 42

    def makeWindow(self):
        print "[[[[ made window! ]]]]"

    def updateWindow(self):
        print "update window! -------------" # when visible, few times a second

    def updateDevice(self):
        print "------------- update device!" # about 10 times a second!

def INIT(robot):
    return {"test": TestDevice()}
