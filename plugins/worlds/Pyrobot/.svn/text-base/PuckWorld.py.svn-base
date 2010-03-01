from pyrobot.simulators.pysim import *
import random

def INIT():

    # (width, height), (offset x, offset y), scale in pixels/meter:
    sim = TkSimulator((650, 650), (20,630), 60.0)
    # x1, y1, x2, y2 in meters:
    sim.addBox(0, 0, 10, 10)
    # args: name, x, y, th, bounding Xs, bounding Ys, color
    pioneer = TkPioneer("Pioneer1", 5, 5, 5.5,
                        ((.225, .225, -.225, -.225),
                         (.175, -.175, -.175, .175)), "green")
    sim.addRobot(60000, pioneer)

    print 'got here'
    # args: width, height, pan, zoom angle, x, y, thr
    cam = Camera(80, 40, 0, 120, 0, 0, 0)
    print 'created a Camera object'
    sim.robots[0].addDevice(cam)
    sim.robots[0].addDevice(PTZ(cam))
    sim.robots[0].addDevice(Gripper())

    # distribute pucks randomly
    numpucks = 5
    for i in range(1, numpucks+1):
        x = random.uniform(1, 9)
        y = random.uniform(1, 9)
        puck = TkPuck("Puck%d" % i, x, y, 0,
                      ((.05, .05, -.05, -.05),
                       (.05, -.05, -.05, .05)), "red")
        sim.addRobot(None, puck)
    return sim
    
