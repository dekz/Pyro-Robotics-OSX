# Boid experiments
# D.S. Blank

from random import random
import math
from time import sleep

version = "0.0"

class Board:
    def __init__(self, width, height, title = "Boids"):
        """ A board for boids to explore """
        from Tkinter import Tk, Canvas, Toplevel
        self.colors = ["white", "black", "red", "yellow", "blue", "green", "purple", "pink", "cyan", "turquoise", "gray"]
        self.width = width
        self.height = height
        self.distance = 10
        self.boids = []
        self.oldVector = []
        self.title = title
        self.app = Tk()
        self.app.withdraw()
        self.win = Toplevel()
        self.win.wm_title(title)
        self.canvas = Canvas(self.win,
                             width=self.width,
                             height=self.height)
        self.canvas.pack(side = 'bottom', expand = "yes", anchor = "n",
                         fill = 'both')
        self.win.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.close)
        #self.canvas.bind("<Configure>", self.changeSize)
        self.draw()

    def close(self):
        """ close the window """
        self.app.destroy()

    def draw(self):
        """ Initialize the board. You must do this if you ever want to see the path """
        print "Drawing...",
        self.canvas.delete("boid")
        for boid in self.boids:
            self.drawBoid( boid )
        self.canvas.update()
        print "Done!"

    def drawBoid(self, boid):
        size = 40
        angle = 80
        x = boid.x - size/2
        y = boid.y - size/2
        start = ((boid.dir + 180 + angle/2) - 55) % 360
        color = self.colors[boid.color]
        self.canvas.create_arc(x, y, x + size, y + size,
                               start = start, extent = angle/2,
                               fill = color, outline = color, tag = "boid")
        
    def addBoid(self, boid):
        self.boids.append( boid )
        self.oldVector.append( 0 )
        self.draw()

    def dist(self, x1, y1, x2, y2):
        return math.sqrt( (x1 - x2) ** 2 + (y1 - y2) ** 2)

    def angleTo(self, b1, b2):
        # figure out angle from boid1 to boid2
        # this is just a test!
        if self.boids[b1].x < self.boids[b2].x:
            return -10
        # return - if to the right, + if to the left
        else:
            return 10

    def avoid(self, num, radius):
        for i in range(len(self.boids)):
            if i != num:
                if self.dist(self.boids[i].x, self.boids[i].y,
                             self.boids[num].x, self.boids[num].y ) < radius:
                    return -self.angleTo( num, i)
        return 0.0
    
    def copy(self, num, radius):
        # if within radius, get closer to their angle
        # return - if to the right, + if to the left
        return 0

    def center(self, num, radius):
        # make yoru angle head toward center
        # return - if to the right, + if to the left
        return 0

    def view(self, num, radius):
        # try to have a clear view
        # return - if to the right, + if to the left
        return 0

    def adjustDirections(self, weights):
        radius = 40
        for boidNum in range(len(self.boids)):
            avoidVector = self.avoid( boidNum, radius )
            copyVector = self.copy( boidNum, radius )
            centerVector = self.center( boidNum, radius )
            viewVector = self.view( boidNum, radius )
            newVector = int(weights[0] * avoidVector + weights[1] * copyVector + weights[2] * centerVector + weights[3] * viewVector)
            self.boids[boidNum].dir += newVector
            self.oldVector[boidNum] = newVector

    def move(self):
        """ Make the boids move """
        self.adjustDirections([1., 1., 1., 1.]) # pass in weights: avoid, copy, center, view
        for boid in self.boids:
            boid.x += self.distance * math.cos( boid.dir / 180.0 * math.pi)
            boid.y -= self.distance * math.sin( boid.dir / 180.0 * math.pi)
            if boid.x > self.width:
                boid.x = 0
            if boid.x < 0:
                boid.x = self.width - 1
            if boid.y > self.height:
                boid.y = 0
            if boid.y < 0:
                boid.y = self.height - 1
        self.draw()

class Boid:
    """ A boid class """
    def __init__(self, x, y, dir = None, color = None):
        self.x = x
        self.y = y
        if dir == None:
            self.dir = int(random() * 360)
        else:
            self.dir = int(dir % 360)
        if color == None:
            self.color = int(random() * 11)
        else:
            self.color = color

if __name__ == "__main__":
    def ask(msg):
        print msg, "(y or n):"
        return raw_input() == 'y'

    if ask("Do you want to see 10 boids on the board?"): 
        board = Board(800, 600)
        for i in range(3):
            boid = Boid(int(random() * board.width), int(random() * board.height))
            board.addBoid( boid )
        while 1:
            board.move()
            #sleep(.25)
