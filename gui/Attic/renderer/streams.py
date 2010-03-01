import string
#from pickle import *
from cPickle import *
from pyrobot.gui.renderer import Renderer

class GenericStream:
   def __init__(self):
      self.status = 0
      self.data = ''
      self.lines = []
      self.copy = []
   def write(self, arg):
      self.data += arg
   def read(self, n):
      if n > len(self.lines[0]):
         raise EOFError
      else:
         retval = self.lines[0][:n]
         self.lines[0] = self.lines[0][n:]
         return retval
   def readline(self):
      retval = self.lines[0]
      self.lines = self.lines[1:]
      return retval + '\012'
   def open(self, type):
      self.__init(self)
      pass
   def close(self): # close it, and now you can read from it
      if not self.status:
         self.lines = string.split(self.data, '\012')
         self.data = ''
         self.copy = self.lines[:]
         self.status = 1
   def reset(self):
      self.lines = self.copy[:]

class StreamTranslator:
   """receives a pickled render command stream from a file
      and sends it to the given renderer"""
   
   def __init__(self,stream,renderer,debug = 0):
      self.debug = debug
      self.stream = Unpickler(stream)
      self.renderer = renderer

   def process(self):
      while (self.process_item()):
         pass
      
   def process_item(self):
      try:
         command, args = self.stream.load()
         if self.debug: print "DEBUG: StreamTranslator, process:", command, args
         self.renderer.__class__.__dict__.get(command)(self.renderer, args)
         return 1
      except EOFError: 
         return 0 


class StreamRenderer(Renderer):
   """writes a pickled command stream to a file as
      the interface is used"""
   
   def __init__(self,file):
      self.stream = Pickler(file)
      
   def xformPush(self):
      self.stream.dump(('xformPush', ()))
   def xformPop(self):
      self.stream.dump(('xformPop',()))
   def xformRotate(self,qty,pt):
      self.stream.dump(('xformRotate',(qty,pt)))
   def xformXlate(self,pt):
      self.stream.dump(('xformXlate',(pt)))
   def xformScale(self,scale):
      self.stream.dump(('xformScale',(scale)))
   def color(self,color):
      self.stream.dump(('color',(color)))
   def ray(self,pta,ptb,arc):
      self.stream.dump(('ray',(pta, ptb, arc)))
   def line(self,pta,ptb):
      self.stream.dump(('line',(pta,ptb)))
   def circle(self,pt,norm,radius):
      self.stream.dump(('circle',(pt,norm,radius)))
   def triangle(self, pta,ptb,ptc):
      self.stream.dump(('triangle',(pta,ptb,ptc)))
   def text(self,(str)):
      self.stream.dump(('text',(str)))
   def rectangle(self,pta,ptb,ptc):
      self.stream.dump(('rectangle',(pta,ptb,ptc)))
   def box(self,pta,ptb,ptc, ptd):
      self.stream.dump(('box',(pta,ptb,ptc, ptd)))
   def torus(self, ir, ora, n, r):
      self.stream.dump(('torus',(ir, ora, n, r)))
   def polygon(self,*args):
      self.stream.dump(('polygon',args))
   def clearState(self):
      self.stream.dump(('clearState',()))
   def clearColor(self, color):
      self.stream.dump(('clearColor',(color)))

