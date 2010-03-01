__author__ = "Matt Fiedler"
__version__ = "$Revision$"

import Tkinter
from pyrobot.brain.conx import *
import pyrobot.brain.VisConx.ActivationsDiag as ActivationsDiag
import pyrobot.brain.VisConx.VisConxBase as VisConxBase

class RobotGUIBase(VisConxBase.VisConxBase):
    def __init__(self):
        VisConxBase.VisConxBase.__init__(self)
        Tkinter.Label(self.root, text="Controls:", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky=Tkinter.W)
        Tkinter.Button(self.root, text="Settings...",
                       command=lambda: VisConxBase.NNSettingsDialog(self.root, self.netStruct.network)).grid(row=1, column=0, sticky=Tkinter.W)
        self.visualFrame.grid(row=2, column=0, sticky=Tkinter.NSEW)
        Tkinter.Frame(self.root, height=2, bg="black").grid(row=3,column=0,sticky=Tkinter.NSEW)
        self.inputFrame.grid(row=4,column=0, sticky=Tkinter.NSEW)
        self.propNum = 0
        
    def handleActivDiag(self):
        if not self.activDiag:
            try:
                self.activDiag = ActivationsDiag.ActivDiag(self.root,self.netStruct)
            except LayerError:
                self.write("Error! You must have called setInputs and setOutputs before using the activation display.")
                self.activDiag.destroy()
                self.activDiag = None
                self.activButton.deselect()
            else:
                self.activDiag.protocol("WM_DELETE_WINDOW", self.handleActivDiag)
        else:
            self.activDiag.destroy()
            self.activDiag = None
            self.activButton.deselect()

    def propagate(self):
        self.updateGUI()
        self.__class__.__bases__[1].propagate(self)
        self.propNum += 1
        if self.activDiag:
            self.activDiag.updateActivs()
        self.updateHintonWeights()

    def backprop(self):
        (error, correct, total) = self.__class__.__bases__[1].backprop(self)
        
        self.TSSData +=  [(self.propNum, error)]
        self.updatePlot(self.TSSPlot, self.TSSData[-1])
        self.RMSData += [(self.propNum, self.RMSError())]
        self.updatePlot(self.RMSPlot, self.RMSData[-1])
        self.pCorrectData += [(self.propNum, float(correct)/total)]
        self.updatePlot(self.pCorrectPlot, self.pCorrectData[-1])

        return (error,correct, total)

    def updateGUI(self):
        if self.root:
            self.root.update()
            
class VisRobotNetwork(RobotGUIBase, Network):
    def __init__(self):
        Network.__init__(self)
        RobotGUIBase.__init__(self)

class VisRobotSRN(RobotGUIBase, SRN):
    def __init__(self):
        SRN.__init__(self)
        RobotGUIBase.__init__(self)

    def predict(self, fromLayer, toLayer):
        SRN.predict(self, fromLayer, toLayer)
        self.updateStructureDiags()
    
