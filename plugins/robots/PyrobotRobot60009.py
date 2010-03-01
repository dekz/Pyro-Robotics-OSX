from pyrobot.robot.symbolic import TCPRobot

def INIT():
	robot = TCPRobot("localhost", 60009)
	return robot

