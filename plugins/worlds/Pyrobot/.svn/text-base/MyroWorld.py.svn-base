"""
A PyrobotSimulator world. A room with one obstacle and
a small inner room.

(c) 2005, PyroRobotics.org. Licensed under the GNU GPL.
"""

from pyrobot.simulators.pysim import *

def INIT():
    # (width, height), (offset x, offset y), scale:
    sim = TkSimulator((585,596), (33,545), 173.983100)
    # x1, y1, x2, y2 in meters:
    sim.addBox(0, 0, 3, 3)
    sim.addRobot(60000, TkMyro("GreenMyro",
                               0.37, 0.33, 5.21,
                               ((.20, .20, -.10, -.10),
                                (.18, -.18, -.18, .18)), "green"))
    sim.addRobot(60001, TkMyro("BlueMyro",
                               2.69, 2.68, 2.03,
                               ((.20, .20, -.10, -.10),
                                (.18, -.18, -.18, .18)), "blue"))
    for i in range(2):
        sim.robots[i].addDevice(BulbDevice(-.10, 0))
        sim.robots[i].addDevice(MyroIR()) # infrared
        sim.robots[i].addDevice(MyroBumper()) # bumpers
        sim.robots[i].addDevice(MyroLightSensors()) # bumpers
    return sim
