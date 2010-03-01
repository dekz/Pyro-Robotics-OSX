from pyrobot.gui.renderer import *
from math import sin, cos

class TKRenderer(Renderer):
   def __init__(self):
      self.blue = (0.1, 0.1, 0.9, 1.)
      self.darkred = (0.6, 0.1, 0.1, 1.0)
      self.red = (1.0, 0.0, 0.0, 1.0)
      self.lightgray = (0.75, 0.75, 0.75, 1.0)
      self.gray = (0.5, 0.5, 0.5, 1.0)
      self.darkgray = (0.25, 0.25, 0.25, 1.0) 
   def xformPush(self, dummy):
      pass
   def xformPop(self, dummy):
      pass
   def xformRotate(self,(qty, pt)):
      pass
   def xformXlate(self,(pt)):
      pass
   def xformScale(self,(scale)):
      pass
   def setLocation(self,x,y,z,theta):
      pass
   def color(self,(color)):
      pass
   def ray(self, (pta, ptb, arc)):
      pt1 = [0, 0, 0]
      pt2 = [0, 0, 0]
      pt3 = [0, 0, 0]
      pt4 = [0, 0, 0]
      # arc off of pta, in radians
      pt1[0] = pta[0] * cos(arc) + pta[1] * sin(arc)
      pt1[1] = pta[1] * cos(arc) - pta[0] * sin(arc)
      pt1[2] = pta[2] 
      # arc off of pta, in radians
      pt2[0] = pta[0] * cos(-arc) + pta[1] * sin(-arc)
      pt2[1] = pta[1] * cos(-arc) - pta[0] * sin(-arc)
      pt2[2] = pta[2] 
      # arc off of pta, in radians
      pt3[0] = ptb[0] * cos(arc) + ptb[1] * sin(arc)
      pt3[1] = ptb[1] * cos(arc) - ptb[0] * sin(arc)
      pt3[2] = ptb[2] 
      # arc off of pta, in radians
      pt4[0] = ptb[0] * cos(-arc) + ptb[1] * sin(-arc)
      pt4[1] = ptb[1] * cos(-arc) - ptb[0] * sin(-arc)
      pt4[2] = ptb[2] 
      self.polygon((pt1, pt2, pt4, pt3))
   def line(self, (pta, ptb)):
      raise "abstract method called in Renderer"
   def circle(self,(pt,norm,radius)):
      raise "abstract method called in Renderer"
   def triangle(self,(pta,ptb,ptc)):
      pass
   def text(self, (str)):
      print str
   def getFourthPoint(self,pta,ptb,ptc):
      return (pta[0]-ptb[0]+ptc[0],pta[1]-ptb[1]+ptc[1],pta[2]-ptb[2]+ptc[2] )
   def normalize(self, out):
      import math
      try:
         length = math.sqrt((out[0] * out[0]) + \
                            (out[1] * out[1]) + \
                            (out[2] * out[2]))
      except OverflowError:
         length = 1
      if length == 0: length = 1
      out[0] /= length
      out[1] /= length
      out[2] /= length
      return out
   def glNormal(self, out):
      pass
   def normal_vector(self, pta, ptb, ptc):
      x, y, z = 0, 1, 2
      v1 = [0, 0, 0]
      v2 = [0, 0, 0]
      out = [0, 0, 0]
      for dim in range(3):
         v1[dim] = pta[dim] - ptb[dim]
         v2[dim] = ptb[dim] - ptc[dim]
      out[x] = v1[y] * v2[z] - v1[z] * v2[y]
      out[y] = v1[z] * v2[x] - v1[x] * v2[z]
      out[z] = v1[x] * v2[y] - v1[y] * v2[x]
      return self.normalize(out)
   def rectangle(self, (pta, ptb, ptc)):
      ptd = self.getFourthPoint(pta,ptb,ptc)
      pass
   def box(self,(pta,ptb,ptc,ptd)):
      pte = self.getFourthPoint(pta,ptb,ptc)
      ptf = self.getFourthPoint(ptb,pta,ptd)
      ptg = self.getFourthPoint(ptc,ptb,ptf)
      self.rectangle((pta,ptb,ptc))
      self.rectangle((ptb,pta,ptd))
      self.rectangle((ptc,ptb,ptf))
      self.rectangle((pte,ptc,ptg))
      self.rectangle((ptd,pta,pte))
      self.rectangle((ptg,ptf,ptd))
      self.rectangle((pte,ptc,ptg))
   def torus(self, (ir, ora, n, r)):
      pass
   def polygon(self,*args):
      args = args[0]
      #self.glNormal(self.normal_vector(args[0], args[1], args[2]));
      #glBegin(GL_POLYGON)
      #for p in args:
      #   glVertex3fv(p)
      #glEnd()
   def clearState(self, dummy):
      pass
   def clearColor(self, color):
      #glClearColor(color[0],color[1],color[2], 0)
      #glClear(GL_COLOR_BUFFER_BIT)
      pass
   
