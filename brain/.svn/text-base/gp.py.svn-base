"""
Pyrobot Module for Genetic Program.
Extension of GA (pyrobot/brain/ga.py)
"""

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision$"

from pyrobot.brain.ga import *
import pyrobot.system.share as share
from math import pi
import operator, sys, types

### WORKAROUND: deepcopy can't copy dicts with functions
### Currently using global share.env to avoid having it
### in gene
### FIX: don't use deepcopy

ALLOW_SELF_EVAL = 1 # self-evaluating terminals (reals, ints, floats, etc)

########## Functions for evaluator. Designed so that you can make your
########## own, too.

def div_func(*operands): 
    """ For protected division. type="regular" so no environment is passed."""
    if operands[1] == 0:
        return sys.maxint # not all python's have "infinity"
    else:
        return operands[0] / float(operands[1])
def ifpos_func(operands, env):
    """ Special form (lazy evaluation) for if-positive. Needs env. """
    test_val, if_val, else_val = operands
    test_result = test_val.eval(env)
    if (test_result):
        return if_val.eval(env)
    else:
        return else_val.eval(env)
def and_func(operands, env):
    """ Special form (lazy evaluation) for short-circuiting 'and'. Needs env. """
    if len(operands) == 0:
        return 1
    else:
        car = operands[0].eval(env)
        if not car:
            return 0
        else:
            return and_func(operands[1:], env)
def or_func(operands, env):
    """ Special form (lazy evaluation) for short-circuiting 'or'. Needs env. """
    if len(operands) == 0:
        return 0
    else:
        car = operands[0].eval(env)
        if car:
            return 1
        else:
            return or_func(operands[1:], env)

########## End of Functions for evaluator

class Operator:
    """ Class to hold operator information. """
    def __init__(self, func, operands = 2, type = "regular"):
        """ Constructor for Operator class. Takes a function. Optional args are:
        - operands (number of operands); used for generating random function calls
        - type ("regular" or "lazy"); determines if args are evaluated before being
          passed to func.
        """
        self.func = func
        self.operands = operands
        self.type = type

class Environment:
    """ Class to hold environment information. """
    def __init__(self, dict = {}):
        self.env = dict.copy()
    def update(self, dict):
        self.env.update( dict )
    def terminals(self):
        retvals = {}
        for item in self.env:
            if not isinstance(self.env[item], Operator):
                retvals[item] = self.env[item]
        return retvals
    def operators(self):
        retvals = {}
        for item in self.env:
            if isinstance(self.env[item], Operator):
                retvals[item] = self.env[item]
        return retvals
    def lazyOps(self):
        retvals = {}
        for item in self.env:
            if isinstance(self.env[item], Operator) and self.env[item].type == "lazy":
                retvals[item] = self.env[item]
        return retvals
    def regularOps(self):
        retvals = {}
        for item in self.env:
            if isinstance(self.env[item], Operator) and self.env[item].type == "regular":
                retvals[item] = self.env[item]
        return retvals

class GPTree:
    """ Main tree structure for GP. """
    def __init__(self, op, *children):
        self.op = op
        self.children = []
        self.root = None
        self.depth = 0
        for child in children:
            if not isinstance(child, GPTree):
                self.children.append(GPTree(child))
            else:
                self.children.append(child)
        self.internals = [0] * len(self.children)
        self.externals = [0] * len(self.children)
        self.resetCounts()
    def leaf(self):
        return len(self.children) == 0
    def totalPoints(self):
        if self.leaf():
            total_points = 1 # just self
        else:
            total_points = 1 # count self
            total_points += reduce(operator.add, self.internals, 0)
            total_points += reduce(operator.add, self.externals, 0)
        return total_points
    def terminalPoints(self):
        if self.leaf():
            total_points = 1 # just self
        else:
            # don't count self
            total_points = reduce(operator.add, self.externals, 0)
        return total_points
    def getTerminalPoints(self):
        if self.leaf():
            return [self.op]
        else:
            lyst = []
            for i in range(len(self.children)):
                lyst.extend( self.children[i].getTerminalPoints() )
            return lyst
    def getTerminalTree(self, pos):
        if pos == 0 and self.leaf():
            return self
        cnt = 0
        for i in range(len(self.children)):
            if pos < self.externals[i] + cnt:
                return self.children[i].getTerminalTree(pos - cnt)
            cnt += self.externals[i]
    def getPoint(self, pos):
        if pos == 0:
            return self
        offset = 1
        for i in range(len(self.children)):
            tp = self.children[i].totalPoints()
            if pos - offset < tp:
                return self.children[i].getPoint(pos - offset)
            offset += tp
        raise AttributeError, ("pos %d is beyond genotype length" % pos)
    def __str__(self):
        s = ''
        if self.leaf():
            s += "%s" % self.op
        else:
            s += "(%s" % self.op
            for child in self.children:
                s += " %s" % child
            s += ")"
        return s
    def resetCounts(self, root = None, depth = 0):
        i = 0
        self.root = root
        self.depth = depth
        if root == None:
            root = self
        for child in self.children:
            internal, ext = child.resetCounts(root, depth + 1)
            self.internals[i] = internal
            self.externals[i] = ext
            i += 1
        if self.leaf():
            return (0,1)
        else:
            return (reduce(operator.add, self.internals, 1),
                    reduce(operator.add, self.externals, 0))
    def eval(self, env = None):
        if env == None:
            env = share.env
        if self.op not in env.operators().keys():
            if self.op in env.env:
                retval = env.env[self.op]
            elif ALLOW_SELF_EVAL:
                retval = self.op
            else:
                raise AttributeError, ("'%s' is not in env, and ALLOW_SELF_EVAL = 0" % self.op)

        else:
            if self.op in env.lazyOps().keys():
                op = env.lazyOps()[self.op].func
                retval = apply(op, (self.children, env))
            elif self.op in env.regularOps().keys():
                op = env.env[self.op].func
                results = map(lambda x: x.eval(env), self.children)
                retval = apply(op, results)
            else:
                # just a terminal? Error?
                retval = env.env[self.op]
        return retval

class GPGene(Gene):
    def __init__(self, **args):
        self.bias = .6
        self.fitness = 0.0
        self.mode = -1
        self.args = args  # can't have env in it
        if args.has_key('bias'):
            self.bias = args['bias']
        # higher the bias, more likely to be shallow
        if (random.random() < self.bias):
            terminals = share.env.terminals().keys()
            if len(terminals) == 0:
                raise AttributeError, "no terminals given in environment or eval()"
            term = terminals[ int(random.random() * len(terminals))]
            self.genotype = GPTree(term)
        else:
            operators = share.env.operators().keys()
            if len(operators) == 0:
                raise AttributeError, "no operators in environment"
            pos = int(random.random() * len(operators)) 
            treeArgs = [operators[ pos ], ]
            for i in range( share.env.env[operators[pos]].operands ):
                treeArgs.append( GPGene(**args).genotype )
            self.genotype = GPTree( *treeArgs )
    def __str__(self):
        return str(self.genotype)
    def display(self):
        print self.genotype
    def eval(self, additionalEnv = {}):
        """ Takes a dictionary """
        share.env.update(additionalEnv)
        return self.genotype.eval(share.env) # takes an Environment
    def mutate(self, mutationRate):
        """
        Changes points based on mutationRate.
        """
        total_points = self.genotype.totalPoints()
        for i in range(total_points): 
            if flip(mutationRate):
                rand = int(random.random() * total_points) 
                subtree = self.genotype.getPoint(rand) # returns a tree
                temp = GPGene( **self.args)
                if subtree.leaf():
                    self.replaceTree(subtree, temp.genotype)
                else: # it is an internal node
                    # same number of kids, just swap operator then
                    if len(temp.genotype.children) == len(subtree.children):
                        self.replaceTree(subtree, temp.genotype, replaceChildren = 0)
                    else: # bigger or smaller, just replace children in subtree
                        self.replaceTree(subtree, temp.genotype)
                self.genotype.resetCounts()
                total_points = self.genotype.totalPoints()# may change!
                if i > total_points: break # no need to do more
    def crossover(self, parent2, crossoverRate):
        """ Make two new genotypes, or return the old ones."""
        if flip(crossoverRate):
            parent1 = self
            term1 = parent1.genotype.totalPoints()
            term2 = parent2.genotype.totalPoints()
            rand1 = int(term1 * random.random())
            rand2 = int(term2 * random.random())
            subtree1 = parent1.genotype.getPoint( rand1 )
            subtree2 = parent2.genotype.getPoint( rand2 )
            p1 = deepcopy( parent1 )
            p2 = deepcopy( parent2 )
            self.replaceTree(p2, subtree1 )
            self.replaceTree(p1, subtree2 )
            p1.genotype.resetCounts()
            p2.genotype.resetCounts()
            return p1, p2 # returns new copies for replacement
        else:
            return self, parent2
    def replaceTree(self, subtree, temp, replaceChildren = 1):
        """ Replace operator and (optionally) children. """
        # these are all trees, or list of trees:
        subtree.op = temp.op
        if replaceChildren:
            subtree.children = temp.children
            subtree.internals = temp.internals
            subtree.externals = temp.externals
               
def wrapObj(current_symbol, objType = GPTree):
    """ A wrapper for parse. Should have been recursive... """
    retval = current_symbol
    if not isinstance(current_symbol, objType):
        if current_symbol in share.env.env:
            retval = objType(current_symbol)
        elif type(current_symbol) == type(""): # self-evaluating number?
            if not ALLOW_SELF_EVAL:
                raise AttributeError, ("'%s' is not in env, and ALLOW_SELF_EVAL = 0" % current_symbol)
            if "." in current_symbol:
                retval = GPTree(float(current_symbol))
            else:
                retval = GPTree(int(current_symbol))
    return retval

def parse(exp, objType = GPTree):
    """ Parser to turn "(+ 4 5)" into a GPTree expression. """
    stack  = []
    current_symbol = ''
    for i in range(len(exp)):
        if exp[i] == "(":
            stack.append( [] )
        elif exp[i] == ")": # end of list
            if current_symbol != '':
                if len(stack[-1]) > 0:
                    stack[-1].append(wrapObj(current_symbol))
                else:
                    stack[-1].append(current_symbol) # don't wrap op
                current_symbol = ''
            current_symbol = apply(objType, stack.pop(-1))
        elif exp[i] == ' ': # next symbol
            if current_symbol != '':
                if len(stack[-1]) > 0:
                    stack[-1].append(wrapObj(current_symbol))
                else:
                    stack[-1].append(current_symbol) # don't wrap op
                current_symbol = ''
        else:
            current_symbol += exp[i]
    return wrapObj(current_symbol)

# A standard environment dictionary:
env = {'+'  : Operator(operator.add), # defaults to operands=2
       '-'  : Operator(operator.sub),
       '*'  : Operator(operator.mul),
       '/'  : Operator(div_func),
       'ifpos' : Operator(ifpos_func, operands=3, type="lazy"), # explicitly list operands
       'and'   : Operator(and_func,  type="lazy"),
       'or'    : Operator(or_func,   type="lazy"),
       # explicitly list operands:
       #'rnd'   : Operator(lambda: random.random(), operands=0, type="regular"),
       #1: 1, 2:2, 3:3, 4:4,
       }

# The standard environment:
share.env = Environment(env)

if __name__ == '__main__':
    share.env.update( {'i1':0, 'i2':0} )
    outputs = [ 0, 1, 1, 0 ] # outputs for XOR
    inputs = [ {'i1' : 0, 'i2' : 0},
               {'i1' : 0, 'i2' : 1},
               {'i1' : 1, 'i2' : 0},
               {'i1' : 1, 'i2' : 1} ]
    class GP(GA):
        def __init__(self, cnt, **args):
            GA.__init__(self, Population( cnt, GPGene, bias =.6, 
                                          elitePercent = .1, verbose = 1),
                        maxGeneration = 100,
                        verbose = 1)
    
        def fitnessFunction(self, pos):
            diff = 0
            for i in range(len(inputs)):
                set, goal = inputs[i], outputs[i]
                retval = self.pop.individuals[pos].eval(set)
                item  = retval - goal
                diff += abs(item)
            return max(4 - diff, 0)
    
        def isDone(self):
            fit = self.pop.bestMember.fitness
            self.pop.bestMember.display()
            print 
            return fit == 4
    
    gp = GP(50)
    gp.evolve()
    print " -----------------------------------------------------------------"
    for ins in inputs:
        print ins, gp.pop.bestMember.eval(ins)
    raw_input("Press enter to continue...")
    class PI_GP(GA):
        def __init__(self, cnt, **args):
            GA.__init__(self, Population(cnt, GPGene, bias = .6,
                                         verbose = 1, 
                                         elitePercent = .1),
                        verbose = 1, maxGeneration = 25)
        def fitnessFunction(self, pos, pr = 0):
            diff = abs(self.pop.individuals[pos].eval() - pi)
            if pr:
                self.pop.individuals[pos].display()
                print
            return max(pi - diff, 0) 
                
        def isDone(self):
            return abs(self.fitnessFunction(0, 1) - pi) < .001
    share.env.update( {'+1': Operator(lambda obj: obj + 1, 1, "regular"),
                       '1/2': .5,
                       'e': math.e } )
    gp = PI_GP(100)
    gp.evolve()
    print " -----------------------------------------------------------------"
