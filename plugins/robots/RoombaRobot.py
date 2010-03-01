# Defines Roomba, a subclass of robot

from pyrobot.robot.roomba import *
from pyrobot.system.share import ask

def INIT():
    # For serial connected Roomba:
    dict = ask("What serial port is the Roomba connected to?",
               [("Serial Port", "/dev/rfcomm0"),
                ("Transfer rate", "57600")])
    return Roomba(port = dict["Serial Port"],
                  rate = int(dict["Transfer rate"]),
                  subtype = "Roomba")
