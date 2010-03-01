__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision$"

from pyrobot.brain.conx import *
import random

def xor(a,b):
    if a and b: return 0
    if not a and not b: return 0
    return 1

def randomBit():
    return int(random.random()*2)

def sequentialXor(n, limit):
    step = 1
    totalErr1 = 0
    totalErr2 = 0
    totalErr3 = 0
    current = randomBit()
    n.setContext()
    while step < limit:
        if n.interactive:
            print "***** Step %dA *****" % step
        n.getLayer('input').copyActivations([current])
        next = randomBit()
        n.getLayer('output').copyTargets([next])
        (error, correct, total, pcorrect) = n.step()
        n.getLayer('context').copyActivations(n.getLayer('hidden').activation)
        err1 = error
        if n.interactive:
            print "***** Step %dB *****" % step
        n.getLayer('input').copyActivations([next])
        result = xor(current,next)
        n.getLayer('output').copyTargets([result])
        (error, correct, count, pcorrect) = n.step()
        n.getLayer('context').copyActivations(n.getLayer('hidden').activation)
        err2 = error
        if n.interactive:
            print "***** Step %dC *****" % step
        n.getLayer('input').copyActivations([result])
        current = randomBit()
        n.getLayer('output').copyTargets([current])
        (error, correct, count, pcorrect) = n.step()
        n.getLayer('context').copyActivations(n.getLayer('hidden').activation)
        err3 = error
        totalErr1 = totalErr1 + err1
        totalErr2 = totalErr2 + err2
        totalErr3 = totalErr3 + err3
        if step % n.reportRate == 0:
            print "Epoch: #%6d Average errors = %.3f %.3f %.3f" \
                  % (step, totalErr1/step, totalErr2/step, totalErr3/step)
        step = step + 1
    print "Epoch: #%6d Total Average errors = %.3f %.3f %.3f" \
          % (step, totalErr1/step, totalErr2/step, totalErr3/step)
    
    
if __name__ == '__main__':
    print "Sequential XOR modeled after Elman's experiment ..........."
    print "The network will see a random 1 or 0, followed by another"
    print "random 1 or 0, followed by their XOR value.  Therefore only"
    print "the second output is predictable so that error should be lower."
    n = SRN()
    n.addSRNLayers(1,5,1)
    n.setEpsilon(0.25)
    n.setMomentum(0.1)
    n.setBatch(0)
    n.setSequenceType("epoch")
    n.setReportRate(100)
    n.setLayerVerification(0) # turn off automatic error checking
    sequentialXor(n, 100000)
    print "Training complete.  Test error again....................."
    n.setLearning(0)
    sequentialXor(n,1000)
