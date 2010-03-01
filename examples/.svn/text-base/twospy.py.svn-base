from pyrobot.brain.cascor import *
net = CascorNetwork(2,1, patience = 12, maxOutputEpochs = 200, maxCandEpochs = 200)
net.maxRandom = 1.0
net.addCandidateLayer(8)
net.useFahlmanActivationFunction()

lines = open("twospiral.dat",'r').readlines()
inputs = [[float(num) for num in line.split()[:-1]] for line in lines]
inputs = Numeric.array(inputs)
targets = Numeric.array([[float(line.split()[-1])] for line in lines])
net.setInputs(inputs)
net.setTargets(targets)

net.tolerance = 0.4
net.outputEpsilon = 1.0/194.0
net.outputDecay = 0.0
net.candEpsilon = 100.0/194.0
net.candDecay = 0.0
net.candChangeThreshold = 0.03
net.outputChangeThreshold = 0.01
net.setSigmoid_prime_offset( 0.1)
net.outputMu = 2.0
net.candMu = 2.0
net.train(50)
