from pyrobot.brain.conx import *

inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]
targets= [[0], [1], [1], [0]]

net = SigmaNetwork()
net.addLayers(2, 5, 21) # make the output as large as you like
net.setInputs( inputs )
net.setTargets( targets)
net.tolerance = 0.4
net.reportRate = 500
net.resetEpoch = 300
net.setEpsilon(0.5)
net.setMomentum(.7)

fp = open("sumXor.dat", "w")
for epsilon in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    for momentum in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        net.setEpsilon(epsilon)
        net.setMomentum(momentum)
        net.initialize()
        net.train()
        print >> fp, epsilon, momentum, net.epoch - 1
        fp.flush()
fp.close()
