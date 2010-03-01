from pyrobot.map.tkmap import TkMap

class occupancyGrid(TkMap):
   """
   GUI for visualizing an occupancy grid style map.
   
   The mouse can be used to change occupancy values:
   Press the left button for 1.0
   Press the middle button for 0.5
   Press the right button  for 0.0

   Certain keys provide other funtionality:
   Press 'S' to set the start cell of the path.
   Press 'G' to set the goal cell of the path.
   Press 'P' to plan the path.
   Press '2' to double the size of the occupancy grid.
   Press 'Q' to quit.
   """
   def __init__(self, start, goal):
      menu = [('File',[['Load map...',self.myLoadMap],
                       ['Save map...',self.saveMap],
                       ['Exit',self.destroy] 
                       ]),
              ]
      keybindings = [ ("<B1-Motion>", self.increaseCell),
                      ("<B2-Motion>", self.middleCell),
                      ("<B3-Motion>", self.decreaseCell),
                      ("<Button-1>", self.increaseCell),
                      ("<Button-2>", self.middleCell),
                      ("<Button-3>", self.decreaseCell),
                      ("<KeyPress-p>", self.findPath),
                      ("<KeyPress-s>", self.setStart),
                      ("<KeyPress-g>", self.setGoal),
                      ("<KeyPress-2>", self.setDouble),
                      ("<KeyPress-q>", self.destroy)
                      ]
      TkMap.__init__(self, 50, 50, 0.5,
                     200, 200, 100, 100,
                     "Occupancy Grid", menu, keybindings)
      self.threshhold = 0.8
      self.lastMatrix = self.grid
      self.lastPath = None
      self.start = start
      self.goal = goal
      self.infinity = 1e5000
      self.bigButNotInfinity = 5000
      self.value= [[self.infinity for col in range(self.cols)]
                   for row in range(self.rows)]

   def myLoadMap(self):
      TkMap.loadMap(self)
      self.redraw(self.grid, None)

   def increaseCell(self, event):
      self.canvas.focus_set()
      cellCol = int(round(event.x /self.colScale))
      cellRow = int(round((event.y - 15)/self.rowScale))
      self.grid[cellRow][cellCol] = 1.0
      self.redraw( self.grid, None)

   def middleCell(self, event):
      self.canvas.focus_set()
      cellCol = int(round(event.x/self.colScale))
      cellRow = int(round((event.y - 15)/self.rowScale))
      self.grid[cellRow][cellCol] = 0.5
      self.redraw( self.grid, None)

   def decreaseCell(self, event):
      self.canvas.focus_set()
      cellCol = int(round(event.x/self.colScale))
      cellRow = int(round((event.y - 15)/self.rowScale))
      self.grid[cellRow][cellCol] = 0.0
      self.redraw( self.grid, None)

   # Overloaded:
   def changeSize(self, event = 0):
      self.width = self.winfo_width() - 2
      self.height = self.winfo_height() - 30 # with menu
      self.canvas.configure(width = self.width, height = self.height)
      self.colScale = int(round(self.width / self.cols))
      self.rowScale = int(round(self.height / self.rows))
      try:
         self.redraw( self.lastMatrix, self.lastPath)
      except:
         pass

   def color(self, value, maxvalue):
      if value == self.infinity:
         return "brown"
      value = 1.0 - value / maxvalue
      color = "gray%d" % int(value * 100.0) 
      return color

   def setDouble(self, event):
      self.rows *= 2
      self.rowScale = int(round(self.height / self.rows))
      self.cols *= 2
      self.colScale = int(round(self.width / self.cols))
      self.value= [[self.infinity for col in range(self.cols)]
                   for row in range(self.rows)]
      self.grid= [[0.0 for col in range(self.cols)]
                  for row in range(self.rows)]
      self.redraw(self.grid)

   def setGoal(self, event):
      self.goal = int(round(event.x/self.colScale)), \
                  int(round((event.y - 15)/self.rowScale))
      self.redraw(self.grid)

   def setStart(self, event):
      self.start = int(round(event.x/self.colScale)), \
                   int(round((event.y - 15)/self.rowScale))
      self.redraw(self.grid)

   def findPath(self, event):
      if self.debug: print "Finding path..."
      if self.grid[self.goal[1]][self.goal[0]] > self.threshhold:
         raise "NoPathExists", "goal is in unattainable location"
      end = 10
      start = 0
      self.initPlanPath()
      done = 0
      path = None
      while not done:
         print "Trying %d iterations..." % end
         try:
            path = self.planPath(self.start, self.goal, range(start, end))
            done = 1
         except "NoPathExists":
            if end > 80:
               done = 1
            else:
               start = end
               end *= 2
      print "iterations:", end
      if path:
         print "Done!"
         self.redraw(g.value, path)
      else:
         raise "NoPathExists", "maximum interation limit exceded"

   def redraw(self, matrix, path = None):
      self.lastMatrix = matrix
      self.lastPath = path
      maxval = 0.0
      for i in range(self.rows):
         for j in range(self.cols):
            if matrix[i][j] != self.infinity:
               maxval = max(matrix[i][j], maxval)
      if maxval == 0: maxval = 1
      self.canvas.delete("cell")
      for i in range(self.rows):
         for j in range(self.cols):
            self.canvas.create_rectangle(j * self.colScale,
                                         i * self.rowScale,
                                         (j + 1) * self.colScale,
                                         (i + 1) * self.rowScale,
                                         width = 0,
                                         fill=self.color(matrix[i][j], maxval),
                                         tag = "cell")
            if path and path[i][j] == 1:
               self.canvas.create_oval((j + .25) * self.colScale,
                                       (i + .25) * self.rowScale,
                                       (j + .75) * self.colScale,
                                       (i + .75) * self.rowScale,
                                       width = 0,
                                       fill = "blue",
                                       tag = "cell")

      self.canvas.create_text((self.start[0] + .5) * self.colScale,
                              (self.start[1] + .5) * self.rowScale,
                              tag = 'cell',
                              text="Start", fill='green')
      self.canvas.create_text((self.goal[0] + .5) * self.colScale,
                              (self.goal[1] + .5) * self.rowScale,
                              tag = 'cell',
                              text="Goal", fill='green')

   def tooTight(self, row, col, i, j):
      """ Check to see if you aren't cutting a corner next to an obstacle."""
      return self.value[row + i][col] == 1e5000 or \
                 self.value[row][col + j] == 1e5000

   def initPlanPath(self):
      self.value= [[self.infinity for col in range(self.cols)] for row in range(self.rows)]

   def planPath(self, start, goal, iterator):
      """
      Path planning algorithm is based on one given by Thrun in the
      chapter 'Map learning and high-speed navigation in Rhino' from
      the book 'Artificial Intelligence and Mobile Robots' edited by
      Kortenkamp, Bonasso, and Murphy.

      Made two key changes to the algorithm given.
      1. When an occupancy probability is above some threshold, assume
         that the cell is occupied and set its value for search to
         infinity.
      2. When iterating over all cells to update the search values, add
         in the distance from the current cell to its neighbor.  Cells
         which are horizontal or vertical from the current cell are
         considered to be a distance of 1, while cells which are diagonal
         from the current cell are considered to be a distance of 1.41.
      """
      startCol, startRow = start
      goalCol, goalRow = goal
      if not self.inRange(goalRow, goalCol):
         raise "goalOutOfMapRange"
      self.value[goalRow][goalCol] = 0.0
      for iter in iterator:
         for row in range(self.rows):
            for col in range(self.cols):
               for i in [-1,0,1]:
                  for j in [-1,0,1]:
                     if self.inRange(row+i, col+j):
                        if self.grid[row][col] > self.threshhold:
                           self.value[row][col] = self.infinity
                        else:
                           if self.tooTight(row, col, i, j):
                              d = self.bigButNotInfinity
                           elif abs(i) == 0 and abs(j) == 0:
                              d = 0.00
                           elif abs(i) == 1 and abs(j) == 1:
                              d = 1.41
                           else:
                              d = 1.00
                           adj = self.value[row+i][col+j] + self.grid[row+i][col+j] + d
                           self.value[row][col] = min(self.value[row][col], adj)
      return self.getPath(startRow, startCol)

   def getPath(self, startRow, startCol):
      path = [[0 for col in range(self.cols)] for row in range(self.rows)]
      row = startRow
      col = startCol
      steps = 0
      while not (self.value[row][col] == 0.0):
         path[row][col] = 1
         min = self.bigButNotInfinity
         nextRow = -1
         nextCol = -1
         for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
               if self.inRange(row+i, col+j):
                  if self.value[row+i][col+j] < min and \
                         not self.tooTight(row, col, i, j):
                     min = self.value[row+i][col+j]
                     nextRow = row+i
                     nextCol = col+j
         if nextRow == -1:
            raise "NoPathExists"
         steps += 1
         row = nextRow
         col = nextCol
      path[row][col] = 1
      print "Path is %d steps" % steps
      return path

if __name__ == '__main__':
   # An occupancy grid of a simple world with an L-shaped obstacle
   map = [[0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
          [0.5, 0.5, 0.5, 0.0, 0.5, 1.0, 1.0, 1.0, 1.0, 0.5],
          [1.0, 1.0, 0.5, 0.0, 0.5, 1.0, 0.5, 0.5, 1.0, 0.5],
          [1.0, 1.0, 0.5, 0.0, 0.5, 1.0, 0.5, 0.5, 0.5, 0.5],
          [0.5, 0.5, 0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 1.0, 0.5],
          [0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 1.0, 0.5],
          ]
   g = occupancyGrid((0, 0), (6, 2))
   g.setGrid( map )
   # Find a path from position 0,0 to a point on the other side of
   # the L-shaped obstacle.
   g.redraw(map) # forces it to redraw the map, rather than default
   g.application = 1
   g.mainloop()
