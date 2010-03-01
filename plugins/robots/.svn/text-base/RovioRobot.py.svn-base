from pyrobot.robot.rovio import RovioRobot
from pyrobot.system.share import ask

def INIT():
    # replace "aibo" with your dog's IP or DNS name
    dict = ask("Which Rovio do you wish to connect to?",
               [("Rovio IP/URL", "")])
    return RovioRobot(dict["Rovio IP/URL"]) 
