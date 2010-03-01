import string
import sys
from pyrobot.system.version import version

def about():
    print "-------------------------------------------------------------"
    print "Pyrobot - Python Robotics"
    print "Version:", version()
    print "See: http://PyroRobotics.org"
    print "(c) 2006, PyroRobotics.org. Released under the GNU GPL"
    print "-------------------------------------------------------------"

def usage():
    print "-------------------------------------------------------------"
    print " Pyrobot Command Line Arguments:"
    print "-------------------------------------------------------------"
    print "  -h                     show this help"
    print "  -a ARGUMENTS           user args; available as string engine.args"
    print "  -b BRAIN               name of brain.py file to load"
    print "  -c CONFIGFILE          name of server config to load"
    print "  -d DEVICE[,...]        names of devices (files or names)"
    print "  -g tty | tk | simple   type of GUI to use"
    print "  -i INIFILE             name of init file to load, or 'None'"
    print "  -p CPULIST             list of integer for CPU affinity taskset"
    print "  -r ROBOT               name of robot.py file to load"
    print "  -s SIMULATOR           name of simulator to run"
    print "  -w WORLDFILE           name of simulator world to load"
    print "  -e \"string\"            eval string of ; separated commands"
    print ""

def help():
    print "-------------------------------------------------------------"
    print "Pyrobot GUI Command line editing commands:"
    print "-------------------------------------------------------------"
    print "  Control+p or UpArrow        previous line"
    print "  Control+n or DownArrow      next line"
    print "  Control+a or Home           beginning of line"
    print "  Control+e or End            end of line"
    print "  Control+f or RightArrow     forward one character"
    print "  Control+b or LeftArrow      back one character"
    print "  TAB                         show command completions"
    print "-------------------------------------------------------------"
    print "Pyrobot TTY and GUI commands:"
    print "-------------------------------------------------------------"
    print "  <command>                   execute <command> in Python"
    print "  <exp>                       print <exp> in Python"
    print "  $ <command>                 shell <command>, print in Pyro"
    print "  $$ <command> &              shell <command>, print in Terminal"
    print "  edit                        edit the brain file"
    print "  help                        this help message"
    print "  info                        show brain and robot info"
    print "  load brain                  load a brain file"
    print "  load robot                  load a robot file"
    print "  load simulator | server     load a simulator or server"
    print "  quit | exit | bye           exit from Pyrobot"
    print "  reload                      reload the brain"
    print "  run                         start brain running"
    print "  stop                        stop brain and robot"
    print "  !                           show command history"
    print "  ! N                         rerun Nth command from history"
    print "  ! N1 - N2                   rerun N1 through N2 commands"
    print "  ! VAL                       search for commands containing VAL"
    print "  !!                          rerun last command from history"
    print "  watch EXP                   display EXP"
    print "  unwatch EXP                 remove display of EXP"
    print "  view EXP                    object tree viewer of EXP"
    print ""

def file_exists(file_name):
    from posixpath import exists
    if type(file_name) == type(""):
        if len(file_name) == 0:
            return 0
        else:
            return exists(file_name)
    else:
        raise AttributeError, "filename nust be a string"
    
def loadINIT(filename, engine=0, redo=0, brain=0, args=None):
    path = filename.split("/")
    modulefile = path.pop() # module name
    module = modulefile.split(".")[0]
    search = string.join(path, "/")
    oldpath = sys.path[:] # copy
    sys.path.insert(0, search)
    print "Attempting to import '%s'..." % module 
    exec("import " + module + " as userspace")
    reload(userspace)
    print "Loaded '%s'!" % userspace.__file__
    sys.path = oldpath
    try:
        userspace.INIT
    except AttributeError:
        raise ImportError, "your program needs an INIT() function"
    if brain is 0:
        if engine is 0:
            retval = userspace.INIT()
            return retval
        else:
            if args:
                retval = userspace.INIT(engine, args)
                return retval
            else:
                retval = userspace.INIT(engine)
                return retval
    else:
        retval = userspace.INIT(engine, brain)
        return retval

