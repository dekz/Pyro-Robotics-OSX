"""
Adaptive Resonance Theory, Fuzzy ART and ARTMap classes.
Based on Matlab code by Aaron Garrett and Python code by Terry Stewart
at http://www.carleton.ca/ics/courses/cgsc5001/index_old.html

Author: D.S. Blank <dblank@cs.brynmawr.edu>
"""
## Current limitations:
#  - ARTMap supervisor is a symbol, whether a string, number, or list
#  - not certain about this fuzzyAnd business

# useful functions
def complementCode(data):
  """ Constructs complement code pairs [n, 1 - n, ...] for n in data """
  r = []
  for n in data:
    r.append(n)
    r.append(1 - n)
  return r
def inner(a, b):
  import operator
  return float(reduce(operator.add, [x * y for (x, y) in zip(a, b)]))    
def fuzzyAnd(a, b):
  """ Fuzzy AND uses min(); scale by total 1's """
  match=0.0
  total=0.0
  for i in range(len(a)):
    match += min(a[i], b[i])
    total += a[i]
  if total == 0:
    return 0.0
  else:
    return match/total
def format(list, dec = 1):
  """ Formats a list for display. dec is decimal places """
  return "[" + ", ".join([("%."+("%d"%dec)+"f") % num for num in list]) + "]"
def mformat(matrix, dec = 1, width = 5, missing = '.'):
  retval = "  " + (" " * width)
  for col in range(len(matrix[0])):
    retval += ("%" + ("%d" % width) + "d") % (col, )
  retval += "\n"
  retval += (" " * width) + " +"
  for col in range(len(matrix[0])):
    retval += "-" * width
  retval += "\n"
  r = 0
  for row in matrix:
    retval += ("%" + ("%d" % width) + "d |") % r
    for num in row:
      if num == None: 
        retval += ("%" + ("%d" % width) + "s") % missing
      else:
        retval += ("%" + ("%d" % width) + "d") % (num, )
    retval += "\n"
    r += 1
  return retval
def makePattern(dict, symbol, size, localist = 0):
  import random
  if symbol in dict:
    return dict[symbol]
  else:
    if localist:
      pattern = [0] * size
      pattern[random.randint(0, size - 1)] = 1
    else:
      pattern = [random.randint(0, 1) for i in range(size)]
    while pattern in dict.values():
      if localist:
        pattern = [0] * size
        pattern[random.randint(0, size - 1)] = 1
      else:
        pattern = [random.randint(0, 1) for i in range(size)]
    dict[symbol] = pattern
    return pattern
class ART:
  """ Adaptive Resonance Theory, Fuzzy ART class """
  def __init__(self, numFeatures, maxNumCategories=None, vigilance=0.75,
               bias=0.000001, learningRate=1.0, complementCode=False):
    """
    numFeatures: size of data patterns and weights
    maxNumCategories: maximum categories
    vigilance: standard threshold; 0 means it rarely says "I do not know"
       (if it does not know during learning, it will make a new category)
    bias: avoid dividing by zero
    learningRate: 1.0 is "fast learning"
    complementCode: often needed for binary codes
    """
    if complementCode: numFeatures *= 2
    self.numFeatures = numFeatures
    self.numCategories = 0
    self.maxNumCategories = maxNumCategories
    self.vigilance = vigilance
    self.bias = bias
    self.learningRate = learningRate
    self.complementCode = complementCode
    self.weight=[]
  
  def __str__(self):
    """ String representation of a network """
    retval = "Model vectors:\n"
    i = 0
    for mv in self.weight:
      retval += "%d %s\n" % (i, format(mv))
      i += 1
    return retval

  def train(self, data, label = None, verbose = 0):
    """ Train all patterns. """
    if verbose: print "Training..."
    retval = [self.step(pattern, label, verbose) for pattern in data]
    if verbose: print "Training done!"
    return retval

  def step(self, currentData, label = None, verbose = 0):
    """ Train one pattern. Returns category number. """
    if self.complementCode: currentData = complementCode(currentData)
    print "Input:", format(currentData)
    categoryActivation = self.activateCategories(currentData)
    sorted=[(categoryActivation[i],i) for i in range(self.numCategories)]
    sorted.reverse() 
    currentSortedIndex = 0
    while 1:
      if self.numCategories == 0:
        # no categories yet (first time); add a category
        self.weight.append([1.0] * self.numFeatures)
        self.updateWeights(currentData, self.weight[0])
        self.numCategories += 1 # now is 1
        if verbose: print "Cat 0:", format(self.weight[0])
        return 0 # winning category
      # at least one category
      currentActivation, currentCategory = sorted[currentSortedIndex]
      currentWeightVector = self.weight[currentCategory]
      match = self.calculateMatch(currentData, currentWeightVector)
      # if match value is close enough:
      if match > self.vigilance:
        # update the weights
        change = self.updateWeights(currentData,self.weight[currentCategory])
        if verbose:
          print "Cat %d:" % currentCategory, format(self.weight[currentCategory])
        return currentCategory
      else:
        if currentSortedIndex == self.numCategories - 1:
          if (self.maxNumCategories!=None and
              self.numCategories==maxNumCategories):
            if verbose: print "No winner"
            return None
          else:
            self.weight.append([1.0]*self.numFeatures)
            self.updateWeights(currentData,self.weight[-1])
            self.numCategories += 1
            if verbose: print "Cat %d:" % (self.numCategories - 1), format(self.weight[self.numCategories - 1])
            return self.numCategories - 1
        else:
          currentSortedIndex+=1

  def activateCategories(self, input):
    """ Propagate the activation to the category layer. Returns activations."""
    r = []
    for j in range(self.numCategories):
      match=0
      weight=0
      for i in range(self.numFeatures):
        match += min(input[i], self.weight[j][i])
        weight += self.weight[j][i]
      r.append(match / (self.bias + weight))
    return r

  def updateWeights(self, input, weight):
    """ Update the weights; returns 1 if actually changes the weights """
    a = self.learningRate
    change = 0
    for i in range(len(input)):
      if input[i] < weight[i]:
        weight[i] = (a*input[i]) + ((1-a)*weight[i])
        change = 1
    return change

  def calculateMatch(self, a, b):
    return fuzzyAnd(a, b)
    #return inner(a, b) / inner(a, a)

  def categorize(self, input, verbose = 0):
    """ Find the closest model vector (category) """
    if self.complementCode: input = complementCode(input)
    if verbose:
      print format(input), "=>", 
    categoryActivation = self.activateCategories(input)
    sorted=[(categoryActivation[i],i) for i in range(self.numCategories)]
    sorted.reverse()
    resonance=0
    match=0
    currentSortedIndex = 0
    while resonance == 0:
        currentActivation,currentCategory = sorted[currentSortedIndex]
        currentWeightVector = self.weight[currentCategory]
        match = self.calculateMatch(input, currentWeightVector)
        if match > self.vigilance:
          if verbose: print currentCategory
          return currentCategory
        else:
          if currentSortedIndex == self.numCategories - 1:
            # End of the line!
            if verbose: print None
            return None
          else:
            currentSortedIndex += 1

  def categorizeAll(self, input, verbose = 0):
    return [self.categorize(x, verbose) for x in input]
    
  def displayConfusionMatrix(self, outputs, testSet):
    # calculate and print confusion matrix
    size = max(outputs) + 1
    matrix=[[0 for j in range(size + 1)] for i in range(size)]
    for i in range(len(testSet)):
      input, target = testSet[i]
      output = outputs[i]
      if output==None: output = size
      matrix[target][output] += 1
    print "Confusion Matrix:"
    r = 0
    print "       ",
    for col in range(len(matrix[0])):
      print "%5d" % (col, ),
    print
    print "       ",
    for col in range(len(matrix[0])):
      print "-" * 5,
    print
    for row in matrix:
      print "%5d |" % r,
      for num in row:
        print "%5d" % (num, ), 
      print
      r += 1

class ARTMap(ART):
  """ ARTMap extends ART. """
  def __init__(self, numFeatures, maxNumCategories=None,
               vigilance=0.75, bias=0.000001, learningRate=1.0,
               complementCode=0):
    self.weight=[]
    self.mapField=[]
    self.complementCode=complementCode
    if complementCode: numFeatures*=2
    self.numFeatures=numFeatures
    self.numCategories=0
    self.maxNumCategories=maxNumCategories
    #self.numClasses=numClasses
    self.vigilance=vigilance
    self.bias=bias
    self.learningRate=learningRate

  def train(self, patterns, verbose = 1):
    changes=0
    if verbose: print "Training..."
    for data, supervisor in patterns:
      if self.complementCode: data=complementCode(data)
      changes += self.step(data, supervisor, verbose)
    if verbose: print "Training done!"
    return changes

  def step(self, data, supervisor, verbose=1):
    if self.weight==[] or supervisor not in self.mapField:
      if verbose: print "New:", data, supervisor
      self.addNewCategory(data, supervisor)
      return 1
    activation=self.activateCategories(data)
    sorted=[(activation[i],i) for i in range(self.numCategories)]
    sorted.sort(lambda a,b: cmp(b,a))
    resonance=0
    currentSortedIndex=0
    while resonance==0:
      currentActivation,currentCategory=sorted[currentSortedIndex]
      currentWeightVector=self.weight[currentCategory]
      match=self.calculateMatch(data,currentWeightVector)
      if match < self.vigilance:
        if currentSortedIndex==self.numCategories-1:
          if self.maxNumCategories!=None and self.numCategories==self.maxNumCategories:
            resonance=1
          else:
            self.addNewCategory(data, supervisor)
            if verbose: print "New: (< vig)", data, supervisor
            return 1
        else:
          currentSortedIndex+=1
      else:
        if self.mapField[currentCategory]==supervisor:
          change=self.updateWeights(data,self.weight[currentCategory])
          if verbose: print "Update:", currentCategory
          return change
        else:
          v=match+0.000001
          if currentSortedIndex==self.numCategories-1:
            if self.maxNumCategories!=None and self.numCategories==self.maxNumCategories:
              resonance=1
            else:
              self.addNewCategory(data,supervisor)
              if verbose: print "New:", data, supervisor
              return 1
          else:
            resonance=0
            currentSortedIndex+=1
    print 'This Should Not Happen'
    return 0

  def addNewCategory(self,data,supervisor):
    self.weight.append([1.0]*self.numFeatures)
    self.mapField.append(0)
    self.updateWeights(data,self.weight[-1])
    self.numCategories+=1
    self.mapField[-1]=supervisor

  def classifyOne(self, input):
    if self.numCategories == 0: return None
    if self.complementCode: input=complementCode(input)
    activation=self.activateCategories(input)
    sorted=[(activation[i],i) for i in range(self.numCategories)]
    sorted.sort(lambda a,b: cmp(b,a))
    resonance=0
    currentSortedIndex=0
    while resonance==0:
      currentActivation,currentCategory=sorted[currentSortedIndex]
      currentWeightVector=self.weight[currentCategory]
      match=self.calculateMatch(input,currentWeightVector)
      if match<self.vigilance:
        if currentSortedIndex==self.numCategories-1:
            return None
        else:
          currentSortedIndex+=1
      else:
        return self.mapField[currentCategory]

  def classifyAll(self, input):
    return [self.classifyOne(x) for x in input]
    
  def classifyRange(self):
    retval = [[0 for i in range(10)] for j in range(10)]
    for row in range(10):
      for col in range(10):
        retval[col][row] = self.classifyOne((col/10., row/10.))
    return retval
    
  def testAll(self, patterns, verbose=0):
    output=[]
    error=0
    for data,supervisor in patterns:
      guess=self.classifyOne(data)
      output.append(guess)
      if guess != supervisor:
        if verbose: print "ERROR:",data,"guess:",guess,"answer:",supervisor
        error+=1
    return output, error

if __name__ == "__main__":
  #################################################################
  # Test ART:
  input=[(1,1,1,1,1,0,0,0,0,0,0,0),
         (1,1,1,0,1,0,0,0,0,0,0,0),
         (0,0,0,0,0,0,0,1,1,1,1,1),
         (1,1,0,1,1,0,0,0,0,0,0,0),
         (0,0,0,0,0,0,0,1,1,1,1,0),
         ]
  net = ART(12, complementCode = 1)
  result = net.train(input, verbose = 1)
  print 'Training results categories:', result
  print net
  print 'Testing results:'
  test=[[1,1,1,0,1,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,1,1,0,1,0],
        [0,0,0,0,0,1,1,0,0,0,0,0],
        [0,0,0,0,0,0.0,0.0,0.6,0.6,0.6,0.6,0.0]]
  for x in test:
    category = net.categorize(x, verbose = 1)
  #################################################################
  # Test ART:
  input=[(0.5,0.7),(0.3,0.4),(0.2,0.3),(0.91,0.55),(1.0,0.2)]
  net=ART(2, complementCode = 1)
  print net.train(input, verbose = 1)
  print "net.categorize((0.2, 0.4)) =>", net.categorize((0.2,0.4))
  print net
  #################################################################
  # Test ART:
  f = open("letters.50.in")
  labels = []
  inputs = []
  for line in f.readlines():
    line = line.split()
    labels.append(line[0])
    inputs.append([int(v) for v in line[1:]])
  f.close()
  network = ART(35, vigilance=.5)
  network.train(inputs[:26], verbose = 1)
  network.categorizeAll(inputs[26:])
  #################################################################
  # Test ARTMap:
  # some of this should become part of the class:
  import random, gzip
  # load the data from the file
  print "Reading data..."
  rawData=gzip.GzipFile('mushroom.data.gz').readlines()
  rawData=[x.split() for x in rawData]
  # convert the letters into a binary representation
  options=[]
  for i in range(len(rawData[0])):
    list=[]
    for r in rawData:
      x=r[i]
      if x not in list: list.append(x)
    options.append(list)
  patterns=[]
  for r in rawData:
    type=options[0].index(r[0])
    input=[]
    for i in range(1,len(r)):
      data=r[i]
      x=[0]*len(options[i])
      x[options[i].index(data)]=1
      input.extend(x)
    patterns.append((input,type))
  random.shuffle(patterns)
  # count up how many features (inputs), and how many classes (outputs)
  features = len(patterns[0][0])
  classes = len(options[0])
  trainingSetCount = 20
  testSetCount = 300
  # take the first few to be the training set
  trainSet = patterns[:trainingSetCount]
  # take the next bunch to be the test set (note: it takes a while
  #  if you use a bigger test set...)
  testSet = patterns[trainingSetCount:trainingSetCount+testSetCount]
  # make the network and train it
  a = ARTMap(features) #, classes)
  a.train(trainSet, verbose = 1)
  outputs, errors = a.testAll(testSet)
  a.displayConfusionMatrix(outputs, testSet)
  print 'Errors: %1.2f%%' % (errors*100.0/len(testSet))
  print a
  #################################################################
  # XOR ARTMap:
  net = ARTMap(2, complementCode = 1)
  patterns = [([1,1], 0), ([1,0], 1), ([0,1], 1), ([0,0], 0)]
  net.train(patterns, verbose = 1)
  print mformat(net.classifyRange(), width=2)
  print net
  #################################################################
  # letter identification
  net = ARTMap(35, complementCode = 0)
  fp = open("letters.50.in")
  pats = []
  catpat = {}
  for line in fp:
    category = line[0]
    pattern = [int(num) for num in line[2:].split()]
    pats.append((pattern, makePattern(catpat, category, 26, localist = 1)))
  net.train(pats[:26], verbose = 1)
  print net
  outputs, errors = net.testAll(pats[27:], verbose = 1)
  #net.displayConfusionMatrix(outputs, pats[27:])
  print 'Errors: %1.2f%%' % (errors*100.0/len(pats[27:]))
