"""
A PyrobotSimulator world. A large room with two robots and
two lights.

(c) 2005, PyroRobotics.org. Licensed under the GNU GPL.
"""

from pyrobot.simulators.pysim import *

def INIT():
    # (width, height), (offset x, offset y), scale:
    sim = TkSimulator((445,496),(26,426),39.911318)
    # x1, y1, x2, y2 in meters:
    sim.addBox(0, 0, 10, 10)
    # port, name, x, y, th, bounding Xs, bounding Ys, color
    # (optional TK color name):
    sim.addRobot(60000, TkPioneer("Pioneer1",
                                  5.60, 5.59, 5.53,
                                  ((.225, .225, -.225, -.225),
                                   (.175, -.175, -.175, .175)),
                                  "green"))
    # add some sensors:
    # x, y relative to body center (beyond bounding box):
    sim.robots[0].addDevice(PioneerFrontSonars())
    cam = Camera(40, 40, 0, 120, 0, 0, 0)
    sim.robots[0].addDevice(cam)
    sim.robots[0].addDevice( PTZ(cam) )
    sim.robots[0].addDevice(Gripper())
    sim.addRobot(None, TkPuck("Puck1", 6.28, 6.34, 0, ((.05, .05, -.05, -.05), (.05, -.05, -.05, .05)), "purple"))
    sim.addRobot(None, TkPuck("Puck2", 6.47, 6.47, 0, ((.05, .05, -.05, -.05), (.05, -.05, -.05, .05)), "blue"))
    sim.addRobot(None, TkPuck("Puck3", 7.0, 7.0, 0, ((.05, .05, -.05, -.05), (.05, -.05, -.05, .05)), "red"))
        
    return sim
