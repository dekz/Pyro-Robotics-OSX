# Uses RobocupRobot, a subclass of robot

from pyrobot.robot.robocup import *

def INIT():
    # Make a team of 11 robots:
    list = [0] * 11
    for x in range(11):
        list[x] = RobocupRobot(name = "TeamA", goalie = (x == 0))
    # store the list on the first one
    list[0].team = list
    # put the goalie in the box
    list[0].simulation[0].setPose(-50, 0)
    # return the first one
    return list[0]
