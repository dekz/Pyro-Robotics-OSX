from pyrobot.robot.player import PlayerRobot
from pyrobot.system.share import ask

# This should work for real and simulated Player-based robots

def INIT():
    retval = ask("Please enter the Player Data",
                 (("Port", "6665"),
                  ("Host", "localhost"),
                  ("Start devices?", "yes")))
    if retval["ok"]:
        startDevices = 1
        if retval["Start devices?"] != "yes":
            startDevices = 0
        return PlayerRobot("Player6665",
                           port = int(retval["Port"]),
                           hostname = retval["Host"],
                           startDevices=startDevices)
    else:
        raise "Cancelled!"


