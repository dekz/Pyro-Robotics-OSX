import Tkinter, os, random, pickle
import Image, ImageTk, ImageDraw, ImageFont 
from Numeric import resize
from string import atof, atoi
import itertools
from pyrobot import pyrobotdir

class GUI(Tkinter.Toplevel):
    """
    A simple world from Russell and Norvig's AIMA. This works
    with SymbolicSimulator.
    """
    def __init__(self, root, width, height):
        Tkinter.Toplevel.__init__(self, root)

        self.inaccessible = [(-1,-1),\
                             ( 4, 2),( 5, 2),( 6, 2),( 4, 3),( 5, 3),( 6, 3),\
                             ( 9, 2),(10, 2),(11, 2),( 9, 3),(10, 3),(11, 3),( 9, 4),(10, 4),(11, 4),\
                             (13, 1),(14, 1),(13, 2),(14, 2),(13, 3),(14, 3),(13, 4),(14, 4),\
                             (3,6),(4,6),(5,6),(3,7),(4,7),(5,7),(3,8),(4,8),(5,8),(3,9),(4,9),(5,9),\
                             (7,6),(8,6),     (7,7),(8,7),     (7,8),(8,8),    \
                             (6,9),(7,9),(8,9),     (6,10),(7,10),(8,10),(9,10),(10,10),(6,11),(7,11),\
                             (8,11),(9,11),(10,11),(6,12),(7,12),(8,12),(9,12),(6,13),(7,13),(8,13),\
                             (11,6),(12,6),(13,6),(11,7),(12,7),(13,7),(11,8),(12,8),(13,8),\
                             (0,11),(1,11),(2,11),(0,12),(1,12),(2,12),(0,13),(1,13),(2,13),(0,14),(1,14),(2,14)];
    
	self.path_color        = "#5ee563"
	self.visited_color     = "#c5c5c5"
        self.current_pos_color = "#00AF32"
	self.inaccessible_color= "black"
	self.gridline_color    = "black"
	self.background_color  = "white"

        self.path    = []
        self.visited = []
	self.pits    = []
	self.goal    = []

	self.goal_id = -1
	self.pit_ids = []

        # how many states ?
        self.num_squares_x = 15
        self.num_squares_y = 15

        self.squares     = resize(   0,(self.num_squares_x,self.num_squares_y)); 

        # various object members
        self.done    = 0
        self.quit    = 0
        self.root    = root
        self.width   = width
        self.height  = height
        self.complete = 0

        # various tk objects
        self.title("SymbolicSimulator: RLWorld")
        self.canvas = Tkinter.Canvas(self,width=self.width,height=self.height,bg="black")
        self.canvas.pack()
        self.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.destroy)

        # set height and width of images
        self.square_height = self.width  / self.num_squares_x;
        self.square_width  = self.height / self.num_squares_y;

        # goal image
        goldFilename = pyrobotdir() + "/images/rlgoal.gif" 
        goldImage = Image.open(goldFilename)
        goldImage = goldImage.resize( [self.square_height-2, self.square_width-2] )
        self.goldImageTk = ImageTk.PhotoImage(goldImage)

        # pit image
        pitFilename = pyrobotdir() + "/images/rlpit.gif" 
        pitImage = Image.open(pitFilename)
        pitImage = pitImage.resize( [self.square_height-2, self.square_width-2] )
        self.pitImageTk = ImageTk.PhotoImage(pitImage, height=self.square_height, width=self.square_width)

	for i in range(0, self.num_squares_x):
	  for j in range(0, self.num_squares_y):
            self.squares[i][j] = self.canvas.create_rectangle( i*self.square_width, j*self.square_height,
                            	        (i+1)*self.square_width - 1, (j+1)*self.square_height - 1,
                                	fill= self.background_color, tag = "square-%d-%d" % (i,j));

        # initialize the world
        self.initWorld()
        self.resetStates()
        
        # used by simulator
        self.properties = ["location", "obstacles", "goal", "home", \
                           "final", "visited", "complete", \
                           "pits", "path"]

        self.movements = ["up", "right", "down", "left"]
        self.ports = [60000]

        # start things off
        self.redraw()
        self.drawInaccessible()
            
    def resetStates(self):
        # various states
        self.home = (0, 0)
        self.location = (0, 0)
       
        num_pits = random.randrange(5) + 1

        del self.pits[0:]

	for i in range(0, self.num_squares_x):
	  for j in range(0, self.num_squares_y):
              if not( (i,j) in self.inaccessible ):
                  self.canvas.itemconfigure( self.squares[i][j], fill=self.background_color )
        

        for i in range(num_pits):
            self.pits.append( (random.randrange(self.num_squares_x), random.randrange(self.num_squares_y)) )
            
        self.goal = []

        while self.goal == [] or self.goal in self.inaccessible or self.goal in self.pits:
            self.goal = (random.randrange(self.num_squares_x), random.randrange(self.num_squares_y))


        self.final_states = [self.goal] + self.pits

        

    def initWorld(self):
        self.completed = 0
        self.location = (0, 0)

        del self.path[0:]
        del self.visited[0:]

    # checks the current motion, if it is valid the location will be changed, otherwise no change
    def moveInDirection( self, loc, dir):
        x = 0

        if (loc[0] + dir[0],loc[1] + dir[1]) in self.inaccessible:
            x = loc[0]
            y = loc[1]

        else:
            if loc[0] + dir[0] >= 0 and loc[0] + dir[0] < self.num_squares_x:
                x = loc[0] + dir[0]
            else:
                x = loc[0]
            if loc[1] + dir[1] >= 0 and loc[1] + dir[1] < self.num_squares_y:
                y = loc[1] + dir[1]
            else:
                y = loc[1]
            
        self.location = (x, y)

    # check if we are at the goal state
    def checkMovement(self):        
        xloc = self.location[0]
        yloc = self.location[1]

        if ( (xloc,yloc) in self.final_states ):
            return "Success!"

        return "ok0"

    # removes all elements in path after el
    def removeAfter(self, el,path):
        if len(path) <= 1:
            return path

        path.reverse()
        path = list(itertools.dropwhile(lambda n: not el == n, path))[1:]
        path.reverse()

        return path

    # returns a list of all elements in l1 that are not in l2
    def getDifferences(self, l1, l2):
        dl = []
        for e in l1:
            if not(e in l2):
                dl.append(e)
        return dl

    # adds a new location to the current path, and removes new loops in the process
    def addToPath( self, el ):
        path = self.path

        # removes loops -- they're not significant
        if len(path) == 0:
            pass
        elif path[len(path)-1] == el:
            return

        if( not( el in self.visited ) ):
            self.canvas.itemconfigure( self.squares[el],
                                       tags=self.canvas.itemcget( self.squares[el], "fill" ) )
            self.visited.append( el )

        if el in path:
            path = self.removeAfter( el, path )
            self.erasePath( self.getDifferences( self.path, path ) )
            self.redrawVisited()
        
        path.append(el)


        if el in self.final_states:
            self.complete = 1
        else:
            self.complete = 0

        self.path = path

    # process incoming requests
    def process(self, request, sockname ):
        if request != 'location' and 'location' in request:
            request = 'location'
        elif request != 'moves' and 'moves' in request:
            request = 'moves'

        retval = "error"

        if request.count('connectionNum'):
            connectionNum, port = request.split(":")
            retval = self.ports.index( int(port) )


        elif request[0:2] == "c_" :
            position= (atoi(request[2:4]), atoi(request[4:6]))
            color = request[7:]
            self.updateColor( position, color )
            retval = color

        elif request == 'location':
            self.addToPath(self.location)
            retval = self.location[0], self.location[1]
        elif request == 'complete':
            retval = self.complete
        elif request == 'path':
            retval = self.path
        elif request == 'final':
            retval = self.final_states
        elif request == 'obstacles':
            retval = self.inaccessible
        elif request == 'visited':
            retval = self.visited
        elif request == 'goal':
            retval = (self.goal)
        elif request == 'pits':
            retval = (self.pits)
        elif request == 'home':
            retval = (self.home)
        elif request == 'reset':
            print "RESET!!"
            self.erasePath(self.visited)
            self.initWorld()
            self.resetStates()
            retval = "reset complete"
            self.redraw()
        elif request == 'end' or request == 'exit':
            retval = "exiting"
            self.done = 1
        elif request == 'quit':
            retval = "quitting"
            self.done = 1
            self.quit = 1
        elif request == 'properties':
            retval = self.properties
        elif request == 'movements':
            retval = self.movements
        elif request == 'up':
            self.moveInDirection( self.location, (0, -1) )
            self.addToPath(self.location)
            retval = self.checkMovement()
            self.redrawPath()
        elif request == 'right':
            self.moveInDirection( self.location, (1, 0) )
            self.addToPath(self.location)
            retval = self.checkMovement()
            self.redrawPath()
        elif request == 'left':
            self.moveInDirection( self.location, (-1, 0) )
            self.addToPath(self.location)
            retval = self.checkMovement()
            self.redrawPath()
        elif request == 'down':
            self.moveInDirection( self.location, (0, 1) )
            self.addToPath(self.location)
            retval = self.checkMovement()
            self.redrawPath()
        elif request == 'supportedFeatures':
            retval = []
        elif request == 'builtinDevices':
            retval = []
        elif request == 'start':
            self.complete = 0
            self.erasePath(self.visited)
            self.initWorld()
            retval = self.location
        else:   # unknown command; returns "error"
            pass

        return pickle.dumps(retval)

    def redrawPath(self):
        for (x,y) in self.path:
           self.canvas.itemconfig( self.squares[x][y], fill=self.path_color )
        self.redrawLocation();

    def redrawVisited(self):
        for (x,y) in self.visited:
           self.canvas.itemconfig( self.squares[x][y], fill = self.visited_color )

    def redrawLocation(self):
        self.canvas.itemconfig( self.squares[self.location], fill = self.current_pos_color )

    def erasePath(self, p):
        for (x,y) in p:
            strcolor = self.canvas.itemcget( self.squares[x][y], "tags" )
            self.canvas.itemconfig( self.squares[x][y], fill = strcolor )

    def drawGoal(self):
        (x,y) = self.goal
	if self.goal_id > -1:
          self.canvas.delete( self.goal_id )

        self.goal_id = self.canvas.create_image( x*self.square_width+1, y*self.square_height+1,
                                  image = self.goldImageTk, anchor=Tkinter.NW, tag="goal")

    def drawPits(self):
	while len( self.pit_ids ) > 0:
          self.canvas.delete( self.pit_ids.pop() );

        for (x,y) in self.pits:
          if not (x,y) in self.inaccessible:
            self.pit_ids.append( self.canvas.create_image( x*self.square_width+1, y*self.square_height+1,
                                 image = self.pitImageTk, anchor=Tkinter.NW, tag="pit") )

    def drawInaccessible(self):
        for (x,y) in self.inaccessible:
            self.canvas.itemconfig( self.squares[x][y], fill = self.inaccessible_color )

    def updateColor(self, loc, color):
        self.canvas.itemconfig( self.squares[loc], fill=color, tag=color )

    def createGridlines(self):
        # grid-lines
        for x in range(self.num_squares_x):
            self.canvas.create_line(  x*self.square_height, 0, x*self.square_height, self.height,
                                      width = 2, fill = gridline_color, tag = "gridline")
        for y in range(self.num_squares_y):
            self.canvas.create_line(  0, y*self.square_width, self.width, y*self.square_width,
                                      width = 2, fill = gridline_color, tag = "gridline")
    

    def redraw(self):
	self.drawGoal()
	self.drawPits()
        self.redrawVisited()

            
    # ------------------------------------------------------------------------        
        
    def destroy(self):
        self.done = 1 # stop processing requests, if handing
        self.quit = 1 # stop accept/bind toplevel
        self.root.quit() # kill the gui

def INIT():
    root = Tkinter.Tk()
    root.withdraw()
    return GUI(root, 240, 240) #375, 375)
