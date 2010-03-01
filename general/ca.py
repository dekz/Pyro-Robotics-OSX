# Cellular Automata Class
# D.S. Blank

from random import random
from math import log

version = "1.2"

class GUI:
    def __init__(self, title, width, height):
        from Tkinter import Tk, Canvas, Toplevel
        self.width = width
        self.height = height
        self.title = title
        self.app = Tk()
        self.app.withdraw()
        self.win = Toplevel()
        self.win.wm_title(title)
        self.canvas = Canvas(self.win,
                             width=(self.width * 2),
                             height=(self.height * 2))
        self.canvas.pack(side = 'bottom', expand = "yes", anchor = "n",
                         fill = 'both')
        self.win.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.close)
        #self.canvas.bind("<Configure>", self.changeSize)
        
    def close(self):
        self.app.destroy()

    def draw(self, lat, length):
        print "Drawing...",
        for h in range(length):
            for w in range(self.width):
                if lat.data[h][w]:
                    self.canvas.create_rectangle(w*2, h*2, w*2+2, h*2+2,
                                                 fill = "black")
            self.win.update_idletasks()
        print "Done!"

def poisson(_lambda):
    """
    Function to generate Poisson distributed random variable between 0 and
    infinity with mean equal to lambda
    """
    p = 0
    r = 0
    while 1:
        p = p - log(random());
        if (p < _lambda):
            r += 1
        else:
            break
    return r

def decimalToBinaryString(val, maxbits = 128): 
    """ 
    A decimal to binary converter. Returns bits in a string. 
    """ 
    retval = ""
    for i in range(maxbits - 1, -1, -1): 
        bit = long(val / (2 ** i)) 
        val = (val % (2 ** i)) 
        retval += "%d" % bit
    assert(val == 0)
    return retval  

def decimalToBinary(val, maxbits = 128): 
    """ 
    A decimal to binary converter. Returns bits in a list. 
    """ 
    retval = []
    for i in range(maxbits - 1, -1, -1): 
        bit = long(val / (2 ** i)) 
        val = (val % (2 ** i)) 
        retval.append(bit)
    assert(val == 0)
    return retval

def binaryStringToDecimal(str):
    retval = 0
    for i in range(len(str)):
        val = long(str[-(i + 1)])
        retval += (val * (2 ** i))
    return retval  

class Matrix:
    def randomize(self, bias = .5):
        for i in range(self.size):
            self.data[0][i] = int(random() < bias)
    def display(self, rows = -1):
        if rows == -1:
            for i in range(self.height):
                self.displayRow(i)
                if i + 1 < self.height and self.data[i] == self.data[i + 1]:
                    return
        else:
            self.displayRow(rows)
    def displayRow(self, row = 0):
        s = ''
        cnt = 0.0
        print "%3d" % row,
        for i in range(self.size):
            if self.data[row][i]:
                s += 'X'
            else:
                s += '.'
            if self.data[row][i]:
                cnt += 1
        print s, "%.2f" % (cnt / self.size)
    def density(self, row):
        cnt = 0.0
        for i in range(self.size):
            if self.data[row][i]:
                cnt += 1
        return (cnt / self.size)
    def init(self, str):
        if type(str) == type("1001"):
            if (len(str) != self.size):
                raise "ImproperLength", str
            for i in range(len(str)):
                self.data[0][i] = int(str[i] == '1' or str[i] == 'X')
        else:
            self.init(decimalToBinaryString(str, self.size))

class Rules(Matrix):
    def __init__(self, radius = 3, values = 2, bias = .5):
        self.radius = radius
        self.values = values
        self.size = (self.values ** (self.radius * 2 + 1))
        self.height = 1
        self.data = [0]
        self.data[0] = [0] * self.size
        self.randomize(bias)
    def watch(self, lat, gui = 1):
        self.width = lat.size 
        length = lat.height - 1
        if gui:
            try:
                self.gui = GUI("Pyrobot CA", lat.size, lat.height - 1)
            except:
                self.gui = None
        else:
            self.gui = None
        for c in range( length):
            self.apply(lat, c)
        if self.gui:
            self.gui.draw(lat, length)
            self.gui.win.mainloop()
        else:
            lat.display()

    def apply(self, lat, c):
        for i in range(lat.size):
            lat.data[c+1][i] = self.data[0][self.size -
                                            lat.bits2rule(c,
                                                          i - self.radius,
                                                          i + self.radius) - 1]
    def applyAll(self, lat, length = -1):
        if length == -1:
            length = lat.height - 1
        for c in range( length):
            self.apply(lat, c)
            if lat.data[c] == lat.data[c + 1]:
                return c + 1
        return length

class Lattice(Matrix):
    def __init__(self, size = 149, height = 150, bias = .5):
        self.size = size
        self.height = height
        self.data = [0] * self.height
        for h in range(self.height):
            self.data[h] = [0] * self.size
        self.randomize(bias)
    def bit(self, row, pos):
        return self.data[row][pos % self.size]
    def bits2rule(self, row, start, stop):
        sum = 0
        cnt = 0
        for i in range(stop, start - 1, -1):
            sum += self.bit(row, i) * 2 ** cnt
            cnt += 1
        return sum

gkl = '11111010111111111111101000000000111110101111111111111010000000001111101000000000111110100000000011111010000000001111101000000000'

if __name__ == '__main__':
    import sys

    def pause():
        print "---Press ENTER to continue---",
        sys.stdin.readline()

    rules = Rules()
    data = Lattice()
    rules.watch( data )

    data = Lattice()
    rules = Rules(radius = 1)
    rules.init(110)
    print "Rule #110:"
    rules.display()
    print "Rule #110 applied to single bit on, Width = %d:" % data.size
    data.init("0" * data.size)
    data.data[0][data.size/2] = 1
    rules.applyAll(data)
    data.display()
    rules.watch(data)
    pause()

    data.randomize(.1)
    print "A 10%% Lattice, Width = %d:" % data.size
    data.display(0)
    pause()

    data.randomize(.5)
    print "A 50%% Lattice, Width = %d:" % data.size
    data.display(0)
    pause()
    
    data.randomize(.9)
    print "A 90%% Lattice, Width = %d:" % data.size
    data.display(0)
    pause()
    
    rules = Rules()
    rules.randomize()
    print "A 50%% Random Rule set, Width = %d:" % rules.size
    rules.display()
    pause()
    
    data.randomize(.05)
    rules.applyAll(data)
    print "A 50%% Rule applied to a 5%% Lattice, Lattice Width = %d:" % data.size
    data.display()
    pause()

    rules.init(gkl)
    print "GKL Rule set:"
    rules.display()
    pause()

    for percent in [ x/10.0 for x in range(10)]:
        data.randomize(percent)
        print "GKL Rule applied to a %d%% Lattice, Width = %d:" % (percent * 100, data.size)
        print rules.applyAll(data)
        data.display()
        pause()
    
    data.randomize()
    rules.randomize()
    print "A 50%% Rule applied to a 50%% Lattice, Lattice Width = %d:" % data.size
    #data.display()
    rules.watch(data)

