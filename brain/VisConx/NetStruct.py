__author__ = "Matt Fiedler"
__version__ = "$Revision: 2020 $"

import Queue

class Vertex:
    def __init__(self,layerObj):
        self.layerObj = layerObj
        self.edgeOut = []
        self.visited = 0
        self.context = []
        self.name=layerObj.name
        
    def addEdgeOut(self, newEdge):
        self.edgeOut += [newEdge]
        if newEdge.type[0] == "c":
            self.context += [newEdge]

    def hasContext(self):
        return len(self.context) > 0

class Edge:
    def __init__(self,fromVer,toVer,type,connection=None):
        self.fromVer = fromVer
        self.toVer = toVer
        self.connection = connection
        self.type = type

class NetStruct:
    def __init__(self, network):
        self.network = network
        self.levelList = []
        self.conList = []
        self.makeLevelList()
        
    def makeLevelList(self):
        self.levelList = []
        self.conList = []
        vertexDict = {}
        inputVertices = []

        # generate vertex list from edge list
        for con in self.network.connections:
            if not vertexDict.has_key(con.toLayer.name):
                newVertex = Vertex(con.toLayer)
                vertexDict[con.toLayer.name] = newVertex

            if not vertexDict.has_key(con.fromLayer.name):
                newVertex = Vertex(con.fromLayer)
                self.conList += [Edge(newVertex, vertexDict[con.toLayer.name],"forward", con)]
                newVertex.addEdgeOut(self.conList[-1])
                if con.fromLayer.kind[0] == "I":
                    inputVertices += [newVertex]
                vertexDict[con.fromLayer.name] = newVertex
            else:
                self.conList += [Edge(vertexDict[con.fromLayer.name], vertexDict[con.toLayer.name],"forward", con)]
                vertexDict[con.fromLayer.name].addEdgeOut(self.conList[-1])

            if con.fromLayer.kind[0] == "C":
                vertexDict[con.toLayer.name].addEdgeOut(Edge(vertexDict[con.toLayer.name], vertexDict[con.fromLayer.name], "context"))

        #add in predictions and associations
        for fromName, toName in self.network.association:
            vertexDict[fromName].addEdgeOut(Edge(vertexDict[fromName], vertexDict[toName], "association"))

        if hasattr(self.network, "prediction"):
            for fromName, toName in self.network.prediction:
                vertexDict[fromName].addEdgeOut(Edge(vertexDict[fromName], vertexDict[toName], "prediction"))

        # modified breadth first search with multiple starting points
        nextLevel = inputVertices
        outputLevel = []

        for vertices in inputVertices:
            vertices.visited = 1

        while len(nextLevel) > 0:
            self.levelList += [nextLevel]
            nextLevel = []
            for vertices in self.levelList[-1]:
                for edges in vertices.edgeOut:
                    if edges.type[0] == "f" and not edges.toVer.visited:
                        edges.toVer.visited = 1
                        if edges.toVer.layerObj.kind[0] == "O":
                            outputLevel += [edges.toVer]
                            if edges.toVer.hasContext():
                                for contextEdge in edges.toVer.context:
                                    contextEdge.toVer.visited =1
                                    outputLevel += [contextEdge.toVer]
                        else:
                            nextLevel += [edges.toVer]
                            if edges.toVer.hasContext():
                                for contextEdge in edges.toVer.context:
                                    contextEdge.toVer.visited =1
                                    nextLevel += [contextEdge.toVer]
        self.levelList += [outputLevel]
        
if __name__ == "__main__":
    #n = Network() 
    #n.add(Layer('input',2))
    #n.add(Layer('hidden',2))
    #n.add(Layer('output',1)) 
    #n.connect('input','hidden')
    #n.connect('hidden','output')
    
    #myNetStruct = NetStruct(n)
    #print myNetStruct.levelList
    #print myNetStruct.layerDict
    #print myNetStruct.edgeList
    from pyrobot.brain.conx import SRN
    x = SRN()
    x.addThreeLayers(3,3,3)
    SRNStruct = NetStruct(x)
    print SRNStruct.levelList

    for layer in x.layers:
        print layer.kind

    for level in SRNStruct.levelList:
        for vertex in level:
            print vertex.name
