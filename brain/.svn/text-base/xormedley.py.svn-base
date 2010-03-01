from pyrobot.brain.conx import *
from pyrobot.brain.governor import *

ep = 0.5
mo = 0.975

def test(net, resolution = 30, sum = 0):
    print "Testing:", net.name
    if "candidate" in [layer.name for layer in net.layers]:
        net["candidate"].active = 0
    for x in range(resolution):
        row = ""
        if sum:
            size = 1
        else:
            size = net["output"].size
        for i in range(size):
            for y in range(resolution):
                input = (x/float(resolution), y/float(resolution))
                if net.symmetricOffset:
                    input = map(lambda x: x - 0.5, input)
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
    if "candidate" in [layer.name for layer in net.layers]:
        net["candidate"].active = 1

def train(net, sweeps = 100, recruit = 0, resolution = 30):
    print "*" * 65
    print net.name
    if "candidate" in [layer.name for layer in net.layers]:
        net["candidate"].active = 1
    cont = 0
    test(net, resolution)
    while not net.complete:
        net.train(sweeps, cont=cont)
        if recruit:
            net.recruitBest()
        print net.name, net.complete
        test(net, resolution)
        cont = 1
    return net.name, net.epoch

inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]
targets= [[0], [1], [1], [0]]

results = []

net5 = Network()
net5.addLayers(2, 2, 1)
net5.quickprop = 1    # this line needs to be right here, for now
net5.setInputs( inputs )
net5.setTargets( targets)
net5.tolerance = 0.4
net5.reportRate = 5
net5.setBatch(1)
results.append(train(net5))

net0 = IncrementalNetwork()
net0.addLayers(2, 1)
net0.setInputs( inputs )
net0.setTargets( targets)
net0.tolerance = 0.4
net0.addCandidateLayer(4)
net0.reportRate = 100
results.append(train(net0, 750, recruit=1))

net1 = SigmaNetwork()
net1.addLayers(2, 5, 5)
net1.setInputs( inputs )
net1.setTargets( targets)
net1.tolerance = 0.4
net1.reportRate = 100
results.append(train(net1, 500, resolution=10))

net2 = GovernorNetwork(5, 2.1, 0.01, 5, 0.2) # 5, 2.1, 0.3, 5, 0.2
net2.reportHistograms = 1
net2.addThreeLayers(2, 10, 1)
net2.setInputs( inputs )
net2.setTargets( targets)
net2.tolerance = 0.4
net2.reportRate = 100

def notAllDone(a, b):
    net2.learning = 0
    net2.governing = 0
    correct = 0
    for i in range(4):
        results = net2.propagate(input = inputs[i])
        if abs(results[0] - targets[i][0]) < net2.tolerance:
            correct += 1
    net2.learning = 1
    net2.governing = 1
    return correct != 4

net2.doWhile = notAllDone
results.append(train(net2))
print net2.ravq

net3 = Network()
net3.addLayers(2, 2, 1)
net3.setInputs( inputs )
net3.setTargets( targets)
net3.tolerance = 0.4
net3.reportRate = 500
net3.setEpsilon(ep)
net3.setMomentum(mo)
results.append(train(net3))

class MyNetwork(Network):
    def getData(self, i):
        patterns = {1.0: [1.0, 0.0], 0.0: [0.0, 1.0]}
        data = {}
        data["input"] = self.inputs[i]
        data["output"] = patterns[self.targets[i][0]]
        return data

net4 = MyNetwork()
net4.addLayers(2, 10, 2)
net4.setInputs( inputs )
net4.setTargets( targets)
net4.tolerance = 0.4
net4.reportRate = 500
net4.setEpsilon(ep)
net4.setMomentum(mo)
results.append(train(net4, 500))

for (name, epoch) in results:
    print name, epoch

