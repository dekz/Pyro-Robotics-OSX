from random import random
from math import sqrt

"""
Author: Lisa Meeden
Date: 2/14/2008

Implementation of GNG as described in the paper 'A Growing Neural Gas
Network Learns Topologies' by Bernd Fritzke published in 'Advances in
Neural Information Processing 7', MIT Press, 1995.

GNG is an incremental network model able to learn the topological
relationships in a given set of input vectors using a simple Hebb-like
learning rule.
"""

def randomCirclePoint(radius):
    """
    Assuming circle is centered at (0,0)
    """
    diameter = 2*radius
    limit = radius**2
    while True:
        x = (diameter*random())-radius
        y = (diameter*random())-radius
        if x**2 + y**2 <= limit:
            return [x, y]

def randomSpherePoint(radius):
    """
    Assuming sphere is centered at (0,0)
    """
    diameter = 2*radius
    limit = radius**2
    while True:
        x = (diameter*random())-radius
        y = (diameter*random())-radius
        z = (diameter*random())-radius
        if x**2 + y**2 + z**2 <= limit:
            return [x, y, z]

class Unit:
    """
    Each unit in the GNG maintains a reference vector, an error
    measure, and a list of edges.
    """
    
    def __init__(self, vector = None, dimension=2, minVal=-1, maxVal=1):
        self.dimension = dimension
        self.minVal = minVal
        self.maxVal = maxVal
        if vector:
            self.vector = vector
        else:
            self.vector = self.randomVector()
        self.error = 0
        self.edges = []

    def __str__(self):
        result = "Unit:\n"
        result += "Vector: " + self.vectorStr()
        result += " Error: " + str(self.error) + "\n" 
        for e in self.edges:
            result += e.__str__()
        return result

    def vectorStr(self):
        result = "[ "
        for i in range(len(self.vector)):
            result += "%.3f " % self.vector[i]
        result += "] "
        return result
    
    def getEdgeTo(self, unit):
        """
        Returns the edge to the given unit or None.
        """
        for edge in self.edges:
            if edge.toUnit == unit:
                return edge
        return None

    def getNeighbors(self):
        """
        Returns a list of its immediate neighboring units. 
        """
        neighbors = []
        for edge in self.edges:
            neighbors.append(edge.toUnit)
        return neighbors

    def randomVector(self):
        """
        Generats a random reference vector within the appropriate bounds.
        """
        vec = []
        for i in range(self.dimension):
            vec.append(((self.maxVal-self.minVal) * random()) + self.minVal)
        return vec

    def moveVector(self, towardPoint, lrate):
        """
        Moves the reference vector toward the given point based on the
        given learning rate.
        """
        for i in range(len(towardPoint)):
            self.vector[i] += lrate*(towardPoint[i]-self.vector[i])

class Edge:
    """
    Edges in the GNG are undirected.  However for ease of
    implementation, the edges are represented as one-way. For example,
    if unitA and unitB and connected, then unitA maintains an edge to
    unitB and unitB maintains an edge to unitA.  Edges also maintain
    their age.  If an edge becomes too old, it will be removed.
    """
    def __init__(self, toUnit):
        self.toUnit = toUnit
        self.age = 0

    def __str__(self):
        result = "Edge to: "
        result += self.toUnit.vectorStr()
        result += " Age: " + str(self.age) + "\n"
        return result

class GrowingNeuralGas:
    """
    Parameters:

    winnerLearnRate   Used to adjust closest unit towards input point
    neighborLearnRate Used to adjust other neighbors towards input point
    maxAge            Edges older than maxAge are removed
    reduceError       All errors are reduced by this amount each GNG step
    stepsToInsert     A new unit is added periodically based on this
    insertError       Error of every new unit is reduced by this amount
    
    NOTE: The default values are taken from the paper.

    The GNG always begins with two randomly placed units.  It takes as
    input a function that will generate the next point from the input
    distribution. 
    """
    def __init__(self, generateNext, length, verbose=0):
        self.winnerLearnRate = 0.2
        self.neighborLearnRate = 0.006
        self.maxAge = 50
        self.reduceError = 0.995
        self.stepsToInsert = 100
        self.insertError = 0.5

        self.verbose = verbose
        self.stepCount = 1
        self.units = [Unit(dimension=length), Unit(dimension=length)]
        self.generateNext = generateNext

    def __str__(self):
        result = "GNG step " + str(self.stepCount) + "\n"
        result += "Number of units: " + str(len(self.units)) + "\n"
        result += "Average error: " + str(self.averageError()) + "\n"
        if self.verbose > 1:
            for unit in self.units:
                result += unit.__str__()
        return result

    def distance(self, v1, v2):
        """
        Returns the Euclidean distance between two vectors.
        """
        total = 0
        for i in range(len(v1)):
            total += (v1[i] - v2[i])**2
        return sqrt(total)

    def plot(self):
        """
        Creates a file readable by xgraph of the first two dimensions
        of every unit vector and its edges
        """
        filename = "plot%d" % self.stepCount
        data = open(filename, "w")
        for unit in self.units:
            for edge in unit.edges:
                data.write("move %f %f\n" % (unit.vector[0], unit.vector[1]))
                next = edge.toUnit
                data.write("%f %f\n" % (next.vector[0], next.vector[1]))
        data.close()

    def unitOfInterest(self, unit, cutoff):
        """
        Used to focus on particular units when debugging.
        """
        for value in unit.vector:
            if abs(value) > cutoff:
                return True
        else:
            return False

    def computeDistances(self, point):
        """
        Computes the distances between the given point and every unit
        in the GNG.  Returns the closest and next closest units.
        """
        dists = []
        for i in range(len(self.units)):
            dists.append((self.distance(self.units[i].vector, point), i))
        dists.sort()
        best = dists[0][1]
        second = dists[1][1]
        if self.verbose > 1:
            print "Processing:", point
            print "Closest:", self.units[best].vectorStr()
            print "Second:", self.units[second].vectorStr()
            print
        return self.units[best], self.units[second]

    def incrementEdgeAges(self, unit):
        """
        Increments the ages of every unit directly connected to the
        given unit.
        """
        for outgoing in unit.edges:
            outgoing.age += 1
            incoming = outgoing.toUnit.getEdgeTo(unit)
            incoming.age += 1

    def connectUnits(self, a, b):
        """
        Adds the appropriate edges to connect units a and b.
        """
        if self.verbose >= 1:
            print "Add edge:", a.vectorStr(), b.vectorStr()
        a.edges.append(Edge(b))
        b.edges.append(Edge(a))

    def disconnectUnits(self, a, b):
        """
        Removes the appropriate edges to disconnect units a and b.
        """
        if self.verbose >= 1:
            print "Remove edge:", a.vectorStr(), b.vectorStr()
        a.edges.remove(a.getEdgeTo(b))
        b.edges.remove(b.getEdgeTo(a))

    def removeStaleEdges(self):
        """
        Checks all edges in the GNG and removes any with an age exceeding
        the maxAge parameter.  Also removes any unit that is completely
        disconnected.
        """
        for unit in self.units:
            i = len(unit.edges)-1
            while i>=0:
                if unit.edges[i].age > self.maxAge:
                    if self.verbose >= 1:
                        adjacent = unit.edges[i].toUnit
                        print "Removing stale edge: %s %s" % \
                              (unit.vectorStr(), adjacent.vectorStr())
                    unit.edges.pop(i)
                i -= 1
                    
        i = len(self.units)-1
        while i>=0:
            if len(self.units[i].edges) == 0:
                if self.verbose >= 1:
                    print "Removing disconnected unit:", unit.vectorStr()
                self.units.pop(i)
            i -= 1

    def maxErrorUnit(self, unitList):
        """
        Given a list of units, returns the unit with the highest error.
        """
        highest = unitList[0]
        for i in range(1, len(unitList)):
            if unitList[i].error > highest.error:
                highest = unitList[i]
        return highest

    def averageError(self):
        """
        Returns the average error across all units in the GNG.
        """
        total = 0.0
        for unit in self.units:
            total += unit.error
        return total/len(self.units)

    def insertUnit(self):
        """
        Inserts a new unit into the GNG.  Finds the unit with the highest
        error and then finds its topological neighbor with the highest
        error and inserts the new unit between the two. 
        """
        worst = self.maxErrorUnit(self.units)
        if self.verbose > 1:
            print "Max error", worst.__str__()
        worstNeighbor = self.maxErrorUnit(worst.getNeighbors())
        newVector = []
        for i in range(len(worst.vector)):
            newVector.append(0.5 * (worst.vector[i] + worstNeighbor.vector[i]))
        newUnit = Unit(newVector)
        if self.verbose > 0:
            print "Insert unit:", newUnit.vectorStr()
        self.units.append(newUnit)
        self.connectUnits(newUnit, worst)
        self.connectUnits(newUnit, worstNeighbor)
        self.disconnectUnits(worst, worstNeighbor)
        worst.error *= self.insertError
        worstNeighbor.error *= self.insertError
        newUnit.error = worst.error

    def reduceAllErrors(self):
        """
        Decays the error at all units.
        """
        for unit in self.units:
            unit.error *= self.reduceError
                
    def step(self):
        """
        Processes one input at a time through the GNG.
        
        Do an experiment to illustrate the ability of GNG to grow and
        shrink.  Generate input from the unit circle.  The change the
        distribution for a time.  Eventually revert back to the
        original distribution.
        """
        if self.stepCount < 5000 or self.stepCount > 10000:
            nextPoint = self.generateNext(1)
        else:
            nextPoint = self.generateNext(0.5)
        best, second = self.computeDistances(nextPoint)
        self.incrementEdgeAges(best)
        best.error += self.distance(best.vector, nextPoint)**2
        best.moveVector(nextPoint, self.winnerLearnRate)
        for unit in best.getNeighbors():
            unit.moveVector(nextPoint, self.neighborLearnRate)
        edgeExists = best.getEdgeTo(second)
        if edgeExists:
            edgeExists.age = 0
            second.getEdgeTo(best).age = 0
        else:
            self.connectUnits(best, second)
        self.removeStaleEdges()
        if self.stepCount % self.stepsToInsert == 0:
            self.insertUnit()
        self.reduceAllErrors()
        ### To view progress of learning
        if self.stepCount % 1000 == 0:
            self.plot()
        self.stepCount += 1

def main():
    gng = GrowingNeuralGas(randomCirclePoint, 2, verbose=0)
    for i in range(15000):
        gng.step()
        if gng.stepCount % 1000==0:
            print gng
    
if __name__ == '__main__':
    main()
