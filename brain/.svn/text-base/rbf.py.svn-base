
# A Radial Basis Function (unit) has three things that can be learned:
#    center - the model vector
#    radius - radius of the function
#    weight - weighting of this node

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision$"

import Numeric, math, random

# Typical activation functions are:

def gaussian(v):
    return map(math.exp, -(v ** 2))

def imqe(v, k = .5):
    return map(lambda z: 1.0 / math.sqrt(z + (k ** 2)), v)

class RBF:
    """ A Radial Basis Function node """
    def __init__(self, size):
        # center can be selected at random from training data. Here
        # we just assign a random vector:
        self.center = Numeric.array([random.random() for r in range(size)])
        # initial radius:
        self.radius = 1.0
        # initial values of activation:
        self.activation = Numeric.zeros(size)
    def propagate(self, input):
        self.activation = gaussian((input - self.center) / self.radius)

class RBFLayer:
    """ A layer of RBF units """
    def __init__(self, size, vsize):
        self.units = [RBF(vsize) for i in range(size)]
    def propagate(self, input):
        for u in self.units:
            u.propagate(input)

# make a layer of 10 units, each capable of storing a 5-length
# model vector:
rbfLayer = RBFLayer(10, 5)

# sample vector:
input = Numeric.array([0.0, 0.2, 0.4, 0.3, 0.8])

# compare it to units:
rbfLayer.propagate(input)

for u in rbfLayer.units:
    print u.activation
