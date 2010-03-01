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
    sim.addBox(3, 4, 7, 4.5)
    sim.addBox(2.5, 4, 3, 8)
    sim.addBox(7, 4, 7.5, 8)
    sim.addBox(2.5, 8, 4, 8.5)
    sim.addBox(6, 8, 7.5, 8.5)
    sim.addBox(4.5, 6.5, 5.5, 7)
    # (x, y) meters, brightness usually 1 (1 meter radius):
    sim.addLight(5, 5.5, 1)
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
