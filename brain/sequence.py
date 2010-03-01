__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision: 2141 $"

from pyrobot.brain.conx import *
from pyrobot.brain.governor import *
import sys

# goal is to remember first input given in several sequences

print "command line expects: {srn | gov | both} pauseInteger # for inter-stimulus wait"

mode = sys.argv[1] # srn, gov, or both
pause = int(sys.argv[2])

#net = SRN()
net = GovernorSRN(1, historySize=5)
net.addThreeLayers(1,5,1)
net.setInputs( [[0.0] + [0.0] * pause + [0.0],
                [0.5] + [0.0] * pause + [0.0],
                [1.0] + [0.0] * pause + [0.0]])               
net.setOutputs( [[0.0] + [0.0] * pause + [0.0],
                 [0.5] + [0.0] * pause + [0.5],
                 [1.0] + [0.0] * pause + [1.0]] )
net.setSequenceType("ordered-segmented")

net.crossValidationCorpus = (
    {"input" : [0.0] + [0.0] * pause + [0.0],
     "output" : [0.0] + [0.0] * pause + [0.0] },
    {"input" : [0.5] + [0.0] * pause + [0.0],
     "output" : [0.5] + [0.0] * pause + [0.5] },
    {"input" : [1.0] + [0.0] * pause + [0.0],
     "output" : [1.0] + [0.0] * pause + [1.0] },
    )
net.setUseCrossValidationToStop(1)
net.setTolerance(.2)
net.setResetEpoch(12000)
net.setResetLimit(1)
net.setEpsilon(0.25) # .25
net.setMomentum(0.0)
net.setReportRate(25)
net.decay = 1
if mode == "gov":
    net.governing = 1
elif mode == "srn":
    net.governing = 0
    net.learning = 1
elif mode == "both":
    net.governing = 1
    net.learning = 1

#net.setInteractive(1)
#net.trainingNetwork.setInteractive(1)
    
net.train()
net.setLearning(0)
net.setInteractive(1)
net.sweep()

# This one can be learned, with learningDuringSequence = 1
# takes about 2100 epochs
