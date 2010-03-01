class Renderer:
   """abstract interface for all things Renderable"""
   def __init__(self):
      raise "abstract method called in Renderer"
   def xformPush(self, dummy):
      raise "abstract method called in Renderer"
   def xformPop(self):
      raise "abstract method called in Renderer"
   def xformRotate(self,(qty,pt)):
      raise "abstract method called in Renderer"
   def xformXlate(self,(pt)):
      raise "abstract method called in Renderer"
   def xformScale(self,(scale)):
      raise "abstract method called in Renderer"
   def setLocation(self,x,y,z,theta):
      raise "abstract method called in Renderer"
   def color(self,(color)):
      raise "abstract method called in Renderer"
   def ray(self,(pta,ptb,arc)):
      raise "abstract method called in Renderer"
   def line(self,(pta,ptb)):
      raise "abstract method called in Renderer"
   def circle(self,(pt,norm,radius)):
      raise "abstract method called in Renderer"
   def triangle(self,(pta,ptb,ptc)):
      raise "abstract method called in Renderer"
   def text(self,(str)):
      raise "abstract method called in Renderer"
   def rectangle(self,(pta,ptb,ptc)):
      raise "abstract method called in Renderer"
   def box(self,(pta,ptb, ptc, ptd)):
      raise "abstract method called in Renderer"
   def torus(self, (ir, ora, n, r)):
      raise "abstract method called in Renderer"
   def polygon(self,*args):
      raise "abstract method called in Renderer"
   def clearState(self, dummy):
      raise "abstract method called int Render"
   def clearColor(self, color):
      raise "abstract method called int Render"

