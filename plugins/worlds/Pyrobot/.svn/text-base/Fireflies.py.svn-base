"""
A PyrobotSimulator world. A large room with two robots and
two lights.

(c) 2005, PyroRobotics.org. Licensed under the GNU GPL.
"""

from pyrobot.simulators.pysim import *

def INIT():
    # (width, height), (offset x, offset y), scale:
    sim = TkSimulator((441,434), (22,420), 40.357554)  
    # x1, y1, x2, y2 in meters:
    sim.addBox(0, 0, 10, 10)
    # port, name, x, y, th, bounding Xs, bounding Ys, color
    # (optional TK color name):
    sim.addRobot(60000, TkPioneer("Pioneer1",
                                  1, 1, 5.42,
                                  ((.225, .225, -.225, -.225),
                                   (.175, -.175, -.175, .175)),
                                  "red"))
    sim.addRobot(60001, TkPioneer("Pioneer2",
                                  1, 9, 3.84,
                                  ((.225, .225, -.225, -.225),
                                   (.175, -.175, -.175, .175)),
                                  "purple"))
    sim.addRobot(60002, TkPioneer("Pioneer3",
                                  9, 9, 2.37,
                                  ((.225, .225, -.225, -.225),
                                   (.175, -.175, -.175, .175)),
                                  "yellow"))
    sim.addRobot(60003, TkPioneer("Pioneer4",
                                  9, 1, .86,
                                  ((.225, .225, -.225, -.225),
                                   (.175, -.175, -.175, .175)),
                                  "green"))
    # add some sensors:
    for i in range(4):
        sim.robots[i].addDevice(PioneerFrontSonars())
        sim.robots[i].addDevice(PioneerFrontLightSensors())
        # x, y relative to body center (beyond bounding box):
        sim.robots[i].addDevice(BulbDevice(0.226, 0))
    return sim
