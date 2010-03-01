"""

Governor code for self regulating networks.

"""

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision$"

from pyrobot.brain.conx import *
from pyrobot.brain.ravq import ARAVQ, euclideanDistance

class Governor:
    """
    An RAVQ vitual baseclass for combination with Network. 
    """
    def __init__(self, bufferSize = 5, epsilon = 0.2, delta = 0.6,
                 historySize = 5, alpha = 0.02, mask = [], verbosity = 0):
        self.governing = 1
        self.decay = 1
        self.learning = 1
        self.ravq = ARAVQ(bufferSize, epsilon, delta, historySize, alpha) 
        self.ravq.setAddModels(1)
        self.setVerbosity(verbosity)
        self.histogram = {}
        self.decayHistogram = {}
        self.reportHistograms = 0
        if mask != []: 
            self.ravq.setMask(mask)
            
    def incompatibility(self):
        """
        For each model, how different is it from each of the buffer items? Returns list of
        incompatibilities. Note: uses mask to scale.
        """
        retval = []
        for model in self.ravq.models:
            sum = 0.0
            for buff in model.contents:
                sum += euclideanDistance(model.vector, buff, self.ravq.mask)
            retval.append(sum)
        return retval

    def distancesTo(self, vector):
        """
        Computes euclidean distance from a vector to all model vectors. Note: uses mask
        to scale.
        """
        retval = []
        for m in self.ravq.models:
            retval.append( euclideanDistance(vector, m.vector, self.ravq.mask) )
        return retval

    def winner(self):
        """
        Get's winning name, m.v. of last winner.
        """
        index = self.ravq.newWinnerIndex
        if index >= 0:
            name = self.ravq.models.names[index]
        else:
            name = index
        return name, self.ravq.winner

    def input(self, vector):
        """
        Wrapper around ravq.input() which returns index and mapped-to m.v. Here, we convert
        index to "name".
        """
        index, modelVector = self.ravq.input(vector)
        if index >= 0:
            name = self.ravq.models.names[index]
        else:
            name = index
        return name, modelVector

    def map(self, vector):
        """
        Returns the index and vector of winning position. Side effect: records
        index of winning pos in histogram and decayHistogram.
        """
        index, modelVector = self.input(vector)
        if self.histogram.has_key(index):
            self.histogram[index] += 1
        else:
            if index >= 0:
                self.histogram[index] = 1
        if self.decayHistogram.has_key(index):
            self.decayHistogram[index] += 1
        else:
            if index >= 0:
                self.decayHistogram[index] = 1
        return (index, modelVector)

    def next(self):
        """ Public interface for getting next item from RAVQ. """
        return self.nextItem()

    def nextItem(self):
        """ Public interface for getting next item from RAVQ. """
        retval = None
        try:
            retval = self.ravq.models.next().next()
        except AttributeError:
            pass
        return retval

    def __nextitem__(self):
        """ For use in iterable positions:
            >>> govnet = GovernorNetwork()
            >>> for item in govnet:
            ...    print item
            ...
        """
        return self.ravq.models.next().next()

    def saveRAVQ(self, filename):
        """ Saves RAVQ data to a file. """
        self.ravq.saveRAVQToFile(filename)

    def loadRAVQ(self, filename):
        """ Loads RAVQ data from a file. """
        self.ravq.loadRAVQFromFile(filename)

    def setBalancedMask(self):
        """
        Give each layer an equal weighting, so that all weights sum to one.
        """
        layerWeights = {}
        for layer in self.layers:
            if layer.kind != 'Hidden':
                layerWeights[layer.name]= layer.size
        parts = len(layerWeights)
        for name in layerWeights:
            layerWeights[name] = (1.0 / layerWeights[name]) * (1.0 / parts)
        print "layerWeights:", layerWeights
        self.setMask(**layerWeights)
        
    def setMask(self, **args):
        """
        Takes a dictionary of layer names and mask weights.
        """
        # Names are sorted to ensure that they are in proper order.
        argsLayerNames = args.keys()
        argsLayerNames.sort()
        maskInput, maskContext, maskOutput = [], [], []
        for name in argsLayerNames:
            if self[name].kind == 'Input':
                maskInput += [args[name]] * self[name].size
            if self[name].kind == 'Context':
                maskContext += [args[name]] * self[name].size
            if self[name].kind == 'Output':
                maskOutput += [args[name]] * self[name].size
        self.ravq.setMask( maskInput + maskContext + maskOutput )
        if self.verbosity:
            print "mask:", self.ravq.mask
 
    def decayModelVectors(self):
        good = []
        goodNames = []
        for name in self.decayHistogram.keys():
            pos = self.ravq.models.names.index(name)
            good.append( self.ravq.models.contents[pos] )
            goodNames.append( self.ravq.models.names[pos] )
        self.decayHistogram = {}
        self.ravq.models.contents = good
        self.ravq.models.names = goodNames
        if len(self.ravq.models.contents):
            self.ravq.models.nextPos = self.ravq.models.nextPos % \
                                       len(self.ravq.models.contents)
        else:
            self.ravq.models.nextPos = 0

class GovernorNetwork(Governor, Network):
    def __init__(self, bufferSize = 5, epsilon = 0.2, delta = 0.6,
                 historySize = 5, alpha = 0.02, mask = [], verbosity = 0):
        # network:
        Network.__init__(self, name = "Governed Network",
                         verbosity = verbosity)
        # ravq
        Governor.__init__(self, bufferSize, epsilon, delta,
                          historySize, alpha, mask, verbosity)

    def setVerbosity(self, val):
        Network.setVerbosity(self, val)
        self.ravq.setVerbosity(val)

    def setLearning(self, value):
        self.learning = value
        self.ravq.setAddModels(value)

    def step(self, **args):
        if self.governing and not self._cv:
            # when layers are added one by one, ensure that mask
            # is in place
            if not self.ravq.mask:
                self.setBalancedMask()
            argLayerNames = args.keys()
            argLayerNames.sort()
            # map the ravq input and target
            netLayerNames = [layer.name for layer in self.layers]
            netLayerNames.sort()
            # get all of the input layer's values
            # and all of the ouput layer's targets mentioned in args:
            inputValues = []
            targetValues = []
            for layerName in argLayerNames:
                if self[layerName].kind == 'Input':
                    inputValues += list(args[layerName])
                elif self[layerName].kind == 'Output':
                    targetValues += list(args[layerName])
            vectorIn = inputValues + targetValues
            if self.verbosity: print "in:", vectorIn
            self.map(vectorIn)
            # get the next
            vectorOut = self.next()
            if self.verbosity: print "out:", vectorOut
            if vectorOut == None:
                vectorOut = vectorIn
            # get the pieces out of vectorOut:
            govNet = {}
            current = 0
            for layerName in argLayerNames: # from args
                if self[layerName].kind == 'Input':
                    length = self[layerName].size
                    govNet[layerName] = vectorOut[current:current+length]
                    current += length
            for layerName in args:          # from args
                if self[layerName].kind == 'Output':
                    length = self[layerName].size
                    govNet[layerName] = vectorOut[current:current+length]
                    current += length
            return Network.step(self, **govNet)
        else:
            # just do it:
            return Network.step(self, **args)

class GovernorSRN(Governor, SRN): 
    def __init__(self, bufferSize = 5, epsilon = 0.2, delta = 0.6,
                 historySize = 5, alpha = 0.02, mask = [], verbosity = 0):
        # network:
        SRN.__init__(self, name = "Governed Acting SRN",
                     verbosity = verbosity)
        self.trainingNetwork = SRN(name = "Governed Training SRN",
                                   verbosity = verbosity)
        # ravq:
        Governor.__init__(self)
        # misc:
        self.trainingNetwork.setInitContext(0)
        self.setInitContext(0)
        self.learning = 0
        self.trainingNetwork.learning = 1

    def setVerbosity(self, val):
        Network.setVerbosity(self, val)
        self.ravq.setVerbosity(val)

    def add(self, layer, verbosity=0):
        SRN.add(self, layer, verbosity)
        self.trainingNetwork.addLayer(layer.name, layer.size, verbosity)

    def addLayer(self, name, size, verbosity=0):
        SRN.addLayer(self, name, size, verbosity)
        self.trainingNetwork.addLayer(name, size, verbosity)

    def addContextLayer(self, name, size, hiddenLayerName = 'hidden', verbosity=0):
        SRN.addContextLayer(self, name, size, hiddenLayerName, verbosity)
        self.trainingNetwork.addContextLayer(name, size, hiddenLayerName, verbosity)

    def connect(self, fromName, toName):
        SRN.connect(self, fromName, toName)
        self.trainingNetwork.connect(fromName, toName)

    def addThreeLayers(self, i, h, o):
        SRN.addThreeLayers(self, i, h, o) 
        self.trainingNetwork.setLayerVerification(0)
        self.trainingNetwork.shareWeights(self)
        if not self.ravq.mask:
            self.setBalancedMask()
                
    def report(self, hist=1):
        if hist:
            print "Model vectors: %d Histogram: %s" %( len(self.ravq.models), self.histogram)
        else:
            print "Model vectors: %d" %( len(self.ravq.models),)

    def sweep(self):
        retval = SRN.sweep(self)
        if self.governing and (self.epoch % self.reportRate == 0):
            self.Print("Model vectors: %d" % len(self.ravq.models))
            if self.reportHistograms:
                self.Print("Report Histogram: %s" % self.histogram)
                if self.decay:
                    self.Print("Decay Histogram : %s" % self.decayHistogram)
            self.histogram = {}
        if self.governing and self.decay:
            self.decayModelVectors()
            if self.epoch % self.reportRate == 0:
                self.Print("After decay  : %d" % len(self.ravq.models))
        return retval

    def trainFromBuffers(self):
        vectorOut = self.next()
        if vectorOut == None:
            return None
        # get the pieces out of vectorOut:
        govNet = {}
        current = 0
        for layer in self.layers:       # from network
            if layer.kind == 'Input':
                length = layer.size
                govNet[layer.name] = vectorOut[current:current+length]
                current += length
        for layer in self.layers:       # from network
            if layer.kind == 'Context':
                length = layer.size
                govNet[layer.name] = vectorOut[current:current+length]
                current += length
        for layer in self.layers:       # from network
            if layer.kind == 'Output':
                length = layer.size
                govNet[layer.name] = vectorOut[current:current+length]
                current += length
        # load them and train training Network
        return self.trainingNetwork.step(**govNet)

    def trainFromModelVectors(self):
        vectorOut = self.models.next()
        if vectorOut == None:
            return None
        # get the pieces out of vectorOut:
        govNet = {}
        current = 0
        for layer in self.layers:       # from network
            if layer.kind == 'Input':
                length = layer.size
                govNet[layer.name] = vectorOut[current:current+length]
                current += length
        for layer in self.layers:       # from network
            if layer.kind == 'Context':
                length = layer.size
                govNet[layer.name] = vectorOut[current:current+length]
                current += length
        for layer in self.layers:       # from network
            if layer.kind == 'Output':
                length = layer.size
                govNet[layer.name] = vectorOut[current:current+length]
                current += length
        # load them and train training Network
        return self.trainingNetwork.step(**govNet)

    def networkStep(self, **args):
        if self.governing and not self._cv:
            # when layers are added one by one, ensure that mask and sharing
            # are in place
            if not self.ravq.mask:
                self.setBalancedMask()
            if self.trainingNetwork.sharedWeights == 0:
                self.trainingNetwork.setLayerVerification(0)
                self.trainingNetwork.shareWeights(self)
            argLayerNames = args.keys()
            argLayerNames.sort()
            # map the ravq input context and target
            # get all of the context layer's activations:
            netLayerNames = [layer.name for layer in self.layers]
            netLayerNames.sort()
            actContext = []
            for name in netLayerNames:
                if self[name].kind == 'Context':
                    actContext += list(self[name].activation)
            # get all of the input layer's values
            # and all of the ouptut layer's targets mentioned in args:
            inputValues = []
            targetValues = []
            for layerName in argLayerNames:
                if self[layerName].kind == 'Input':
                    inputValues += list(args[layerName])
                elif self[layerName].kind == 'Output':
                    targetValues += list(args[layerName])
            vectorIn = inputValues + actContext + targetValues
            self.map(vectorIn)
            # get the next
            vectorOut = self.next()
            if vectorOut == None:
                vectorOut = vectorIn
            # get the pieces out of vectorOut:
            govNet = {}
            current = 0
            for layerName in argLayerNames: # from args
                if self[layerName].kind == 'Input':
                    length = self[layerName].size
                    govNet[layerName] = vectorOut[current:current+length]
                    current += length
            for layer in self.layers:       # from network
                if layer.kind == 'Context':
                    length = layer.size
                    govNet[layer.name] = vectorOut[current:current+length]
                    current += length
            for layerName in args:          # from args
                if self[layerName].kind == 'Output':
                    length = self[layerName].size
                    govNet[layerName] = vectorOut[current:current+length]
                    current += length
            # load them and train training Network
            self.trainingNetwork.step(**govNet)
        return Network.step(self, **args)

    def setEpsilon(self, liveEpsilon, govEpsilon = None):
        if govEpsilon == None:
            govEpsilon = liveEpsilon
        SRN.setEpsilon(self, liveEpsilon)
        self.trainingNetwork.setEpsilon(govEpsilon)

    def setMomentum(self, liveMomentum, govMomentum = None):
        if govMomentum == None:
            govMomentum = liveMomentum
        SRN.setMomentum(self, liveMomentum)
        self.trainingNetwork.setMomentum(govMomentum)

    def setSequenceType(self, value):
        self.trainingNetwork.setSequenceType(value)
        # needs to be set, but ordered/random doesn't matter:
        SRN.setSequenceType(self, value) 
        
    def setLearning(self, value):
        self.governing = value
        self.trainingNetwork.learning = value
        self.ravq.setAddModels(value)
        self.learning = value

if __name__ == '__main__':
    import os, gzip, sys
    if len(sys.argv) != 4:
        print "call with: python govenor.py governing resetEpoch decay"
        sys.exit(1)
    # read in 20,000 lines of experimental training data
    locationfile = gzip.open('location.dat.gz', 'r')
    sensorfile = gzip.open('sensors.dat.gz', 'r')
    sensors = sensorfile.readlines()
    locations = locationfile.readlines()
    locationfile.close()
    sensorfile.close()
    # make input/target patterns:
    inputs = []
    for line in sensors:
        inputs.append( map(lambda x: float(x), line.strip().split()))
    targets = []
    for line in locations:
        targets.append( map(lambda x: float(x), line.strip().split()))
    inSize = len(sensors[0].strip().split())
    # The choice of epsilon and delta may change the required
    # weights. For binary nodes, changing the value will make the vector
    # distance one from every vector with the opposite value in that
    # node. This change is enough if the delta value is less than
    # one. Use of a high weight value is more to reflect that that
    # node is important in determining the function of the network.
    net = GovernorSRN(5, 2.1, 0.3, 5, 0.2)
    net.setSequenceType("ordered-continuous")
    net.addLayer("sonar", 16)
    net.addLayer("color", 4)
    net.addLayer("stall", 1)
    net.addContextLayer('context', inSize/2, 'hidden')
    net.addLayer("hidden", inSize/2)
    net.addLayer("output", 4)
    net.connect("sonar", "hidden")
    net.connect("color", "hidden")
    net.connect("stall", "hidden")
    net.connect("context", "hidden")
    net.connect("hidden", "output")
    net.mapInputs([['sonar', 0], ['color', 16], ['stall', 17]])
    net.setTargets( targets[:389] ) # 389 = one trip around
    net.setInputs( inputs[:389] ) # has some pauses in there too
    net.setStopPercent(.95)
    net.setReportRate(1)
    net.setResetLimit(1)
    net.setTolerance(0.2)
    net.governing = int(sys.argv[1])
    if not net.governing: # if not governing, then turn on learning in act net
        net.learning = 1
    net.setResetEpoch(int(sys.argv[2]))
    net.decay = int(sys.argv[3])
    print "Governing is", net.governing
    print "Decay is", net.decay
    net.train()
    print net.ravq
    print "Decay:", net.decay
    print "Testing..."
    print "This takes a while..."
    net.governing = 0
    net.setTargets( targets )
    net.setInputs( inputs )
    net.governing = 0
    tss, correct, total, pcorrect = net.sweep()
    print "TSS: %.4f Percent: %.4f" % (tss, correct / float(total))
    # run with -i to see net
    
