"""
A PyrobotSimulator world. A room with one obstacle and
a small inner room.

(c) 2005, PyroRobotics.org. Licensed under the GNU GPL.
"""

from pyrobot.simulators.pysim import *

def INIT():
    # (width, height), (offset x, offset y), scale:
    sim = TkSimulator((600,600), (0,600), 100)  
    #sim = TkSimulator((446,491),(21,451),80.517190)

    # x1, y1, x2, y2 in meters:
    sim.addBox(0, 0, 6, 6)

    # (x, y) meters, brightness usually 1 (1 meter radius):
    sim.addLight(3, 3, 0.1, "red")
 
    # port, name, x, y, th, bounding Xs, bounding Ys, color
    # (optional TK color name):
    sim.addRobot(60000, TkPioneer("RedPioneer",
                                  3, 0.5, 0.00,
                                  ((.225, .225, -.225, -.225),
                                   (.175, -.175, -.175, .175))))
    # add some sensors:
    sim.robots[0].addDevice(PioneerFrontSonars())
    sim.robots[0].addDevice(PioneerFrontLightSensors())
    return sim



##   # (x, y) meters, brightness usually 1 (1 meter radius):
##    sim.addLight(1, 2, 0.1, "green")
##
##    # (x, y) meters, brightness usually 1 (1 meter radius):
##    sim.addLight(4, 1, 0.1, "green")
##
##    # (x, y) meters, brightness usually 1 (1 meter radius):
##    sim.addLight(2, 4, 0.1, "green")

