import code, readline, atexit, os, sys
from pyrobot.gui import gui
from pyrobot.system import version

class TTYGui(code.InteractiveConsole, gui):
    def __init__(self, filename="<console>",
                 histfile=os.path.expanduser("~/.pyrobothist"),
                 engine=None):
        code.InteractiveConsole.__init__(self)
        self.init_history(histfile)
        gui.__init__(self, "TTY Gui", engine = engine)

    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass

    def save_history(self, histfile = None):
        if histfile == None:
            histfile=os.path.expanduser("~/.pyrobothist")
        readline.write_history_file(histfile)

    def raw_input(self, prompt):
        # init business
        if self.engine.gui.watcher:
            self.engine.gui.watcher.update(self.engine.gui.environment)
        return code.InteractiveConsole.raw_input(self, prompt)

    def push(self, line):
        retval = self.processCommand(line)
        if retval == 1:
            sys.exit(0)
        return
    # if you want python to process:
        #return code.InteractiveConsole.push(self, line)

    def run(self, evalcommand = []):
        sys.ps1 = "pyrobot> "
        done = 0
        while len(evalcommand) > 0 and done == 0:
            print evalcommand[0],
            retval = evalcommand[0].strip()
            evalcommand = evalcommand[1:]
            done = self.processCommand(retval)
        banner=("=========================================================\n"+
                "Pyrobot, Python Robotics, (c) 2005, D.S. Blank\n" +
                "http://PyroRobotics.org\n" +
                "Version " + version() + "\n" + 
                "=========================================================")
        if not done:
            self.interact(banner=banner)
        self.save_history()

if __name__ == "__main__":
    console = TTYGui()
    console.run()
