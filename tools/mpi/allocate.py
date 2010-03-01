"""
Classes to allow easy allocation of tasks to remote nodes.

NOTES:

1. node 0 doesn't get to do anything but deal out the tasks
2. this uses pickle across the wire, so pickle better work!
3. tasks better have a run method!
"""

import sys, random, time

try:
    import mpi
except:
    raise ImportError, "must run under mpi!"

class TestTask:
    def run(self):
        print "DEBUG: Starting... "
        time.sleep(random.random() * 5)
        print "DEBUG: done!"

def sampleTaskList(size):
    return [TestTask() for x in range(size)]

class TaskWrapper:
    def __init__(self, *args, **keywords):
        self.args = args
        self.keywords = keywords
    def run(self):
        e = Experiment(*self.args, **self.keywords)
        return e.run()

class TaskAllocator:
    """ Generic class to deal out tasks. """
    def __init__(self, taskList):
        self.taskList = taskList

    def run(self):
        for task in self.taskList:
            data, message = mpi.recv()
            source = message.source
            mpi.send( task, source)

class TaskHandler:
    """ Generic class to handle tasks. Tasks need a run method. """
    def run(self):
        while 1:
            print >> sys.stderr, "======= Node #%d waiting..." % mpi.rank
            try:
                mpi.send("request", 0)
                task, message = mpi.recv(0)
                print >> sys.stderr, "Node #%d received task! ---------------------------" % mpi.rank
                task.run()
            except:
                print >> sys.stderr, "======= Node %d done!" % mpi.rank
                break

if __name__ == '__main__':
    if mpi.rank == 0:
        taskListSize = int(sys.argv[1])
        taskList = sampleTaskList(taskListSize)
        a = TaskAllocator(taskList)
        a.run()
##         from pyrobot.brain.conx import *
##         n = Network()
##         n.addThreeLayers(2, 2, 1)
##         n.setInputs([[0.0, 0.0],
##                      [0.0, 1.0],
##                      [1.0, 0.0],
##                      [1.0, 1.0]
##                      ])
##         n.setTargets([[0.0],
##                       [1.0],
##                       [1.0],
##                       [0.0]
##                       ])
##         n.setBatch(1)
##         a = TaskAllocator([n] * 10)
##         a.run()
    else:
        th = TaskHandler()
        th.run()
