# Test of Elman-style XOR in time. 

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision: 2554 $"

from pyrobot.brain.conx import *

def xor(a,b):
    """ XOR for floating point numbers """
    if a < .5 and b < .5: return 0.2
    if a > .5 and b > .5: return 0.2
    return 0.8

def randVal():
    """ Random 0 or 1, represented as 0.2 and 0.8, respectively. """
    if random.random() < .5:
        return .2
    else:
        return .8

def sequentialXorSweeps(n, runLength, maxtimes = 1000):
    """
    Given a network, length of random sequence, and max steps to try,
    this function will compute XOR for every last and current pair.
    """
    step = 0
    totalError, totalCorrect, totalCount = 0.0, 0.0, 1.0
    while totalCorrect/totalCount < 1.0 and step < maxtimes:
        ins = []
        outs = []
        last = randVal() # to get started
        for t in range(runLength):
            current = randVal()
            predicted = xor(last, current)
            ins.append([current])
            outs.append([predicted])
            last = current
        n.setInputs( ins )
        n.setOutputs( outs )
        (tssError, totalCorrect, totalCount, totalPCorrect) = n.sweep()
        totalError += tssError
        if step % n.reportRate == 0:
            print " Step: #%6d, Error = %.4f Correct = %d" % (step, tssError, totalCorrect)
        step = step + 1
    print "Total error  : %.4f" % totalError
    
if __name__ == '__main__':
    print "Sequential XOR modeled after Elman's experiment ..........."
    print "The network will see a random 1 or 0, followed by another"
    print "random 1 or 0, followed by their XOR value.  Therefore only"
    print "the second output is predictable."
    n = SRN()
    n.addSRNLayers(1,5,1)
    n.setSequenceType("random-continuous")
    n.setEpsilon(0.2)
    n.setMomentum(0.1)
    n.setBatch(0)
    n.setTolerance(.25)
    n.setReportRate(1)
    sequentialXorSweeps(n, 100)
    print "Training complete.  Test error again....................."
    n.setLearning(0)
    n.setInteractive(1)
    sequentialXorSweeps(n, 10, 1)
    n.setInteractive(0)
    sequentialXorSweeps(n, 1000, 1)
