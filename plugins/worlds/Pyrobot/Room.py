"""
A PyrobotSimulator world. A large room with a robot

(c) 2005, PyroRobotics.org. Licensed under the GNU GPL.
"""

from pyrobot.simulators.pysim import *
import math

def INIT():
    # (width, height), (offset x, offset y), scale:
    sim = TkSimulator((357,486), (38,397), 57.838547)
    # x1, y1, x2, y2 in meters:
    #sim.addBox(0, 0, 5, 5)
    x, y = 2, 2
    length = 1.0
    parts = 20
    ds = (math.pi * 2)/parts
    for i in range(0, 360, 360/parts):
        d = i * math.pi/180
        print "d:", d, "d+ds:", d + ds
        x1, y1 = x + math.cos(d) * length, y + math.sin(d) * length
        x2, y2 = x + math.cos(d + ds) * length, y + math.sin(d + ds) * length
        print "adding wall:", x1, y1, x2, y2
        sim.addWall(x1, y1, x2, y2)

    # port, name, x, y, th, bounding Xs, bounding Ys, color
    # (optional TK color name):
    sim.addRobot(60000, TkPioneer("RedPioneer",
                                  2.0, 2.0, 6.28,
                                  ((.225, .225, -.225, -.225),
                                   (.175, -.175, -.175, .175)),
                                  "red"))
    # add some sensors:
    sim.robots[0].addDevice(Pioneer16Sonars())
    return sim
