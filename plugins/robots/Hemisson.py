# Uses KheperaRobot, a subclass of robot, for the Hemisson

from pyrobot.robot.khepera import *
from pyrobot.system.share import ask

def INIT():
    retval = ask("Please enter the Hemisson Data",
                 (("Port", "6665"),
                  ("Baud", 115200)))
    if retval["ok"]:
        # For serial connected Hemisson:
        return KheperaRobot(port = retval["Port"],
                            rate = int(retval["Baud"]),
                            subtype = "Hemisson")
    else:
        raise "Cancelled!" 
