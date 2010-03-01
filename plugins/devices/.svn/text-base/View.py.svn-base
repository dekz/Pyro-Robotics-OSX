from pyrobot.gui.plot.simple import SimplePlot
from pyrobot.system.share import ask

def INIT(robot):
    retval = ask("Please enter what sensor group you would like to view (all, left, right, front-right, etc.)",
                 (("Sensor group", ""),
                  ))
    if retval["ok"]:
        return {"view": SimplePlot(robot, retval["Sensor group"])}
    else:
        raise "Cancelled!"
