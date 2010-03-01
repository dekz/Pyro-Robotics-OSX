# -------------------------------------------------------
# Scatter Plotter
# -------------------------------------------------------

from Tkinter import *
import os

class Line:
    def __init__(self, x, y, lineId, pointId):
        self.x = x
        self.y = y
        self.lineId = lineId
        self.pointId = pointId

class Scatter(Toplevel):
    """
    Scatter(Tpolevel)
    app = None,
    xLabel = None,
    yLabel = None,
    legend = None,
    title = None,
    winTitle = "Pyrobot Scatter Plot",
    width = 400,
    height = 300,
    history= None,
    linecount = 1,
    xStart = 0.0, xEnd = 1.0,
    connectPoints = 1,
    yStart = 0.0, yEnd = 1.0):
    """
    COLOR = ['blue', 'red', 'green', 'yellow', 'orange',
             'black', 'azure', 'beige', 'brown', 'coral',
             'gold', 'ivory', 'moccasin', 'navy', 'salmon',
             'tan', 'ivory', 'pink', 'violet', 'cyan',
             'magenta', 'aquamarine', 'khaki', 'sea green', 'hot pink',
             'sienna', 'tomato', 'orchid', 'cornflower blue', 'deep sky blue',
             'forest green', 'rosy brown']
    def __init__(self, app = None, xLabel = None, yLabel = None, legend = None,
                 title = None, winTitle = "Pyrobot Scatter Plot",
                 width = 400, height = 300,
                 history= None, linecount = 1, xStart = 0.0, xEnd = 1.0,
                 connectPoints = 1, yStart = 0.0, yEnd = 1.0):
        Toplevel.__init__(self, app)
        if legend == None:
            legend = [''] * linecount
        else:
            legend = map(str, legend)
        if history == None:
            history = [100] * linecount
        if winTitle == None:
            self.wm_title("scatter@%s:"%os.getenv('HOSTNAME'))
        else:
            self.wm_title(winTitle)
        self.xLabel = xLabel
        self.yLabel = yLabel
        self.connectPoints = connectPoints
        self.width = width
        self.height = height
        self.title = title
        if self.yLabel:
            self.leftBorder = 70
        else:
            self.leftBorder = 45
        if self.title:
            self.topBorder = 45
        else:
            self.topBorder = 10
        if self.xLabel:
            self.bottomBorder = 70
        else:
            self.bottomBorder = 45
        self.plotHeight = self.height - (self.topBorder + self.bottomBorder)
        self.plotWidth =  self.plotHeight 
        self.xStart = xStart
        self.xEnd = xEnd
        self.yStart = yStart
        self.yEnd = yEnd
        self.linecount = linecount
        self.legend = legend
        # ----------------------------------------------------------
        self.lineCount = self.linecount
        self.hist = [0] * self.linecount # actual hist of line
        self.history = history[:] # history counts for each line
        self.data = [] # keeps tracks of lines and points drawn, for redraw
        self.firstEver = [0] * self.linecount
        self.last = [0] * self.linecount
        self.count = [0] * self.linecount
        self.dot = 2
        for i in range(self.linecount):
            self.hist[i] = [0] * history[i]
            self.firstEver[i] = 1
            self.last[i] = 0
            self.count[i] = 0
        # background
        self.canvas = Canvas(self, width=width, height=height)
        self.bind("<Configure>", self.changeSize)
        self.canvas.pack({'fill':'both', 'expand':1, 'side': 'left'})
        self.inChangeSize = 0
        self.init_graphics()
        
    def init_graphics(self):
        self.canvas.delete('graph')
        self.canvas.delete('object')
        self.canvas.create_rectangle(self.leftBorder,
                                     self.topBorder,
                                     self.leftBorder + self.plotWidth,
                                     self.topBorder + self.plotHeight,
                                     #self.height - self.bottomBorder,
                                     tag = 'graph',
                                     width = 1, fill='white')
        # title
        self.canvas.create_text(self.width / 2.0, 13,
                                tag = 'graph',
                                text=self.title, fill='black')
        # legend
        for i in range(self.linecount):
            self.canvas.create_rectangle(self.leftBorder + self.plotWidth + 5,
                                         self.topBorder + i * 20,
                                         self.leftBorder + self.plotWidth + 5 + 15,
                                         self.topBorder + i * 20 + 15,
                                         tag = 'graph',
                                         width = 1, fill=self.COLOR[i])
            self.canvas.create_text(self.leftBorder + self.plotWidth + 5 + 20,
                                    self.topBorder + i * 20 + 8,
                                    text=self.legend[i], fill='black',
                                    tag = 'graph',
                                    anchor='w')
        # text across bottom
        tick = 0.0 
        xtick_label = self.xStart
        while tick <= 1.0: 
            self.canvas.create_text(self.leftBorder + self.plotWidth * tick,
                                    self.height - self.bottomBorder + 15,
                                    tag = 'graph',
                                    text=xtick_label, fill='black')
            self.canvas.create_line(self.leftBorder + self.plotWidth * tick,
                                    self.height - self.bottomBorder - 5,
                                    self.leftBorder + self.plotWidth * tick,
                                    self.height - self.bottomBorder + 5,
                                    tag = 'graph',
                                    width = 2, fill='black')
            tick += 1.0 / 4.0
            xtick_label += (self.xEnd - self.xStart) / 4.0
        # labels down the side:
        tick = 1.0
        ytick_label = self.yStart
        while tick >= 0.0:
            self.canvas.create_text(self.leftBorder - 10,
                                    self.topBorder + self.plotHeight * tick,
                                    anchor='e',
                                    tag = 'graph',
                                    text=ytick_label, fill='black')
            self.canvas.create_line(self.leftBorder - 5,
                                    self.topBorder + self.plotHeight * tick,
                                    self.leftBorder + 5,
                                    self.topBorder + self.plotHeight * tick,
                                    tag = 'graph',
                                    width = 2, fill='black')
            tick -= 1.0 / 4.0
            ytick_label += (self.yEnd - self.yStart) / 4.0
        if self.xLabel:
            self.canvas.create_text(self.plotWidth /2 + self.leftBorder,
                                    self.height - self.bottomBorder/2,
                                    text=self.xLabel,
                                    tag='graph',
                                    fill='black')
        if self.yLabel:
            self.canvas.create_text(20,
                                    self.topBorder + (self.plotHeight - (len(self.yLabel) * 13))/2,
                                    text=self.yLabel,
                                    width=2,
                                    anchor="n",
                                    tag='graph',
                                    fill='black')
        # clear the points and lines:
        data, self.data = self.data, []
        # then go through and re-add them (in case the position has changed):
        for item in data:
            if item[0] == "point":
                self.addPoint( item[1], item[2], item[3], color = item[4], size = item[5])
            elif item[0] == "line":
                self.addLine( item[1], item[2], item[3], item[4], item[5], item[6])
        #self.canvas.lower('graph')
            
    def changeSize(self, event = None):
        if self.inChangeSize: return
        self.inChangeSize = 1
        if self.title:
            self.topBorder = 45
        else:
            self.topBorder = 10
        if self.xLabel:
            self.bottomBorder = 70
        else:
            self.bottomBorder = 45
        if self.yLabel:
            self.leftBorder = 70
        else:
            self.leftBorder = 45
        self.width = self.winfo_width() 
        self.height = self.winfo_height() 
        self.plotHeight = self.height - (self.topBorder + self.bottomBorder) 
        self.plotWidth =  self.width - self.leftBorder - 20 - (max(map(len, self.legend)) * 12) # left side, legend box, legend text
        #self.plotHeight # / max value
        self.init_graphics()
        self.inChangeSize = 0
            
    def setTitle(self, title):
        self.wm_title(title)

    def _x(self, val):
        val = (val - self.xStart) / (self.xEnd - self.xStart)
        return int(val * self.plotWidth) + self.leftBorder

    def _y(self, val):
        val = (val - self.yStart) / (self.yEnd - self.yStart)
        return int(self.plotHeight - val * self.plotHeight + self.topBorder)

    def clear(self, linenum = None):
        if linenum == None:
            self.canvas.delete('object')
        else:
            self.canvas.delete('line%d' % linenum)

    def addLine(self, x1, y1, x2, y2, color = "black", width = 2, line = 0):
        # add the line to data, in case of redraw:
        self.data.append( ("line", x1, y1, x2, y2, color, width, line))
        my_x1, my_y1 = self._x(x1), self._y(y1)
        my_x2, my_y2 = self._x(x2), self._y(y2)
        self.canvas.create_line(my_x1, my_y1,
                                my_x2, my_y2,
                                tags = ('graph','line%d' % line),
                                width = width,
                                fill=color)
    def addPoint(self, x, y, line = 0, flush = 1, color = 'coral', size = None):
        if not (x >= self.xStart and x <= self.xEnd and
                y >= self.yStart and y <= self.yEnd):
            print "pyrobot scatter: data point out of range (%f,%f)" % (x, y)
            return
        if size == None: size = self.dot
        # add the points to data, in case of redraw:
        self.data.append( ("point", x, y, line, color, size) )
        if self.count[line] >= self.history[line]:
            self.count[line] = 0
        # if there is an old one here, delete it
        if type(self.hist[line][self.count[line]]) != type(1):
            self.canvas.delete( self.hist[line][self.count[line]].lineId )
            self.canvas.delete( self.hist[line][self.count[line]].pointId )
        if type(self.last[line]) != type(1) and self.connectPoints:
            last_x = self._x(self.last[line].x)
            last_y = self._y(self.last[line].y)
            self.canvas.delete( self.last[line].pointId)
            try:

                self.last[line].pointId = self.canvas.create_oval(last_x - size,
                                                                  last_y - size,
                                                                  last_x + size,
                                                                  last_y + size,
                                                                  width = 0,
                                                                  tags = ('object','line%d' % line),
                                                                  fill = color)
            except:
                pass
        try:
            my_x = self._x(x)
            my_y = self._y(y)
            if self.firstEver[line]:
                self.firstEver[line] = 0
                lid = -1
            elif self.connectPoints:
                last_x = self._x(self.last[line].x)
                last_y = self._y(self.last[line].y)
                lid = self.canvas.create_line(last_x,
                                              last_y,
                                              my_x,
                                              my_y,
                                              width = 1,
                                              tags = ('object','line%d'%line),
                                              fill = 'tan')
            pid = self.canvas.create_oval(my_x - size,
                                          my_y - size,
                                          my_x + size,
                                          my_y + size,
                                          width = 0,
                                          tags = ('object','line%d'%line),
                                          fill = color)
            self.hist[line][self.count[line]] = Line(x, y, lid, pid)
            self.last[line] = self.hist[line][self.count[line]]
            self.count[line] += 1
        except:
            pass
        if flush:
            #self.update_idletasks()
            self.update()

    def update(self):
        while self.tk.dooneevent(2): pass

if __name__ == '__main__':
    import Tkinter
    tk = Tkinter.Tk()
    #tk.withdraw()
    sp = Scatter(tk)
    from random import random
    for y in range(100):
        for x in range(10):
            sp.addPoint(random(), random(), color="blue")
            sp.update()
    sp.mainloop()
