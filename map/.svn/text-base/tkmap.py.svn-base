from pyrobot.map import Map
import Tkinter
from math import cos, sin
import pyrobot.gui.widgets.TKwidgets as TKwidgets
import pyrobot.system as system
import pyrobot.gui.console as console
from pyrobot import pyrobotdir

class TkMap(Map, Tkinter.Tk):
    """ Map with Tkinter GUI functions """
    def __init__(self, cols, rows, value,
                 width, height, widthMM, heightMM,
                 title, menu = None, keybindings = []):
        """ TkMap extends Map and Tkinter """
        Map.__init__(self, cols, rows, widthMM, heightMM)
        Tkinter.Tk.__init__(self)
        self.title(title)
        if menu == None:
            menu = [('File',[['Exit',self.destroy]])]
        keybindings.append( ("<Configure>", self.changeSize))
        self.menuButtons = {}
        self.debug = 0
        self.application = 0
        self.width = width
        self.height = height
        self.colScale = self.width / self.cols
        self.rowScale = self.height / self.rows
        self.addMenu(menu)
        self.frame = Tkinter.Frame(self,relief=Tkinter.RAISED,borderwidth=2)
        self.frame.pack(side = "top", expand = "yes", fill = "both")
        self.canvas = Tkinter.Canvas(self.frame,width=self.width,height=self.height)
        self.canvas.pack(side = "top", expand = "yes", fill = "both")
        self.addKeyBindings(keybindings)
        self.protocol('WM_DELETE_WINDOW', self.destroy)
        self.update_idletasks()
        self.canvas.focus_set()
        self.canvas_width_diff = int(self.winfo_width()) - int(self.canvas["width"])
        self.canvas_height_diff = int(self.winfo_height()) - int(self.canvas["height"])

    def addText(self, x, y, label, **args):
        """ Millimeters """
        x_pos = (float(x)/self.colScaleMM) * self.colScale
        y_pos = self.height - ((float(y)/self.rowScaleMM) * self.rowScale)
        if "fill" not in args:
            args["fill"] = "black"
        self.canvas.create_oval(x_pos-1, y_pos-1, x_pos+1, y_pos+1, width=0, **args)
        self.canvas.create_text(x_pos+2, y_pos, text=label, anchor="w", **args)

    def addKeyBindings(self, keybindings):
        """ Bind keys and mice events to the canvas """
        for keyname, func in keybindings:
            self.canvas.bind(keyname, func)

    def addMenu(self, menu):
        """ Create a menu """
        self.mBar = Tkinter.Frame(self,relief=Tkinter.RAISED,borderwidth=2)
        self.mBar.pack(fill=Tkinter.X)
        for entry in menu:
            self.mBar.tk_menuBar(self.makeMenu(self.mBar, entry[0],entry[1]))
        self.mBar.pack(side = "top")

    def makeMenu(self, bar, name, commands):
        """ Assumes self.menuButtons exists """
        menu = Tkinter.Menubutton(bar,text=name,underline=0)
        self.menuButtons[name] = menu
        menu.pack(side=Tkinter.LEFT,padx="2m")
        menu.filemenu = Tkinter.Menu(menu)
        for cmd in commands:
            menu.filemenu.add_command(label=cmd[0],command=cmd[1])
        menu['menu'] = menu.filemenu
        return menu

    def changeSize(self, event = 0):
        try:
            self.width = int(self.winfo_width()) - self.canvas_width_diff
            self.height = int(self.winfo_height()) - self.canvas_height_diff
        except:
            return
        #print self.width, self.height
        self.canvas.configure(width = self.width, height = self.height)
        #print self.canvas["width"], self.canvas["height"]
        self.colScale = self.width / self.cols
        self.rowScale = self.height / self.rows
        self.redraw()

    def setGrid(self, grid):
        Map.setGrid(self, grid)
        self.changeSize()

    def destroy(self):
        self.withdraw()
        self.update_idletasks()
        if self.application:
            Tkinter.Tk.destroy(self)

    def redraw(self):
        print "warn: Need to overload redraw() from TkMap class"
        print "colScale: %f, rowScale: %f" % (self.colScale, self.rowScale)

    def fileloaddialog(self, filetype, skel, startdir = ''):
        from string import replace
        from os import getcwd, getenv, chdir
        retval = ""
        cwd = getcwd()
        if startdir == '':
            chdir(pyrobotdir() + "/plugins/" + filetype)
        else:
            chdir(startdir)
        d = TKwidgets.LoadFileDialog(self, "Load " + filetype, skel,
                                     pyrobotdir() + "/plugins/" + filetype)
        if d.Show() == 1:
            doc = d.GetFileName()
            d.DialogCleanup()
            retval = doc
        else:
            d.DialogCleanup()
        chdir(cwd)
        return retval

    def loadMap(self):
        f = self.fileloaddialog("maps","*.py")
        if f != '':
            self.loadMapFile(f)

    def loadMapFile(self, file):
        import os
        if file[-3:] != '.py':
            file = file + '.py'
        if system.file_exists(file):
            grid = system.loadINIT(file)
        elif system.file_exists(pyrobotdir() + \
                                '/plugins/maps/' + file): 
            grid = system.loadINIT(pyrobotdir() + \
                                   '/plugins/plots/' + file)
        else:
            raise 'Map file not found: ' + file
        self.setGrid(grid)

    def saveMap(self):
        pass

class TkSimpleMap(TkMap):
    def __init__(self, x_meter, y_meter, title = "Simple Map"):
        TkMap.__init__(self, 1, 1, 0,
                       x_meter * 50, y_meter * 50, # pixels
                       x_meter * 1000, y_meter * 1000, # MM
                       title)
    def addText(self, x, y, label, **args):
        """ Meters """
        TkMap.addText(self, x * 1000, y * 1000, label, **args)

if __name__ == '__main__':
    print "Testing TkMap()..."
    map = TkMap(8, 10, .5,
                200, 500,
                200, 500,
                "Sample Map")
    map.display()
    map.reset()
    map.display()
    print "Setting Grid location..."
    map.setGridLocation(400, 900, 1.0, "A")
    map.validateGrid()
    print "Setting Grid to new size..."
    map.setGrid( [[0, 0, 0],
                  [0, 1, 0],
                  [0, 0, 0],
                  [1, 0, 0]] )
    map.validateGrid()
    map.display()
    print "All done!"
    map.application = 1
    for x in range(0, 200, 10):
        map.addText( x, x*5/float(2), "%d" % x)
    map.mainloop()

    map = TkSimpleMap(2, 5, "Testing Map")
    for x in range(0, 2000, 100):
        map.addText( x/1000.0, (x/1000.0)*5/float(2), "%d" % x)
    map.mainloop()
    
