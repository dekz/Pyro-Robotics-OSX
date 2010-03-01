from pyrobot.brain import Brain
from pyrobot.brain.behaviors import *
from pyrobot.brain.conx import *
from pyrobot.system.log import *
from math import *
from os import system
from time import *
from random import *
import pdb
"""

This is a copy of iac.py adapted to run on Aibo


"""

def square(x):
    return x * x

def indexOfMin(ls):
    if len(ls) == 1:
        return 0
    index = 0
    for i in range(1,len(ls)):
        if ls[i] < ls[index]:
            index = i
    return index

def indexOfMax(ls):
    if len(ls) == 1:
        return 0
    index = 0
    for i in range(1,len(ls)):
        if ls[i] > ls[index]:
            index = i
    return index

class Region:
    """
    
    A region primarily consists of a list of exemplars (stored in
    self.inputs and self.targets), a list of errors (stored in
    self.errors in newest to oldest order), and an expert (stored in
    self.expert which tries to learn to predict the correct targets
    from the inputs).

    The parameters self.timeWindow and self.smoothing are used to
    calculate error progress.

    The lists self.inputTotals and self.targetTotals maintain a
    running sum of all the exemplars stored in the region to allow
    for quick calculation of their center points.

    Currently the expert is implemented as a standard three-layer
    backprop network.  This is NOT how it was done in the original
    paper.

    """
    def __init__(self, inputVectorSize, targetVectorSize, errors):
        self.inputVectorSize = inputVectorSize
        self.targetVectorSize = targetVectorSize
        self.errors = errors
        self.regionSize = 0
        self.timeWindow = 10
        self.smoothing = 15
        self.inputs = []
        self.targets = []
        self.inputTotals = [0] * self.inputVectorSize
        self.targetTotals = [0] * self.targetVectorSize
        self.expert = Network()
        self.expert.addThreeLayers(self.inputVectorSize,
                                   self.inputVectorSize / 2,
                                   self.targetVectorSize)
        self.expert.resetEpoch = 1
        self.expert.resetLimit = 1
    def __str__(self):
        result = ""
        if self.regionSize > 0:
            result += "Region: size "
            result += str(self.regionSize)
            result += ", learning progress "
            result += str(self.learningProgress())
            result += ", variance of targets "
            result += str(self.varianceOfTargets())
            result += ", center "
            result += str(self.getCenter())
        else:
            result += "Region is empty"
        return result
    def saveRegion(self, filename):
        """
        Stores the input patterns associated with the region to
        the given file name.
        """
        fp = open(filename, "w")
        for vector in self.inputs:
            for coordinate in vector:
                fp.write("%f\t" % coordinate)
            fp.write("\n")
        fp.close()
    def trainExpert(self):
        """
        Will train the expert once there are a reasonable number of
        training patterns available.
        """
        if len(self.inputs) > (self.timeWindow + self.smoothing):
            self.expert.setInputs(self.inputs)
            self.expert.setOutputs(self.targets)
            self.expert.train()
    def askExpert(self, input):
        """
        Find out what the expert predicts for the given input.
        """
        self.expert['input'].copyActivations(input)
        self.expert.propagate()
        return self.expert['output'].activation
    def storeError(self, error):
        """
        Errors are stored with the most recent at the head of the list.
        """
        self.errors.insert(0, error)
    def learningProgress(self):
        """
        Returns the learning progress which is an approximation of
        the first derivative of the error.
        """
        if len(self.errors) < (self.timeWindow + self.smoothing + 1):
            return 0
        decrease = self.meanErrorRate(0) - self.meanErrorRate(self.timeWindow)
        return -1 * decrease
    def meanErrorRate(self, start):
        """
        Returns the average error rate over self.smoothing steps
        starting from the given start index.
        """
        result = 0
        end = start + self.smoothing + 1
        if end > len(self.errors):
            return 0
        for i in range(start, end, 1):
            result += self.errors[i]
        return result / float(self.smoothing + 1)
    def addExemplar(self, input, target):
        """
        Adds the given input and target to the appropriate lists.
        Also updates the totals used for calculating the centers.
        """
        self.inputs.append(input)
        self.targets.append(target)
        self.regionSize += 1
        for i in range(self.inputVectorSize):
            self.inputTotals[i] += input[i]
        for i in range(self.targetVectorSize):
            self.targetTotals[i] += target[i]
    def varianceOfTargets(self):
        c = self.getTargetCenter()
        variances = [0] * self.targetVectorSize
        for v in self.inputs:
            for i in range(self.targetVectorSize):
                variances[i] += square(v[i] - c[i])
        total = 0
        for i in range(self.targetVectorSize):
            total += variances[i]/float(self.regionSize)
        return total
    def getTargetCenter(self):
        """
        Used to quickly calculate the variances of the target
        vectors. 
        """
        center = self.targetTotals[:]
        if self.regionSize == 0: return None
        for i in range(self.targetVectorSize):
            center[i] /= float(self.regionSize)
        return center
    def getCenter(self):
        """
        The regions are clustered based on the input vectors.
        This returns the center point of the region's cluster.
        """
        center = self.inputTotals[:]
        if self.regionSize == 0: return None
        for i in range(self.inputVectorSize):
            center[i] /= float(self.regionSize)
        return center
    def dist(self, v1, v2):
        """
        Returns the euclidean distance between two given
        vectors.
        """
        d = 0
        try:
            for i in range(self.inputVectorSize):
                d += square(v1[i] - v2[i])
        except TypeError:
            pdb.set_trace()
        return sqrt(d)
    def distFromCenter(self, v):
        """
        Returns the distance from the region's center.
        """
        return self.dist(self.getCenter(), v)

class Memory:
    """
    A memory consists of a list of regions.  When exemplars are added,
    it determines when a region needs to be split, and then performs
    the split using a k-means analysis.  This is NOT how the split
    was done in the original paper.
    
    """
    def __init__(self, maxRegionSize, inputVectorSize, targetVectorSize):
        self.regions = [Region(inputVectorSize, targetVectorSize, [])]
        self.maxRegionSize = maxRegionSize
        self.inputVectorSize = inputVectorSize
        self.targetVectorSize = targetVectorSize
    def __str__(self):
        result = ""
        result += "Memory contains "
        result += str(len(self.regions))
        result += " region(s):\n"
        for region in self.regions:
            result += region.__str__()
            result += "\n"
        return result
    def saveCenters(self):
        fp = open("centers", "w")
        for region in self.regions:
            center = region.getCenter()
            for coordinate in center:
                fp.write("%f\t" % coordinate)
            fp.write("\n")
        fp.close()
    def saveRegions(self):
        for i in range(len(self.regions)):
            self.regions[i].saveRegion("region%d" % i)
    def splitRegion(self, r):
        """
        Randomly chooses two of the existing vectors in the region
        as the initial centers of two new regions.  Then uses the
        k-means technique to continue to re-center until the
        clusters stablize.
        """
        # only copy enough error history to allow for
        # continued calculations of learning progress
        # in the newly split regions
        # if they are all same:
        if len(set(map(tuple, r.inputs))) == 1:
            print "Can't split region!"
            # add r back, and return
            self.regions.append(r)
            return
        numErrors = r.timeWindow + r.smoothing + 1
        while True:
            n = r.regionSize-1
            i1 = randint(0,n)
            i2 = randint(0,n)
            if r.inputs[i1] != r.inputs[i2]:
                break
        center1 = r.inputs[i1]
        center2 = r.inputs[i2]
        prev1 = None
        prev2 = None
        while True:
            if prev1 == center1 and prev2 == center2:
                self.regions.append(r1)
                self.regions.append(r2)
                return
            r1 = Region(r.inputVectorSize,
                        r.targetVectorSize,
                        r.errors[:numErrors])
            r2 = Region(r.inputVectorSize,
                        r.targetVectorSize,
                        r.errors[:numErrors])
            for i in range(r.regionSize):
                if r.dist(r.inputs[i],center1) < r.dist(r.inputs[i],center2):
                    r1.addExemplar(r.inputs[i], r.targets[i])
                else:
                    r2.addExemplar(r.inputs[i], r.targets[i])
            prev1 = center1
            prev2 = center2
            center1 = r1.getCenter()
            center2 = r2.getCenter()
    def closestRegion(self, input):
        return self.regions[self.indexOfClosestRegion(input)]
    def indexOfClosestRegion(self, input):
        if len(self.regions) == 1:
            return 0
        dists = [r.distFromCenter(input) for r in self.regions]
        return indexOfMin(dists)
    def addExemplar(self, input, target, region):
        """
        Adds the given input and target exemplar to the given
        region.  If the region is now too large, it is removed
        and split into two new regions.
        """
        region.addExemplar(input, target)
        #print "Region added exemplar, size is", len(region.inputs)
        if region.regionSize > self.maxRegionSize:
            print "*** MEMORY splitting a region ***"
            index = self.regions.index(region)
            self.regions.pop(index)
            self.splitRegion(region)
            print self.__str__()

class IACBrain(FSMBrain):
    """

    A copy of the prototype of the IAC model. This was adapted to to Aibo.
    There are some key differences between the model described in the Oudeyer
    et. al. paper and this
    implementation.  This implementation uses k-means to do the
    splitting of the sensorimotor space.  It does not try to minimize
    the variance of the prediction space.  Also, each region's
    expert is a neural network.  

    Using the Aibo. Using 3 sensors 2 camera filters to sense tag presence and
    motion, and 1 mouth sensor to detect if the robot has something in its mouth
    
    """
    def setup(self, **args):
        #if self.hasA("camera"):
        #    self.cam = self.robot.camera[0]
        #else:
        #    raise AttributeError, "requires a camera"
        #camera = self.cam # local variable
        if self.hasA("ptz"):
            self.ptz = self.robot.ptz[0]
        else:
            raise AttributeError, "requires a ptz"
        #target filter
        #camera.addFilter("match", 222,46,36) #ear tag
        #camera.addFilter("match", 146,39,23) #bear tag
        #camera.addFilter("blobify", 0,255,255,0,1,1,1,)
        #camera.addFilter("motion")

        self.maxRegionSize = args['maxRegionSize']
        self.motorVectorSize = args['motorVectorSize']
        self.sensorVectorSize = args['sensorVectorSize']
        self.inputVectorSize = self.sensorVectorSize + self.motorVectorSize
        self.targetVectorSize = self.sensorVectorSize
        self.memory = Memory(self.maxRegionSize,
                             self.inputVectorSize,
                             self.targetVectorSize)
        print "MEMORY created"
        self.fr = open("bbResult", "w")
        self.fr.write("Bites  Bashes     Steps\n")
        self.steps = 0
        #self.robot.range.units = 'SCALED'
        self.numCandidates = 3
        self.winningRegion = None
        self.prediction = None
        self.sensorimotor = None
        self.probOfRandAction = 0.35
        self.motorval = []
        self.bashLeg = ""
        self.goodBites = 0
        self.goodBashes = 0
        self.simulate = 1  # 1 robot does not move
        # Create a dictionary to count interesting states
        self.monitor = {'stall':0, 'light':0, 'blockedL':0,
                        'blockedR':0, 'blockedF':0}
        self.testEpoch = 100
        # Open file to store this data
        self.data = open("monitor.data", "w")
        self.data.write("% Columns represent: ")
        for key in self.monitor.keys():
            self.data.write("%s " % key)
        self.data.write("\n")
    def computeError(self, actual, prediction):
        error = 0
        for i in range(self.targetVectorSize):
            error += square(actual[i] - prediction[i])
        return error
    def scale(self, m):
        """
        Motor values are stored in range [0.0,1.0]
        However, the robot uses range [-1.0,1.0]
        """
        return (m + 1.0)/ 2.0

    def scaleBack(self,m):
        return (m * 2.0) - 1.0
    
    def destroy(self):
        self.cam.clearFilters()
    
class chooseMotion(State):

    def onActivate(self):
        print "Selecting Action"
    
        """
        
        Implements the main action loop of the IAC model.
        
        """

    def step(self):
        # Read in current sensors S(t)
        print "Step select Action" 
        tag, motion, mouth = 0, 0, 0
        #tg = self.robot.camera[0].filterResults[0] #sees ear tag
        #if tg > 350:
        #    tag = 1
        #tg = self.robot.camera[0].filterResults[1] #sees bear tag
        #if tg > 400:
        #    tag = .5
        #mo = self.robot.camera[0].filterResults[2]
        #print "motion value is:  " + str(mo)
        #set motion flag based on last selections
        #set mouth flag based on last selections
        self.brain.steps += 1
        if self.brain.steps % 100 == 0:
            self.brain.fr.write("%d\t %d\t %d\n" % (self.brain.goodBites, self.brain.goodBashes, self.brain.steps))
        print "last selections " + str(self.brain.motorval)
        if len(self.brain.motorval) > 0:
            if self.brain.motorval[3] > .8:
                tag = .5
            if self.brain.motorval[0] == 0: #did it bite last time?
                if self.brain.motorval[5] == -1: #roll head pos right for bite
                    mouth = 1
                    tag = 1
                    self.brain.goodBites += 1
            if self.brain.motorval[0] == 1: #biting
                print "BASH"
                if self.brain.motorval[2] > .6: #elevation high
                    print "HIGH"
                    if self.brain.motorval[3] > .8: #pan bear tag in sight
                        print "TAG"
                        if self.brain.motorval[6] > .49:
                            print "LEFT"
                            motion = 1
                            self.brain.goodBashes += 1
        sensors = [tag, motion, mouth]
        print "reading sensors tag motion mouth"
        print tag, motion, mouth
        if self.brain.prediction != None:
            # Compute error between S(t) and prediction
            error = self.brain.computeError(sensors, self.brain.prediction)
            self.brain.winningRegion.storeError(error)
            # Add the most recent exemplar to memory
            self.brain.memory.addExemplar(self.brain.sensorimotor,
                                    sensors,
                                    self.brain.winningRegion)
            #print "adding memory"
            #print "sensorimotor " + str(self.brain.sensorimotor)
            #print "sensors " + str(sensors)
            #print "winner " + str(self.brain.winningRegion)
            # Train the updated region's expert
            self.brain.winningRegion.trainExpert()
        # Choose a motor action M(t)
        self.brain.motorval = self.selectAction(sensors)
        #need to scale just pan and rotate
        if self.brain.motorval[0] == 1:
            if self.brain.motorval[6] > .49:
                self.brain.bashLeg = "leg front left"
            else:
                self.brain.bashLeg = "leg front right"
        self.brain.motorval[3] = self.brain.scaleBack(self.brain.motorval[3])
        self.brain.motorval[4] = self.brain.scaleBack(self.brain.motorval[4])
        self.brain.motorval[5] = self.brain.scaleBack(self.brain.motorval[5])
        #print "motorval choice" + str(self.brain.motorval)
        # Execute the action
        # Execute pan action
        sleep(2)
        self.goto("moveHead")
        # Execute bit or bash action
        
    def selectAction(self, sensors):
        """
        Considers a number of candidate actions and chooses the one
        in which the maximal progress is expected (most of the time).
        With some small probability will also take random actions.
        """
        # Generate a set of candidate actions
        candidateActions = []
        for i in range(self.brain.numCandidates):
            motorval = [randint(0,1)] #action, 0=bite, 1=bash
            wide = randint(0,1)
            if wide == 0:
                motorval.extend([.7, .3])
            else:
                motorval.extend([.7, .7])
            #motorval.append(float(randrange(20,100,1))/100) #rotate
            #motorval.append(float(randrange(40,100,1))/100) #elevate
            self.pan, self.roll, self.tilt = self.lookAround(random())
            #print "self pan " + str(self.pan)
            #print "self.roll " + str(self.roll)
            #print "self.tilt " + str(self.tilt)
            motorval.append(self.brain.scale(self.pan))
            motorval.append(self.brain.scale(self.roll))
            motorval.append(self.brain.scale(self.tilt))
            motorval.append(random())  #left or right bash
            #motorval.extend([random() for i in range(3)]) #pan,tilt,roll
            #print "motor val selections"
            #print motorval
            #zero out rotate and elevate if action is bite
            if motorval[0] == 0:
                motorval[1],motorval[2], motorval[6] = 0, 0, 0
            candidateActions.append(motorval)
        progress = []
        candidateRegions = []
        # For each sensorimotor vector, find the associated region
        # and determine learning progress
        for self.motorval in candidateActions:
            region = self.brain.memory.closestRegion(sensors+self.motorval)
            candidateRegions.append(region)
            progress.append(region.learningProgress())
            #print "progress"
            #print progress
        # Choose the action from region with maximal progress
        # most of the time
        if random() < self.brain.probOfRandAction:
            choice = randint(0,self.brain.numCandidates-1)
        else:
            choice = indexOfMax(progress)
        #print "ChOICE" + str(candidateActions[choice])
        self.brain.sensorimotor = sensors + candidateActions[choice]
        #print "sEnsorImotor " + str(self.brain.sensorimotor)
        self.brain.winningRegion = candidateRegions[choice]
        # Determine the expert's prediction of the next sensors
        self.brain.prediction = region.askExpert(self.brain.sensorimotor)
        #print "prediction " + str(self.brain.prediction)
        return candidateActions[choice]
    
    def lookAround(self, case):
      print case
      pan, roll, tilt = 0, 0, 0
      if case <= .16: #look Right Up
         pan = -.8
         roll = .5
         tilt = -.1
      elif case <= .32: #look down at ear
         pan = 0
         roll = .4
         tilt = -1    
      elif case <= .48: #look Straight Up ahead
         pan = 0
         roll = .4
         tilt = -.5
      elif case <= .64: #look Right down
         pan = -.4
         roll = .3
         tilt = -.7
      elif case <=.80: #look Left Up at bear
         pan = .9
         roll = .1
         tilt = -.1
      else: #look Left Down
         pan = .4
         roll = .3
         tilt = -.7

      return pan, roll, tilt
      

class moveHead(State):
    def onActivate(self):
        print "activate moveHead"
        print "motor vals"
        print self.brain.motorval
        #self.robot.playSound("mew")

    def step(self):
        print "moving head"
        if self.brain.simulate == 0: # 1 = Robot does not move
            if self.brain.motorval[0] == 0:
                self.robot.setPose("mouth", .8)
                self.robot.ptz[0].pan(self.brain.motorval[3])
                sleep(.01)
                print "pan" + str(self.brain.motorval[3])
                self.robot.ptz[0].roll(self.brain.motorval[4])
                sleep(.01)
                self.robot.ptz[0].tilt(self.brain.motorval[5])
                sleep(2)
        if self.brain.motorval[0] == 0:
            self.goto("bite")
        else:
            self.goto("bash")
    
class bash(State):
    def onActive(self):
        #self.robot.move(0,0)
        #self.robot.playSound("3yips")
        print "bash Leg" + self.brain.bashLeg
        #self.speed = 0.05
        #self.turnSpeed= 0.1
        #self.turnHeadMin = 0.4
        #self.turnHeadMax = 0.5

    def step(self):
        print "Bashing"
        #self.robot.playSound("3yips")
        print "leg " + self.brain.bashLeg
        if self.brain.simulate == 0: # 1 = Robot does not move
            if self.brain.bashLeg == "leg front left":
                self.robot.runMotion("lp_raise")
            else:
                self.robot.runMotion("rp_raise")
                sleep(2)
                self.robot.setPose(self.brain.bashLeg,self.brain.motorval[1], self.brain.motorval[2],.5) #random elevate and rotate
                sleep(2)
                if self.brain.bashLeg == "leg front left":
                    self.robot.runMotion("lp_lower")
                else:
                    self.robot.runMotion("rp_lower")
                    sleep(4)
        self.goto("chooseMotion")

class bite(State):
    def onActive(self):
        #self.robot.playSound("growl")
        print "Bite"

    def step(self):
        print "Biting"
        if self.brain.simulate == 0: # 1 = Robot does not move
            self.robot.playSound("growl")
            self.robot.setPose("mouth", 0)
            sleep(2)
            print "mouth joint " + str(self.robot.getJoint("mouth"))
            self.robot.setPose("mouth",.3)
            sleep(2)
            self.robot.ptz[0].tilt((self.brain.motorval[5]+.5))
            sleep(2)
            self.robot.setPose("mouth",0)
        self.goto("chooseMotion")

class pause(State):
    def onActivate(self):
	print "pause"

    def step(self):
        self.goto("chooseMotion")


def INIT(engine):
    brain = IACBrain(engine=engine,
                      maxRegionSize=50,
                      motorVectorSize=7,
                      sensorVectorSize=3)
    brain.add(chooseMotion(1))
    brain.add(moveHead())
    brain.add(bash())
    brain.add(bite())
    brain.add(pause())
    return brain
   #before  
   #return IACBrain('IACBrain',
   #                engine,
   #                maxRegionSize=75,
   #                motorVectorSize=7,
   #                sensorVectorSize=3)


