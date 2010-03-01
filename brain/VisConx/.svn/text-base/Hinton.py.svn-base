__author__ = "Matt Fiedler"
__version__ = "$Revision$"

# -------------------------------------------------------
# Hinton Diagrams
# -------------------------------------------------------

import Tkinter

class HintonBlock(Tkinter.Canvas):
    PADDING=4
    BG_WIDTH=34
    BG_HEIGHT=12
    BG_GRAY = "#d9d9d9"
    NUM_BG_GRAY = "#b0b0b0"
    def __init__(self, parent, size, value, maxAbs, areaScaling=1, showLabel=0):
        Tkinter.Canvas.__init__(self, parent)
        self.config(width=size, height=size, highlightbackground="black")
        self.value = value
        self.maxAbs=maxAbs
        self.size =size
        self.areaScaling = areaScaling
        self.showLabel = showLabel
        self.center = (size)//2
        self.numBG = self.create_rectangle(0,0,self.BG_WIDTH,self.BG_HEIGHT, fill=self.BG_GRAY)
        self.rect = self.create_rectangle(0,0,0,0,outline="black")
        self.label = self.create_text(self.BG_WIDTH-1, 0, text="%.1f" % (self.value,), \
                                      font=("Arial", 10, "bold"), anchor=Tkinter.NE, justify=Tkinter.RIGHT)
        self.redraw()

    def setScaling(self, areaScaling):
        self.areaScaling = areaScaling
        self.redraw()

    def setLabel(self, showLabel):
        self.showLabel = showLabel
        self.redraw()
    
    def updateRectangle(self, value, maxAbs, showValue=0):
        self.value = value
        self.maxAbs=maxAbs
        self.redraw()

    def redraw(self):
        #update rectangle
        if self.areaScaling:
            offset = (self.size*(abs(self.value)/self.maxAbs)**.5)/2 - self.PADDING
        else:
            offset = self.size*(abs(self.value)/self.maxAbs)/2 - self.PADDING

        if self.value > 0:
            fillCol = "white"
            borderCol = "black"
        elif self.value < 0:
            fillCol = "black"
            borderCol = "black"
        else:
            fillCol=self.BG_GRAY #if zero, blend in with the gray
            borderCol=self.BG_GRAY
        self.coords(self.rect, self.center-offset, self.center-offset, self.center+offset+1, self.center+offset+1)
        self.itemconfig(self.rect, fill=fillCol, outline = borderCol)

        #update label
        if self.showLabel:
            self.itemconfig(self.numBG, fill=self.NUM_BG_GRAY, outline="black")
            self.itemconfig(self.label, fill=fillCol, text="%.1f" % (self.value,))
            self.lift(self.numBG)
            self.lift(self.label)
        else:
            self.itemconfig(self.numBG, fill=self.BG_GRAY, outline=self.BG_GRAY)
            self.itemconfig(self.label, fill=self.BG_GRAY)
            self.lower(self.label)
            self.lower(self.numBG)
        
class MatrixHinton(Tkinter.Toplevel):
    OUTSIDE_COL="white"
    TOP_SPACE = 10
    def __init__(self, parent, title, weightMatrix, fromAxisLabel="", toAxisLabel="", blockSize=50):
        Tkinter.Toplevel.__init__(self, parent)
        self.title(title)
        self.config(bg="white")
        
        self.fromAxisLabel = fromAxisLabel
        self.toAxisLabel = toAxisLabel
        
        self.weightMatrix = weightMatrix
        self.maxAbs = self.findMax()
        self.rectMatrix = []

        #top spacer
        Tkinter.Frame(self, bg="white", highlightthickness=0, height=self.TOP_SPACE).grid(row=0, col=0, columnspan=3)
                                                                                             
        # place "axis" labels
        if not toAxisLabel=="":
            Tkinter.Label(self, text=toAxisLabel, bg=self.OUTSIDE_COL,).grid(row=1, col=0)
        if not fromAxisLabel=="":
            Tkinter.Label(self, text=fromAxisLabel, bg=self.OUTSIDE_COL).grid(row=2,col=1)
            
        #show values checkbox
        buttonFrame = Tkinter.Frame(self, bg="white")
        self.showValues = Tkinter.IntVar(self)
        self.showValues.set(0)
        Tkinter.Label(buttonFrame, bg=self.OUTSIDE_COL, text="Options:").grid(col=0, row=1, sticky=Tkinter.W)
        self.valueButton = Tkinter.Checkbutton(buttonFrame, text="Show Values", bg=self.OUTSIDE_COL, activebackground=self.OUTSIDE_COL, \
                                               highlightthickness=0, variable=self.showValues, command=self.updateLabels)
        self.valueButton.grid(col=0, row=1, sticky=Tkinter.W)
        buttonFrame.grid(col=1, row=3, columnspan=2, sticky=Tkinter.N)

        diagFrame = Tkinter.Frame(self, bg="white")
        #create the specific data labels
        if len(weightMatrix[0]) > 1:
            for i in xrange(len(weightMatrix[0])):
                Tkinter.Label(diagFrame, text="%u" % (i,), bg=self.OUTSIDE_COL).grid(col=0, row=i, sticky=Tkinter.NSEW)
        for i in xrange(len(weightMatrix)):
            Tkinter.Label(diagFrame, text="%u" % (i,), bg=self.OUTSIDE_COL).grid(row = len(self.weightMatrix[0]), col=i+1, sticky=Tkinter.NSEW)

        #draw rectangles
        for i in xrange(len(weightMatrix)):
            tempRectList = []
            for j in xrange(len(weightMatrix[i])):
                tempRectList += [HintonBlock(diagFrame, blockSize, self.weightMatrix[i][j], self.maxAbs)]
                tempRectList[-1].grid(col=i+1, row=j)
            self.rectMatrix += [tempRectList]
        diagFrame.grid(row=1,col=1)
        
        self.update_idletasks()

    def updateWeights(self, weightMatrix):
        self.weightMatrix = weightMatrix
        self.maxAbs = self.findMax()
        for i in xrange(len(self.rectMatrix)):
            for j in xrange(len(self.rectMatrix[i])):
                self.rectMatrix[i][j].updateRectangle(self.weightMatrix[i][j], self.maxAbs)
        self.update_idletasks()

    def findMax(self):
        maxAbs = 0
        for row in self.weightMatrix:
            for weight in row:
                if abs(weight) > maxAbs:
                    maxAbs = abs(weight)

        if maxAbs == 0.0:
            return 1.0
        else:
            return maxAbs

    def updateScaling(self):
        for rows in self.rectMatrix:
            for items in rows:
                items.setScaling(self.byArea.get())
        self.update_idletasks()

    def updateLabels(self):
        for rows in self.rectMatrix:
            for items in rows:
                items.setLabel(self.showValues.get())
        self.update_idletasks()
        
if __name__ == '__main__':
    root = Tkinter.Tk()
    myDiag = MatrixHinton(root, "Matrix Hinton Test", [[5.0, 3.0, 2.0], [-99.9, -3.4, -6.0], [1.0, 4.0, -7.0]])
    myDiag = MatrixHinton(root, "Scaling Test", [[-9.88652774], [4.94260928]])
    root.mainloop()
