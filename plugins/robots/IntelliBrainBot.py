# Defines IntelliBrainBot, a subclass of robot

from pyrobot.robot.intellibrain import *

def INIT():
    # For serial connected IntelliBrainBot:
    return IntelliBrainBot(port = "/dev/ttyUSB0",
                        rate = 38400,
                        subtype = "IntelliBrainBot")
