__author__ = "Matt Fiedler"
__version__ = "$Revision$"

import Tkinter

class ArchDiag(Tkinter.Toplevel):
    SLAB_WIDTH = 150
    SLAB_HEIGHT = 20
    SLAB_VER_SEP = 40
    SLAB_HORIZ_SEP = 40
    EDGE_SEP = 20
    LINE_WIDTH = 1
    FORWARD_COLOR = "black"
    CONTEXT_COLOR = "red"
    PREDICT_COLOR = "blue"
    ASSOC_COLOR = "green"
    LINE_SEP = 2
    LEGEND_LINE_LENGTH = 25
    EXTRA_BUFFER = 15
    
    def __init__(self, parent, netStruct):
        Tkinter.Toplevel.__init__(self,parent)
        self.netStruct = netStruct
        self.title("Network Architecture")

        # find the level with the maximum number of layers
        self.maxLayers = 0
        for level in netStruct.levelList:
            if len(level) > self.maxLayers:
                self.maxLayers = len(level)

        self.canvasWidth = self.maxLayers*self.SLAB_WIDTH + (self.maxLayers + 1)*self.SLAB_HORIZ_SEP
        self.canvasHeight = len(self.netStruct.levelList)*self.SLAB_HEIGHT + (len(self.netStruct.levelList)+1)*self.SLAB_VER_SEP
        self.diagCanvas = Tkinter.Canvas(self, bg = "white", width=self.canvasWidth, height=self.canvasHeight)
        
        self.coordDict = {}
        self.drawDiag()
        self.diagCanvas.grid(row=0,col=0)

        #connection legend
        legendFrame = Tkinter.Canvas(self)
        forwardCanvas = Tkinter.Canvas(legendFrame, width=self.LEGEND_LINE_LENGTH, height=self.SLAB_HEIGHT)
        forwardCanvas.create_line(0, self.SLAB_HEIGHT/2, self.LEGEND_LINE_LENGTH, self.SLAB_HEIGHT/2, fill=self.FORWARD_COLOR, width=2)
        forwardCanvas.grid(row=0,col=0, sticky=Tkinter.W)
        Tkinter.Label(legendFrame,text="forward connection").grid(row=0, col=1, sticky=Tkinter.W)
        contextCanvas = Tkinter.Canvas(legendFrame, width=self.LEGEND_LINE_LENGTH, height=self.SLAB_HEIGHT)
        contextCanvas.create_line(0, self.SLAB_HEIGHT/2,self.LEGEND_LINE_LENGTH, self.SLAB_HEIGHT/2, fill=self.CONTEXT_COLOR, width=2)
        contextCanvas.grid(row=0,col=2, sticky=Tkinter.W)
        Tkinter.Label(legendFrame,text="context").grid(row=0,col=3, sticky=Tkinter.W)
        assocCanvas = Tkinter.Canvas(legendFrame, width=self.LEGEND_LINE_LENGTH, height=self.SLAB_HEIGHT)
        assocCanvas.create_line(0, self.SLAB_HEIGHT/2,self.LEGEND_LINE_LENGTH, self.SLAB_HEIGHT/2, fill=self.ASSOC_COLOR, width=2)
        assocCanvas.grid(row=1,col=0, sticky=Tkinter.W)
        Tkinter.Label(legendFrame,text="autoassociation").grid(row=1,col=1, sticky=Tkinter.W)
        predCanvas = Tkinter.Canvas(legendFrame, width=self.LEGEND_LINE_LENGTH, height=self.SLAB_HEIGHT)
        predCanvas.create_line(0, self.SLAB_HEIGHT/2,self.LEGEND_LINE_LENGTH, self.SLAB_HEIGHT/2, fill=self.PREDICT_COLOR, width=2)
        predCanvas.grid(row=1,col=2, sticky=Tkinter.W)
        Tkinter.Label(legendFrame,text="prediction").grid(row=1,col=3, sticky=Tkinter.W)
        legendFrame.grid(row=1,col=0)
        #end connection legend

        self.update_idletasks()
        
    def drawDiag(self):
        #place all the vertices and store coordinates in dictionary by name
        verOffset = self.canvasHeight - self.SLAB_VER_SEP - self.SLAB_HEIGHT
        for level in self.netStruct.levelList:
            horizOffset = (self.canvasWidth - self.SLAB_WIDTH*len(level) - self.SLAB_HORIZ_SEP*(len(level)-1))/2
            for vertex in level:
                self.drawLayer((horizOffset, verOffset), vertex.name, vertex.layerObj.size)
                self.coordDict[vertex.layerObj.name] = (horizOffset, verOffset)
                horizOffset += self.SLAB_HORIZ_SEP + self.SLAB_WIDTH
            verOffset -= self.SLAB_VER_SEP + self.SLAB_HEIGHT

        #add connections by iterating through list again
        for level in self.netStruct.levelList:
            for vertex in level:
                for edge in vertex.edgeOut:
                    self.drawConnection(edge.fromVer.name, edge.toVer.name, edge.type)
                
    def drawLayer(self, posTuple, name, numNodes):
        self.diagCanvas.create_rectangle(posTuple[0], posTuple[1], posTuple[0]+self.SLAB_WIDTH, posTuple[1]+self.SLAB_HEIGHT, \
                                  fill="white", outline="black", width=self.LINE_WIDTH)
        self.diagCanvas.create_text(posTuple[0]+2, posTuple[1]+self.SLAB_HEIGHT/2, fill="black", text=name, anchor=Tkinter.W)
        self.diagCanvas.create_text(posTuple[0]+self.SLAB_WIDTH-2, posTuple[1]+self.SLAB_HEIGHT/2, fill="black", \
                                    text="# Nodes=%u" % (numNodes,), anchor=Tkinter.E)

    def drawConnection(self, fromName, toName, type):
        fromLoc = self.coordDict[fromName]
        toLoc = self.coordDict[toName]
        distance = self.levelDistance(fromLoc, toLoc)

        
        #select color
        if type[0] == "f":
            color = self.FORWARD_COLOR
        elif type[0] == "c":
            color = self.CONTEXT_COLOR
        elif type[0] == "a":
            color = self.ASSOC_COLOR
        elif type[0] == "p":
            color = self.PREDICT_COLOR
        
        #draw link
        if distance == 0:
            if type[0] == "f":
                startLoc = self.bottomConnect(fromLoc)
                finishLoc = self.bottomConnect(toLoc)
                verOffset = self.SLAB_VER_SEP/2
            else:
                startLoc = self.topConnect(fromLoc)
                finishLoc = self.topConnect(toLoc)
                verOffset = -self.SLAB_VER_SEP/2
            self.diagCanvas.create_line(startLoc[0], startLoc[1], \
                                        (startLoc[0]+finishLoc[0])/2, startLoc[1]+verOffset,\
                                        finishLoc[0], finishLoc[1], fill=color, arrow=Tkinter.LAST,
                                        width=self.LINE_WIDTH, smooth=Tkinter.TRUE)
        elif distance == 1:
            startLoc = self.topConnect(fromLoc)
            finishLoc = self.bottomConnect(toLoc)
            self.diagCanvas.create_line(startLoc[0], startLoc[1], finishLoc[0], finishLoc[1],
                                        fill=color, arrow=Tkinter.LAST, width=self.LINE_WIDTH)
        elif distance > 1:
            startLoc = self.topConnect(fromLoc)
            finishLoc = self.bottomConnect(toLoc)
            verOffset = self.SLAB_VER_SEP/2
            if (startLoc[0]+finishLoc[0])/2 > self.canvasWidth/2:
                bendLoc = self.canvasWidth - self.SLAB_HORIZ_SEP/2 + self.EXTRA_BUFFER*(distance-2)
                if bendLoc > self.canvasWidth-1:
                    bendLoc = self.canvasWidth - 1
            else:
                bendLoc = self.SLAB_HORIZ_SEP/2 - self.EXTRA_BUFFER*(distance-2)
                if bendLoc < 0:
                    bendLoc = 0

            self.diagCanvas.create_line(startLoc[0], startLoc[1], \
                                        bendLoc, startLoc[1]-verOffset, \
                                        bendLoc, finishLoc[1]+verOffset, \
                                        finishLoc[0], finishLoc[1], \
                                        fill=color, arrow=Tkinter.LAST, width=self.LINE_WIDTH,
                                        smooth=Tkinter.TRUE)

    def topConnect(self, tuple):
        return tuple[0]+self.SLAB_WIDTH/2, tuple[1]

    def bottomConnect(self, tuple):
        return tuple[0]+self.SLAB_WIDTH/2, tuple[1]+self.SLAB_HEIGHT

    def levelDistance(self, t1,t2):
        return abs(t2[1]-t1[1])/(self.SLAB_HEIGHT + self.SLAB_VER_SEP)
