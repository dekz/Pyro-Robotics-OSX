from pyrobot.brain.conx import *
import math

__author__  = "George Dahl <gdahl1@swarthmore.edu>"
__version__ = "$Revision: 2409 $"

def findMax(seq):
    """
    Returns the index of the maximum value in the sequence.
    """
    bestSoFar = 0
    for i in range(len(seq)-1):
        if seq[i+1] > seq[bestSoFar]:
            bestSoFar = i+1
    return bestSoFar

def findMin(seq):
    """
    Returns the index of the minimum value in the sequence.
    """
    bestSoFar = 0
    for i in range(len(seq)-1):
        if seq[i+1] < seq[bestSoFar]:
            bestSoFar = i+1
    return bestSoFar

class CascorNetwork(Network):
    """
    This network implements the cascade-correlation training method.
    """
    def __init__(self, inputLayerSize = 0, outputLayerSize = 0, patience = 12, maxOutputEpochs = 200, maxCandEpochs = 200,
                 name = 'Cascor Network', verbosity = 0):
        Network.__init__(self, name, verbosity)
        self.incrType = "cascade" # only "cascade" is supported at the moment
        self.setQuickprop(1)
        if inputLayerSize != 0 and outputLayerSize != 0:
            self.addLayers(inputLayerSize, outputLayerSize)
            self.candEpsilon = inputLayerSize * 0.6 # 2.0
        else:
            self.candEpsilon = None
        self.outputEpsilon = 0.7
        self.outputMu = 2.0
        self.candMu = 2.0
        #Fahlman had 0.01 and 0.03
        self.outputChangeThreshold = 0.01
        self.candChangeThreshold = 0.03
        self.outputDecay = -0.001
        self.candDecay = -0.001
        self.quitEpoch = patience
        self.patience = patience
        self.splitEpsilon = 0 #we will handle this manually since it is different for input and output phases
        self.previousError = sys.maxint
        self.maxOutputEpochs = maxOutputEpochs #perhaps duplicates the purpose of a datamember that already exists?
        self.maxCandEpochs = maxCandEpochs
        self.sigmoid_prime_offset = 0.001#0.0001
        self.sig_prime_offset_copy = self.sigmoid_prime_offset
        self.candreportRate = self.reportRate
        self.correlations = []
        self.autoSaveNetworkFile = "cascor-??.net"
        self.switchToOutputParams()

    def displayCorrelations(self):
        fromColWidth = 15
        colWidth = 8
        decimals = 2
        layer = self["candidate"]
        # top bar
        line = ("=" * fromColWidth) + "="
        for i in range(layer.size):
            line += ("=" * colWidth) + "="
        print line
        # to layer name:
        line = " " * fromColWidth + "|" + pad(layer.name, (colWidth * layer.size) + (layer.size - 1), align="center", )
        print line
        # sep bar:
        line = ("-" * fromColWidth) + "+"
        for i in range(layer.size):
            line += ("-" * colWidth) + "+"
        print line
        # col header:
        line = pad("correlations", fromColWidth, align="center")
        for i in range(layer.size):
            line += pad(str(i), colWidth, align = "center")
        print line
        # sep bar:
        line = ("-" * fromColWidth) + "+"
        for i in range(layer.size):
            line += ("-" * colWidth) + "+"
        print line
        # correlations:
        for i in range(self["output"].size):
            line = pad(str(i), fromColWidth, align = "center")
            for j in range(layer.size):
                line += pad(("%." + str(decimals) + "f") % self.correlations[i][j], colWidth, align = "right")
            print line
        # bottom bar:
        line = ("=" * fromColWidth) + "="
        for i in range(layer.size):
            line += ("=" * colWidth) + "="
        print line
                    
    def displayConnections(self, title = "Cascade Connections"):
        Network.displayConnections(self, title)
        self.displayCorrelations()
        
    def displayNet(self):
        """
        Displays the weights of the network in a way similar to how Fahlman's code
        stores them.
        """
        print "Output weights:"
        print self["output"].weight[0]
        for r in range(len(self["input","output"].weight[0])):
            for c in range(len(self["input","output"].weight)):
                print self["input","output"].weight[c][r]
        #print hidden to output weights
        for layer in self:
            if layer.type == "Hidden":
                #print len(self["input","output"].weight)+1,self[layer.name, "output"].weight[0][0]
                print self[layer.name, "output"].weight[0][0]
        #print input to hidden weights and hidden to hidden weights
        print "Weights incident on hidden units"
        for layer in self:
            if layer.type == "Hidden":
                print layer.name[-1],layer.weight[0]
                for connection in self.connections:
                    if connection.toLayer.name == layer.name:
                        for r in range(len(connection.weight[0])):
                            for c in range(len(connection.weight)):
                                print layer.name[-1], connection.weight[c][r]
    def setSigmoid_prime_offset(self, value):
        self.sigmoid_prime_offset = value
        self.sig_prime_offset_copy = self.sigmoid_prime_offset
    def switchToOutputParams(self):
        """
        This function must be called before trainOutputs is called since the output training phase
        accepts and sometimes requires different parameters than the candidate training phase.
        """
        self.sigmoid_prime_offset = self.sig_prime_offset_copy #restore the original sigmoid prime offset
        self.epsilon = self.outputEpsilon
        self.mu = self.outputMu
        self.changeThreshold = self.outputChangeThreshold
        self.decay = self.outputDecay
    def switchToCandidateParams(self):
        """
        This function must be called before trainCandidates is called.  It switches the various learning parameters to their
        values for the candidate training phase and makes sure the sigmoid prime offset is zero during candidate
        training.
        """
        #+1.0 for bias, should be fan in for candidate layer#this is what Fahlman does?
        #we basically do the 'split epsilon' trick, but only for candidate training and we do it manually
        self["candidate"].active = 1
        if self.candEpsilon == None:
            self.candEpsilon = self["input"].size * 0.6
        self.epsilon = self.candEpsilon / self.numConnects("candidate")
        self.sig_prime_offset_copy = self.sigmoid_prime_offset #store the sigmoid prime offset for later recovery
        self.sigmoid_prime_offset = 0.0 #necessary because a non zero prime offset may confuse correlation machinery
        self.mu = self.candMu
        self.changeThreshold = self.candChangeThreshold
        self.decay = self.candDecay
    def setup(self):
        #self.setSeed(113) #FOR DEBUGGING ONLY, DISABLE WHEN DEBUGGING COMPLETE
        pass
    def train(self, maxHidden):
        self.totalEpoch = 0
        self.maxHidden = maxHidden
        cont = 1
        self.switchToOutputParams()
        while (not self.done()) and self.trainOutputs(self.maxOutputEpochs, cont): #add hidden units until we give up or win
            self.epoch = 0
            if self.autoSaveNetworkFile != None:
                self.saveNetworkToFile(self.autoSaveNetworkFile, mode = self.autoSaveNetworkFileFormat, counter = len(self) - 3)
                self.Print("   Saving network to '%s'..." % self.lastAutoSaveNetworkFilename)
            self.switchToCandidateParams()
            best = self.trainCandidates()
            self.switchToOutputParams()
            self.recruit(best)
            act = self["output"]
            self["output"].active = 1
            self.setCache(1)
            self["output"].active = act
            print len(self)-3, " Hidden nodes"
        if len(self)-3 == self.maxHidden:
            self.trainOutputs(self.maxOutputEpochs, cont)
        self.saveNetworkToFile(self.autoSaveNetworkFile, mode = self.autoSaveNetworkFileFormat, counter = len(self) - 3)
        self.Print("   Saving network to '%s'..." % self.lastAutoSaveNetworkFilename)
        print "Total epochs:", self.totalEpoch
    def trainCandidates(self):
        """ This function trains the candidate layer to maximize its
        correlation with the output errors.  The way this is done is
        by setting weight error derivatives for connections and layers
        and assuming the change_weights function will update the
        weights appropriately based on those data members.  """
        print "Candidate phase ------------------------------------"
        self["output"].active = 1 #we need the output error, etc. so the output layer must be active during propagation
        self["candidate"].active = 1 #candidate should be active throughout this function

        #E_po will hold a list of errors for each pattern for each output unit, E_po[i][j] will be error
        #          of jth output on ith pattern in the load order
        #E_o_avg is the mean of E_po over the different patterns
        #outputs[i][j] is the output of the jth output unit on the ith pattern
        E_po, E_o_avg, outputs, layerActivations = self.computeDataFromProp()

        numCandidates = len(self["candidate"])
        incomingConnections = [connection for connection in self.connections if connection.toLayer.name=="candidate"]
        numOutputs = len(outputs[0])

        ep = 0
        self.quitEpoch = self.patience
        previousBest = 0 #best candidate correlation on last iteration

        #we need to get the initial correlations to know what direction to update the weights in
        ###################################################### equivalent to Fahlman's correlation epoch function
        V_p, netInptToCnd = self.computeChangingDataFromProp(layerActivations)
        V_avg = Numeric.sum(V_p)/len(V_p)
        S_co = self.computeFahlmanS_co(V_p, V_avg, E_po, E_o_avg)
        S_co = -1.0 * S_co
        #sigma_o[i][j] is the sign of the correlation between the ith candidate and the jth output
        sigma_o = Numeric.sign(S_co)
        ######################################################

        while ep < self.maxCandEpochs and ep < self.quitEpoch:
            #V sub p on page 5 of Fahlman's paper "The Cascade-Correlation Learning Architecture (1991)"
            #will hold  a list of activations for each candidate for each training pattern, each row a
            #           different pattern, each column a different candidate
            #
            #no need to reactivate output layer here since we don't need to recompute any data about its propagation status
            V_p, netInptToCnd = self.computeChangingDataFromProp(layerActivations)
            V_avg = Numeric.sum(V_p)/len(V_p)
            
            sumSqErr = [Numeric.sum(Numeric.multiply(E_po[:,j], E_po[:,j])) for j in range(numOutputs)] ##does this help?
            for c in range(numCandidates): #for every candidate unit in the layer, get ready to train the bias weight
                #recompute dSdw for the bias weight for this candidate
                dSdw_bias = Numeric.sum( [Numeric.sum([sigma_o[i][c]*(E_po[p][i] - E_o_avg[i])*self.actDeriv(netInptToCnd[p][c]) \
                                                       for p in self.loadOrder]) for i in range(numOutputs)] )
                #dSdw_bias = Numeric.divide(dSdw_bias, sumSqErr) ##is this what fahlman does?
                self.updateCandidateLayer(dSdw_bias, c)
            for conxn in incomingConnections: #for every connection going into the candidate layer, prepare to train the weights
                #dSdw[i][j] is the derivative of S for the ith, jth weight of the current connection
                dSdw = self.compute_dSdw(sigma_o, E_po, E_o_avg, netInptToCnd, layerActivations, conxn)
                #dSdw = Numeric.divide(dSdw, sumSqErr)
                self.updateConnection(conxn, dSdw)
            #deactivate output layer here so we don't change its weights
            self["output"].active = 0
            self.change_weights() #change incoming connection weights and bias weights for the entire candidate layer

            #My original code for computing S_c has been replaced by something more like Fahlman's implementation and less like his paper
            #S_c is a list of the covariances for each candidate, or
            #Fahlman's 'S' quantity, computed for each candidate unit
            #perhaps construction of uneccesary temporary lists could be avoided with
            #generator expressions, but Numeric.sum doesn't seem to
            #fold a generator expression
            #S_c = self.computeS_c(V_p, V_avg, E_po, E_o_avg)
            #best = findMax(S_c)

            S_co = self.computeFahlmanS_co(V_p, V_avg, E_po, E_o_avg)
            #sign error when compared with Fahlman,  from our different convention for err (goal - actual or actual - goal)
            #Our quickprop rule is negated from what Fahlman has in his Cascade-correlation code (but not in his quickprop code?)
            #
            #We only use S_c to pick what we recruit so we need to fix its sign, alternatively we could probably find a min instead of a max
            #  but that obfuscates the intent and motivation of the algorithm even more
            S_co = -1.0 * S_co
            S_c = Numeric.sum(S_co)
            best = findMax([abs(cr) for cr in S_c])
            bestScore = abs(S_c[best])
            sigma_o = Numeric.sign(S_co)
            ep += 1
            self.totalEpoch += 1
            self.cor = S_co[:,best] #need to save this for in order to know a good initial weight from the newly recruited candidate to
            #                        the output layer
            self.correlations = S_co
            if ep == 1:
                previousBest = bestScore
            else:
                #if there is an appreciable change in the error we don't need to worry about stagnation
                if abs(bestScore - previousBest) > previousBest*self.changeThreshold:
                    self.quitEpoch = ep + self.patience
                    previousBest = bestScore
            if ep % self.candreportRate == 0: #simplified candidate epoch reporting mechanism
                print "Epoch: %6d | Candidate Epoch: %7d | Best score: %7.4f" % (self.totalEpoch, ep, previousBest)
        #self.totalEpoch += ep
        return best #return the index of the candidate we should recruit
    def updateCandidateLayer(self, dSdw_bias, c):
        """
        Updates the information used in changing the bias weight for the cth candidate unit in the candidate layer.
        """
        #let g(x) = -f(x), dg/dx = -df/dx since we maximize correlation (S) but minimize error
        self["candidate"].wed[c] = -1.0*dSdw_bias + self["candidate"].weight[c] * self.decay
    def updateConnection(self, conxn, dSdw):
        self[conxn.fromLayer.name, conxn.toLayer.name].wed = -1.0* dSdw +conxn.weight*self.decay
    def computeDataFromProp(self):
        """
        Computes data based on propagation that need not be recomputed between candidate weight changes.
        """
        self.setLayerVerification(0)
        E_po, outputs = [0 for i in self.loadOrder], [0 for i in self.loadOrder]
        layerActivations = {}
        for i in self.loadOrder: #for each training pattern, save all the information that will be needed later
            self.propagate(**self.getData(i))
            for layer in self.layers:
                if layer.name not in ("candidate", "output"):
                    layerActivations[(i, layer.name)] = layer.activation
            E_po[i] = self.errorFunction(self["output"].target, self["output"].activation) #need not be recomputed later
            outputs[i] = self["output"].activation #need not be recomputed later
        E_o_avg = [E/len(E_po) for E in Numeric.sum(E_po)] # list of the average error over all patterns for each output
        return (Numeric.array(E_po), Numeric.array(E_o_avg), Numeric.array(outputs), layerActivations)
    def computeChangingDataFromProp(self, layerActivations):
        """
        Computes data based on propagation that needs to be recomputed between candidate weight changes.
        """
        # passes in layerActivations so that we could take advantage, but don't yet
        # initial experiments should that this slowed down processing
        V_p, netInptToCnd = [0 for i in self.loadOrder], [0 for i in self.loadOrder]
        for i in self.loadOrder:
            self.propagate(**self.getData(i))
            netInptToCnd[i] = self["candidate"].netinput
            V_p[i] = [neuron.activation for neuron in self["candidate"]]
        return (Numeric.array(V_p), Numeric.array(netInptToCnd))
    def computeS_c(self, V_p, V_avg, E_po, E_o_avg):
        """
        S_c is a list of the covariances for each candidate, or
        Fahlman's 'S' quantity, computed for each candidate unit
        perhaps construction of uneccesary temporary lists could be avoided with
        generator expressions, but Numeric.sum doesn't seem to
        evaluate a generator expression
        """
        return Numeric.sum(Numeric.fabs(Numeric.sum(
            [[Numeric.multiply( Numeric.subtract(V_p[i], V_avg), E_po[i][j] - E_o_avg[j])  
                for j in range(len(E_po[0])) ] for i in range(len(V_p)) ])))
    def computeFahlmanS_co(self, V_p, V_avg, E_po, E_o_avg):
        return (Numeric.array([Numeric.sum(Numeric.transpose(Numeric.multiply(Numeric.transpose(V_p), E_po[:,c]))) \
                               for c in range(len(E_po[0]))]) - V_avg*E_o_avg)/Numeric.sum(Numeric.sum(E_po*E_po))
    def compute_dSdw(self, sigma_o, E_po, E_o_avg, netInptToCnd, layerActivations, conxn):
        """
        Computes dSdW for a specific connection to the candidate layer.
        """
        numOutputs = len(E_po[0])
        return Numeric.array([[Numeric.sum( [Numeric.sum( \
                    [sigma_o[i][col]*(E_po[p][i] - E_o_avg[i])*self.actDeriv( netInptToCnd[p][col] )*layerActivations[(p, conxn.fromLayer.name)][row] \
                     for p in self.loadOrder]) for i in range(numOutputs)] ) \
                                 for col in range(len(conxn.weight[0]))] for row in range(len(conxn.weight))])
        
    def done(self):
        return len(self) >= (self.maxHidden + 3)
    def trainOutputs(self, sweeps, cont = 0):
        """
        Trains the outputs until self.patience epochs have gone by since a noticable change in the error,
        error drops below the threshold (either self.stopPercent or cross validation if self.useCrossValidationToStop
        is set), or a maximum number of training epochs have been performed.
        """
        print "Output phase    ------------------------------------"
        self["output"].active = 1 #make sure output layer is active, afterall, that is what we are training in this function
        self["candidate"].active = 0 #in fact, don't let the candidate layer do anything!  Hopefully this won't cause problems
        self.quitEpoch = self.patience
        for layer in self.layers:
            layer.wedLast = Numeric.zeros(layer.size, 'f')
            layer.dweight = Numeric.zeros(layer.size, 'f')
        for connection in self.connections:
            connection.wedLast =  Numeric.zeros((connection.fromLayer.size, connection.toLayer.size), 'f')
            connection.dweight =  Numeric.zeros((connection.fromLayer.size, connection.toLayer.size), 'f')
        # check architecture
        self.complete = 0
        self.verifyArchitecture()
        tssErr = 0.0; rmsErr = 0.0; totalCorrect = 0; totalCount = 1; totalPCorrect = {}
        if not cont: # starting afresh
            self.resetFlags()
            self.epoch = 0
            self.reportStart()
            self.resetCount = 1
            self.epoch = 1
            self.lastLowestTSSError = sys.maxint # some maximum value (not all pythons have Infinity)
            if sweeps != None:
                self.resetEpoch = sweeps
        else:
            if sweeps != None:
                self.resetEpoch = self.epoch + sweeps - 1
        while self.doWhile(totalCount, totalCorrect):
            (tssErr, totalCorrect, totalCount, totalPCorrect) = self.sweep()
            self.complete = 1
            if totalCount != 0:
                rmsErr = math.sqrt(tssErr / totalCount)
            else:
                self.Print("Warning: sweep didn't do anything!")
            if self.epoch % self.reportRate == 0:
                self.reportEpoch(self.epoch, tssErr, totalCorrect, totalCount, rmsErr, totalPCorrect)
                if len(self.crossValidationCorpus) > 0 or self.autoCrossValidation:
                    (tssCVErr, totalCVCorrect, totalCVCount, totalCVPCorrect) = self.sweepCrossValidation()
                    rmsCVErr = math.sqrt(tssCVErr / totalCVCount)
                    self.Print("CV    #%6d | TSS Error: %.4f | Correct: %.4f | RMS Error: %.4f" % \
                               (self.epoch, tssCVErr, totalCVCorrect * 1.0 / totalCVCount, rmsCVErr))
                    if self.autoSaveWeightsFile != None and tssCVErr < self.lastLowestTSSError:
                        self.lastLowestTSSError = tssCVErr
                        self.saveWeightsToFile(self.autoSaveWeightsFile)
                        self.Print("auto saving weights to '%s'..." % self.autoSaveWeightsFile)
                    if totalCVCorrect * 1.0 / totalCVCount >= self.stopPercent and self.useCrossValidationToStop:
                        self.epoch += 1
                        self.totalEpoch += 1
                        break
            if self.resetEpoch == self.epoch:
                self.Print("Reset limit reached; ending without reaching goal")
                self.epoch += 1
                self.totalEpoch += 1
                self.complete = 0
                break
            self.epoch += 1
            self.totalEpoch += 1
            ################
            #if there is an appreciable change in the error we don't need to worry about stagnation
            if abs(tssErr - self.previousError) > self.previousError*self.changeThreshold:
                self.previousError = tssErr
                self.quitEpoch = self.epoch + self.patience
            elif self.epoch == self.quitEpoch:
                break #stagnation occured, stop training the outputs
            ################
        #print "----------------------------------------------------"
        if totalCount > 0:
            self.reportFinal(self.epoch, tssErr, totalCorrect, totalCount, rmsErr, totalPCorrect)
            if len(self.crossValidationCorpus) > 0 or self.autoCrossValidation:
                (tssCVErr, totalCVCorrect, totalCVCount, totalCVPCorrect) = self.sweepCrossValidation()
                rmsCVErr = math.sqrt(tssCVErr / totalCVCount)
                self.Print("CV    #%6d | TSS Error: %.4f | Correct: %.4f | RMS Error: %.4f" % \
                           (self.epoch-1, tssCVErr, totalCVCorrect * 1.0 / totalCVCount, rmsCVErr))
                if self.autoSaveWeightsFile != None and tssCVErr < self.lastLowestTSSError:
                    self.lastLowestTSSError = tssCVErr
                    self.saveWeightsToFile(self.autoSaveWeightsFile)
                    self.Print("auto saving weights to '%s'..." % self.autoSaveWeightsFile)
        else:
            print "Final: nothing done"
        #print "----------------------------------------------------"
        #self.totalEpoch += self.epoch
        return (totalCorrect * 1.0 / totalCount <  self.stopPercent) #true means we continue
    
    def addCandidateLayer(self, size=8):
        """
        Adds a candidate layer for recruiting the new hidden layer cascade
        node. Connect it up to all layers except outputs.
        """
        self.addLayer("candidate", size, position = -1)
        for layer in self:
            if layer.type != "Output" and layer.name != "candidate":
                self.connectAt(layer.name, "candidate", position = -1)
        self.correlations = [[0.0 for n in range(size)] for m in range(self["input"].size)] # initialize corrleations (for printing)
    def recruit(self, n):
        """
        Grab the Nth candidate node and all incoming weights and make it
        a layer unto itself. New layer is a frozen layer.
        """
        print "Recruiting candidate: %d, correlation(s): %s" % (n, self.correlations[:,n])
        # first, add the new layer:
        hcount = 0
        for layer in self:
            if layer.type == "Hidden": 
                hcount += 1
        hname = "hidden%d" % hcount
        hsize = 1 # wonder what would happen if we added more than 1?
        self.addLayer(hname, hsize, position = -2)
        # copy all of the relevant data:
        for i in range(hsize):
            self[hname].dweight[i] = self["candidate"].dweight[i + n]
            self[hname].weight[i] = self["candidate"].weight[i + n]
            self[hname].wed[i] = self["candidate"].wed[i + n]
            self[hname].wedLast[i] = self["candidate"].wedLast[i + n]
        self[hname].frozen = 1 # don't change these biases
        #in case we are using a different activation function
        #     the fact that this code needs to be here is indicative of a poor design in Conx
        self[hname].minTarget, self[hname].minActivation = self["candidate"].minTarget, self["candidate"].minActivation
        # first, connect up input
        for layer in self: 
            if layer.type == "Input" and layer.name != hname: # includes contexts
                self.connectAt(layer.name, hname, position = 1)
                self[layer.name, hname].frozen = 1 # don't change incoming weights
        # next add hidden connections
        if self.incrType == "cascade": # or parallel
            for layer in self: 
                if layer.type == "Hidden" and layer.name not in [hname, "candidate"]: 
                    self.connectAt(layer.name, hname, position = -1)
                    self[layer.name, hname].frozen = 1 # don't change incoming weights
        # and then output connections
        for layer in self: 
            if layer.type == "Output" and layer.name not in ["candidate", hname]: 
                self.connectAt(hname, layer.name, position = -1)
                # not frozen! Can change these hidden to the output
        # now, let's copy the weights, and randomize the old ones:
        for c in self.connections:
            if c.toLayer.name == "candidate":
                for i in range(hsize):
                    for j in range(c.fromLayer.size):
                        if self.isConnected(c.fromLayer.name, hname):
                            self[c.fromLayer.name, hname][j][i] = self[c.fromLayer.name, "candidate"][j][i + n]
                if self.isConnected(c.fromLayer.name, hname):
                    self[c.fromLayer.name, "candidate"].randomize(1)
            elif c.fromLayer.name == "candidate":
                for i in range(c.toLayer.size):
                    for j in range(hsize):
                        if self.isConnected(hname, c.toLayer.name):
                            self[hname, c.toLayer.name][j][i] = self["candidate", c.toLayer.name][j + n][i]
                if self.isConnected(hname, c.toLayer.name):
                    self["candidate", c.toLayer.name].randomize(1)
        self["candidate"].randomize(1)
        # finally, connect new hidden to candidate
        self.connectAt(hname, "candidate", position = -1)
        self[hname, "output"].weight = Numeric.array( [ -1.0 * self.cor ])

