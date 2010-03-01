"""
A PyrobotSimulator world. A large room with two robots and
two lights.

(c) 2005, PyroRobotics.org. Licensed under the GNU GPL.
"""

from pyrobot.simulators.pysim import TkSimulator, TkPioneer, \
     PioneerFrontSonars, PioneerFrontLightSensors

def INIT():
    # (width, height), (offset x, offset y), scale:
    sim = TkSimulator((441,434), (22,420), 40.357554)  
    # x1, y1, x2, y2 in meters:
    sim.addBox(0, 0, 10, 10)
    sim.addBox(1, 7.5, 9, 8)
    sim.addBox(2, 3, 8, 6)
    # (x, y) meters, brightness usually 1 (1 meter radius):
    sim.addLight(5, 9, 1)
    # port, name, x, y, th, bounding Xs, bounding Ys, color
    # (optional TK color name):
    sim.addRobot(60000, TkPioneer("RedPioneer",
                                  5, 2, -0.86,
                                  ((.225, .225, -.225, -.225),
                                   (.175, -.175, -.175, .175))))
    # add some sensors:
    sim.robots[0].addDevice(PioneerFrontSonars())
    sim.robots[0].addDevice(PioneerFrontLightSensors())
    return sim
