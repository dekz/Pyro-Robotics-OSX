from pyrobot.brain.governor import *

def test(net, resolution = 30):
    for x in range(resolution):
        row = ""
        for y in range(resolution):
            input = (x/float(resolution), y/float(resolution))
            results = net.propagate(input = input)
            row += "%d" % int(round(results[0]))
        print row

fp = open("two-spiral.dat", "r")
inputs = []
targets = []
for line in fp:
    data = map(float, line.split())
    inputs.append( data[:2] )
    targets.append( data[2:] )

net2 = GovernorNetwork(5, 2.1, 0.01, 5, 0.2) # 5, 2.1, 0.3, 5, 0.2
net2.reportHistograms = 1
net2.addThreeLayers(2, 10, 1)
net2.setInputs( inputs )
net2.setTargets( targets)
net2.tolerance = 0.4
net2.reportRate = 1
net2.train(10)
print net2.ravq

