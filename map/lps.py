
from pyrobot.map.tkmap import TkMap
from math import cos, sin, pi, sqrt

class LPS(TkMap):
   """
   GUI for visualizing the local perceptual space of a robot.
   """
   def __init__(self, cols, rows, value = 0.5,
                width = 200, height = 200,
                widthMM = 7500, heightMM = 7500,
                title = "Local Perceptual Space"):
      """ Pass in grid cols, grid cells, and total width/height in MM"""
      self.step = 0
      TkMap.__init__(self, cols, rows, value,
                     width, height,
                     widthMM, heightMM, title)

   def color(self, value, maxvalue):
      value = 1.0 - value / maxvalue
      color = "gray%d" % int(value * 100.0) 
      return color

   def computeOccupancy(self, origx, origy, hitx, hity, arc, senseObstacle, label = None):
      """
      Initially only compute occupancies on the line from the robot to
      the sensor hit.  
      """
      if self.debug: print "occupancyGrid:", (origx, origy, hitx, hity)
      # set the origin of sensor empty:
      self.setGridLocation(origx, origy, 0.0)
      rise = hity - origy
      if abs(rise) < 0.1:
         rise = 0
      run  = hitx - origx
      if abs(run) < 0.1:
         run = 0
      steps = int(round(max(abs(rise/self.rowScaleMM), abs(run/self.colScaleMM))))
      if steps == 0:
         self.setGridLocation(hitx, hity, 1.0, label)
         return
      stepx = run / float(steps)
      if abs(stepx) > self.colScaleMM:
         stepx = self.colScaleMM
         if run < 0:
            stepx *= -1
      stepy = rise / float(steps)
      if abs(stepy) > self.rowScaleMM:
         stepy = self.rowScaleMM
         if rise < 0:
            stepy *= -1
      currx = origx
      curry = origy
      for step in range(steps):
         curry += stepy
         currx += stepx
         self.setGridLocation(currx, curry, 0.0, label)
      if senseObstacle:
         self.setGridLocation(hitx, hity, 1.0, label)
      else:
         self.setGridLocation(hitx, hity, 0.0, label)

   def sensorHits(self, robot, item):
      """
      Point (0,0) is located at the center of the robot.
      Point (offx, offy) is the location of the sensor on the robot.
      Theta is angle of the sensor hit relative to heading 0.
      Dist is the distance of the hit from the sensor.
      Given these values, need to calculate the location of the hit
      relative to the center of the robot (hitx, hity).  

                    .(hitx, hity)
                   /
                  / 
                 /  
           dist /   
               /    
              /     
             /theta 
            .-------
           (offx, offy)
        
      .-->heading 0
      (0,0)
      
      """
      originalUnits = robot.__dict__[item].units
      robot.__dict__[item].units = 'METERS'
      radius = robot.radius
      # -----------------------------------
      for i in range(robot.__dict__[item].count):
         # in MM:
         offx, offy, z, theta, arc = robot.__dict__[item][i].geometry
         # in METERS, because we set it so above:
         dist = robot.__dict__[item][i].value
         if dist < robot.__dict__[item].getMaxvalue():
            senseObstacle = 1
         else:
            senseObstacle = 0
         # convert to MMs:
         hitx = cos(theta) * dist * 1000 + offx
         hity = sin(theta) * dist * 1000 + offy
         self.computeOccupancy(offx, offy, hitx, hity, arc, senseObstacle, i)
      robot.__dict__[item].units = originalUnits

   def redraw(self, drawRobot = False, drawLabels = True):
      maxval = 1
      for a in range(self.rows):
         for b in range(self.cols):
            i = self.cols - 1 - b
            j = a
            
            self.canvas.create_rectangle(int(j * self.colScale),
                                         int(i * self.rowScale),
                                         int((j + 1) * self.colScale),
                                         int((i + 1) * self.rowScale),
                                         width = 0,
                                         fill=self.color(self.grid[a][b],
                                                         maxval),
                                         tag = "cell%d" % self.step)
            if drawLabels and self.label[a][b]:
               self.canvas.create_text(int((j + .5) * self.colScale),
                                       int((i + .5) * self.rowScale),
                                       text = self.label[a][b],
                                       fill="yellow",
                                       tag = "cell%d" % self.step)
      if drawRobot:
         self.canvas.create_oval( self.width / 2.0 - 10,
                                  self.height / 2.0 - 10,
                                  self.width / 2.0 + 10,
                                  self.height / 2.0 + 10,
                                  fill = "red",
                                  tag = "cell%d" % self.step)
         self.canvas.create_rectangle( self.width / 2.0 - 5,
                                       self.height / 2.0 - 5,
                                       self.width / 2.0 + 5,
                                       self.height / 2.0 - 15,
                                       fill = "blue",
                                       tag = "cell%d" % self.step)
      self.step = not self.step
      self.canvas.delete("cell%d" % self.step)
      self.update_idletasks()

if __name__ == '__main__':
   lps = LPS(10, 10)
   lps.redraw()
   lps.application = 1
   lps.mainloop()
