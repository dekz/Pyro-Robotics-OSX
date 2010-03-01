from pyrobot.simulators.pysim import *
import random

def overlaps(x, y, walls):
    buffer = 0.1
    for (x1, y1, x2, y2, color) in walls:
        if x1-buffer <= x <= x2+buffer and y1-buffer <= y <= y2+buffer:
            return True
    return False

def INIT():
    # (width, height), (offset x, offset y), scale in pixels/meter:
    sim = TkSimulator((650, 650), (20,630), 60.0)
    # x1, y1, x2, y2 in meters:
    sim.addBox(0, 0, 10, 10)
    # args: name, x, y, th, bounding Xs, bounding Ys, color
    pioneer1 = TkPioneer("Red Pioneer", 5, 5, 5.5,
                         ((.225, .225, -.225, -.225),
                          (.175, -.175, -.175, .175)), "red")
    sim.addRobot(60000, pioneer1)
#     pioneer2 = TkPioneer("Green Pioneer", 3, 3, 1,
#                          ((.225, .225, -.225, -.225),
#                           (.175, -.175, -.175, .175)), "green")
#     sim.addRobot(60001, pioneer2)

    # configure red robot
    # add camera w/PTZ
    cam1 = Camera(80, 40, 0, 120, 0, 0, 0) # width, height, pan, zoom angle, x, y, thr
    sim.robots[0].addDevice(cam1)
    sim.robots[0].addDevice(PTZ(cam1))
    # add gripper
    sim.robots[0].addDevice(Gripper())
    # add 16 sonars
    sim.robots[0].addDevice(Pioneer16Sonars())
    # add front light sensors
    sim.robots[0].addDevice(PioneerFrontLightSensors())

#     # configure green robot
#     # add camera w/PTZ
#     cam2 = Camera(80, 40, 0, 120, 0, 0, 0)
#     sim.robots[1].addDevice(cam2)
#     sim.robots[1].addDevice(PTZ(cam2))
#     # add gripper
#     sim.robots[1].addDevice(Gripper())

    # add the walls
    walls = [(7.5, 1.5, 8, 8.5, "blue"),
#             (1.5, 5, 3, 7.5, "magenta")
             ]
    for (x1, y1, x2, y2, color) in walls:
        sim.addBox(x1, y1, x2, y2, color, wallcolor=color)

    # add a light
    sim.addLight(2, 2, 1.9) # (x, y) meters, brightness usually 1 (1 meter radius)

    # add red pucks at random positions
    numpucks = 10
    for i in range(1, numpucks+1):
        x = random.uniform(0.5, 9.5)
        y = random.uniform(0.5, 9.5)
        # avoid putting puck inside a wall
        while overlaps(x, y, walls):
            x = random.uniform(0.5, 9.5)
            y = random.uniform(0.5, 9.5)
        puck = TkPuck("Puck%d" % i, x, y, 0,
                      ((.05, .05, -.05, -.05),
                       (.05, -.05, -.05, .05)), "red")
        sim.addRobot(None, puck)
    
    return sim
