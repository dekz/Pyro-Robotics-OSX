from pyrobot.brain.governor import *
net = GovernorSRN(5, 2.1, 0.01, 5, 0.2) 
net.addLayers(1, 2, 1) 
net.setSequenceType("ordered-continuous")
# XOR, in time:
net.setInputs( [[0], [0], [0], [1], [1], [0], [1], [1]])
net.setTargets([[0.5], [0], [0.5], [1], [0.5], [1], [0.5], [0]])
net.tolerance = .1
net.train(100)
net.complete = 0
cont = 1
sweeps = 100
while not net.complete:
    print "continuing..."
    net.train(sweeps, cont=cont)
    cont = 1
net.governing = 0
net.interactive = 1
net.sweep()
