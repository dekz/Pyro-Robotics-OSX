# pyrobot.gui.console
#
# This is a text output facility for the xrcl base.
# it is modeled after the normal syslog(3) 
#
# It is pretty simple.
#

#isdale: July 10, 2006 added logging as well as print
import logging

#verbosity levels
FATAL   = 0
ERROR   = 1
WARNING = 2
INFO    = 3
DEBUG   = 4

#verbosity strings
verbosityMessage = ["fatal","error","warning","info","debug"]

verbosityLevel = 4
USE_COLOR = 0

def colorize(txt, col):
    """Return colorized text"""
    cols = { 'fatal':1, 'info':2, 'warning':3, 'debug':4, "error":1}
    # fatal,error - red, info - green, warning - yellow, debug - blue
    initcode = '\033[;3'
    endcode  = '\033[0m'
    if type(col) == type(1): 
        return initcode + str(col) + 'm' + txt + endcode
    try: return initcode + str(cols[col]) + 'm' + txt + endcode
    except: return txt

def log(level, message):
    if level <= verbosityLevel:
        if not USE_COLOR:
            print message
        else:
            print colorize(message, level)
    if level == 'fatal' or level == FATAL:
        # isdale: fixed 'fatal' vs FATAL check
        logging.critical(message)
        raise message
    if level == ERROR:
        logging.error(message)
    elif level == WARNING:
        logging.warn(message)
    elif level == DEBUG:
        logging.debug(message)
    else:
        logging.info(message)

def logDebug(message):
    log(DEBUG, message)
    
def logInfo(message):
    log(INFO, message)
    
def logWarn(message):
    log(WARNING, message)
    
def logError(message):
    log(ERROR, message)
    
def logFatal(message):
    log(FATAL, message)
    
def setVerbosity(level):
    verbosityLevel = level

