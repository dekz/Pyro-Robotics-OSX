config = 0
gui    = 0
debug  = 0

def ask(title, qlist):
    """
    A little function to get info from the user.

    May be redefined for other GUIs.
    """
    print title
    retval = {"ok": 1}
    for (name, value) in qlist:
        print "%s [%s]: " % (name, value),
        retval[name] = raw_input()
        if retval[name] == "":
            retval[name] = value
    return retval

