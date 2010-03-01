from pyrobot.system.share import ask

def INIT(robot):
    retval = ask("Please enter the name of a device (ptz, camera, etc.)",
                 (("Device", ""),))
    if retval["ok"]:
        return [retval["Device"]]
    else:
        raise "Cancelled!"


