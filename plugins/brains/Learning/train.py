# Train a network offline
# Inputs: 7 sensor readings 
# Outputs: translate and rotate values (unscaled) 
   
from pyrobot.brain.conx import * 
from pyrobot.system.log import * 
    
# Create the network 
n = Network() 
n.addThreeLayers(8,1,2) # size of input, hidden, output
# Set learning parameters 
n.setEpsilon(0.5) 
n.setMomentum(0.0) 
n.setTolerance(0.05) 
# set inputs and targets (from collected data set) 
n.loadInputsFromFile('sensors.dat')
n.loadTargetsFromFile('targets.dat')
# Logging 
log = Log(name = 'E05M01.txt') # for epsilon 0.5 momentum 0.1
best = 0 
for i in xrange(0,1000,1): 
   tssError, totalCorrect, totalCount = n.sweep()   
   correctpercent = (totalCorrect*0.1) / (totalCount*0.1) 
   log.writeln( "Epoch # "+ str(i)+ " TSS ERROR: "+ str(tssError)+
                " Correct: "+ str(totalCorrect)+ " Total Count: "+
                str(totalCount)+ " %correct = "+ str(correctpercent)) 
   if best < correctpercent: 
      n.saveWeightsToFile("E05M01.wts") 
      best = correctpercent 
print "done"
