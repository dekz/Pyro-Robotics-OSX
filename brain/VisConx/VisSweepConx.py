__author__ = "Matt Fiedler"
__version__ = "$Revision: 2020 $"

from pyrobot.brain.conx import *
import Tkinter
import tkSimpleDialog
import pyrobot.brain.VisConx.ActivationsDiag as ActivationsDiag
import pyrobot.brain.VisConx.VisConxBase as VisConxBase

class SweepGUIBase(VisConxBase.VisConxBase):
    def __init__(self):
        VisConxBase.VisConxBase.__init__(self)
        self.pausedFlag = 0
        self.stopFlag = 0
        
        #start/pause/stop buttons       
        controlFrame = Tkinter.Frame(self.root)
        labelFrame = Tkinter.Frame(controlFrame)
        Tkinter.Label(labelFrame, text="Controls:", font=("Arial", 14, "bold")).pack(side=Tkinter.LEFT)
        labelFrame.pack(side=Tkinter.TOP, expand=Tkinter.YES, fill=Tkinter.X)
        innerButtonFrame = Tkinter.Frame(controlFrame)
        self.trainButton = Tkinter.Button(innerButtonFrame, text="Start", command=self.handleTrainButton)
        self.trainButton.pack(side=Tkinter.LEFT)
        self.pauseButton = Tkinter.Button(innerButtonFrame, text="Pause",
                                          state=Tkinter.DISABLED, command=self.handlePauseButton)
        self.pauseButton.pack(side=Tkinter.LEFT)
        self.stopButton = Tkinter.Button(innerButtonFrame, text="Stop",
                                         state=Tkinter.DISABLED, command=self.handleStopButton)
        self.stopButton.pack(side=Tkinter.LEFT)
        Tkinter.Label(innerButtonFrame, text="Epoch: ").pack(side=Tkinter.LEFT)
        self.epochLabel = Tkinter.Label(innerButtonFrame, text="0")
        self.epochLabel.pack(side=Tkinter.LEFT)
        self.settingsButton = Tkinter.Button(innerButtonFrame, text="Settings..", command=lambda:
                                             VisConxBase.NNSettingsDialog(self.root, self.netStruct.network))
        self.settingsButton.pack(side=Tkinter.RIGHT)
        innerButtonFrame.pack(side=Tkinter.BOTTOM, expand=Tkinter.YES, fill=Tkinter.X)

        #assemble frames
        controlFrame.pack(side=Tkinter.TOP, expand=Tkinter.YES, fill=Tkinter.X)
        #spacer
        Tkinter.Frame(self.root, height=2, bg="black").pack(side=Tkinter.TOP, expand=Tkinter.YES, fill=Tkinter.X)
        self.visualFrame.pack(side=Tkinter.TOP, expand=Tkinter.YES, fill=Tkinter.X)
        #spacer
        Tkinter.Frame(self.root, height=2, bg="black").pack(side=Tkinter.TOP, expand=Tkinter.YES, fill=Tkinter.X)
        self.inputFrame.pack(side=Tkinter.TOP, expand=Tkinter.YES, fill=Tkinter.X)
        
    #overloaded methods from Network/SRN
    def train(self):
        self.handleTrainButton()

    def propagate(self):
        #update the GUI
        if self.root:
            self.root.update()
        
        #hack to allow intervention in sweep for purposes of extracting data
        self.__class__.__bases__[1].propagate(self)
        if self.activDiag:
            self.activDiag.extractActivs() 

    #train network
    def trainGUI(self):
        if self.activDiag:
            self.handleActivDiag()
        self.activButton.config(state=Tkinter.DISABLED)
        tssErr = 1.0; self.epoch = 1; totalCorrect = 0; totalCount = 1;
        self.resetCount = 1
        while totalCount != 0 and \
              totalCorrect * 1.0 / totalCount < self.stopPercent:
            (tssErr, totalCorrect, totalCount) = self.sweep()
            if self.pausedFlag:
                if self.root:
                    self.activButton.config(state=Tkinter.NORMAL)
                while self.pausedFlag and not self.stopFlag:
                    self.root.update()
                if self.root:
                    self.activButton.config(state=Tkinter.DISABLED)
                if self.activDiag:
                    self.handleActivDiag()
            if self.stopFlag:
                break
            
            #update data plots
            self.TSSData +=  [(self.epoch, tssErr)]
            self.updatePlot(self.TSSPlot, self.TSSData[-1])
            self.RMSData += [(self.epoch, self.RMSError())]
            self.updatePlot(self.RMSPlot, self.RMSData[-1])
            self.pCorrectData += [(self.epoch, float(totalCorrect)/totalCount)]
            self.updatePlot(self.pCorrectPlot, self.pCorrectData[-1])
            
            #update Hinton diagram
            self.updateHintonWeights()
            if self.resetEpoch == self.epoch:
                if self.resetCount == self.resetLimit:
                    self.write("Reset limit reached. Ending without reaching goal.\n")
                    break
                self.resetCount += 1
                self.write("RESET! resetEpoch reached; starting over...\n")
                self.clearErrorPlots()
                self.initialize()
                tssErr = 1.0; self.epoch = 1; totalCorrect = 0
                continue
            sys.stdout.flush()
            self.epoch += 1
            self.updateEpochLabel()
        if totalCount > 0:
            self.TSSData +=  [(self.epoch, tssErr)]
            self.updatePlot(self.TSSPlot, self.TSSData[-1])
            self.RMSData += [(self.epoch, self.RMSError())]
            self.updatePlot(self.RMSPlot, self.RMSData[-1])
            self.pCorrectData += [(self.epoch, totalCorrect * 1.0 / totalCount)]
            self.updatePlot(self.pCorrectPlot, self.pCorrectData[-1])
        else:
            self.write("Nothing done.")
        if self.root:
            self.activButton.config(state=Tkinter.NORMAL)

    #handlers for activations diagram
    def handleActivDiag(self):
        if not self.activDiag:
            try:
                self.activDiag = ActivationsDiag.ActivSweepDiag(self.root,self.netStruct)
            except LayerError, err:
                self.write("Error! You must have called setInputs and setOutputs before using the activation display.")
                self.write(err)
                self.activDiag.destroy()
                self.activDiag = None
                self.activButton.deselect()
            else:
                self.activDiag.protocol("WM_DELETE_WINDOW", self.handleActivDiag)
        else:
            self.activDiag.destroy()
            self.activDiag = None
            self.activButton.deselect()

    #handlers for buttons
    def handleTrainButton(self):
            self.pausedFlag = 0
            self.stopFlag = 0
            self.pauseButton.config(state=Tkinter.NORMAL)
            self.stopButton.config(state=Tkinter.NORMAL)
            self.trainButton.config(state=Tkinter.DISABLED)
            
            #clear data collected during the last run
            self.initialize()
            self.clearErrorPlots()
            try:
                self.trainGUI()
            except AttributeError, err:
                self.write("Error!  Must call setInputs and setOutputs before training.")
                self.write(err)

            #set buttons and flags back after train concludes
            if self.root:
                self.trainButton.config(state=Tkinter.NORMAL)
                self.pauseButton.config(state=Tkinter.DISABLED)
                self.pauseButton.config(text="Pause")
                self.stopButton.config(state=Tkinter.DISABLED)
                self.pausedFlag=0
                self.stopFlag=0

    def handlePauseButton(self):
        if not self.pausedFlag:
            self.pausedFlag = 1
            self.trainButton.config(state=Tkinter.DISABLED)
            self.stopButton.config(state=Tkinter.NORMAL)
            self.pauseButton.config(text="Resume")
        else:
            self.pausedFlag = 0
            self.pauseButton.config(text="Pause")            

    def handleStopButton(self):
        self.stopFlag = 1
        self.pausedFlag = 0
        self.trainButton.config(state=Tkinter.NORMAL)
        self.pauseButton.config(state=Tkinter.DISABLED)
        self.stopButton.config(state=Tkinter.DISABLED)

    #updates epoch label
    def updateEpochLabel(self):
        self.epochLabel.config(text="%d" % (self.epoch,))

    def clearErrorPlots(self):
        self.TSSData = []
        if self.TSSPlot:
            self.TSSPlot.clearData()
        self.RMSData = []
        if self.RMSPlot:
            self.RMSPlot.clearData()
        self.pCorrectData = []
        if self.pCorrectPlot:
            self.pCorrectPlot.clearData()

    def handleWindowClose(self):
        VisConxBase.VisConxBase.handleWindowClose(self)
        self.stopFlag = 1
        
class VisSweepNetwork(SweepGUIBase, Network): 
    def __init__(self):
        Network.__init__(self)
        SweepGUIBase.__init__(self)
        
class VisSweepSRN(SweepGUIBase, SRN):
    def __init__(self):
        SRN.__init__(self)
        SweepGUIBase.__init__(self)

    def predict(self, fromLayer, toLayer):
        SRN.predict(self, fromLayer, toLayer)
        self.updateStructureDiags()

if __name__ == "__main__":
    def testXORBatch():
        n = VisSweepNetwork()
        n.addThreeLayers(2, 2, 1)
        n.setInputs([[0.0, 0.0],
                     [0.0, 1.0],
                     [1.0, 0.0],
                     [1.0, 1.0]])
        n.setTargets([[0.0],
                      [1.0],
                      [1.0],
                      [0.0]])
        n.setReportRate(100)
        n.setBatch(1)
        n.reset()
        n.setEpsilon(0.5)
        n.setMomentum(.975)
        
    def testXORNonBatch():
        n = VisSweepNetwork()
        n.addThreeLayers(2, 2, 1)
        n.setInputs([[0.0, 0.0],
                     [0.0, 1.0],
                     [1.0, 0.0],
                     [1.0, 1.0]])
        n.setTargets([[0.0],
                      [1.0],
                      [1.0],
                      [0.0]])
        n.setReportRate(100)
        n.setBatch(0)
        n.initialize()
        n.setEpsilon(0.5)
        n.setMomentum(.975)
        n.train()
        
    def testAND():
        n = VisSweepNetwork()
        #n.setSeed(114366.64)
        n.add(Layer('input',2)) 
        n.add(Layer('output',1)) 
        n.connect('input','output') 
        n.setInputs([[0.0,0.0],[0.0,1.0],[1.0,0.0],[1.0,1.0]]) 
        n.setTargets([[0.0],[0.0],[0.0],[1.0]]) 
        n.setEpsilon(0.5) 
        n.setTolerance(0.2) 
        n.setReportRate(5) 
   
    def testSRN():
        n = VisSweepSRN()
        #n.setSeed(114366.64)
        n.addSRNLayers(3,2,3)
        n.predict('input','output')
        seq1 = [1,0,0, 0,1,0, 0,0,1]
        seq2 = [1,0,0, 0,0,1, 0,1,0]
        n.setInputs([seq1, seq2])
        n.setLearnDuringSequence(1)
        n.setReportRate(75)
        n.setEpsilon(0.1)
        n.setMomentum(0)
        n.setBatch(1)
        n.setTolerance(0.25)
        n.setStopPercent(0.7)
        n.setResetEpoch(2000)
        n.setResetLimit(0)
        #n.setInteractive(1)
        #n.verbosity = 3

    def testAutoAssoc():
        n = VisSweepNetwork()
        #n.setSeed(114366.64)
        n.addThreeLayers(3,2,3)
        n.setInputs([[1,0,0],[0,1,0],[0,0,1],[1,1,0],[1,0,1],[0,1,1],[1,1,1]])
        n.associate('input','output')
        n.setReportRate(25)
        n.setEpsilon(0.1)
        n.setMomentum(0.9)
        n.setBatch(1)
        n.setTolerance(0.25)
        n.setStopPercent(0.9)
        n.setResetEpoch(1000)
        n.setResetLimit(2)

    def testRAAM():
        # create network:
        raam = VisSweepSRN()
        #raam.setSeed(114366.64)
        raam.setPatterns({"john"  : [0, 0, 0, 1],
                          "likes" : [0, 0, 1, 0],
                          "mary"  : [0, 1, 0, 0],
                          "is" : [1, 0, 0, 0],
                          })
        size = len(raam.getPattern("john"))
        raam.addSRNLayers(size, size * 2, size)
        raam.add( Layer("outcontext", size * 2) )
        raam.connect("hidden", "outcontext")
        raam.associate('input', 'output')
        raam.associate('context', 'outcontext')
        raam.setInputs([ [ "john", "likes", "mary" ],
                         [ "mary", "likes", "john" ],
                         [ "john", "is", "john" ],
                         [ "mary", "is", "mary" ],
                         ])
        # network learning parameters:
        raam.setLearnDuringSequence(1)
        raam.setReportRate(10)
        raam.setEpsilon(0.1)
        raam.setMomentum(0.0)
        raam.setBatch(0)
        # ending criteria:
        raam.setTolerance(0.4)
        raam.setStopPercent(1.0)
        raam.setResetEpoch(5000)
        raam.setResetLimit(0)

    def testSRNPredictAuto():
        n = VisSweepSRN()
        #n.setSeed(114366.64)
        n.addSRNLayers(3,3,3)
        n.add(Layer('assocInput',3))
        n.connect('hidden', 'assocInput')
        n.associate('input', 'assocInput')
        n.predict('input', 'output')
        n.setInputs([[1,0,0, 0,1,0, 0,0,1, 0,0,1, 0,1,0, 1,0,0]])
        n.setLearnDuringSequence(1)
        n.setReportRate(25)
        n.setEpsilon(0.1)
        n.setMomentum(0.3)
        n.setBatch(1)
        n.setTolerance(0.1)
        n.setStopPercent(0.7)
        n.setResetEpoch(2000)
        n.setResetLimit(0)
        n.setOrderedInputs(1)

    def testChangeLayerSize():
        n = VisSweepNetwork()
        n.addThreeLayers(3,3,3)
        n.archButton.invoke()
        size = tkSimpleDialog.askinteger("Change hidden layer size", "Enter new hidden layer size", minvalue=0)
        n.archButton.invoke()
        try:
            # exception thrown from changeSize in Connection class
            n.changeLayerSize('hidden', size)
        except LayerError, err:
            print err
        n.archButton.invoke()
            
    def dispatchToTest():
        index = int(testList.curselection()[0])
        callList[index]()
        
    root = Tkinter.Tk()
    testList = Tkinter.Listbox(root, selectmode=Tkinter.SINGLE, width=50)

    listButton = Tkinter.Button(root, text="Run test", command=dispatchToTest)
    nameList = ["Test XOR in batch mode",
                "Test XOR in non-batch mode",
                "Test AND",
                "Test SRN",
                "Test auto association",
                "Test RAAM",
                "Test SRN with prediction and auto association",
                "Test changing a layer's size"]
    callList = [testXORBatch, testXORNonBatch, testAND, testSRN, testAutoAssoc, testRAAM,testSRNPredictAuto, \
                testChangeLayerSize]
    
    for name in nameList:
        testList.insert(Tkinter.END, name)
        testList.pack()
        listButton.pack()
                
    root.mainloop()
