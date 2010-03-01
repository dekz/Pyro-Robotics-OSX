__author__ = "Matt Fiedler"
__version__ = "$Revision$"

from Hinton import *
import Tkinter

class Hinton(MatrixHinton):
    def __init__(self,blocks = 1, title = "", width = 275, maxvalue = 1.0, data = None, parent=None, xDataLabel="", yDataLabel=""):
        if not parent:
            parent = Tkinter.Tk()
        MatrixHinton.__init__(self, parent, title, [[0.0]]*blocks, blockSize=width/blocks, fromAxisLabel=xDataLabel, toAxisLabel=yDataLabel)
            
    def setTitle(self, title):
        self.title(title)

    def changeSize(self, event):
        print "Unsupported operation"

    def update(self, vec):
        inputData = []
        for dat in vec:
            inputData += [[dat]]
        self.updateWeights(inputData)
    
    def destroy(self):
      MatrixHinton.destroy(self)

if __name__ == '__main__':
    root = Tkinter.Tk()
    hinton1 = Hinton(6,parent=root, xDataLabel="x axis", yDataLabel="y axis")
    hinton1.update([0.0, 1.0, .5, 0.0, -1.0, -.5])
    hinton2 = Hinton(8, parent=root)
    v = [1.0, 1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -5.0]
    hinton2.update(v)
    print v
