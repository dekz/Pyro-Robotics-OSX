from pyrobot.brain.conx import *
import sys

print "ARGS: input, hidden, trials, e, mu, r, epoch limit, symmetric offset, splitEp?"

inputSize = int(sys.argv[1])
hiddenSize = int(sys.argv[2])
trials = int(sys.argv[3])
e = float(sys.argv[4])
mu = float(sys.argv[5])
r = float(sys.argv[6])
limit = int(sys.argv[7])
symmetric = float(sys.argv[8])
splitEp = float(sys.argv[9])

print "ARGS: input=%d, hidden=%d, trials=%d, e=%f, mu=%f, r=%f, epoch limit=%d, symmetric offset=%f, splitEp=%d" % (
    inputSize, hiddenSize, trials, e, mu, r, limit, symmetric, splitEp)    

def test(net, resolution = 30, sum = 0):
    for x in range(resolution):
        row = ""
        if sum:
            size = 1
        else:
            size = net["output"].size
        for i in range(size):
            for y in range(resolution):
                input = (x/float(resolution), y/float(resolution))
                results = net.propagate(input = input)
                if sum:
                    retval = reduce(operator.add, net["output"].activation) / net["output"].size
                else:
                    retval = results[i]
                c = round(retval, 1)
                if c == 1.0:
                    c = "#"
                else:
                    c = str(c * 10)[0]
                row += "%s" % c
            row += "   "
        print row

def train(net, sweeps = 100):
    cont = 0
    test(net)
    net.train(sweeps, cont=cont)
    while not net.complete:
        cont = 1
        test(net)
        net.train(sweeps, cont=cont)

def readData(file = "two-spiral.dat"):
    fp = open(file, "r")
    inputs = []
    targets = []
    for line in fp:
        data = map(float, line.split())
        inputs.append( data[:2] )
        targets.append( data[2:] )
    return inputs, targets

inputs, targets = readData()

net = Network()
net.quickprop = 1
net.epsilon = e
net.splitEpsilon = splitEp
net.autoSymmetric = 1
net.symmetricOffset = symmetric
net.mu = mu
net.maxRandom = r
net.addLayers(inputSize, hiddenSize, 1)
net.setInputs( inputs )
net.setTargets(targets)
net.resetEpoch = limit
net.resetLimit = 1
net.reportRate = 1000000
resetCount = 0
sum = 0
total = 0
minEpoch = 10000000
maxEpoch =-10000000
while total < trials:
    net.initialize()
    train(net, 10)
    if net.complete:
        total += 1
        sum += net.epoch
        maxEpoch = max(net.epoch, maxEpoch)
        minEpoch = min(net.epoch, minEpoch)
    else:
        resetCount += 1
print "ARGS: input=%d, hidden=%d, trials=%d, e=%f, mu=%f, r=%f, epoch limit=%d, symmetric offset=%f, splitEp=%d" % (
    inputSize, hiddenSize, trials, e, mu, r, limit, symmetric, splitEp)    
print "Total:", total
print "Max:", maxEpoch
print "Min:", minEpoch
print "Average:", sum / float(total)
print "Resets:", resetCount
