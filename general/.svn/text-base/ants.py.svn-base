# Ant algorithm experiments
# D.S. Blank

from random import random

version = "0.2"

class Board:
    def __init__(self, width, height, pixelsPerCell = 10, title = "Ants"):
        """ A board for ants to explore """
        from Tkinter import Tk, Canvas, Toplevel
        self.width = width
        self.height = height
        self.color = ["white", "black", "red", "yellow", "blue", "green", "purple", "pink", "cyan", "turquoise", "gray"]
        self.board = [[0 for x in range(self.width)] for y in range(self.height)]
        self.box = [[0 for x in range(self.width)] for y in range(self.height)]
        self.pixelsPerCell = pixelsPerCell
        self.title = title
        self.app = Tk()
        self.app.withdraw()
        self.win = Toplevel()
        self.win.wm_title(title)
        self.canvas = Canvas(self.win,
                             width=(self.width * pixelsPerCell),
                             height=(self.height * pixelsPerCell))
        self.canvas.pack(side = 'bottom', expand = "yes", anchor = "n",
                         fill = 'both')
        self.win.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.close)
        #self.canvas.bind("<Configure>", self.changeSize)
        self.draw()

    def __getitem__(self, args):
        """ A shortcut to get a board state """
        x, y = args
        xpos, ypos = self.move(x, y)
        return self.board[xpos][ypos]

    def __setitem__(self, (x, y), value):
        """ A shortcut to assign a board state """
        xpos, ypos = self.move(x, y)
        self.canvas.itemconfig(self.box[x][y], fill = self.color[value], outline = self.color[value])
        self.canvas.update()
        self.board[x][y] = value

    def move(self, x, y, xoffset = 0, yoffset = 0):
        """ Move an ant in a direction """
        return (x + xoffset) % self.width, (y + yoffset) % self.height

    def close(self):
        """ close the window """
        self.app.destroy()

    def draw(self):
        """ Initialize the board. You must do this if you ever want to see the path """
        print "Drawing...",
        s = self.pixelsPerCell
        for h in range(self.height):
            for w in range(self.width):
                self.box[w][h] = self.canvas.create_rectangle(w*s, h*s, w*s+s, h*s+s,
                                                              fill = "gray", outline = "gray")
        self.canvas.update()
        print "Done!"

class Ant:
    """ An ant class """
    def __init__(self, x = None, y = None, dir = None, rule = "01"):
        if x == None:
            self.x = random()
        else:
            self.x = x
        if y == None:
            self.y = random()
        else:
            self.y = y
        if dir == None:
            self.dir = "NSEW"[int(random() * 4)]
        else:
            self.dir = dir
        self.rule = rule

    def nextPositionOffset(self):
        """ The offsets of the next move """
        if self.dir == "N":
            return (0, -1)
        elif self.dir == "S":
            return (0, 1)
        elif self.dir == "E":
            return (1, 0)
        elif self.dir == "W":
            return (-1, 0)
        else:
            raise TypeError, "invalid direction '%s'" % self.dir
        
    def turn(self, turnDir):
        """ What dir will the ant face next? """
        if turnDir == 0: # left
            if self.dir == "N":
                self.dir = "W"
            elif self.dir == "W":
                self.dir = "S"
            elif self.dir == "S":
                self.dir = "E"
            elif self.dir == "E":
                self.dir = "N"
            else:
                raise ValueError, "invalid dir %s" % self.dir
        elif turnDir == 1: # right
            if self.dir == "N":
                self.dir = "E"
            elif self.dir == "E":
                self.dir = "S"
            elif self.dir == "S":
                self.dir = "W"
            elif self.dir == "W":
                self.dir = "N"
            else:
                raise ValueError, "invalid dir %s" % self.dir
        else:
            raise ValueError, "invalid turnDir %d" % turnDir

    def move(self, board):
        """ Make the ant move """
        # first, make your turn:
        currentState = board[self.x,self.y]
        turnDir = self.rule[(currentState + 1) % len(self.rule)]
        self.turn( int(turnDir) )
        # next, let's change this cell's state:
        if currentState >= len(self.rule) - 1:
            board[self.x,self.y] = 0
        else:
            board[self.x,self.y] = currentState + 1
        # and let's move:
        offsets = self.nextPositionOffset() # based on x, y, and dir
        self.x, self.y = board.move(self.x, self.y, offsets[0], offsets[1])

if __name__ == "__main__":
    def ask(msg):
        print msg, "(y or n):"
        return raw_input() == 'y'

    if ask("Do you want to see Langton's Highway?"): 
        board = Board(100, 100, 5)
        ant = Ant(board.width / 2, board.height / 2, "S", "10")
        for i in range(11000):
            ant.move(board)

    if ask("Do you want to see an ant with nine states?"): 
        board = Board(100, 100, 6)
        ant = Ant(board.width / 2, board.height / 2, "S", "101111101")
        for i in range(11000):
            ant.move(board)

    if ask("Do you want to see a board with two ants?"): 
        board = Board(100, 100, 4)
        ant1 = Ant(board.width / 2, board.height / 2, "S", "10")
        ant2 = Ant(board.width / 4, board.height / 4, "N", "10")
        for i in range(11000):
            ant1.move(board)
            ant2.move(board)

    if ask("Do you want to see a board with two different kinds of ants?"): 
        board = Board(200, 200, 4)
        ant1 = Ant(board.width / 2, board.height / 2, "S", "101111")
        ant2 = Ant(board.width / 4, board.height / 4, "N", "10")
        for i in range(11000):
            ant1.move(board)
            ant2.move(board)
