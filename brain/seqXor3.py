# Test of Elman-style XOR in time. 

from pyrobot.brain.conx import *

low, high = 0.2, 0.8

def xor(a,b):
    """ XOR for floating point numbers """
    if a < .5 and b < .5: return low
    if a > .5 and b > .5: return low
    return high

def randVal():
    """ Random 0 or 1, represented as 0.2 and 0.8, respectively. """
    if random.random() < .5:
        return low
    else:
        return high

if __name__ == '__main__':
    print "Sequential XOR modeled after Elman's experiment ..........."
    print "The network will see a random 1 or 0, followed by another"
    print "random 1 or 0. The target on the first number is 0.5, and "
    print "the target on the second is the XOR of the two numbers."
    n = Network()
    size = 20
    n.addLayer("input", 1)
    n.addLayer("context", size)
    n.addLayer("hidden", size)
    n.addLayer("output", 1)
    
    n.connect("input", "hidden")
    n.connect("context", "hidden")
    n.connect("hidden", "output")

    n.setEpsilon(0.1)
    n.setMomentum(0.9)
    n.setBatch(0)
    n.setTolerance(.25)
    n.setReportRate(100)
    n.setLearning(1)
    n.setInteractive(1)

    lastContext = [.5] * size
    lastTarget = 0.5
    count = 1
    sweep = 1
    correct_all = 0
    total_all = 0
    tss_all = 0.0
    while True:
        value1 = randVal()
        value2 = randVal()
        target = xor(value1, value2)
        lastContext = [.5] * size
        n.step(input=[target], context=lastContext, output=[value1])
        lastContext = n["hidden"].getActivations()
        n.step(input=[value1], context=lastContext, output=[value2])
        lastContext = n["hidden"].getActivations()
        tss, correct, total, perr = n.step(input=[value2], context=lastContext, output=[target])
        lastTarget = target
        correct_all += correct
        tss_all += tss
        total_all += total
        if (count % n.reportRate) == 0:
            percentage = float(correct_all)/float(total_all)
            print "Epoch: %5d, steps: %5d, error: %7.3f, Correct: %3d%%" % \
                (sweep, count, tss_all, int(percentage * 100))
            if percentage > .9:
                break
            correct_all = 0
            total_all = 0
            tss_all = 0.0
            sweep += 1
        count += 1
        
    print "Training complete."
    n.setInteractive(1)
    n.setLearning(0)
