__author__ = "Matt Fiedler"
__version__ = "$Revision: 2361 $"

from pyrobot.brain.conx import *
import pyrobot.system.share
from pyrobot.brain.VisConx import VisRobotConx
from pyrobot.brain.VisConx import VisSweepConx
import Tkinter

VNetwork = VisSweepConx.VisSweepNetwork
VINetwork = VisRobotConx.VisRobotNetwork

VSRN = VisSweepConx.VisSweepSRN
VISRN = VisRobotConx.VisRobotSRN

class NetworkWatcher(Tkinter.Toplevel):
   def __init__(self, network):
       self.network = network
       self._width = 500
       self._height = 500
       if pyrobot.system.share.gui:
           root = pyrobot.system.share.gui
       else:
           root = Tkinter.Tk()
           root.withdraw()
       Tkinter.Toplevel.__init__(self, root)
       self.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.minimize)
       self.wm_title("Pyrobot Network Watcher")
       self.protocol('WM_DELETE_WINDOW',self.destroy)
       self.frame = Tkinter.Frame(self)
       self.frame.pack(side = 'bottom', expand = "yes", anchor = "n",
                       fill = 'both')
       self.canvas = Tkinter.Canvas(self.frame, bg="white", width=self._width,
                                    height=self._height)
       self.canvas.pack(expand="yes", fill="both", side="top", anchor="n")
       self.addMouseBindings()
   def addMouseBindings(self):
       pass
   def minimize(self):
       self.withdraw()
   def update(self):
       self.canvas.delete("all")
       size = 10
       space = 20
       border = 10
       for n in range(len(self.network["input"])):
           # draw horizontal lines
           self.canvas.create_line(border,
                                   self._height - ((n + 1) * space),
                                   self._width - border,
                                   self._height - ((n + 1) * space),
                                   fill = "black")
           # left input nodes
           self.canvas.create_oval(border - size/2,
                                   self._height - ((n + 1) * space) - size/2,
                                   border + size/2,
                                   self._height - ((n + 1) * space) + size/2,
                                   fill = "red")
       for n in range(len(self.network["output"])):
           # draw vertical lines
           self.canvas.create_line(self._width - ((n + 1) * space),
                                   border,
                                   self._width - ((n + 1) * space),
                                   self._height - border,
                                   fill = "black")
           # left output nodes
           self.canvas.create_oval(self._width - ((n + 1) * space) - size/2,
                                   border - size/2,
                                   self._width - ((n + 1) * space) + size/2,
                                   border + size/2,
                                   fill = "blue")
       hiddenCount = 0
       for layer in self.network.layers:
           if "hidden" in layer.name:
               self.canvas.create_line(4 * border + hiddenCount * space,
                                       self._height - (len(self.network["input"]) + 1) * space - hiddenCount * space,
                                       self._width - border,
                                       self._height - (len(self.network["input"]) + 1) * space - hiddenCount * space,
                                       fill = "black")
               self.canvas.create_line(4 * border + hiddenCount * space,
                                       self._height - (len(self.network["input"]) + 1) * space - hiddenCount * space,
                                       4 * border + hiddenCount * space,
                                       self._height - border,
                                       fill = "black")
               self.canvas.create_oval(4 * border + hiddenCount * space - size/2,
                                       self._height - (len(self.network["input"]) + 1) * space - hiddenCount * space - size/2,
                                       4 * border + hiddenCount * space + size/2,
                                       self._height - (len(self.network["input"]) + 1) * space - hiddenCount * space + size/2,
                                       fill = "green")
               hiddenCount += 1

if __name__ == "__main__":
    network = IncrementalNetwork()
    network.addLayers(3, 2)
    network.addCandidateLayer(8)
    network.recruit(2)
    network.recruit(4)
    nw = NetworkWatcher(network)
    nw.update()
