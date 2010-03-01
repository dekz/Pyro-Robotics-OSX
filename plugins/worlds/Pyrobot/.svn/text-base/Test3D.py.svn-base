from pyrobot.simulators.pysim3d import *

def INIT():
    # (width, height), (offset x, offset y), scale:
    sim = Tk3DSimulator((446,491),(21,451),80.517190)
    # x1, y1, x2, y2 in meters:
    sim.addBox(0, 0, 5, 5)
    sim.addBox(0, 4, 1, 5, "blue", wallcolor="blue")
    sim.addBox(2.5, 0, 2.6, 2.5, "green", wallcolor="green")
    sim.addBox(2.5, 2.5, 3.9, 2.6, "green", wallcolor="green")
    # port, name, x, y, th, bounding Xs, bounding Ys, color
    # (optional TK color name):
    sim.addRobot(60000, TkPioneer("RedPioneer",
                                  .5, 2.5, 0.00,
                                  ((.225, .225, -.225, -.225),
                                   (.175, -.175, -.175, .175))))
    # add some sensors:
    # sim.robots[0].addDevice(PioneerFrontSonars()) # for 8 front sonar
    sim.robots[0].addDevice(Pioneer16Sonars()) # for full 360 sonar
    sim.robots[0].addDevice(PioneerFrontLightSensors())
    # x, y relative to body center (beyond bounding box):
    sim.robots[0].addDevice(BulbDevice(0.226, 0)) # pose x, pose y
    # width, height, startAngle, stopAngle, pose x, pose y, pose thr:
    cam = Camera(60, 40, 0, 120, 0, 0, 0)
    sim.robots[0].addDevice(cam)
    sim.robots[0].addDevice(PTZ(cam))
    return sim
