"""
A simple Genetic Algorithm in Python
"""

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision$"

import Numeric, math, random, time, sys, string
from copy import deepcopy

def display(v):
    print v,

def sum(a):
    sum = 0
    for n in a:
        sum += n
    return sum

def flip(probability):
    """
    Flip a biased coin
    """
    return random.random() <= probability


# The classes:
#  Gene - specifics of gene representation 
#  Population - collection of Genes
#  GA - the parameters of evolution

class Gene:
    def __init__(self, **args):
        self.verbose = 0
        self.genotype = []
        self.fitness = 0.0
        self.mode = 'float'
        self.crossoverPoints = 1
        self.bias = 0.5
        self.min = -1 # inclusive
        self.max = 1 # inclusive
        self.imin = -1 # inclusive, initial
        self.imax = 1 # inclusive, initial
        self.maxStep = 1
        self.args = args
        self.alphabet = "abcdefghijklmnopqrstuvwxyz "
        if args.has_key('verbose'):
            self.verbose = args['verbose']
        if args.has_key('min'):
            self.min = args['min']
            self.imin = args['min']
        if args.has_key('max'):
            self.max = args['max']
            self.imax = args['max']
        if args.has_key('imin'):
            self.imin = args['imin']
        if args.has_key('imax'):
            self.imax = args['imax']
        if args.has_key('maxStep'):
            self.maxStep = args['maxStep']
        if args.has_key('crossoverPoints'):
            self.crossoverPoints = args['crossoverPoints']
        if args.has_key('mode'):
            self.mode = args['mode']
        if args.has_key('bias'):
            self.bias = args['bias']
        for i in range(args['size']):
            if self.mode == 'bit':
                self.genotype.append( random.random() < self.bias)
            elif self.mode == 'integer':
                self.genotype.append( math.floor(random.random() *
                                                 (self.imax - self.imin + 1)) + self.imin)
            elif self.mode == 'float':
                self.genotype.append( (random.random() * (self.imax - self.imin)) + self.imin)
            elif self.mode == 'char':
                self.genotype.append( self.alphabet[int(random.random() * len(self.alphabet)) ] )
            else:
                raise "unknownMode", self.mode

    def copy(self):
        return deepcopy(self)

    def __getitem__(self, val):
        return self.genotype[val]

    def __len__(self):
        return len(self.genotype)

    def display(self):
        if self.mode == 'bit' or self.mode == 'integer': 
            print string.join(map(lambda v: `int(v)`, self.genotype), "")
        elif self.mode == 'float':
            map(lambda v: display("%3.2f" % v), self.genotype)
        elif self.mode == 'char':
            print string.join(self.genotype, '')
        else:
            raise "unknownMode", self.mode

    def mutate(self, mutationRate):
        """
        Depending on the mutationRate, will mutate the genotype.
        """
        for i in range(len(self.genotype)):
            if flip(mutationRate):
                if self.verbose > 2:
                    print "mutating at position", i
                if self.mode == 'bit': 
                    self.genotype[i] = not self.genotype[i]
                elif self.mode == 'integer': 
                    r = random.random()
                    if (r < .33):
                        self.genotype[i] += round(random.random() * self.maxStep)
                        self.genotype[i] = min(self.genotype[i], self.max) 
                    elif (r < .67):
                        self.genotype[i] -= round(random.random() * self.maxStep)
                        self.genotype[i] = max(self.genotype[i], self.min) 
                    else:
                        self.genotype[i] = round(random.random() * (self.max - self.min + 1)) + self.min
                elif self.mode == 'float': 
                    r = random.random()
                    if (r < .33):
                        self.genotype[i] += (random.random() * self.maxStep)
                        self.genotype[i] = min(self.genotype[i], self.max) 
                    elif (r < .67):
                        self.genotype[i] -= (random.random() * self.maxStep)
                        self.genotype[i] = max(self.genotype[i], self.min) 
                    else:
                        self.genotype[i] = (random.random() * (self.max - self.min)) + self.min
                elif self.mode == 'char':
                    self.genotype[i] = self.alphabet[ int(random.random() * len(self.alphabet)) ]
                else:
                    raise "unknownMode", self.mode

    def crossover(self, parent2, crossoverRate):
        """
        Depending on the crossoverRate, will return two new children
        created by crossing over the given parents at a single point,
        or will return copies of the parents.
        """
        parent1 = self
        geneLength = len(parent1.genotype)
        if flip(crossoverRate):
            p1 = parent1.genotype[:]
            p2 = parent2.genotype[:]
            child1 = [0] * geneLength
            child2 = [0] * geneLength
            # go through and pick the crossoverpoints:
            if self.crossoverPoints == -3:
                # one right in middle
                crossPoints = [0] * geneLength
                crossPoints[int(geneLength/2)] = 1
            elif self.crossoverPoints == -2:
                # no crossoverpoints; I know, this should be zero
                crossPoints = [0] * geneLength
            elif self.crossoverPoints == -1:
                # shuffle: every other one
                crossPoints = [1] * geneLength
            elif self.crossoverPoints > 0:
                # number of cross points:
                # NOTE: not guaranteed to be exactly that many;
                # could duplicate randomly
                crossPoints = [0] * geneLength
                for i in range(self.crossoverPoints):
                    crossPoints[(int)(random.random() * geneLength)] = 1
            elif self.crossoverPoints == 0:
                # uniform crossover when crossoverPoints = 0
                crossPoints = [0] * geneLength
                for i in range(geneLength):
                    # flip coin for each position:
                    if random.random() < .5:
                        crossPoints[i] = 1
            else:
                raise "unknownCrossoverType", self.crossoverPoints
            # now, each time there is a cross point, swap parents
            for i in range(geneLength):
                if crossPoints[i]:
                    if self.verbose > 2:
                        print "crossing over at point", i
                    p1, p2 = p2, p1
                child1[i] = p1[i]
                child2[i] = p2[i]
            new_child1 = self.__class__(**self.args)
            new_child2 = self.__class__(**self.args)
            new_child1.genotype = child1
            new_child2.genotype = child2
            return new_child1, new_child2
        else:
            if self.verbose > 2:
                print "no crossover"
            return parent1.copy(), parent2.copy()

class Population:
    def __init__(self, cnt, geneConstructor, **args):
        self.sumFitness = 0   
        self.avgFitness = 0   
        self.individuals = []
        self.eliteMembers = []
        self.elitePercent = 0.0
        self.bestMember = -1
        self.size = cnt
        self.verbose = 0
        self.args = args
        self.geneConstructor = geneConstructor
        if args.has_key('elitePercent'):
            self.elitePercent = args['elitePercent']
        if args.has_key('verbose'):
            self.verbose = args['verbose']
        for i in range(cnt):
            self.individuals.append(geneConstructor(pos = i,
                                                    popSize = cnt,
                                                    **args))
    def copy(self):
        newPop = self.__class__(0, self.geneConstructor, **self.args)
        newPop.size = self.size
        for i in range(self.size):
            newPop.individuals.append( self.individuals[i].copy() )
        return newPop
        
    def __getitem__(self, val):
        return self.individuals[val]

    def __len__(self):
        return len(self.individuals)

    def select(self):
        """
        Select a single individual via the roulette wheel method.
        Algorithm from Goldberg's book, page 63.  NOTE: fitness
        function must return positive values to use this method
        of selection.
        """
        index = 0
        partsum = 0.0
        if self.sumFitness == 0:
            raise "Population has a total of zero fitness"
        spin = random.random() * self.sumFitness
        while index < self.size-1:
            fitness = self.individuals[index].fitness
            if fitness < 0:
                raise "Negative fitness in select", fitness
            partsum += self.individuals[index].fitness
            if partsum >= spin:
                break
            index += 1
        if self.verbose > 2:
            print "selected",
            self.individuals[index].display(),
            print "fitness", self.individuals[index].fitness
        return self.individuals[index].copy()

    def statistics(self):
        """
        Maintains important statistics about the current population.
        It calculates total fitness, average fitness, best fitness,
        and worst fitness.  Stores the best individual in the variable
        self.bestMember.  When the elitePercent is greater than zero,
        this method also maintains a list of the elite members of the
        population so that they can be saved for the next generation.
        """
        self.sumFitness = 0
        best = self.individuals[0]
        best.bestPosition = 0
        worst= self.individuals[0]
        self.eliteMembers = self.individuals[0:int(self.elitePercent * len(self.individuals))]
        self.eliteMembers.sort(lambda x, y: cmp( x.fitness, y.fitness))
        for i in range(self.size):
            current = self.individuals[i]
            current.position = i #needed to save the elite members of the population
            self.sumFitness += current.fitness
            if current.fitness < worst.fitness:
                worst = current
            if current.fitness > best.fitness:
                best = current
                best.bestPosition = i
            if len(self.eliteMembers) > 0 and current.fitness > self.eliteMembers[0].fitness:
                self.eliteMembers.append( current )
                self.eliteMembers.sort(lambda x, y: cmp( x.fitness, y.fitness))
                self.eliteMembers = self.eliteMembers[1:]
        self.bestMember = best
        self.avgFitness = (self.sumFitness * 1.0) / self.size
        if self.verbose > 0:
            print "Fitness: Total", "%7.2f" % self.sumFitness, 
            print "Best", "%5.2f" % best.fitness,
            print "Average", "%5.2f" % self.avgFitness,
            print "Worst", "%5.2f" % worst.fitness
            print "Elite fitness:", map( lambda x: x.fitness, self.eliteMembers)
            sys.stdout.flush()

class GA:
    """
    Class which defines everything needed to run a GA.
    """
    def __init__(self, population, **args):
        self.averageLog = None
        self.bestLog = None
        self.mutationRate = 0.1
        self.crossoverRate = 0.6
        self.maxGeneration = 0
        self.generation = 0
        self.verbose = 0
        if args.has_key('verbose'):
            self.verbose = args['verbose']
        if args.has_key('mutationRate'):
            self.mutationRate = args['mutationRate']
        if args.has_key('crossoverRate'):
            self.crossoverRate = args['crossoverRate']
        if args.has_key('maxGeneration'):
            self.maxGeneration = args['maxGeneration']
        x = random.random() * 100000 + time.time()
        self.setSeed(x)
        self.origPop = population
        if self.verbose > 0:
            print "crossoverRate  = %.3f" % self.crossoverRate
            print "mutationRate   = %.3f" % self.mutationRate
            print "populationSize = %d" % self.origPop.size
            print "elitePercent   = %.3f" % self.origPop.elitePercent
            print "maxGeneration  = %d" % self.maxGeneration
            print "================================================================================"
        self.setup(**args)
        self.reInitialize()

    def setup(self, **args):
        pass
    
    def reInitialize(self):
        self.pop = self.origPop.copy()
        self.initialize()

    def initialize(self):
        self.applyFitnessFunction() 
        if self.verbose > 0:
            print "-" * 60
            print "Initial population"
        self.pop.statistics()
        if self.verbose > 1:
            self.display()

    def logAverageFitness(self, filename="GAAvgFitness"):
        self.averageLog = open(filename, 'w')

    def logBestFitness(self, filename="GABestFitness"):
        self.bestLog = open(filename, 'w')

    def isDone(self):
        # Override this
        pass

    def fitnessFunction(self, genePosition, **args):
        # Override this
        pass

    def applyFitnessFunction(self):
        for i in range( len(self.pop.individuals) ):
            self.pop.individuals[i].fitness = self.fitnessFunction(i)
            
    def setSeed(self, value):
        self.seed = value
        random.seed(self.seed)

    def display_one(self, p):
        self.pop.individuals[p].display()
        print "Fitness:", self.pop.individuals[p].fitness

    def display(self):
        print "Population:"
        for p in range(len(self.pop.individuals)):
            self.display_one(p)

    def generate(self):
        """
        Iteratively creates a new population from the current population.
        Selects two parents, attempts to cross them, and then attempts to
        mutate the resulting children.  The probability of these operations
        occurring is determined by the crossoverRate and the mutationRate.
        Overwrites the old population with the new population.
        """
        newpop = range(self.pop.size)
        i = 0
        while i < self.pop.size - 1:
            parent1 = self.pop.select()
            parent2 = self.pop.select()
            newpop[i], newpop[i+1] = parent1.crossover(parent2, self.crossoverRate)
            newpop[i].mutate(self.mutationRate)
            newpop[i+1].mutate(self.mutationRate)
            i += 2
        # For odd sized populations, need to create the last child
        if self.pop.size % 2 == 1:
            newpop[self.pop.size-1] = self.pop.select()
            newpop[self.pop.size-1].mutate(self.mutationRate)
        # Copy new generation into population
        elitePositions = map( lambda x: x.position, self.pop.eliteMembers)
        for i in range(self.pop.size):
            if i not in elitePositions:
                self.pop.individuals[i] = newpop[i]
    
    def evolve(self, cont = 0):
        if not cont:
            self.generation = 0
        else:
            if self.generation == self.maxGeneration:
                self.maxGeneration = self.generation + 100
        while self.generation < self.maxGeneration or self.maxGeneration == 0:
            self.generation += 1
            if self.verbose > 0:
                print "-" * 60
                print "Generation", self.generation
            self.generate()
            self.applyFitnessFunction()
            self.pop.statistics()
            if self.bestLog != None:
                self.bestLog.write("%d %5.2f\n" %
                                          (self.generation,
                                           self.pop.bestMember.fitness))
            if self.averageLog != None:
                self.averageLog.write("%d %5.2f\n" %
                                         (self.generation,
                                          self.pop.avgFitness))
            if self.verbose > 1:
                self.display()
            if self.isDone():
                break
        print "-" * 60
        print "Done evolving at generation", self.generation
        print "Current best individual [#%d]" % self.pop.bestMember.bestPosition,
        self.pop.bestMember.display()
        print "Fitness", self.pop.bestMember.fitness

    def saveToFile(self, filename):
        import pickle
        fp = open(filename, "w")
        if self.verbose > 0:
            print "Saving GA to '%s'..." % (filename,)
        pickle.dump(self, fp)
        fp.close()

    def loadFromFile(self, filename):
        # probably just copy this... no need to create an entire object
        # to load another one.
        import pickle
        fp = open(filename, "w")
        if self.verbose > 0:
            print "Loading GA from '%s'..." % (filename,)
        fp.close()
        return pickle.load(fp)

    def saveGenesToFile(self, filename, listOfPositions = None):
        import pickle
        if listOfPositions == None:
            listOfPositions = range(len(self.pop.individuals))
        fp = open(filename, "w")
        if self.verbose > 0:
            print "Saving %d genes to '%s'..." % (len(listOfPositions), filename)
        pickle.dump( len(listOfPositions), fp)
        for i in listOfPositions:
            pickle.dump(self.pop.individuals[i], fp)
        fp.close()

    def getGenesFromFile(self, filename):
        import pickle
        fp = open(filename, "r")
        geneCount = pickle.load(fp)
        if self.verbose > 0:
            print "Loading %d genes from '%s'..." % (geneCount, filename)
        individuals = []
        for i in range(geneCount):
            individuals.append(pickle.load(fp))
        fp.close()
        return individuals

    def loadGenesFromFile(self, filename):
        self.pop.individuals = self.getGenesFromFile(filename)

    def initGenesFromFile(self, filename, sampleSize = 0,mutate = 1,full = 0):
        # sampleSize = how many to get from saved pop?
        # mutate = should I mutate them?
        # full = should I create a full pop, or just replace sampleSize?
        oldGenes = self.getGenesFromFile(filename)
        if sampleSize == 0:
            sampleSize = len(oldGenes)
        if self.verbose > 0:
            print "oldGenes had %d individuals" % len(oldGenes)
            print "current  has %d individuals" % len(self.pop.individuals)
            print "Loading %d..." % sampleSize
        if full:
            currentOld = 0
            for i in range(len(self.pop.individuals)):
                currentOld = currentOld % len(oldGenes)
                self.pop.individuals[i] = oldGenes[currentOld]
                currentOld += 1
                if mutate:
                    self.pop.individuals[i].mutate(self.mutationRate)
        else:
            for i in range(sampleSize):
                self.pop.individuals[i] = oldGenes[i]
                if mutate:
                    self.pop.individuals[i].mutate(self.mutationRate)

if __name__ == '__main__':
    # Here is a test to evolve a list of integers to maximize their sum:

    class MaxSumGA(GA):
        def fitnessFunction(self, i):
            return max(sum(self.pop.individuals[i].genotype), 0)
        def isDone(self):
            print "Best:",
            self.pop.bestMember.display()
            print
            return self.pop.bestMember.fitness > 30

    print "Do you want to evolve a list of integers to maximize their sum? ",
    if sys.stdin.readline().lower()[0] == 'y':
        print
        ga = MaxSumGA(Population(20, Gene, size=10, mode='integer',
                                 verbose=1, elitePercent = .1,
                                 max = 3, maxStep = 2, min = 0,
                                 crossoverPoints = 1),
                      mutationRate=0.1, crossoverRate=0.5, verbose=1,
                      maxGeneration=50)
        ga.evolve()
        print "Testing loading/saving..."
        ga.saveGenesToFile("maxsumga.genes")
        print "Deleting genes..."
        ga.pop.individuals = []
        ga.loadGenesFromFile("maxsumga.genes")
        print "Press enter to continue evolving...",
        sys.stdin.readline()
        ga.evolve()
        print "Press enter to Test init from file (load all with mutate)...",
        sys.stdin.readline()
        print "reInitialize pop..."
        ga.reInitialize()
        ga.initGenesFromFile("maxsumga.genes")
        ga.evolve()
        print "Press enter to Test init from file (load 1 no mutate)...",
        sys.stdin.readline()
        ga.saveGenesToFile("bestsumga.genes", (ga.pop.bestMember.position,))
        ga.reInitialize()
        ga.initGenesFromFile("bestsumga.genes", 1, 0)
        ga.evolve()
        print "Press enter to Test init from file (load 1, with mutate, full)...",
        sys.stdin.readline()
        ga.reInitialize()
        ga.initGenesFromFile("bestsumga.genes", mutate = 1, full = 1)
        ga.evolve()
    print 

    # Here is a test to evolve the weights/biases in a neural network
    # that solves the XOR problem:

    from pyrobot.brain.conx import *
    class NNGA(GA):
        def __init__(self, cnt):
            n = Network()
            n.add( Layer('input', 2) )
            n.add( Layer('hidden', 3) )
            n.add( Layer('output', 1) )
            n.connect('input', 'hidden')
            n.connect('hidden', 'output')
            n.setInputs([[0.0, 0.0],
                         [0.0, 1.0],
                         [1.0, 0.0],
                         [1.0, 1.0]])
            n.setOutputs([[0.0],
                          [1.0],
                          [1.0],
                          [0.0]])
            n.setVerbosity(0)
            n.setTolerance(.4)
            n.setLearning(0)
            g = n.arrayify()
            self.network = n
            GA.__init__(self,
                        Population(cnt, Gene, size=len(g), verbose=1,
                                   min=-10, max=10, maxStep = 1,
                                   imin=-10, imax=10, 
                                   elitePercent = .01),
                        mutationRate=0.05, crossoverRate=0.6,
                        maxGeneration=400, verbose=1)
        def fitnessFunction(self, genePos):
            self.network.unArrayify(self.pop.individuals[genePos].genotype)
            error, correct, count, pcorrect = self.network.sweep()
            return 4 - error
        def isDone(self):
            self.network.unArrayify(self.pop.bestMember.genotype)
            error, correct, count, pcorrect = self.network.sweep()
            print "Correct:", correct
            return correct == 4

    print "Do you want to evolve a neural network that can do XOR? ",
    if sys.stdin.readline().lower()[0] == 'y':
        ga = NNGA(300)
        ga.evolve()
        ga.network.unArrayify(ga.pop.bestMember.genotype)
        ga.network.setInteractive(1)
        ga.network.sweep()
        ga.saveGenesToFile("gann.pop")
        ga.initGenesFromFile("gann.pop")

    print "Do you want to evolve a phrase? ",
    if sys.stdin.readline().lower()[0] == 'y':
        phrase = "evolution is one cool search mechanism"
        size = len(phrase)
        print
        class PhraseGA(GA):
            def fitnessFunction(self, i):
                sum = 0
                for c in range(len(self.pop.individuals[i].genotype)):
                    if self.pop.individuals[i].genotype[c] == phrase[c]:
                        sum += 1
                return float(sum) / len(self.pop.individuals[i].genotype)
            def isDone(self):
                print "Best:",
                self.pop.bestMember.display()
                return (phrase == string.join(self.pop.bestMember.genotype, ""))

        ga = PhraseGA(Population(300, Gene, size=size, mode='char',
                                 verbose=1, elitePercent = .1,
                                 crossoverPoints = 2),
                      mutationRate=0.06, crossoverRate=0.6, verbose=1,
                      maxGeneration=0)
        ga.evolve()

    print "Do you want to play mastermind? ",
    if sys.stdin.readline().lower()[0] == 'y':
        # composed of N colors, M places (usually 6 and 4)
        # feedback is # in correct place, # of correct color
        phrase = "abcdefghijklmnopqrstuvwxyz"
        size = len(phrase)
        primer = 0
        print
        class MasterMindGA(GA):
            def fitnessFunction(self, i):
                sumPosition = 0
                sumColor = 0
                guessed = []
                correct = []
                for c in range(len(self.pop.individuals[i].genotype)):
                    if self.pop.individuals[i].genotype[c] == phrase[c]:
                        sumPosition += 1
                    else:
                        guessed.append(self.pop.individuals[i].genotype[c])
                        correct.append(phrase[c])
                for g in guessed:
                    if g in correct:
                        correct.remove(g)
                        sumColor += 1
                if primer:
                    if (sumColor + sumPosition > size/2):
                        goodPosition = 10
                        goodColor    =  1
                    else:
                        goodPosition = 0
                        goodColor    = 1
                else:
                    goodPosition = 100
                    goodColor    =   1
                return sumColor * goodColor + sumPosition * goodPosition
            def isDone(self):
                print "Best:",
                self.pop.bestMember.display()
                return (phrase == string.join(self.pop.bestMember.genotype, ""))

        ga = MasterMindGA(Population(300, Gene, size=size, mode='char',
                                 verbose=1, elitePercent = .1,
                                 crossoverPoints = 2),
                      mutationRate=0.06, crossoverRate=0.6, verbose=1,
                      maxGeneration=0)
        ga.evolve()

# 26 ** 26  = 6,156,119,580,207,157,310,796,674,288,400,203,776 6x10^36
#  60 * 300 = 18,000
# 224 * 300 = 67200

# generations
# 224 
# 171 
#  60 
# 167
# 404

# With priming
#  73
# 126
# 260

# no overlap
#  98
# 158
