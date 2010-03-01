import code
import readline
import atexit
import os
import sys
import signal
from traceback import print_exc as print_exc
from traceback import extract_stack

def _colorize(txt, col="red"):
    """Return colorized text"""
    cols = { 'red':1, 'green':2, 'yellow':3, 'blue':4}
    initcode = '\033[;3'
    endcode  = '\033[0m'
    if type(col) == type(1): 
        return initcode + str(col) + 'm' + txt + endcode
    try: return initcode + str(cols[col]) + 'm' + txt + endcode
    except: return txt

class PyrobotDebugger(code.InteractiveConsole):
    def __init__(self, filename="<console>",
                 histfile=os.path.expanduser("~/.pyrobothist"),
                 frame=None):
        code.InteractiveConsole.__init__(self)
        self.init_history(histfile)
        self.stack = extract_stack()
        self.frames = [frame]
        thisFrame = frame
        while 1:
            try:
                self.frames.append(thisFrame.f_back)
                thisFrame = thisFrame.f_back
            except:
                break
        self.frames.reverse()
        self.frames.append(None)
        self.frames.append(None)
        self.currentPos = -len(self.frames) + 1
        self.lastPos = self.currentPos
        self.locals = self.frames[self.currentPos].f_locals
        self.initDisplay = 0

    def displayTrace(self):
        maxFuncName = 0
        c = 1
        for i in range(-len(self.frames) + 1, -3 + 1):
            a_es, b_es, c_es, d_es = self.stack[i]
            maxFuncName = max(maxFuncName, len(c_es))
        for i in range(-len(self.frames) + 1, -3 + 1):
            a_es, b_es, c_es, d_es = self.stack[i]
            if c_es == '?':
                c_es = '__main__'
            else:
                c_es += '()'
            if self.currentPos + len(self.frames) == c:
                pointer = ">"
            else:
                pointer = " "
            nameFormat = ("%-" + ("%d" % (maxFuncName + 2))) + "s"
            if pointer == ">":
                print _colorize((" %s %2d) "+ nameFormat +" at %s:%s") % (pointer, c, c_es, a_es, b_es),"green")
            else:
                print (" %s %2d) "+ nameFormat +" at %s:%s") % (pointer, c, c_es, a_es, b_es)
            c += 1
        print

    def displayHelp(self):
        print "Commands:", _colorize("up, down, top, bot, help, quit, a frame number, edit,")
        print _colorize("          or any Python expression. <CONTROL+D> to continue.")

    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass
            #atexit.register(self.save_history, histfile)

    def save_history(self, histfile = None):
        if histfile == None:
            histfile=os.path.expanduser("~/.pyrobothist")
        readline.write_history_file(histfile)

    def raw_input(self, prompt):
        if not self.initDisplay or self.currentPos != self.lastPos:
            self.displayTrace()
            self.displayHelp()
            self.initDisplay = 1
            self.lastPos = self.currentPos
        return code.InteractiveConsole.raw_input(self, prompt)

    def push(self, line):
        if line in ["up", "down", "top", "bot"]:
            if line == "up":
                self.currentPos -= 1
            elif line == "down":
                self.currentPos += 1
            elif line == "top":
                self.currentPos = -len(self.frames) + 1
            elif line == "bot":
                self.currentPos = -3
            # ---------------- check and return
            if self.currentPos >= -len(self.frames) + 1 and \
               self.currentPos <= -3:
                self.locals = self.frames[self.currentPos].f_locals
            else:
                self.currentPos = self.lastPos
            return
        if line in map(str, range(len(self.stack))):
            self.currentPos = int(line) - len(self.stack) - 1
            self.locals = self.frames[self.currentPos].f_locals
            return
        if line == "quit":
            sys.exit(1)
        elif line == "help":
            self.displayHelp()
            return
        elif line == "edit":
            a_es, b_es, c_es, d_es = self.stack[self.currentPos]
            fileName = a_es
            lineNumber =  b_es
            os.system("emacs +%s %s &" % (lineNumber, fileName))
            return
        return code.InteractiveConsole.push(self, line)

def Break():
    import inspect
    _handler(None, inspect.currentframe())

def _handler(signum, frame):
    console = PyrobotDebugger(frame=frame)
    console.interact()
    console.save_history()
    print _colorize("\nContinuing...", "yellow")
signal.signal(signal.SIGTSTP, _handler) # suspend

print _colorize("Pyrobot debugger is installed. Press <CONTROL+Z> to activate.")
