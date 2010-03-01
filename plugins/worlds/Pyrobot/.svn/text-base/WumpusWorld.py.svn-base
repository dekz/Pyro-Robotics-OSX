import Tkinter, os, random, pickle
import Image, ImageTk, ImageDraw, ImageFont 
from pyrobot import pyrobotdir

class GUI(Tkinter.Toplevel):
    """
    A simple world from Russell and Norvig's AIMA. This works
    with PyrobotSimulator.
    """
    def __init__(self, root, width, height):
        Tkinter.Toplevel.__init__(self, root)
        self.done = 0
        self.quit = 0
        self.root = root
        self.width = width
        self.height = height
        self.visible = 1
        self.title("PyrobotSimulator: WumpusWorld")
        self.canvas = Tkinter.Canvas(self,width=self.width,height=self.height,bg="white")
        self.canvas.pack()
        self.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.destroy)
        # sensors: stench, breeze, glitter, bump, scream
        self.goldFilename = pyrobotdir() + "/images/gold.gif" 
        self.wumpusFilename = pyrobotdir() + "/images/wumpus.gif" 
        self.pitFilename = pyrobotdir() + "/images/pit.gif"
        self.agentFilename = pyrobotdir() + "/images/agent.gif" 
        # --------------------------------------------------------
        self.goldImage = Image.open(self.goldFilename)
        self.goldImage = self.goldImage.resize( (100, 25), Image.BILINEAR )
        self.wumpusImage = Image.open(self.wumpusFilename)
        self.wumpusImage = self.wumpusImage.resize( (100, 100), Image.BILINEAR )
        self.pitImage = Image.open(self.pitFilename)
        self.pitImage = self.pitImage.resize( (100, 100), Image.BILINEAR )
        self.agentImage = Image.open(self.agentFilename)
        self.agentImage = self.agentImage.resize( (100, 100), Image.BILINEAR )
        # --------------------------------------------------------
        self.goldImageTk = ImageTk.PhotoImage(self.goldImage)
        self.wumpusImageTk = ImageTk.PhotoImage(self.wumpusImage)
        self.pitImageTk = ImageTk.PhotoImage(self.pitImage)
        self.agentImageTk = ImageTk.PhotoImage(self.agentImage)
        # --------------------------------------------------------
        self.properties = ["percept", "location", "x", "y", "direction", "arrow", "score", "alive"]
        for i in self.properties:
            self.__dict__[i] = None
        self.initWorld()
        self.count = 0
        self.tag = "data-%d" % self.count
        self.movements = ["left", "right", "forward", "shoot", "grab"]
        self.ports = [60000]
        self.redraw()

    def initWorld(self):
        self.direction = "right"
        self.location = (0, 0)
        self.x, self.y = self.location
        self.dead = 0
        self.score = 0
        self.arrow = 1
        self.wumpusDead = 0
        self.bump = 0
        self.stench = 0
        self.breeze = 0
        self.gold = 0
        self.scream = 0
        self.world = [['' for y in range(4)] for x in range(4)]
        # ''  = nothing
        # 'W' = wumpus
        # 'G' = gold
        # 'P' = pit
        # 'A' = agent
        for x in range(1, 4):
            for y in range(1, 4):
                if random.random() < .20:
                    self.world[x][y] = 'P'
        # Assign the positions of the gold and the wumpus:
        x = random.randint(0, 3); y = random.randint(0, 3)
        while x == 0 and y == 0:
            x = random.randint(0, 3); y = random.randint(0, 3)
        self.world[x][y] += 'G'
        x = random.randint(0, 3); y = random.randint(0, 3)
        while x == 0 and y == 0:
            x = random.randint(0, 3); y = random.randint(0, 3)
        self.world[x][y] += 'W'
        self.checkMovement()

    def add(self, loc, dir):
        x = 0
        if loc[0] + dir[0] >= 0 and loc[0] + dir[0] < 4:
            x = loc[0] + dir[0]
        else:
            x = loc[0]
            self.bump = 1
        if loc[1] + dir[1] >= 0 and loc[1] + dir[1] < 4:
            y = loc[1] + dir[1]
        else:
            y = loc[1]
            self.bump = 1
        self.location = (x, y)
        self.x, self.y = self.location


    def checkMovement(self):
        if ('W' in self.world[self.location[0]][self.location[1]] and not self.wumpusDead) or \
               'P' in self.world[self.location[0]][self.location[1]]:
            self.dead = 1
            self.score -= 1000
            return "you died a miserable death!"
        self.stench = self.nearby(self.location, 'W')
        self.breeze = self.nearby(self.location, 'P')
        self.gold = int('G' in self.world[self.location[0]][self.location[1]])
        # bump computed when you move
        # scream computed when you shoot
        return "ok"

    def nearby(self, loc, ch):
        for x,y in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            xpos, ypos = loc[0] + x, loc[1] + y
            if ypos >= 0 and ypos < 4 and xpos >= 0 and xpos < 4:
                if ch in self.world[xpos][ypos]:
                    return 1
        return 0

    def inLine(self, loc, change):
        xpos, ypos = self.sum(loc , change)
        while ypos >= 0 and ypos < 4 and xpos >= 0 and xpos < 4:
            if 'W' in self.world[xpos][ypos]:
                self.wumpusDead = 1
                self.scream = 1
                self.world[xpos][ypos] = self.world[xpos][ypos].replace('W', '')
            xpos, ypos = self.sum((xpos,ypos), change)

    def sum(self, a, b):
        return a[0] + b[0], a[1] + b[1]

    def process(self, request, sockname):
        # moves: 'forward', 'left', 'right', 'grab', 'shoot'
        dirs = {'up':0, 'right':1, 'down':2, 'left':3}
        pos  = {0:'up', 1:'right', 2:'down', 3:'left'}
        retval = "error"
        if request.count('connectionNum'):
            connectionNum, port = request.split(":")
            retval = self.ports.index( int(port) )
        elif request == 'location':
            retval = (self.location[0] + 1, self.location[1] + 1)
        elif request == 'x':
            retval = self.x + 1
        elif request == 'y':
            retval = self.y + 1
        elif request == 'direction':
            retval = self.direction
        elif request == 'arrow':
            retval = self.arrow
        elif request == 'score':
            retval = self.score
        elif request == 'alive':
            retval = (not self.dead)
        elif request == 'reset':
            self.initWorld()
            retval = "ok"
            self.redraw()
        elif request == 'end' or request == 'exit':
            retval = "ok"
            self.done = 1
        elif request == 'quit':
            retval = "ok"
            self.done = 1
            self.quit = 1
        elif request == 'properties':
            retval = self.properties
        elif request == 'movements':
            retval = self.movements
        elif request == 'percept':
            retval = ({1:"stench", 0:None}[self.stench],
                      {1:"breeze", 0:None}[self.breeze],
                      {1:"glitter", 0:None}[self.gold],
                      {1:"bump", 0:None}[self.bump],
                      {1:"scream", 0:None}[self.scream])
        elif self.dead:
            retval = "you died a miserable death!"
            self.redraw()
        elif request == 'left': # ------------------------below here, you are alive!
            self.bump = 0
            self.scream = 0
            self.score -= 1
            self.direction = pos[(dirs[self.direction] - 1) % 4]
            retval = self.checkMovement()
            self.redraw()
        elif request == 'shoot':
            # shoot arrow
            self.scream = 0
            if self.arrow:
                self.arrow = 0
                self.score -= 10
                if self.direction == 'up':
                    self.inLine( self.location, (0, 1) )
                elif self.direction == 'right':
                    self.inLine( self.location, (1, 0) )
                elif self.direction == 'left':
                    self.inLine( self.location, (-1, 0) )
                elif self.direction == 'down':
                    self.inLine( self.location, (0, -1) )
                retval = 'ok'
            self.redraw()
        elif request == 'grab':
            if 'G' in self.world[self.location[0]][self.location[1]]:
                self.score += 1000
                self.world[self.location[0]][self.location[1]] = self.world[self.location[0]][self.location[1]].replace('G','')
                retval = "you win!"
            self.redraw()
        elif request == 'right':
            self.bump = 0
            self.scream = 0
            self.score -= 1
            self.direction = pos[(dirs[self.direction] + 1) % 4]
            retval = self.checkMovement()
            self.redraw()
        elif request == 'forward':
            self.bump = 0
            self.scream = 0
            self.score -= 1
            if self.direction == 'up':
                self.add( self.location, (0, 1) )
            elif self.direction == 'right':
                self.add( self.location, (1, 0) )
            elif self.direction == 'left':
                self.add( self.location, (-1, 0) )
            elif self.direction == 'down':
                self.add( self.location, (0, -1) )
            retval = self.checkMovement()
            self.redraw()
        elif request == 'supportedFeatures':
            retval = []
        elif request == 'builtinDevices':
            retval = []
        else:   # unknown command; returns "error"
            pass
        return pickle.dumps(retval)

    def drawDir(self, x, y, dir):
        if dir == "left":
            self.canvas.create_line(x, y + 50, x + 50, y + 50, width = 2, fill = "red", tag = self.tag)
            self.canvas.create_line(x, y + 50, x + 25, y + 25, width = 2, fill = "red", tag = self.tag)
            self.canvas.create_line(x, y + 50, x + 25, y + 75, width = 2, fill = "red", tag = self.tag)
        elif dir == "right":
            self.canvas.create_line(x + 100, y + 50, x + 50, y + 50, width = 2, fill = "red", tag = self.tag)
            self.canvas.create_line(x + 100, y + 50, x + 75, y + 25, width = 2, fill = "red", tag = self.tag)
            self.canvas.create_line(x + 100, y + 50, x + 75, y + 75, width = 2, fill = "red", tag = self.tag)
        elif dir == "up":
            self.canvas.create_line(x + 50, y, x + 50, y + 50, width = 2, fill = "red", tag = self.tag)
            self.canvas.create_line(x + 50, y, x + 25, y + 25, width = 2, fill = "red", tag = self.tag)
            self.canvas.create_line(x + 50, y, x + 75, y + 25, width = 2, fill = "red", tag = self.tag)
        elif dir == "down":
            self.canvas.create_line(x + 50, y + 100, x + 50, y + 50, width = 2, fill = "red", tag = self.tag)
            self.canvas.create_line(x + 50, y + 100, x + 25, y + 75, width = 2, fill = "red", tag = self.tag)
            self.canvas.create_line(x + 50, y + 100, x + 75, y + 75, width = 2, fill = "red", tag = self.tag)

    def redraw(self):
        oldtag = self.tag
        self.count = int(not self.count)
        self.tag = "data-%d" % self.count
        for x in range(4):
            for y in range(4):
                posx = x * 100
                posy = 300 - y * 100
                if self.location[0] == x and self.location[1] == y:
                    self.canvas.create_image(posx, posy, image = self.agentImageTk, anchor=Tkinter.NW,tag=self.tag)
                    self.drawDir(posx, posy, self.direction)
                if 'P' in self.world[x][y]:
                    self.canvas.create_image(posx, posy, image = self.pitImageTk, anchor=Tkinter.NW,tag=self.tag)
                if 'W' in self.world[x][y]:
                    self.canvas.create_image(posx, posy, image = self.wumpusImageTk, anchor=Tkinter.NW,tag=self.tag)
                if 'G' in self.world[x][y]:
                    self.canvas.create_image(posx, posy + 75, image = self.goldImageTk, anchor=Tkinter.NW,tag=self.tag)
        # ------------------------------------------------------------------------        
        self.canvas.create_line(  2,   2,   2, 400, width = 2, fill = "black", tag = self.tag)
        self.canvas.create_line(100,   0, 100, 400, width = 2, fill = "black", tag = self.tag)
        self.canvas.create_line(200,   0, 200, 400, width = 2, fill = "black", tag = self.tag)
        self.canvas.create_line(300,   0, 300, 400, width = 2, fill = "black", tag = self.tag)
        self.canvas.create_line(400,   0, 400, 400, width = 2, fill = "black", tag = self.tag)
        self.canvas.create_line(  2,   2, 400,   2, width = 2, fill = "black", tag = self.tag)
        self.canvas.create_line(  0, 100, 400, 100, width = 2, fill = "black", tag = self.tag)
        self.canvas.create_line(  0, 200, 400, 200, width = 2, fill = "black", tag = self.tag)
        self.canvas.create_line(  0, 300, 400, 300, width = 2, fill = "black", tag = self.tag)
        self.canvas.create_line(  0, 400, 400, 400, width = 2, fill = "black", tag = self.tag)
        # ------------------------------------------------------------------------        
        self.canvas.delete(oldtag)
        
    def destroy(self):
        self.done = 1 # stop processing requests, if handing
        self.quit = 1 # stop accept/bind toplevel
        self.root.quit() # kill the gui

def INIT():
    root = Tkinter.Tk()
    root.withdraw()
    return GUI(root, 400, 400)
