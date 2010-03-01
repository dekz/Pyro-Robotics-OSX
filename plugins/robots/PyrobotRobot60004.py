from pyrobot.robot.symbolic import TCPRobot

def INIT():
	robot = TCPRobot("localhost", 60004)
	return robot

