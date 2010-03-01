#
# this is the geometry code. It is all R^3.
#
# All vectors/points are lists w/ 3 elements [x,y,z]
#
# Affine vectors are tuples like: ([x,y,z],[i,j,k])
#
#
# - stephen -
#

import math
TOLERANCE = .0001
PIOVER180 = math.pi / 180.0
PITIMES180 = math.pi * 180.0
DEG90RADS = 0.5 * math.pi
COSDEG90RADS = math.cos(DEG90RADS) / 1000.0
SINDEG90RADS = math.sin(DEG90RADS) / 1000.0

def distance(x1, y1, x2, y2):
    return math.sqrt( (x1 - x2) ** 2 + (y1 - y2) ** 2 )

def angleAdd(angle, degree): # angles in degrees
    return (angle + degree) % 360 # make positive, in range 0-360

def angleEqual(angle1, angle2, tolerance = 5): # angles and tolerance in degrees
    return abs((angle1 % 360)  - (angle2 % 360)) < tolerance

class Polar:
   def __init__(self, dt = 0.0, dr = 0.0, bIsPolar = 1):
      if (bIsPolar):
         self.t = dt
         self.r = dr
      else:
         self.t = math.atan2(dr,dt)
         self.r = math.sqrt(dr*dr + dt*dt)

   def setCartesian(self, dx, dy):
      self.t = math.atan2(dy,dx)
      self.r = math.sqrt(dx*dx + dy*dy)
      return self

class Vector:
   def __init__(self, d, a):
      self.distance = d
      self.angle = a

def vector():
    return [0,0,0]

def point():
    return [0,0,0]

def PrintPoint(a):
    return "(" + str(a[0]) + " ," + str(a[1]) + " ," + str(a[2])+")"

def affineVector():
    return (point(),vector())

def sub(a,b):
    c = vector()
    c[0] = a[0]-b[0]
    c[1] = a[1]-b[1]
    c[2] = a[2]-b[2]
    return c

def inverse(a):
    c = vector()
    c[0] = -a[0]
    c[1] = -a[1]
    c[2] = -a[2]
    return c

def add(a,b):
    c = vector()
    c[0] = a[0]+b[0]
    c[1] = a[1]+b[1]
    c[2] = a[2]+b[2]
    return c

def multiply(a,b):
    "a is float, b is matrix "
    c = point()
    for x in range(0,3):
        c[x] = a*b[x]
    return c

def dot(a,b, dim=3):
    sum = 0
    for x in range(0,dim):
        sum = sum + a[x]*b[x]
    return sum

def cross(a,b):
    c = vector()    
    c[0] = a[1]*b[2] - a[2]*b[1]
    c[1] = a[2]*b[0] - a[0]*b[2]
    c[2] = a[0]*b[1] - a[1]*b[0]
    return c

def norm(a):
    return math.sqrt(dot(a,a))

def normalize(a, dim = 3):
    b = vector()
    l = norm(a)
    for x in range(0,dim):
        b[x] = a[x]/l
    return b

def angle(a,b=[1,0,0]):
    #print "angle", a, b
    return math.acos(dot(normalize(a),normalize(b)))

def toleq(a,b):
    if abs(a-b) > TOLERANCE:
        return 0
    return 1

def distance2(a, b):
    c = sub(a,b)
    return dot(c,c)
	
def pol2car(ang, length):#2d
    return [math.cos(ang)*length, math.sin(ang)*length, 0]

def rotate(vec, ang):#2d
    if (ang==0):
        return vec
    if (norm(vec) ==0):	#length of vec is 0!
        return vec
    #print "rotate",vec, ang
    return pol2car(angle(vec) + ang, dot(vec, vec))

class Segment:
    def __init__(self, start, end, id = None):
        self.start = start
        self.end = end
        self.id = id
    def midpoint(self):
        return ((self.start[0] + self.end[0])/2.,
                (self.start[1] + self.end[1])/2.)
    def length(self):
        return math.sqrt((self.start[0] - self.end[0])**2 +
                         (self.start[1] - self.end[1])**2)
    def vertical(self):
        return self.start[0] == self.end[0]
    # don't call this if the line is vertical
    def slope(self):
        return (self.end[1] - self.start[1])/(self.end[0] - self.start[0])
    # or this
    def yintercept(self):
        return self.start[1] - self.start[0] * self.slope()
    def angle(self):
        return math.atan2(self.end[1] - self.start[1], self.end[0] - self.start[0])
    def parallel(self, other):
        if self.vertical():
            return other.vertical()
        elif other.vertical():
            return 0
        else:
            return self.slope() == other.slope()
    # return the point at which two segments would intersect if they extended
    # far enough
    def intersection(self, other):
        if self.parallel(other):
            # the segments may intersect, but we don't care
            return None
        elif self.vertical():
            return other.intersection(self)
        elif other.vertical():
            return (other.start[0],
                    self.yintercept() + other.start[0] * self.slope())
        else:
            # m1x + b1 = m2x + b2; so
            # (m1 - m2)x + b1 - b2 == 0
            # (m1 - m2)x = b2 - b1
            # x = (b2 - b1)/(m1 - m2)
            x = ((other.yintercept() - self.yintercept()) /
                 (self.slope() - other.slope()))
            return (x, self.yintercept() + x * self.slope())
    def in_bbox(self, point):
        return ((point[0] <= self.start[0] and point[0] >= self.end[0] or
                 point[0] <= self.end[0] and point[0] >= self.start[0]) and
                (point[1] <= self.start[1] and point[1] >= self.end[1] or
                 point[1] <= self.end[1] and point[1] >= self.start[1]))
    # is a point collinear with this line segment?
    def on_line(self, point):
        if self.vertical():
            return point[0] == self.start[0]
        else:
            return (point[0] * self.slope() + self.yintercept() == point[1])
    def intersects(self, other):
        if self.parallel(other):
            # they can "intersect" if they are collinear and overlap
            if not (self.in_bbox(other.start) or self.in_bbox(other.end)):
                return None
            elif self.vertical():
                if self.start[0] == other.start[0]:
                    return self.intersection(other)
                else:
                    return None
            else:
                if self.yintercept() == other.yintercept():
                    return self.intersection(other)
                else:
                    return None
        else:
            i = self.intersection(other)
            if self.in_bbox(i) and other.in_bbox(i):
                return i
            else:
                return None

if __name__ == '__main__':
    print math.sqrt(9)
    x1 = [1,0,0]
    x2 = [0,1,0]
    x3 = [0,0,1]
    a  = [1,1,1]
    b  = [-1,1,2]
    
    if not toleq(angle(x1,x2),math.pi/2):
        print "angle is broken ",angle(x1,x2)," insted of ",math.pi/2
        
    if cross(x1,x2) != x3:
        print "cross is broken"

