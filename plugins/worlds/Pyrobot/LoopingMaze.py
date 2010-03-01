# World for looping-maze experiment as described in
# section 4.2 of the book "Evolutionary Robotics".

from pyrobot.simulators.pysim import *

def INIT():
    sim = TkSimulator((400,280), (20, 260), 50)
    sim.addBox(0, 0, 7, 4.75)
    sim.addWall(0, 0, 2, 4.75)
    sim.addWall(6, 4.75, 7, 3.5)
    sim.addWall(7, 3.5, 5.9, 1)
    sim.addWall(3.4, 0, 3.9, 1)
    sim.addWall(3.9, 1, 5.9, 1)
    sim.addWall(2.3, 1.5, 2.8, 2.5)
    sim.addWall(2.8, 2.5, 4.5, 2.5)
    sim.addWall(4.5, 2.5, 4.9, 3.25)

    # port, name, x, y, th, bounding Xs, bounding Ys, color
    # (optional TK color name):
    sim.addRobot(60000, TkPioneer("RedPioneer",
                                  1, 1, 5.42,
                                  ((.225, .225, -.225, -.225),
                                   (.175, -.175, -.175, .175)),
                                  "red"))
    # add sonars to the robot
    sim.robots[0].addDevice(Pioneer16Sonars())

    return sim
