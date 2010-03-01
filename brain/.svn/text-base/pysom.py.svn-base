# A Python Self-organizing Map

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision$"

import RandomArray, random, math, sys

class SOM:

    def __init__(self, rows, cols, size):
        self.rows = rows
        self.cols = cols
        self.vectorLen = size
        self.weight = RandomArray.random((rows, cols, size))
        self.input = []
        self.loadOrder = []
        self.step = 0
        self.maxStep = 1000.0

    def setInputs(self, inputs):
        self.input = inputs
        self.loadOrder = range(len(self.input)) # not random
        # will randomize later, if need be

    def euclidian(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def distance(self, v1, v2):
        dist = 0.0
        for i in range(len(v1)):
            d = v1[i] - v2[i]
            dist += (d ** 2)
        return dist

    def winner(self, pattern):
        diff = self.distance(self.weight[0][0], pattern)
        x = 0; y = 0
        for r in range(0, len(self.weight)):
            for c in range(0, len(self.weight[r])):
                d = self.distance(self.weight[r][c], pattern)
                if d < diff:
                    diff = d
                    x = c
                    y = r
        return (x, y, diff)

    def radius(self):
        return (1.0 - (self.step * 1.0) / self.maxStep) * min(self.rows, self.cols, 5)

    def testMap(self, pos, x, y): # winner at (x, y)
        for r in range(self.rows):
            for c in range(self.cols):
                dist = self.euclidian(x, y, c, r)
                scale = self.gaussian(dist)
                print "%+.2f " % scale,
            print ""
        print ""
        #print "--More-- ",
        #sys.stdin.readline()

    def gaussian(self, dist):
        if dist == 0:
            scale = .9
        elif dist == 1:
            scale = -.1
        elif dist < self.radius() / 2.0:
            scale = .1
        else:
            scale = 0.0
        return scale

    def gaussian1(self, dist):
        if dist == 0:
            scale = .9
        elif dist < self.radius() * 1/5.0: 
            scale = .9
        elif dist < self.radius() * 2/5.0:
            scale = -.1
        elif dist < self.radius() * 3/5.0:
            scale = .3
        elif dist < self.radius() * 4/5.0:
            scale = .2
        elif dist < self.radius():
            scale = .1
        else:
            scale = 0.0
        return scale
    
    def scale(self):
        return (1.0 - (self.step * 1.0) / self.maxStep) 

    def updateMap(self, pattern, x, y): # winner at (x, y)
        error = 0.0
        for r in range(self.rows):
            for c in range(self.cols):
                scale = self.scale()
                # self.gaussian( self.euclidian(x, y, c, r))
                # if (scale != 0.0):
                if self.euclidian(x, y, c, r) <= 1.0:
                    for i in range( self.vectorLen):
                        e = (pattern[i] - self.weight[r][c][i])
                        error += abs(e)
                        self.weight[r][c][i] += scale * e
                        # (scale * self.radius()) * e
                        # to protect random array values from getting too small
                        if self.weight[r][c][i] < 0.00001: 
                            self.weight[r][c][i] = 0.0
        return error
                    
    def randomizeOrder(self):
        flag = [0] * len(self.input)
        self.loadOrder = [0] * len(self.input)
        for i in range(len(self.input)):
            pos = int(random.random() * len(self.input))
            while (flag[pos] == 1):
                pos = int(random.random() * len(self.input))
            flag[pos] = 1
            self.loadOrder[pos] = i

    def train(self):
        self.step = 0
        for t in range(self.maxStep):
            print "Epoch #", t,
            error = 0.0
            self.randomizeOrder()
            for p in self.loadOrder:
                x, y, d = self.winner(self.input[p])
                #print "Winner for input #", p, "is weight at (", x, y, ") (diff was", d,  ")"
                error += self.updateMap(self.input[p], x, y)
                #self.testMap(p, x, y)
            self.step += 1
            print "Error =", error

    def trainPattern(self, pattern):
        # will depend on self.step
        x, y, d = self.winner(pattern)
        error += self.updateMap(pattern, x, y)
        print "Winner is weight at (", x, y, ") (diff was", d,  ") error = ", \
              error

    def test(self):
        self.loadOrder = range(len(self.input))
        histogram = Numeric.zeros((self.cols, self.rows), 'i')
        for p in self.loadOrder:
            x, y, d = self.winner(self.input[p])
        #    print "Input[%d] =" % p, self.input[p],"(%d, %d)" % (x, y)
            histogram[x][y] += 1
        for r in range(self.rows):
            for c in range(self.cols):
                print "%5d" % histogram[c][r],
            print ""
        print ""

if __name__ == '__main__':
    import Numeric
    s = SOM(5, 7, 5) # rows, cols; length of high-dimensional input
    s.setInputs( RandomArray.random((100, 5))) 
    s.maxStep = 100
    s.train()
    s.test()
