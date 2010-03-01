# pyrobot/map/__init__.py

class Map:
    """ Basic class for global internal robot maps"""

    def __init__(self, cols, rows, widthMM, heightMM):
        """ Constructor for basic map class """
        self.cols = cols
        self.rows = rows
        self.widthMM = widthMM
        self.heightMM = heightMM
        self.originMM = self.widthMM / 2.0, self.heightMM / 2.0
        self.colScaleMM = self.widthMM / self.cols
        self.rowScaleMM = self.heightMM / self.rows
        self.reset()

    def reset(self, value = 0.5):
        self.grid = [[value for col in range(self.cols)]
                     for row in range(self.rows)]
        self.label = [['' for col in range(self.cols)]
                      for row in range(self.rows)]

    def setGridLocation(self, x, y, value, label = None, absolute = 0):
        if( absolute == 0 ):
            xpos = int((self.originMM[0] + x) / self.colScaleMM)
            ypos = int((self.originMM[1] - y) / self.rowScaleMM)
        else:
            xpos = x
            ypos = y

        if self.inRange(ypos, xpos):
            # if hit was already detected, leave it alone!
            ##if self.grid[ypos][xpos] != 1.0:
            self.grid[ypos][xpos] = value
            if label != None:
                self.label[ypos][xpos] = "%d" % label
        else:
            print "INVALID GRID LOCATION"

    def getGridLocation(self, x, y, absolute = 0 ):
        if( absolute == 0 ):
            xpos = int((self.originMM[0] + x) / self.colScaleMM)
            ypos = int((self.originMM[1] - y) / self.rowScaleMM)
        else:
            xpos = x
            ypos = y

        if self.inRange(ypos, xpos):
            return( self.grid[ypos][xpos] )
        else:
            print "INVALID GRID LOCATION"
            return( -1 )
        
    def addGridLocation(self, x, y, value, label = None, absolute = 0 ):
        if( absolute == 0 ):
            xpos = int((self.originMM[0] + x) / self.colScaleMM)
            ypos = int((self.originMM[1] - y) / self.rowScaleMM)
        else:
            xpos = x
            ypos = y

        if self.inRange(ypos, xpos):
            self.grid[ypos][xpos] += value
            if label != None:
                self.label[ypos][xpos] = "%d" % label

    def inRange(self, r, c):
        return r >= 0 and r < self.rows and c >= 0 and c < self.cols

    def display(self, m = None):
        if m == None: m = self.grid
        for i in range(self.rows):
            for j in range(self.cols):
                print "%8.2f" % m[i][j],
            print
        print "-------------------------------------------------"

    def setGrid(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.colScaleMM = self.widthMM / self.cols
        self.rowScaleMM = self.heightMM / self.rows
        self.label = [['' for col in range(self.cols)]
                      for row in range(self.rows)]

    def validateGrid(self):
        print "Validating Grid: Checking bounds (%d, %d)..." % \
              (self.rows, self.cols),
        for r in range(self.rows):
            for c in range(self.cols):
                assert(self.inRange(r, c))
        print "done!"
                
if __name__ == '__main__':
    print "Testing Map()..."
    map = Map(8, 10, 500, 1000)
    map.display()
    map.reset()
    map.display()
    print "Setting Grid location..."
    map.setGridLocation(400, 900, 1.0, "A")
    map.validateGrid()
    print "Setting Grid to new size..."
    map.setGrid( [[0, 0, 0],
                  [0, 1, 0],
                  [0, 0, 0],
                  [1, 0, 0]] )
    map.validateGrid()
    map.display()
    print "All done!"
