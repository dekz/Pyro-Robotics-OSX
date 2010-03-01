"""
A PyrobotSimulator world. A room with one obstacle and
a small inner room.

(c) 2005, PyroRobotics.org. Licensed under the GNU GPL.
"""

from pyrobot.simulators.pysim import *
import math

def INIT():
    # (width, height), (offset x, offset y), scale:
    sim = TkSimulator((273,544),(38,521),70.977619)
    # x1, y1, x2, y2 in meters:
    sim.addBox(0, 0, 3, 7)
    sim.addBox(0, 0, 1, 2.5, "black")
    sim.addBox(2.5, 2, 3.0, 3.5, "black")
    sim.addBox(2.0, 3.5, 3.0, 7, "black")
    # port, name, x, y, th, bounding Xs, bounding Ys, color
    # (optional TK color name):
    sim.addRobot(60000, TkPioneer("RedPioneer",
                                  2, 0.5, -45 * math.pi / 180,
                                  ((.225, .225, -.225, -.225),
                                   (.175, -.175, -.175, .175))))
    # add some sensors:
    sim.robots[0].addDevice(PioneerFrontSonars())
    return sim
