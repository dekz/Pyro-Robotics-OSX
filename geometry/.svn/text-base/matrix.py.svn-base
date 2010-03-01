"""
Classes for 3D Matrix manipulations.
"""

import math
import Numeric

RAD = math.pi/180.0

class Line:
    """ A line class for 3D graphics """
    def __init__(self, x0, y0, x1, y1):
        self.data = Numeric.array([x0, y0, 0, x1, y1, 0])

class Vertex3D(object):
    """ A vertex class for 3D graphics """
    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self.data = Numeric.array([x, y, z])
    def _getX(self): return self.data[0]
    def _getY(self): return self.data[1]
    def _getZ(self): return self.data[2]
    x = property(_getX)
    y = property(_getY)
    z = property(_getZ)
    def __mul__(self, other):
        if isinstance(other, float):
            return self.data * other

class Matrix:
    """ A matrix class for 3D graphics """
    def __init__(self, *args):
        if len(args) == 0:
            self.matrix = Numeric.array([[[0.0] for y in range(4)] for x in range(4)])
            self.init(1.0, 0.0, 0.0, 0.0,
                      0.0, 1.0, 0.0, 0.0,
                      0.0, 0.0, 1.0, 0.0,
                      0.0, 0.0, 0.0, 1.0)            
        elif len(args) == 16:
            self.matrix = Numeric.array([[[0.0] for y in range(4)] for x in range(4)])
            self.init(*args)
        else:
            self.matrix = args[0]
    def __mul__(self, other):
        if isinstance(other, Line):
            return Matrix(self.matrix * other.data)
        elif isinstance(other, Matrix):
            result = Matrix()
            for i in range(4):
                for j in range(4):
                    result.matrix[i][j] = 0.0
                    for k in range(4):
                        result.matrix[i][j] += self.matrix[k][j] * other.matrix[i][k]
            return result
        elif isinstance(other, Vertex3D):
            v = other
            result = Vertex3D()
            result.data[0] = self.matrix[0][0] * v.x + self.matrix[1][0] * v.y + self.matrix[2][0] * v.z + self.matrix[3][0]
            result.data[1] = self.matrix[0][1] * v.x + self.matrix[1][1] * v.y + self.matrix[2][1] * v.z + self.matrix[3][1]
            result.data[2] = self.matrix[0][2] * v.x + self.matrix[1][2] * v.y + self.matrix[2][2] * v.z + self.matrix[3][2]
            return result
    __rmul__ = __mul__
    def init(self, x0, y0, z0, w0,
                   x1, y1, z1, w1,
                   x2, y2, z2, w2,
                   x3, y3, z3, w3):
        self.matrix[0][0] = x0
        self.matrix[1][0] = y0
        self.matrix[2][0] = z0
        self.matrix[3][0] = w0
        
        self.matrix[0][1] = x1
        self.matrix[1][1] = y1
        self.matrix[2][1] = z1
        self.matrix[3][1] = w1
        
        self.matrix[0][2] = x2
        self.matrix[1][2] = y2
        self.matrix[2][2] = z2
        self.matrix[3][2] = w2
        
        self.matrix[0][3] = x3
        self.matrix[1][3] = y3
        self.matrix[2][3] = z3
        self.matrix[3][3] = w3
        
def translate(x, y, z):
    return Matrix(1.0, 0.0, 0.0, x,
                  0.0, 1.0, 0.0, y,
                  0.0, 0.0, 1.0, z,
                  0.0, 0.0, 0.0, 1.0)

def scale(x, y, z):
    return Matrix(x,   0.0, 0.0, 0.0,
                  0.0, y,   0.0, 0.0,
                  0.0, 0.0, z,   0.0,
                  0.0, 0.0, 0.0, 1.0)

def rotate(x, y, z):
    return rotateXDeg(x) * rotateYDeg(y) * rotateZDeg(z)

def rotateXDeg(rot):
    return rotateXRad(rot * RAD)
def rotateYDeg(rot):
    return rotateYRad(rot * RAD)
def rotateZDeg(rot):
    return rotateZRad(rot * RAD)

def rotateXRad(rot):
    s = math.sin(rot)
    c = math.cos(rot)
    return Matrix( 1.0,    0.0,	   0.0,   0.0,
                   0.0,      c,     -s,   0.0,
                   0.0,      s,      c,   0.0,
                   0.0,    0.0,    0.0,   1.0)
def rotateYRad(rot):
    """ Return a matrix to rotate around Y axis """
    s = math.sin(rot)
    c = math.cos(rot)
    return Matrix(  c,    0.0,      s,   0.0,
                  0.0,    1.0,    0.0,   0.0,
                   -s,    0.0,      c,   0.0,
                  0.0,    0.0,    0.0,   1.0)
def rotateZRad(rot):
    """ Return a matrix to rotate around Z axis """
    s = math.sin(rot)
    c = math.cos(rot)
    return Matrix (  c,     -s,    0.0,   0.0,
                     s,      c,    0.0,   0.0,
                   0.0,    0.0,    1.0,   0.0,
                   0.0,    0.0,    0.0,   1.0)

def addPerspective(vert, scale):
    """ Adds perspective; changes vert! """
    closeness = -2.0
    perspective = 1.0
    if (vert.z < closeness):
        perspective = scale / vert.z
    vert = vert * perspective
