from pyrobot.gui.renderer import *

class TTYRenderer(Renderer):
   def __init__(self):
      pass
   def ray(self, (pta, ptb, arc)):
      print "-> Ray", pta, ptb, arc
   def xformPush(self, dummy):
      print "-> PushMatrix"
   def xformPop(self, dummy):
      print "-> PopMatrix"
   def xformRotate(self,(qty,pt)):
      print "-> Rotate"
   def xformXlate(self,(pt)):
      print "-> Translate", pt
   def xformScale(self,(scale)):
      print "-> Scale", scale
   def color(self,(color)):
      print "-> Color", color
   def line(self,(pta,ptb)):
      print "-> Line", pta, ptb
   def circle(self,(pt,norm,radius)):
      print "-> Circle", pt, norm, radius
   def triangle(self,(pta,ptb,ptc)):
      print "-> Triangle", pta, ptb, ptc
   def text(self,(str)):
      print "-> Text", str
   def rectangle(self,(pta,ptb,ptc)):
      print "-> Rectangle"
   def box(self,(pta,ptb,ptc, ptd)):
      print "-> Box"
   def torus(self, (ir, ora, n, r)):
      print "-> Torus"
   def polygon(self,*args):
      print "-> Polygon", args
   def clearState(self, dummy):
      print "-> Clear"
   def clearColor(self, color):
      print "-> ClearColor"
   

