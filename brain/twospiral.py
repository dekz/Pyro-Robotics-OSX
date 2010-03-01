from pyrobot.brain.conx import *
from pyrobot.brain.governor import *

def test(net, resolution = 30, sum = 0):
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

def train(net, sweeps = 100, recruit = 0):
    if "candidate" in [layer.name for layer in net.layers]:
        net["candidate"].active = 1
    cont = 0
    test(net)
    while not net.complete:
        net.train(sweeps, cont=cont)
        if recruit:
            net.recruitBest()
        test(net)
        cont = 1

fp = open("two-spiral.dat", "r")
inputs = []
targets = []
for line in fp:
    data = map(float, line.split())
    inputs.append( data[:2] )
    targets.append( data[2:] )

net0 = IncrementalNetwork()
net0.addLayers(2, 1)
net0.setInputs( inputs )
net0.setTargets( targets)
net0.tolerance = 0.4
net0.addCandidateLayer(4)
net0.reportRate = 100
#train(net0, 500, recruit=1)

net2 = GovernorNetwork(5, 2.1, 0.01, 5, 0.2) # 5, 2.1, 0.3, 5, 0.2
net2.reportHistograms = 1
net2.addThreeLayers(2, 10, 1)
net2.setInputs( inputs )
net2.setTargets( targets)
net2.tolerance = 0.4
net2.reportRate = 5
net2.doWhile = lambda a, b: 1
#train(net2)
#print net2.ravq

net3 = Network()
net3.addLayers(2, 10, 10, 1)
net3.setInputs( inputs )
net3.setTargets( targets)
net3.tolerance = 0.4
net3.batch = 1
net3.reportRate = 10
train(net3)

class MyNetwork(Network):
    def getData(self, i):
        patterns = {1.0: [1.0, 0.0], 0.0: [0.0, 1.0]}
        data = {}
        data["input"] = self.inputs[i]
        data["output"] = patterns[self.targets[i][0]]
        return data

net4 = MyNetwork()
net4.addLayers(2, 10, 10, 2)
net4.setInputs( inputs )
net4.setTargets( targets)
net4.tolerance = 0.4
net4.reportRate = 100
#train(net4, 100)
