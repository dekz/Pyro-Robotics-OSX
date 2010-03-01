from pyrobot.brain.conx import *
net = IncrementalNetwork("cascade") # "parallel" or "cascade"
net.addLayers(2, 2, 1) # sizes
net.addCandidateLayer(8) # size
net.setInputs( [[0, 0], [0, 1], [1, 0], [1, 1]])
net.setTargets([[0], [1], [1], [0]])
net.tolerance = .1
sweeps = 100
cont = 0
while not net.complete:
    net.train(sweeps, cont=cont)
    net.recruitBest()
    cont = 1
net["candidate"].active = 0
net.displayConnections()
net.interactive = 1
net.sweep()
