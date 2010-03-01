import Numeric, math, random, sys
from pyrobot.tools.circularlist import CircularList

__author__ = "Jeremy Stober"
__version__ = "$Revision$"

class ModelList(CircularList):
    def __init__(self, bucketSize=5):
        CircularList.__init__(self)
        self.bucketSize = bucketSize
    def addItem(self, vector):
        tmp = CircularList(self.bucketSize)
        tmp.vector = vector
        tmp.counter = 0
        CircularList.addItem(self, tmp)
    def __str__(self):
        retval = ""
        for i in range(len(self)):
            retval += "Model vector: %s\n" % self[i].vector
            for j in range(len(self[i])):
                retval += "%s\n" % self[i][j]
        return retval
        
# general functions
def averageVector(V):
    """
    Determines the average vector of a set of vectors V.
    """
    return Numeric.add.reduce(V) / len(V)

def tooSmall(v):
    if v < 1.0e-32:
        return 0.0
    return v

def euclideanDistance(x, y, mask):
    """
    Takes two Numeric vectors as arguments.
    d(x, y) = sqrt(Sum[i = 1 to |x|]{(x_i - y_i) ^ 2 * mask_i})
    """
    try:
        result = math.sqrt(Numeric.add.reduce( ((x - y)  ** 2) * mask))
    except:
        x = Numeric.array(map(tooSmall, x))
        y = Numeric.array(map(tooSmall, y))
        result = math.sqrt(Numeric.add.reduce( ((x - y)  ** 2) * mask))
    return result

def getDistance(V, X, mask):
    """
    d(V, X) = (1/|X|) Sum[i = 1 to |X|]{ min[j = 1 to |V|] {|| x_i - v_j||} }
    where x_i is in X and v_j is in V.  
    """
    min = []
    sum = 0
    for x in X:
        for v in V:
            min.append(euclideanDistance(x,v,mask))
        sum += min[Numeric.argmin(min)]
    return sum / len(X)

def stringArray(a, newline = 1, width = 0, format = "%4.4f "):
    """
    String form of an array (any sequence of floats, really) to the screen.
    """
    s = ""
    cnt = 0
    if type(a) == type('string'):
        return a
    for i in a:
        s += format % i
        if width > 0 and (cnt + 1) % width == 0:
            s += '\n'
        cnt += 1
    if newline:
        s += '\n'
    return s

def logBaseTwo(value):
    """
    Returns integer ceil of log_2 of value.
    Python 2.3 should support different log bases.
    """
    if value < 2:
        return 1
    else:
        return int(math.ceil(math.log(value)/math.log(2)))

def makeBitList(maxbits = 8): 
    """ 
    This version is much more flexible as it relies on a general function 
    that takes any number and converts it to binary. You can make any 
    size bit representation that you want: 
    makeBitList(2) will give you: [[0, 0], [0, 1], [1, 0], [1, 1]] 
    for example. Defaults to 8 bits. 
    """ 
    retval = [] 
    for i in range((2 ** maxbits)): 
        retval.append( dec2bin(i, maxbits) ) 
    return retval 

def dec2bin(val, maxbits = 8): 
    """ 
    A decimal to binary converter. Returns bits in a list. 
    """ 
    retval = [] 
    for i in range(maxbits - 1, -1, -1): 
        bit = int(val / (2 ** i)) 
        val = (val % (2 ** i)) 
        retval.append(bit) 
    return retval

def makeNoisyList(ls, percentNoise=0.1, minVal=0.0, maxVal=1.0):
    """
    Returns a noisy version of the given list, and assumes a range
    of values between 0.0 and 1.0.
    """
    retval = []
    for i in range(len(ls)):
        if random.random() < 0.5:
            retval.append(max(ls[i] - (random.random() * percentNoise), minVal))
        else:
            retval.append(min(ls[i] + (random.random() * percentNoise), maxVal))
    return retval

def makeNoisySequence(sequence, repeat, percentNoise=0.1):
    """
    Returns a noisy version of the given sequence, with each item
    repeated the number of times designated by the repeat variable.
    """
    retval = []
    for i in range(len(sequence)):
        for j in range(repeat):
            retval.append(makeNoisyList(sequence[i], percentNoise))
    return retval

class RAVQ:
    """
    Implements RAVQ algorithm as described in Linaker and Niklasson.
    """
    def __init__(self, bufferSize, epsilon, delta, historySize=0):
        self.epsilon = epsilon
        self.delta = delta
        self.buffer = CircularList(bufferSize) # moving average buffer
        self.models = ModelList(historySize)
        self.mask = None 
        self.time = 0
        self.movingAverage = 'No Moving Average'
        self.movingAverageDistance = -1
        self.modelVectorsDistance = -1
        self.winner = 'No Winner'
        self.newWinnerIndex = -1
        self.previousWinnerIndex = -1
        self.verbosity = 0
        self.tolerance = delta
        self.addModels = 1
        self.winnerCount = 0
        self.printDistance = 0
        self.newModelVector = (None, None)
        self.mapModelVector = (None, None)
      
    # update the RAVQ
    def input(self, vec):
        """
        Drives the ravq. For most uses, the vector categorization
        is as simple as calling ravq.input(vec) on all vec in the
        dataset. Accessing the winning model vector (after the buffer
        is full) can be done directly. Using the get commands after
        calling input will return any information necessary from the
        ravq.
        """
        if self.verbosity > 1:
            print "Step:", self.time
        if self.verbosity > 2:
            print vec
        array = Numeric.array(vec, 'd')
        if self.mask == None:
            self.mask = Numeric.ones(len(array), 'd')
        self.buffer.addItem(array)
        if self.time >= len(self.buffer):
            self.process() 
        if self.verbosity > 2: print self
        self.time += 1
        return (self.newWinnerIndex, self.winner)

    # attribute methods
    def getNewWinner(self):
        """
        Returns boolean depending on whether or not there is a new
        winner after the last call to input.
        """
        if self.winnerCount > 0:
            return 0
        else:
            return 1
    def setMask(self, mask):
        """
        The mask serves to weight certain components of the inputs in
        the distance calculations.
        """
        self.mask = Numeric.array(mask, 'd')
    def getWinnerCount(self):
        """
        Returns the number of times the current winner has been the
        winner, ie. the number of consecutive calls to input where the
        current winner has been the winner.
        """
        return self.winnerCount
    def setVerbosity(self, value):
        """
        Determines which print statements to call.
        Debugging only.
        """
        self.verbosity = value
    def setAddModels(self, value):
        """
        Allows the RAVQ to dynamically add model vectors.
        """
        self.addModels = value
        
    # process happens once the buffer is full
    def process(self):
        """
        The RAVQ Algorithm:
        1. Calculate the average vector of all inputs in the buffer.
        2. Calculate the distance of the average from the set of inputs
        in the buffer.
        3. Calculate the distance of the model vectors from the inputs
        in the buffer.
        4. If distance in step 2 is small and distance in step 3 is large,
        add current average to list of model vectors.
        5. Calculate the winning model vector based on distance between
        each model vector and the buffer list.
        6. Update history.
        ---The metric used to calculate distance is described in
        "Sensory Flow Segmentation Using a Resource Allocating
        Vector Quantizer" by Fredrik Linaker and Lars Niklasson
        (2000).---
        """
        self.newModelVector = (None, None)
        self.setMovingAverage()
        self.setMovingAverageDistance()
        self.setModelVectorsDistance()
        if self.verbosity > 2:
            print "Moving average:", self.movingAverage
        if self.verbosity > 1:
            print "Moving average distance: ", self.movingAverageDistance
            print "Model vectors distance: ", self. modelVectorsDistance
        if self.addModels:
            self.updateModelVectors()
        self.updateWinner()
    def setMovingAverage(self):
        """
        Determine moving average.
        """
        self.movingAverage = averageVector(self.buffer.contents)
    def setMovingAverageDistance(self):
        """
        How close is the moving average to the current inputs?
        """
        self.movingAverageDistance = getDistance([self.movingAverage], self.buffer.contents, self.mask)
    def setModelVectorsDistance(self):
        """
        How close are the model vectors to the current inputs?
        """
        if len(self.models) != 0:
            self.modelVectorsDistance = getDistance([v.vector for v in self.models], self.buffer.contents, self.mask)
        else:
            self.modelVectorsDistance = self.epsilon + self.delta
    def updateModelVectors(self):
        """
        Update models vectors with moving average if the moving
        average is the best model of the inputs.
        """
        if self.movingAverageDistance <= self.epsilon and \
               self.movingAverageDistance <= self.modelVectorsDistance - self.delta:
            self.models.addItem(self.movingAverage)
            name = self.models.names[-1]
            self.newModelVector = (name, self.movingAverage)
            if self.verbosity > 1:
                print '***Adding model vector***'
                print 'Unique name', name
                print 'Moving avg dist', self.movingAverageDistance
                print 'Model vec dist', self.modelVectorsDistance
            if self.verbosity > 2:
                print 'New model vector', self.movingAverage

    def updateWinner(self):
        """
        Calculate the current winner based on which model vector is
        closest to the moving average.
        """
        min = []
        for m in self.models:
            min.append(euclideanDistance(m.vector, self.movingAverage, self.mask))
        if min == []:
            self.winner = 'No Winner'
        else:
            self.previousWinnerIndex= self.newWinnerIndex
            self.newWinnerIndex = Numeric.argmin(min)
            if self.previousWinnerIndex == self.newWinnerIndex:
                self.winnerCount += 1
            else:
                self.winnerCount = 0
            winner = self.models[self.newWinnerIndex]
            winner.counter += 1
            #if winner.maxSize != -1:
            winner.addItem(self.buffer[0])
            self.winner = winner.vector
    def distanceMap(self):
        """
        Calculate distance map.
        """
        map = []
        for x, y in [(x.vector,y.vector) for x in self.models for y in self.models]:
            map.append(euclideanDistance(x,y,self.mask))
        return map

    def __str__(self):
        """
        To display ravq just call print <instance>.
        """
        s = ""
        s += "Settings:\n"
        s += "Delta: " + str(self.delta) + " Epsilon: " + str(self.epsilon) + " Buffer Size: " + str(len(self.buffer)) + "\n"
        s += "Time: " + str(self.time) + "\n"
        if self.verbosity > 0:
            s += "Moving average distance: " +  "%4.4f " % self.movingAverageDistance + "\n"
            s += "Model vectors distance: " +  "%4.4f " % self.modelVectorsDistance + "\n"
            s += "Moving average:\n"
            s += "   " + stringArray(self.movingAverage)
            s += "Last winning model vector:\n"
            s += "   " + stringArray(self.winner)
            s += self.bufferString()
        s += self.modelString()
        if self.printDistance:
            s += "Distance map:\n"
            s += self.distanceMapAsString()
        if self.verbosity > 0:
            s += str(self.models)
        return s

    def distanceMapAsString(self):
        return stringArray(self.distanceMap(), 1, len(self.models), format="%4.2f ")

    def saveRAVQToFile(self, filename):
        import pickle
        fp = open(filename, 'w')
        pickle.dump(self, fp)
        fp.close()

    def loadRAVQFromFile(self, filename):
        import pickle
        fp = open(filename, 'r')
        self = pickle.load(fp)

    # helpful string methods, see __str__ method for use.
    def modelString(self):
        s = ""
        cnt = 0
        totalCount = 0
        totalIncompatibility = 0.0
        for m in self.models:
            s += ("%4d Model: " % cnt) + stringArray(m.vector) 
            sum = 0.0
            for b in m.contents:
                sum += euclideanDistance(m.vector, b, self.mask)
            totalIncompatibility += sum
            s += "     Count: %d Buffer size: %d Incompatibility: %f\n" % (m.counter, len(m.contents), sum)
            totalCount += m.counter
            cnt += 1            
        return ("%d Model vectors:\n" % cnt) + s + "Total model vectors  : %d\nTotal mapped vectors : %d\nTotal incompatibility: %f\n" % \
               (cnt, totalCount, totalIncompatibility)
    def bufferString(self):
        s = "Buffer:\n"
        for array in self.buffer:
            s += stringArray(array)
        return s

class ARAVQ(RAVQ):
    """
    Extends RAVQ as described in Linaker and Niklasson.
    """
    def __init__(self, bufferSize, epsilon, delta, historySize, learningRate):
        self.alpha = learningRate
        self.deltaWinner = 'No Winner'
        self.learning = 1
        RAVQ.__init__(self, bufferSize, epsilon, delta, historySize)
    def __str__(self):
        s = RAVQ.__str__(self)
        return s[:10] + "Alpha (learning rate): " + str(self.alpha) + " " + s[10:]
    def setLearning(self, value):
        self.learning = value
    def updateDeltaWinner(self):
        if not self.winner == 'No Winner':
            if self.verbosity > 3:
                print 'MAandW' , euclideanDistance(self.movingAverage, self.winner, self.mask)
                print 'MA' ,  self.movingAverageDistance
                print 'MV' ,  self.modelVectorsDistance
                print 'MVMD' ,  self.modelVectorsDistance - self.delta
            if euclideanDistance(self.movingAverage, self.winner, self.mask) < self.epsilon / 2:
                self.deltaWinner = self.alpha * (self.movingAverage - self.winner)
                if self.verbosity > 4: print 'Learning'
            else:
                self.deltaWinner = Numeric.zeros(len(self.winner)) 
        else:
            self.deltaWinner = 'No Winner'
    def learn(self):
        """
        Only updates the model vector, not the winner. Winner will change
        next time step anyway.
        """
        if self.deltaWinner != 'No Winner' and self.learning:
            if self.verbosity > 2: print "LEARNING: was:", self.models[self.newWinnerIndex].vector, "delta:", self.deltaWinner
            self.models[self.newWinnerIndex].vector += self.deltaWinner
        else:
            pass 
    def process(self):
        """
        Here we add the new learning methods.
        """
        RAVQ.process(self)
        self.updateDeltaWinner()
        self.learn()

if __name__ == '__main__':
    print "Creating a RAVQ using all possible lists of 8 bits"
    print "------------------------------------------------------------"
    bitlist = makeBitList()
    #parameters are buffer size, epsilon, delta, and history size
    ravq = RAVQ(4, 2.1, 1.1, 5)
    #ravq.setVerbosity(2)
    for bits in bitlist:
        ravq.input(bits)
    print ravq
    print "Distance map:"
    print ravq.distanceMapAsString()

    print "Creating an adaptive RAVQ using all possible lists of 8 bits"
    print "------------------------------------------------------------"
    #parameters are buffer size, epsilon, delta, history size, and alpha (learning rate)
    ravq = ARAVQ(4, 2.1, 1.1, 2, .2)
    #ravq.setVerbosity(2)
    for bits in bitlist:
        ravq.input(bits)
    print ravq
    print "Distance map:"
    print ravq.distanceMapAsString()

    print "Creating a RAVQ using a sequence of real-valued lists"
    print "------------------------------------------------------------"
    seq = makeNoisySequence([[0.0, 0.5, 1.0],
                             [0.5, 0.5, 0.5],
                             [1.0, 0.1, 0.1],
                             [0.9, 0.9, 0.9],
                             [0.3, 0.3, 0.8]], 5, 0.05)
    ravq = RAVQ(4, 2.1, 0.5, 2)
    #ravq.setVerbosity(2)
    for i in range(len(seq)):
        ravq.input(seq[i])
    print ravq
    
    print "Test the masking capability and distance measures"
    print "------------------------------------------------------------"
    print "mask:", ravq.mask
    print "Test masking functionality in euclidean distance calc's:", 
    print euclideanDistance(Numeric.array([1,2]),
                            Numeric.array([3,5]),
                            Numeric.array([1,0]))
    print ravq
    print "Saving to file..."
    ravq.saveRAVQToFile('test.ravq')
    print "Loading from file..."
    ravq.loadRAVQFromFile('test.ravq')
    print "Comparing after save..."
    print ravq
    print "Done testing!"
