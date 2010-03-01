from pyrobot.brain.governor import *
net = GovernorNetwork(5, 2.1, 0.01, 5, 0.2) 
net.addLayers(2, 2, 1) # sizes
net.setInputs( [[0, 0], [0, 1], [1, 0], [1, 1]])
net.setTargets([[0], [1], [1], [0]])
net.tolerance = .1
net.train(100)
net.complete = 0
cont = 0
sweeps = 100
while not net.complete:
    net.train(sweeps, cont=cont)
    cont = 1
net.governing = 0
net.interactive = 1
net.sweep()
