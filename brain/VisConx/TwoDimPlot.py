__author__ = "Matt Fiedler"
__version__ = "$Revision: 2020 $"

import Tkinter
import tkFileDialog
import tkMessageBox

class TwoDimPlot(Tkinter.Toplevel):
    TICK_LENGTH = 7
    TICK_SPACING = 75

    def __init__(self, parent, plotName=" ", xTitle=" ", yTitle=" ", xMax=1.0, yMax=1.0, plotWidth=300, plotHeight=225, closeCallback=None):
        Tkinter.Toplevel.__init__(self, parent)
        self.plotData = []
        self.plotName = plotName
        self.xTitle=xTitle
        self.yTitle=yTitle
        self.xMax = xMax
        self.yMax = yMax
        self.linesOn = 1
        self.plotWidth = plotWidth - (plotWidth % self.TICK_SPACING)
        self.plotHeight = plotHeight - (plotHeight % self.TICK_SPACING)
        self.xNumTicks = self.plotWidth//self.TICK_SPACING
        self.yNumTicks = self.plotHeight//self.TICK_SPACING

        #---- BEGIN GUI SETUP ----

        #main window
        self.config(bg="white")
        self.title(self.plotName)
        self.resizable(0,0)

        #begin create menus
        rootMenu = Tkinter.Menu(self)
        self.config(menu = rootMenu)
        fileMenu = Tkinter.Menu(rootMenu)
        rootMenu.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="Save data ...", command=self.writeToFile)
        fileMenu.add_separator()
        if closeCallback != None:
            fileMenu.add_command(label="Exit", command=closeCallback)
        else:
            fileMenu.add_command(label="Exit", command=self.destroy)
        viewMenu = Tkinter.Menu(rootMenu)
        rootMenu.add_cascade(label="View", menu=viewMenu)
        viewMenu.add_checkbutton(label="Hide Lines", command=self.alterLines, state=Tkinter.ACTIVE)
        #end create menus
        
        #begin axis labels
        xLabel = Tkinter.Label(self, text=self.xTitle, bg="white")
        xLabel.grid(row=3,col=2)
        yLabel = Tkinter.Label(self, text=self.yTitle, bg="white")
        yLabel.grid(row=1, col=0)
        #end axis labels
        
        #begin x axis ticks and tick labels
        self.xTickLabels = []
        self.xAxisCanvas = Tkinter.Canvas(self, bg="white", width=self.plotWidth+25, height=21,highlightthickness=0)
        for xLoc in xrange (self.plotWidth/self.xNumTicks, self.plotWidth+1, self.plotWidth/self.xNumTicks):
            self.xAxisCanvas.create_line(xLoc, 0, xLoc, self.TICK_LENGTH)
            self.xTickLabels += [self.xAxisCanvas.create_text(xLoc, self.TICK_LENGTH, anchor=Tkinter.N, text="%.2g"%(xLoc*self.xMax/self.plotWidth))]

        self.xAxisCanvas.create_line(0,0,self.plotWidth,0)
        self.xAxisCanvas.grid(row=2, col=2, columnspan=2)
        # end x axis ticks and tick labels
        
        #begin y axis ticks and tick labels
        yCanvasWidth = 50
        self.yTickLabels = []
        self.yAxisCanvas = Tkinter.Canvas(self, bg="white", height=self.plotHeight+25, width=yCanvasWidth, highlightthickness=0)
        for yLoc in xrange(25, self.plotHeight+25, self.plotHeight/self.yNumTicks):
            self.yAxisCanvas.create_line(yCanvasWidth, yLoc, yCanvasWidth-self.TICK_LENGTH , yLoc)
            self.yTickLabels += [self.yAxisCanvas.create_text(yCanvasWidth-self.TICK_LENGTH-4, yLoc, anchor=Tkinter.E, \
                                                              text="%.2g"%((self.plotHeight+25-yLoc)*self.yMax/self.plotHeight))]
        self.yAxisCanvas.create_line(yCanvasWidth-1,25,yCanvasWidth-1,self.plotHeight+25)
        self.yAxisCanvas.grid(row=0, col=1, rowspan=2)
        #end y axis ticks and tick labels
        
        #fill in corner of graph
        cornerCanvas = Tkinter.Canvas(self, bg="white", width =yCanvasWidth, height =21, highlightthickness=0)
        cornerCanvas.create_line(yCanvasWidth-1,0,yCanvasWidth,0)
        cornerCanvas.grid(row=2,col=1)

        #top spacer
        self.xSpacer = Tkinter.Frame(self, height=25, width=self.plotWidth, bg="white")
        self.xSpacer.grid(row=0, col = 2)
        self.ySpacer = Tkinter.Frame(self, width=25, height =self.plotHeight, bg="white")
        self.ySpacer.grid(row=1,col=3)
        
        #set up plotArea
        self.plotArea = Tkinter.Canvas(self, bg="white", \
                               highlightthickness=0,width = self.plotWidth, height = self.plotHeight)
        self.plotArea.grid(row=1, col=2)               

        ## ---- END GUI SETUP ---- 
    def addPoint(self, dataTuple):
        """
        Adds a point to the plot.  The tuple should contain a point (x,y) to add.
        """
        if dataTuple[0] > self.xMax or  dataTuple[1] > self.yMax:
            if dataTuple[0] > self.xMax:
                oldXMax = self.xMax
                self.xMax = 2.0*dataTuple[0]
                self.relabelXAxis()
            if dataTuple[1] > self.yMax:
                oldYMax = self.yMax
                self.yMax = 2.0*dataTuple[1]
                self.relabelYAxis()
            self.redrawAll()
            
        self.drawPoint(dataTuple[0], dataTuple[1])
        if len(self.plotData) > 0:
            self.drawLine(self.plotData[-1][0], self.plotData[-1][1], dataTuple[0], dataTuple[1])
        self.plotData += [dataTuple]
        self.update_idletasks()

    def addPoints(self, dataTupleList):
        """
        Adds a list of points to the plot.  Each tuple in dataTupleList should contain a point (x,y) to add.
        """
        for points in dataTupleList:
            self.addPoint(points)
        
    def xToCanvas(self, x):
        """
        Converts an x value to a pixel location on the canvas.
        """
        return (float(self.plotArea.cget("width"))/self.xMax)*x

    def yToCanvas(self, y):
        """
        Converts a y value to a pixel location on the canvas.
        """
        return float(self.plotArea.cget("height")) -  (float(self.plotArea.cget("height"))/self.yMax)*y
    
    def drawPoint(self, x, y):
        """
        Draws a point (x,y) on the canvas.
        """
        self.plotArea.create_oval(self.xToCanvas(x), self.yToCanvas(y), self.xToCanvas(x), self.yToCanvas(y))

    def drawLine(self, x1, y1, x2, y2):
        """
        Draws a line on the canvas connecting (x1,y1) and (x2,y2).
        """
        if self.linesOn:
            self.plotArea.create_line(self.xToCanvas(x1), self.yToCanvas(y1), self.xToCanvas(x2), self.yToCanvas(y2), width=1)
        else:
            self.plotArea.lower(self.plotArea.create_line(self.xToCanvas(x1), self.yToCanvas(y1), self.xToCanvas(x2), self.yToCanvas(y2), fill="white"))

    def redrawAll(self):
        """
        Redraws all points and lines on the graph.  Useful if the scaling of the axes changes.
        """
        for items in self.plotArea.find_all():
            self.plotArea.delete(items)

        prev = -1
        for tuples in self.plotData:
            self.drawPoint(tuples[0], tuples[1])
            if prev != -1:
                self.drawLine(prev[0], prev[1], tuples[0], tuples[1])
            prev = tuples
        self.update_idletasks()


    def relabelXAxis(self):
        """
        Relabels the x axis.  Useful if the scaling of the x axis changes.
        """
        newLabels = [self.xMax*float(i+1)/self.xNumTicks for i in xrange(self.xNumTicks)]
        for i in xrange(len(self.xTickLabels)):
            self.xAxisCanvas.itemconfig(self.xTickLabels[i], text="%.2g"%(newLabels[i]))

    def relabelYAxis(self):
        """
        Relabels the y axis.  Useful if the scaling of the y axis changes.
        """
        newLabels = [0]*self.yNumTicks
        for i in xrange(0,self.yNumTicks):
            newLabels[i] = self.yMax*float(self.yNumTicks+1-i)/self.yNumTicks
        for i in xrange(len(self.yTickLabels)):
            self.yAxisCanvas.itemconfig(self.yTickLabels[i], text="%.2g"%(newLabels[i]))

    #GUI event handlers
    def writeToFile(self):
        """
        Called by the GUI to open a SaveAs dialog and write the data represented in the plot to a file.
        """
        fileWindow = tkFileDialog.SaveAs(self)
        fileName = fileWindow.show()

        try:
            filePoint = open(fileName, "w")
            filePoint.write(self.xTitle + "\t" + self.yTitle +"\n")
            for tuples in self.plotData:
                filePoint.write(str(tuples[0]) + "\t" + str(tuples[1]) + "\n")
            filePoint.close()
        except:
            tkMessageBox.showerror("File Error", "Writing to file failed.")
                    
    def alterLines(self):
        """
        Toggles the lines connecting points on and off.
        """
        if self.linesOn:
            for item in self.plotArea.find_all():
                if self.plotArea.type(item) == "line":
                    self.plotArea.itemconfig(item, fill="white")
                    self.plotArea.lower(item)
            self.linesOn = 0
        else:
            for item in self.plotArea.find_all():
                if self.plotArea.type(item) == "line":
                    self.plotArea.itemconfig(item, fill="black")
            self.linesOn = 1

    def clearData(self):
        self.plotData = []
        self.xMax = 1.0
        self.yMax = 1.0
        self.relabelXAxis()
        self.relabelYAxis()
        self.redrawAll()
        
if __name__ == "__main__":
    root = Tkinter.Tk()
    root.withdraw()
    test = TwoDimPlot(None, plotName="TestPlot",xTitle="XLabel", yTitle="YLabel", plotHeight=556, plotWidth=647)
    for i in xrange(20):
        test.addPoint((i, i**2))
    test.addPoint((0,0))
    test.mainloop()
