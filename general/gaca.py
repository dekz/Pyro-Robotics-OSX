
from pyrobot.general.ca import *
from pyrobot.brain.ga import *

class GACAGene(Gene):
    def __init__(self, **args):
        Gene.__init__(self, **args)
        pos = args["pos"]
        popSize = args["popSize"]
        bias = pos / float(popSize) #random.random()
        self.genotype = []
        for i in range(args['size']):
            self.genotype.append( random.random() < bias)

class GACA(GA):
    def __init__(self, cnt, **args):
        self.rules = Rules()
        self.lattice = Lattice(height = 500, size = 100)
        if args.has_key('testCases'):
            self.testCases = args['testCases']
        GA.__init__(self, Population( cnt, GACAGene, **args), **args)
              
    def fitnessFunction(self, genePos):
        self.rules.data[0] = self.pop.individuals[genePos].genotype[:]
        totalSteps = 0
        method = 'complexity' # 'correct' or 'complexity' or 'both'
        for i in range(0, self.testCases): # 
            self.lattice.randomize((i + (.1 * self.testCases)) / float(self.testCases))
            p = poisson(149)
            print "   Running for max ", p, "steps; completed in = ",
            steps = self.rules.applyAll(self.lattice, p) 
            print steps, ";",
            initialDensity = self.lattice.density(0)
            finalDensity = self.lattice.density(steps)
            print "initial density = %.3f final density = %.3f " % (initialDensity, finalDensity), 
            #print 
            #self.lattice.display()
            if steps < p:
                if method == 'complexity':
                    incr = steps
                elif method == 'correct':
                    incr = 1
                elif method == 'both':
                    incr = 100000 + steps
                else:
                    raise ValueError, "Invalid fitness method : '%s'" % method
                if initialDensity < .5 and finalDensity == 0.0:
                    totalSteps += incr
                    print "correct!"
                elif initialDensity >= .5 and finalDensity == 1.0:
                    totalSteps += incr
                    print "correct!"
                else:
                    print "wrong"
            else:
                print "steps >= p wrong"
        print "Generation: %d individual #%d ============== Total Fitness = %.3f" % (self.generation, genePos, totalSteps)
        return totalSteps

    def isDone(self):
        print "Best:", self.pop.bestMember.fitness
        self.pop.bestMember.display()
        # if type is correct:
        #return (self.pop.bestMember.fitness == (self.testCases + 2))
        return 0

if __name__ == '__main__':
    print "----------------------------------------------------"
    print "Running GACA: Genetic Algorithm on Cellular Automata"
    print "----------------------------------------------------"
    ga = GACA(10, elitePercent = .1, size = 2 ** 7,
              mode = 'bit', testCases = 8, mutationRate = .01, crossoverRate = .6, verbose = 1)
    ga.evolve()
