# -------------------------------------------------------
# Sample Plotter
# -------------------------------------------------------

import Tkinter
import random
from pyrobot.robot.device import Device
import pyrobot.system.share as share

class SimplePlot(Device): 
    COLORS = ['blue', 'red', 'tan', 'yellow', 'orange', 'black',
              'azure', 'beige', 'brown', 'coral', 'gold', 'ivory',
              'moccasin', 'navy', 'salmon', 'tan', 'ivory']
    def __init__(self, robot, what, width = 400, height = 120):
        Device.__init__(self, "view")
        self.width = width
        self.height = height
        self.what = what
        self.robot = robot
        self.dataMin = 0
        self.dataMax = robot.range.getMaxvalue()
        self.dataWindowSize = 400
        self.dataSample = 1
        self.dataCount = 0
        self.lastRun = 0
        self.dataHist = [0] * self.robot.range.count
        self.source = self.what
        self.startDevice()
        self.makeWindow()
    def makeWindow(self):
        try:
            self.win.state()
            ok = 1
        except:
            ok = 0
        if ok:
            self.win.deiconify()
            self.setVisible(1)
        else:
            try:
                self.win = Tkinter.Toplevel(share.gui)
            except:
                print "Pyrobot view cannot make window. Check DISPLAY variable."
                self.setVisible(0)
                return
            self.win.title("Pyrobot view: %s range sensors" % self.what)
            self.canvas = Tkinter.Canvas(self.win,width=self.width,height=self.height)
            self.canvas.pack()
            self.win.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.hideWindow)
            self.setVisible(1)
    def hideWindow(self):
        self.setVisible(0)
        self.win.withdraw()
    def updateWindow(self, options = {}):
        # do something to draw yourself
        if self.dataCount > self.dataWindowSize:
            self.canvas.delete('data1')
            self.canvas.move("data2", -self.width/2, 0)
            self.canvas.itemconfigure("data2", tag = "data1")
            self.dataCount = self.dataWindowSize / 2
        else:
            self.dataCount += 1
        results = [(x.value, x.pos) for x in self.robot.range[self.what]]
        for dist,sensor in results:
            if self.dataCount < self.dataWindowSize/2:
                tag = "data1"
            else:
                tag = "data2"
            self.canvas.create_line(self.dataCount - 1,
                                    self.dataHist[sensor],
                                    self.dataCount,
                                    int(float(dist)/self.dataMax * 100.0),
                                    tags = tag,
                                    width = 2,
                                    fill = SimplePlot.COLORS[sensor])
            self.dataHist[sensor] = int(float(dist)/self.dataMax * 100.0 - 1)
        self.win.update_idletasks()

if __name__ == '__main__':
    class Robot:
        def __init__(self):
            self.groups = {'all': (0,1)}
            self.range = Range(2)
    class Range:
        def __init__(self, count):
            self.count = count
            self.maxvalue = 10.0
        def __getitem__(self, pos):
            return [Sensor(self.maxvalue, self.count)] * self.count
    class Sensor:
        pos = 0
        def __init__(self, maxvalue, count):
            self.value = random.random() * maxvalue
            self.pos = Sensor.pos
            Sensor.pos = (Sensor.pos + 1) % count

    plot = SimplePlot(Robot(), 'all')
    for i in range(2500):
        plot.updateWindow()
    print "Done!"
