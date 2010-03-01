__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision: 2141 $"

from pyrobot.brain.governor import GovernorSRN
#from pyrobot.brain.conx import SRN

mask = [0] * 4 + [0] * 5 + [1] * 4
net = GovernorSRN(delta = 0.3, epsilon = 2.1, historySize = 5, mask = mask)
#net = SRN()
net.addThreeLayers(4,5,4)
net.setPatterns({"a" : [1,0,0,0],
                 "b" : [0,1,0,0],
                 "c" : [0,0,1,0],
                 "d" : [0,0,0,1]})
net.setInputs( [["a", "b", "b", "b", "a", "d", "b"],
                ["a", "c", "c", "c", "a", "d", "c"]] )
#net.setInputs( [["a", "b", "a", "d", "b"],
#                ["a", "c", "a", "d", "c"]] )
net.setSequenceType("ordered-segmented")
net.predict("input", "output")
net.setInitContext(0)
net.setTolerance(.3)
net.setStopPercent(0.75)
net.setResetEpoch(2500)
net.setResetLimit(1)
net.setEpsilon(0.05)
net.setMomentum(0)
net.governing = 1
net.train()
print net.ravq
net.setLearning(0)
net.setInteractive(1)
net.sweep()

