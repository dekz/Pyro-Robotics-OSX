"""
The basic brain class. All brains derive from these classes.

(c) 2005, PyrobRobotics.org. Licenced under the GNU GPL.
"""

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision: 2569 $"

import threading, time, operator, copy
import pyrobot.gui.console

def avg(myList):
    """Returns the arithemetic average of a sequences of numbers."""
    if len(myList) < 1:
        raise ValueError, "avg() arg is an empty sequence"
    sum = reduce(operator.add, myList)
    return sum / float(len(myList))

def middle(myList):
    """Returns the middle (len/2) value of a sequences of numbers."""
    # If len == even, then next one
    if len(myList) < 1:
        raise ValueError, "middle() arg is an empty sequence"
    return myList[len(myList)/2]

def median(myList):
    """Returns the middle (len/s) value of a sorted copy of a sequence."""
    # If len == even, then next one
    if len(myList) < 1:
        raise ValueError, "median() arg is an empty sequence"
    tmpList = copy.copy(myList)
    tmpList.sort()
    return tmpList[len(tmpList)/2]

class Brain(threading.Thread):
    """
    The Brain is the basis for all brains.
    """
    def __init__(self, name = 'brain', engine = 0, **kwargs):
        """
        Constructor for Brain class.

        You should set the engine, if nothing else.
        """
        threading.Thread.__init__(self)
        self.debug = 0
        self.stack = [] # used in brains with states (BehaviorBasedBrain and FSMBrain)
        self.stepCount = 0
        self.lastRun = time.time() # seconds
        self.name = name
        self.engine = engine
        if engine is not 0:
            self.robot = engine.robot
	self.thread = 0
        self.condition = threading.Condition()
        self.needToStop = 1
        self.needToQuit = 0
        self.needToStep = 0
        self.pauseTime = 0.1 # time to sleep() in main loop. 0.1 means brain step() runs at max 10/sec
        if self.robot != 0:
            self.robot.localize()
        # user setup:
        self.profilePerformance = 0
        self.profileCount = 0
        self.setup(**kwargs)
        # start the thread:
        self.start()

    # wrappers here to talk to default robot:
    def move(self, *args):
        """Short-cut to call the robot's move method."""
        return self.robot.move(*args)
    def translate(self, *args):
        """Short-cut to call the robot's translate method."""
        return self.robot.translate(*args)
    def rotate(self, *args):
        """Short-cut to call the robot's rotate method."""
        return self.robot.rotate(*args)
    def stop(self):
        """Short-cut to call the robot's stop method."""
        return self.robot.stop()
    def startDevice(self, *args, **keywords):
        """Short-cut to call the robot's startDevice method."""
        return self.robot.startDevice(*args, **keywords)
    def removeDevice(self, *args, **keywords):
        """Short-cut to call the robot's removeDevice method."""
        return self.robot.removeDevice(*args, **keywords)
    def update(self):
        """Short-cut to call the robot's update method."""
        return self.robot.update()
    def motors(self, *args):
        """Short-cut to call the robot's motors method."""
        return self.robot.motors(*args)
    def getDevice(self, *args):
        """Short-cut to call the robot's getDevice method."""
        return self.robot.getDevice(*args)
    def hasA(self, *args):
        """Short-cut to call the robot's hasA method."""
        return self.robot.hasA(*args)
    def requires(self, *args):
        """Short-cut to call the robot's requires method."""
        return self.robot.requires(*args)
    def _draw(self, options, renderer):
        """Internal draw method."""
        pass
    def getEngine(self):
        """Returns the engine property."""
        return self.engine
    def quit(self):
        """Signals the thread that we need to stop running."""
        self.needToStop = 0
        self.needToQuit = 1
        if self.engine and self.engine.gui:
            self.engine.gui.done = 1
    def run(self):
        """
        Runs the brain/thread.

        self.pauseTime determines how many times a second it is called.
        """
        self.couldBeMoving = 0
        while self.needToQuit is not 1 and self.isAlive():
            #print "Acquire ----------------------------"
            count = 0
            while self.isAlive() and self.condition.acquire(0) == 0:
                #print "r",
                count += 1
                if count > 20:
                    return
            
            if self.needToQuit:
                #print "release()"
                self.condition.release()
                #print "Return  ----------------------------"
                return
            elif self.needToStep > 0:
                self.needToStep -= 1 #protectedvariable
                self.needToStop = 1 #will be picked up next pass
            elif self.needToStop:
                #print "wait()"
                self.condition.wait(.25) # FIX: .5?
                #print "release()"
                self.condition.release()
                if self.couldBeMoving:
                    self.couldBeMoving = 0
                    self.robot.move(0, 0)
                continue #check for quit before we step
            
            #print "step()"
            self.robot.update()
            self.step()
            self.stepCount += 1
            self.couldBeMoving = 1
            time.sleep(self.pauseTime)
            if self.profilePerformance == 2:
                self.profileCount += 1
                self.profileTotalTime += time.time() - self.lastRun
                if self.profileCount % 100 == 0:
                    print "Profile: brain running at %.3f steps/second" % (float(self.profileCount) / self.profileTotalTime)
                    self.profileTotalTime = 0.0
                    self.profileCount = 0
            if self.profilePerformance == 1:
                self.profileTotalTime = 0.0
                self.profilePerformance = 2
            self.lastRun = time.time() # seconds
            #print "release()"
            self.condition.release()
            #print "Return  ----------------------------"
            #print self.needToStep
        #print "End of run!"
            
    def pleaseQuit(self):
        """Signals the thread that we need to stop running."""
        self.needToQuit = 1
        
    def pleaseStep(self):
        """Signals the thread to make a step."""
        count = 0
        while self.isAlive() and self.condition.acquire(0) == 0:
            count += 1
            if count > 20:
                return
        self.needToStep += 1 #protected variable
        self.condition.notify()
        self.condition.release()
        self.pleaseRun()
        
    def pleaseStop(self):
        """Signals the thread that we need to stop stepping the robot."""
        self.needToStop = 1
        
    def pleaseRun(self, callback = 0):
        """Signals the thread that we need to start stepping."""
        if not self.isAlive():
            pyrobot.gui.console.log(pyrobot.gui.console.WARNING,"Brain thread is not alive but request to run was made.");
        self.needToStop = 0
        if callback != 0:
            callback()
		
    def step(self):
        """This is the method that does all of the work."""
        print "need to override pyrobot.brain.Brain.step()."

    def setup(self, **kwargs):
        """
        User init method. Call this instead of overloading __init__.
        """
        pass

    def makeWindow(self):
        """Method that creates a window; seen under Brain -> Watch."""
        import Tkinter
        self.window = Tkinter.Toplevel()
        self.window.wm_title("Brain View")
        self.canvas = Tkinter.Canvas(self.window,width=550,height=300)
        self.canvas.pack()

    def redraw(self):
        """Redraws the brain watch window."""
        if getattr(self, 'canvas', None) is not None:
            self.canvas.create_text(100,130, tags='pie',fill='black', text = "This Brain needs a redraw method!")

    def destroy(self):
        """
        Method to override if you create objects (such as devices).
        """
        pass

