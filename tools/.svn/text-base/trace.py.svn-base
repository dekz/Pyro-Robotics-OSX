# Python Program to display a path in a window

from pyrobot import pyrobotdir
import Image, ImageChops, ImageDraw, ImageFont
import sys, os, colorsys, math
import random
import Tkinter, ImageTk
import string

class ColorSet:
    def __init__(self):
        self.colors = [ 0, 90, 215, 190, 138, 172, 24, 116, 233]
        self.colorCount = 0
    def next(self):
        retval = self.colors[self.colorCount]
        self.colorCount = (self.colorCount + 1) % len(self.colors)
        return retval

class SymbolSet:
    def __init__(self):
        self.symbols = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        self.symbolCount = 0
    def next(self):
        retval = self.symbols[self.symbolCount]
        self.symbolCount = (self.symbolCount + 1) % len(self.symbols)
        return retval

class Trace:
    """
    Trace provides a general way of displaying a path on an image.
    """

    def __init__(self, pathDataFilename = "", worldImageFilename = "", resolution = 0.01):
        self.worldImageFilename = worldImageFilename
        self.pathDataFilename = pathDataFilename
        self.outfile = ""
        self.app = 0
        path = pyrobotdir()
        self.fontFilename = path + "/tools/pilfonts/courR08.pil"
        self.symbols = 1        # activates/deactivates symbol mode
        self.color = "0"          # activates/deactivates color
        self.length = 10     # the length of lines in non-symbol mode
        # the resolution given for the bitmap in the world file
        self.resolution = resolution
        self.interval = 2       # frequency datapoints should be displayed
        self.robotPathData = self.readDataFile()
        im = Image.open(self.worldImageFilename)
        if self.color == "0":
            self.imageData = ImageChops.invert(im)
        self.imageData = im.convert("RGB")
        self.convertXPositionData(self.imageData, self.robotPathData)
        self.drawObj = ImageDraw.Draw(self.imageData)
        self.textDict = {}
        self.symbolDict = {}
        self.symbolSet = SymbolSet()
        self.colorSet = ColorSet()
        self.quitWhenDone = 1

    def readDataFile(self):
        dataFile = open(self.pathDataFilename, "r")
        dataList = []
        for line in dataFile:
            elements = line.split()
            if len(elements) < 3 or len(elements) > 5:
                continue
            elif len(elements) == 3:
                dataList += [[float(x) for x in elements] + [" "]]
            else:
                dataList += [[float(x) for x in elements[:3]] + [string.join(elements[3:])]]
            dataList[-1][0] = dataList[-1][0]/self.resolution
            dataList[-1][1] = dataList[-1][1]/self.resolution
            dataList[-1][2] = (dataList[-1][2] + 90.0) * math.pi/180.0
        return dataList

    def getColor(self, label):
        if label in self.textDict:
            return self.textDict[label]
        else:
            self.textDict[label] = self.colorSet.next()
            return self.textDict[label]

    def getSymbol(self, label):
        if label in self.symbolDict:
            return self.symbolDict[label]
        else:
            self.symbolDict[label] = self.symbolSet.next()
            return self.symbolDict[label]

    def drawSymbol(self, loc, angle, label = None):
        pointList = []
        if type(label) == type("") and len(label) >= 2 and label[0] == '"':
            label = label[1:-1]
        elif label:
            label = self.getSymbol(label)
        else:
            label = self.getSymbol(1)
        colorNum = self.getColor(label)
        if self.symbols:
            self.drawObj.text(loc, label, font = ImageFont.load(self.fontFilename),
                              fill = self.indexToColor(colorNum) )
        else:
            self.drawObj.line([(loc[0], loc[1]),
                          (loc[0] + self.length * math.sin(angle),
                           loc[1] + self.length * math.cos(angle))],
                         fill = self.indexToColor(colorNum))
            self.drawObj.ellipse( (loc[0] - 2, loc[1] - 2, loc[0] + 2, loc[1] + 2),
                             fill = (0, 0, 0))

    def makeWindow(self):
        if self.app != 0:
            self.window.deiconify()
        else:
            self.app = Tkinter.Tk()
            self.app.withdraw()
            self.window = Tkinter.Toplevel()
            self.window.wm_title("Trace View")
            self.im = self.getImage()
            self.image = ImageTk.PhotoImage(self.im)
            self.label = Tkinter.Label(self.window, image=self.image, bd=0)
            self.label.pack({'fill':'both', 'expand':1, 'side': 'left'})
            self.window.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.hideWindow)
            self.visible = 1
        while self.window.tk.dooneevent(2): pass

    def hideWindow(self, signum = None, frame = None):
        self.visible = 0
        self.window.withdraw()
        if self.quitWhenDone:
            sys.exit(1)
      
    def updateWindow(self):
        self.rawImage = ImageTk.PhotoImage(self.im)
        self.label.configure(image = self.rawImage)
        while self.window.tk.dooneevent(2): pass

    def getImage(self):
        return self.imageData

    def indexToColor(self, index):
        maxIndex = 256
        if self.color == "A":
            retColor = colorsys.hsv_to_rgb(float(index)/maxIndex, 1.0, 1.0)
        elif self.color == "0":
            retColor = (0,0,0)
        elif self.color == "1":
            retColor = (255, 0, 0)
        else:
            raise ValueError, "invalid color: '%s'" % self.color
        return (int(retColor[0]*255), int(retColor[1]*255), int(retColor[2]*255))

    def convertXPositionData(self, image, data):
        imWidth = image.size[1]
        for ls in data:
            ls[1] = imWidth - ls[1]

    def addLine(self, data):
        if len(data) == 4:
            x, y, angle, symbol = data
        elif len(data) == 3:
            x, y, angle = data
            symbol = None
        else:
            print "Skipping data; wrong number of values (should be 3 or 4):", data
        self.drawSymbol((x,y), angle, symbol)
        self.updateWindow()

    def output(self):
        iteration = 0
        for x, y, angle, label in self.robotPathData:
            if iteration % self.interval == 0:
                self.drawSymbol((x,y), angle, label)
            iteration += 1
        self.imageData.save(self.outfile)

    def run(self):
        for data in self.robotPathData:
            self.addLine(data)

if __name__ == "__main__":
    import sys, getopt, signal
    if len(sys.argv) < 2:
        opts, args = [('-h','',)], []
    else:
        opts, args = getopt.getopt(sys.argv[3:], "c:s:i:l:r:o:hvw", ["color=", "symbols=", "interval=", "length=", "resolution=", "outfile=", "help", "view", "window"])
    resolution = 0.01
    defaults = {"color": "'0'", "symbols": "1", "interval": "1", 
                "length": "10", "outfile": '""', "window": "0", "view": "0"}
    for opt, val in opts:
        if opt in ("-h", "--help"):
            print "Help:"
            print "-c --color      [0|1|A] B&W, color, or Automatic"
            print "-s --symbols    [0|1] Show lines or symbols"
            print "-i --interval   <INT> Frequency data should be displayed"
            print "-l --length     <INT> Line width (use with -s 0)"
            print "-r --resolution <REAL> Value given in stage world file"
            print "-o --outfile    <FILENAME> Output filename (.gif, .jpg, .ppm)"
            print "-h --help       This help message"
            print "-w --window     Show data interactively in Tk window"
            print "-v --view       Open xview after creating an output file"
            sys.exit()
        elif opt in ("-c", "--color"): 
            defaults["color"] = "'" + val + "'"
        elif opt in ("-s", "--symbols"): 
            defaults["symbols"] = val
        elif opt in ("-i", "--interval"):
            defaults["interval"] = val
        elif opt in ("-l", "--length"):
            defaults["length"] = val
        elif opt in ("-r", "--resolution"):
            resolution = float(val)
        elif opt in ("-o", "--outfile"):
            defaults["outfile"] = "'" + val + "'"
        elif opt in ("-w", "--window"):
            defaults["window"] = "1"
        elif opt in ("-v", "--view"):
            defaults["view"] = "1"
        else:
            raise ValueError, "invalid option: '%s'" % opt
    tracer = Trace(sys.argv[1], sys.argv[2], resolution) # world, data
    prevsighandler = signal.signal(signal.SIGINT, tracer.hideWindow)
    for item in defaults:
        exec("tracer.%s = %s" % (item, defaults[item]))
    if tracer.outfile == '' and tracer.window == 0:
        print "Nothing to do. Try -v -o outputfile.gif, or -w"
        sys.exit(1)
    if tracer.window:
        tracer.makeWindow()
        tracer.run()
    if tracer.view:
        if tracer.outfile:
            print "Creating file '%s'..." % tracer.outfile, 
            tracer.output()
            print "Done!"
            os.system("xview %s &" % tracer.outfile)
        else:
            print "No outfile specified. Try -o outputfile "
    elif tracer.outfile:
        print "Creating file '%s'..." % tracer.outfile, 
        tracer.output()
        print "Done!"
    if tracer.window:
        tracer.app.mainloop()
    
