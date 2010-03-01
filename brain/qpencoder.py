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

def makeReps(net):
    n = net["input"].size
    retval = []
    for i in range(1, n + 1):
        pattern = [(0.0 - net.symmetricOffset)] * n
        pattern[-i] = (1.0 - net.symmetricOffset)
        retval.append(pattern)
    return retval

net = Network()
net.quickprop = 1
net.epsilon = e
net.splitEpsilon = splitEp
net.autoSymmetric = 0 # take care of it here (above in makeReps)
net.hyperbolicError = 1
net.symmetricOffset = symmetric
net.mu = mu
net.maxRandom = r
net.addLayers(inputSize, hiddenSize, inputSize)
net.associate("input", "output")
net.setInputs( makeReps(net) )
net.resetEpoch = limit
net.resetLimit = 1
net.reportRate = 1000000
resetCount = 0
sum = 0
total = 0
minEpoch = 10000000
maxEpoch =-10000000
result = []
while total < trials:
    net.initialize()
    net.train()
    if net.complete:
        total += 1
        sum += net.epoch
        result.append( net.epoch)
        maxEpoch = max(net.epoch, maxEpoch)
        minEpoch = min(net.epoch, minEpoch)
    else:
        resetCount += 1
print "ARGS: input=%d, hidden=%d, trials=%d, e=%f, mu=%f, r=%f, epoch limit=%d, symmetric offset=%f, splitEp=%d" % (
    inputSize, hiddenSize, trials, e, mu, r, limit, symmetric, splitEp)
avg = sum / float(total)
print "Total  : %d" % total
print "Resets : %d" % resetCount
print "Max    : %d" % maxEpoch
print "Min    : %d" % minEpoch
print "Average: %.2f" % avg
sum = 0.0
for val in result:
    sum += (val - avg) ** 2
print "Std dev: %.2f" % math.sqrt(sum / (total - 1))
