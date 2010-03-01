# A Simple Device

from pyrobot.robot.device import Device

class TestDevice(Device):
    def setup(self):
        self.type = "test"
        self.visible = 1
        self.specialvalue = 42
        self.threadCount = 0
        self.updateCount = 0
        self.async = 1
        
    def update(self):
        if not self.active: return
        self.threadCount += 1

    def updateDevice(self):
        self.updateCount += 1

    def addWidgets(self, window):
        window.addData("name1", "specialvalue:", self.specialvalue)
        window.addData("name2", "thread count:", self.threadCount)
        window.addData("name3", "update count:", self.updateCount)
        window.addCommand("sleep", "time between thread updates:",
                          self.asyncSleep,
                          self.setSleep)

    def setSleep(self, value):
        self.asyncSleep = float(value)

    def updateWindow(self):
        if self.window != 0:
            self.window.updateWidget("name1", self.specialvalue)
            self.window.updateWidget("name2", self.threadCount)
            self.window.updateWidget("name3", self.updateCount)


def INIT(robot):
    return {"test": TestDevice()}
