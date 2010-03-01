"""
Fuzzy Logic Base Class
E. Jucovy, 2005
based on fuzzy.py by D.S. Blank, 2001
"""

__author__ = "E. Jucovy, Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision$"

from math import exp
  
class FuzzyOperators:
  def Union(self,a,b):
    pass

  def Intersection(self,a,b):
    pass

  def Complement(self,a):
    pass

  def __str__(self):
    return self.__class__.__name__

class StandardFuzzyOperators(FuzzyOperators):
  def Union(self,a,b):
    return max(a,b)

  def Intersection(self,a,b):
    return min(a,b)

  def Complement(self,a):
    return 1.0 - a

class FuzzyError(TypeError):
  def __init__(self, st=""):
    TypeError.__init__(self, st)

class FuzzyValue:
  """
  Fuzzy value class

  Contains a floating-point value between 0 and 1
  """
  
  def __init__(self, val, ops = StandardFuzzyOperators()):
    """
    Initialize the fuzzy value

    If val is less than zero or greater than one, limit val to those bounds
    """
    
    self.Ops = ops
    if val < 0:
      self.Value = 0.0
    elif val > 1:
      self.Value = 1.0
    else:
      self.Value = float(val)

  def __and__(self, other):
    """
    Return the intersection of self and other
    """  
    return FuzzyValue(self.Ops.Intersection(self.Value, float(other)), self.Ops)

  def __or__(self, other):
    """
    Return the union of self and other
    """
    return FuzzyValue(self.Ops.Union(self.Value, float(other)), self.Ops)

  def __neg__(self):
    """
    Return the complement of self
    """
    return FuzzyValue(self.Ops.Complement(self.Value), self.Ops)

  __invert__ = __neg__

  def __add__(self, other):
    return FuzzyValue(self.Value + float(other), self.Ops)

  __radd__ = __add__
  
  def __sub__(self, other):
    return FuzzyValue(self.Value - float(other), self.Ops)

  def __rsub__(self, other):
    return FuzzyValue(float(other) - self.Value, self.Ops)

  def __mul__(self, other):
    return FuzzyValue(self.Value * float(other), self.Ops)

  __rmul__ = __mul__
  
  def __div__(self, other):
    return FuzzyValue(self.Value / float(other), self.Ops)

  def __rdiv__(self, other):
    return FuzzyValue(float(other) / self.Value, self.Ops)

  def __cmp__(self, other):
    return self.Value - float(other)
  
  def __float__(self):
    return self.Value

  defuzzify = __float__

  def __str__(self):
    return "<Fuzzy value " + str(self.Value) + ">"
  
#  def alphaCut(self, alpha):
#    return self.Value >= alpha 

class FuzzyClassifier:
  """
  Fuzzy classifier class with a membership function and parameters.

  Membership function can be set on initialization or with
  setMembershipFunction(function). The membership function should
  return a value between 0 and 1 (values outside that range will be
  automatically set to either 0 or 1).
  
  All relevant parameters used by the membership function can be set
  on initialization or by setParams()
  """
  
  def __init__(self, func=None, fName=None, ops=StandardFuzzyOperators(), **kwargs):
    """
    Initialize the FuzzyClassifier
    
    First argument is a reference to the membership function
    Second argument is the name of the membership function
    Remaining arguments are parameter names and values
    """

    self.myParams = {}

    if func.__class__ is FuzzyClassifier:
      self.Function = func.Function
      self.myParams = func.myParams 
    elif not func is None:
      self.Function = func
    else:
      def Halfway():
        return 0.5
      self.Function = Halfway

    if func.__class__ is FuzzyClassifier:
      self.FunctionName = func.FunctionName      
    elif not fName is None:
      self.FunctionName = fName
    else:
      self.FunctionName = self.Function.__name__
    self.__name__ = "FuzzyClassifier:%s" % self.FunctionName

    self.Ops = ops
    for i in kwargs:
      self.myParams[i] = kwargs[i]
    
  def __call__(self, *args):
    """
    Apply the fuzzy classifier to a set of values

    Return a FuzzyValue with value Function(args)
    """

    # get params and function arguments
    mydict = {}
    args = list(args)
    funcargs = list(self.Function.func_code.co_varnames
                    [:self.Function.func_code.co_argcount])
    for i in funcargs:
      try:
        mydict[i] = self.myParams[i]
      except KeyError:
        try:
          mydict[i] = args.pop(0)
        except IndexError:
          raise TypeError("Too few arguments to FuzzyClassifier %s()" \
                          % (self.FunctionName))

    x = len(mydict) - self.Function.func_code.co_argcount
    if x == -1:
      raise FuzzyError("1 undefined parameter to FuzzyClassifier %s" \
                      % self.FunctionName)
    elif x < 0:
      raise FuzzyError("%d undefined parameters to FuzzyClassifier %s" \
                      % (-x, self.FunctionName))
    
    return FuzzyValue(self.Function(**mydict), self.Ops)

  def safesetParams(self, **kwargs):
    """
    Set one or more of the classifier's parameters
    without overwriting any predefined parameters.
    If a parameter is already defined safesetParams
    will not overwrite it.
    """
    keys = kwargs.keys()
    for key in keys:
      if not self.myParams.has_key(key):
        self.myParams[key] = kwargs[key]

  def setParams(self, **kwargs):
    """
    Set one or more of the classifier's parameters
    without deleting predefined parameters; but will
    overwrite parameters.
    """
    keys = kwargs.keys()
    for key in keys:
      self.myParams[key] = kwargs[key]

  def resetParams(self, **kwargs):
    """
    Set all the classifier's parameters at once and
    delete all parameters that might already exist
    """
    self.myParams = kwargs
    
  def getParam(self, *names):
    """
    Return one or more of the classifier's parameters
    """
    retlist = []
    for name in names:
      try:
        retlist.append(self.myParams[name])
      except KeyError:
        retlist.append(None)
    return retlist

  def setFunction(self, func, fName = None):
    """
    Set the classifier's membership function

    First (required) parameter is the membership function itself.
    
    Second (optional) parameter is a name for the function, recommended,
    e.g., for lambda functions; if this is not set then the function's
    actual name will be used
    """

    if not fName is None:
      self.FunctionName = fName      
    elif func.__class__ is FuzzyClassifier:
      self.FunctionName = func.FunctionName
    else:
      self.FunctionName = func.__name__

    if func.__class__ is FuzzyClassifier:
      self.Function = func.Function
      self.safesetParams(**func.myParams)
    else:
      self.Function = func

    self.__name__ = "FuzzyClassifier:%s" % self.FunctionName
   
  def __str__(self):
    return "FuzzyClassifier instance with\n\tmembership function " + \
           "%s\n\tparameters %s\n\toperator set %s" \
           % (self.FunctionName, self.myParams, self.Ops)
   
  def __nonzero__(self):
    return True

  def __rshift__(self, val):
    """
    Return a FuzzyValue classified under a linear rising
    membership function whose parameters are decided by the
    current FuzzyClassifier's parameters

    Implemented for backwards compatibility
    """
    keys = self.myParams.keys()
    if len(keys) > 2:
      print "This may not do what you expect."
    a = self.myParams[keys[0]]
    b = self.myParams[keys[1]]
    if a > b:
      aFC = RisingFuzzy(b,a)
    else:
      aFC = RisingFuzzy(a,b)
    return aFC(val)

  def __lshift__(self, val):
    """
    Return a FuzzyValue classified under a linear falling
    membership function whose parameters are decided by the
    current FuzzyClassifier's parameters

    Implemented for backwards compatibility
    """
    keys = self.myParams.keys()
    if len(keys) > 2:
      print "This may not do what you expect."
    a = self.myParams[keys[0]]
    b = self.myParams[keys[1]]
    if a > b:
      aFC = FallingFuzzy(b,a)
    else:
      aFC = FallingFuzzy(a,b)
    return aFC(val)

def Fuzzy(a,b):
  """
  Create a new FuzzyClassifier with two parameters and
  default membership function

  Implemented for backwards compatibility
  """
  return FuzzyClassifier(a=a,b=b)

def RisingFuzzy(a,b):
  """
  Create a new FuzzyClassifier with a linear rising membership
  function and parameters a,b

  a: lower bound, mu(a) = 0.0
  b: upper bound, mu(b) = 1.0
  """
  
  def __upMF(x0,a,b):
    """
    A linear rising membership function
    """
    if x0 < a:
      return 0.0
    elif x0 > b:
      return 1.0
    else:
      return float(x0 - a) / (b - a)

  return FuzzyClassifier(__upMF, "Rising", a=a, b=b)

def FallingFuzzy(a,b):
  """
  Create a new FuzzyClassifier with a linear falling membership
  function and parameters a,b

  a: lower bound, mu(a) = 1.0
  b: upper bound, mu(b) = 0.0
  """

  def __downMF(x0,a,b):
    """
    A linear falling membership function
    """
    if x0 < a:
      return 1.0
    elif x0 > b:
      return 0.0
    else:
      return float(b - x0) / (b - a)

  return FuzzyClassifier(__downMF, "Falling", a=a, b=b)

def TriangleFuzzy(a,b,c):
  """
  Create a new FuzzyClassifier with a linear triangular membership
  function and parameters a,b,c

  a: lower bound, mu(a) = 0.0
  b: midpoint, mu(b) = 1.0
  c: upper bound, mu(c) = 0.0
  """

  def __triMF(x0,a,b,c):
    """
    A linear triangular membership function
    """
    if x0 < a:
      return 0.0
    elif x0 < b:
      return float(x0 - a) / (b - a)
    elif x0 < c:
      return float(c - x0) / (c - b)
    else:
      return 0.0

  return FuzzyClassifier(__triMF, "Triangle", a=a, b=b, c=c)

def TrapezoidFuzzy(a,b,c,d):
  """
  Create a new FuzzyClassifier with a linear trapezoidal membership
  function and parameters a,b,c,d

  a: lower bound, mu(a) = 0.0
  b: start of top, mu(b) = 1.0
  c: end of top, mu(c) = 1.0
  d: upper bound, mu(d) = 0.0
  """
  
  def __trapMF(x0,a,b,c,d):
    """
    A linear trapezoidal membership function
    """
    if x0 < a:
      return 0.0
    elif x0 < b:
      return float(x0 - a) / (b - a)
    elif x0 < c:
      return 1.0
    elif x0 < d:
      return float(d - x0) / (d - c)
    else:
      return 0.0

  return FuzzyClassifier(__trapMF, "Trapezoid", a=a, b=b, c=c, d=d)

def GaussianFuzzy(c,s):
  """
  Create a new FuzzyClassifier with a gaussian membership function
  and parameters c,s

  c: center (mean), mu(c) = 1.0
  s: spread (standard deviation)
  """

  def __GaussMF(x0,c,s):
    """
    A Gaussian membership function
    """
    return exp(pow((float(x0) - c) / s, 2.0) / -2.0)

  return FuzzyClassifier(__GaussMF, "Gaussian", c=c, s=s)

# needs comment
def BellFuzzy(a,b,c):
  """
  All values will effectively be mapped to either 0, 0.5, or 1.
  (Not quite, since it's continuous, but close.)
  """
  
  def __BellMF(x,a,b,c):
    return 1.0 / (1.0 + pow((x - c) / a, 2.0*b))
  
  return FuzzyClassifier(__BellMF, "BellCurve", a=a,b=b,c=c)

# NOT YET
def SigmoidFuzzy(a,c):
  """
  Create a new FuzzyClassifier with a sigmoid membership function
  and parameters a,c

  I wouldn't use this yet if I were you.
  """

  def __SigmoidMF():
    """
    I wouldn't use this yet if I were you
    """
    return 1.0 / (1.0 + exp(-a * (x - c)))

  return FuzzyClassifier(__SigmoidMF, "Sigmoid", a=a, c=c)

# NOT YET TESTED
def LRFuzzy(f,g,c,a,b):
  """
  Create a new FuzzyClassifier with a left-right membership
  function and parameters f,g,c,a,b

  f: left-side function (or FuzzyClassifier)
  g: right-side function (or FuzzyClassifier)
  c: switching point
  """

  def __LRMF():
    """
    I wouldn't use this yet if I were you
    """
    if x <= c:
      return f((c - x) / a)
    return g((x - c) / b)

  return FuzzyClassifier(__LRMF, "Left"+f.__name__+"Right"+g.__name__,
                         f=f,g=g,c=c,a=a,b=b)
    
if __name__ == '__main__': # some tests
  f = BellFuzzy(10,20,30)
  for i in range(100):
    print str(i) + ", " + str(float(f(i)))

