import Tkinter, os, random, pickle
import Image, ImageTk, ImageDraw, ImageFont 

class GUI(Tkinter.Toplevel):
    """
    Konane: Hawaiian Checkers
    """
    def __init__(self, root, width, height):
        Tkinter.Toplevel.__init__(self, root)
        self.done = 0
        self.quit = 0
        self.root = root
        self.width = width
        self.height = height
        self.lastMove = (0,0)
        self.visible = 1
        self.title("PyrobotSimulator: KonaneWorld")
        self.mBar = Tkinter.Frame(self, relief=Tkinter.RAISED, borderwidth=2)
        self.mBar.pack(fill=Tkinter.X)
        #menubar = self.tk_menuBar(self.makeMenu(self.mBar,
        #                                        "Game",
        #                                        [["Done with move", self.playDone],
        #                                         ["Reset", self.initWorld],
        #                                         ]))
        button = Tkinter.Button(self.mBar, text="Done!", command=self.playDone)
        button.pack(side="left")
        button = Tkinter.Button(self.mBar, text="Reset!", command=self.initWorld)
        button.pack(side="right")
        self.canvas = Tkinter.Canvas(self,width=self.width,height=self.height,bg="white")
        self.canvas.pack()
        self.canvas.bind('<Button-1>', self.click)
        self.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.destroy)
        self.count = 0
        self.tag = "data-%d" % self.count
        self.properties = ["world", "whosMove", "board"]
        for i in self.properties:
            self.__dict__[i] = None
        self.movements = ["remove", "jump"]
        self.ports = [60000, 60001]
        self.initWorld()

    def makeMenu(self, bar, name, commands):
        """ Assumes self.menuButtons exists """
        menu = Tkinter.Menubutton(bar,text=name,underline=0)
        #self.menuButtons[name] = menu
        menu.pack(side=Tkinter.LEFT,padx="2m")
        menu.filemenu = Tkinter.Menu(menu)
        for cmd in commands:
            if cmd:
                menu.filemenu.add_command(label=cmd[0],command=cmd[1])
            else:
                menu.filemenu.add_separator()
        menu['menu'] = menu.filemenu
        return menu

    def playDone(self):
        self.whosMove = int(not self.whosMove)
        self.redraw()

    def click(self, event):
        posx = int((event.x / float(self.width)) * 8 + 1)
        posy = 8 - int((event.y / float(self.height)) * 8)
        if self.world[posx - 1][posy - 1] != '':
            print "remove(%d,%d) (or picking up for jump)" % (posx, posy)
            self.world[posx - 1][posy - 1] = ''
            self.lastMove = (posx, posy)
        elif self.lastMove == (posx, posy):
            print "Took back move at (%d,%d)" % (posx, posy)
            if posx % 2 == posy % 2:
                self.world[posx - 1][posy - 1] = 'O'
            else:
                self.world[posx - 1][posy - 1] = 'X'
        else:
            if posx % 2 == posy % 2:
                self.world[posx - 1][posy - 1] = 'O'
            else:
                self.world[posx - 1][posy - 1] = 'X'
            x1,y1 = self.lastMove
            x2,y2 = posx, posy
            if x1 == x2:
                self.world[x1-1][(y2+y1)/2 - 1] = ''
            else:
                self.world[(x1+x2)/2 - 1][y1-1] = ''
            self.lastMove = (x2, y2)
            print "jump(%d,%d,%d,%d)" % (x1, y1, posx, posy)
        self.redraw()

    def initWorld(self):
        self.whosMove = int(round(random.random()))
        self.world = [['' for y in range(8)] for x in range(8)]
        for x in range(0, 8):
            for y in range(0, 8):
                if x % 2 == y % 2:
                    self.world[x][y] = 'O'
                else:
                    self.world[x][y] = 'X'
        self.redraw()

    def process(self, request, sockname):
        retval = "error"
        if request.count("remove"):
            request = request.replace(")", "")
            remove, pos = request.split("(")
            x,y = map(int, pos.split(","))
            self.world[x-1][y-1] = ''
            retval = "ok"
            self.redraw()
        elif request.count("jump"):
            request = request.replace(")", "")
            jump, pos = request.split("(")
            places = map(int, pos.split(","))
            while len(places) >= 4:
                x1, y1, x2, y2 = places[:4]
                piece = self.world[x1-1][y1-1]
                self.world[x1-1][y1-1] = ''
                self.world[x2-1][y2-1] = piece
                if x1 == x2:
                    self.world[x1-1][(y2+y1)/2 - 1] = ''
                else:
                    self.world[(x1+x2)/2 - 1][y1-1] = ''
                places = places[2:]
            retval = "ok"
            self.redraw()
        elif request == "done":
            self.playDone()
            return "ok"
        elif request == "whosMove":
            retval = self.whosMove
        elif request.count('connectionNum'):
            connectionNum, port = request.split(":")
            retval = self.ports.index( int(port) )
        elif request == 'board':
            retval = self.world
        elif request == 'reset':
            self.initWorld()
            retval = "ok"
        elif request == 'end' or request == 'exit':
            retval = "ok"
            self.done = 1
        elif request == 'quit':
            retval = "ok"
            self.done = 1
            self.quit = 1
        elif request == 'properties':
            retval = self.properties
        elif request == 'movements':
            retval = self.movements
        elif request == 'supportedFeatures':
            retval = []
        elif request == 'builtinDevices':
            retval = []
        else:   # unknown command; returns "error"
            pass
        return pickle.dumps(retval)

    def redraw(self):
        oldtag = self.tag
        self.count = int(not self.count)
        self.tag = "data-%d" % self.count
        for x in range(8):
            for y in range(8):
                posx = x * (self.width / 8) + self.width/8/2
                posy = self.height - (self.height/8/2) - y * (self.height / 8)
                if ((self.whosMove == 0 and self.world[x][y] == "O") or
                    (self.whosMove == 1 and self.world[x][y] == "X")):
                    color = "red"
                else:
                    color = "gray"
                self.canvas.create_text(posx, posy, text = self.world[x][y], fill = color, tag = self.tag, font = ("times", 31))
        # ------------------------------------------------------------------------        
        self.canvas.create_line(  2,   2,   2, self.height, width = 2, fill = "black", tag = self.tag)
        self.canvas.create_line(  2,   2, self.width,   2, width = 2, fill = "black", tag = self.tag)
        for i in range(1,  8 + 1):
            self.canvas.create_line(i * self.width/8,   0, i * self.width/8, self.height, width = 2, fill = "black", tag = self.tag)
        for i in range(1,  8 + 1):
            self.canvas.create_line(  0, i * self.height/8, self.width, i * self.height/8, width = 2, fill = "black", tag = self.tag)
        for x in range(8):
            for y in range(8):
                self.canvas.create_text(x * self.width/8 + self.width/8/2,
                                        self.height - self.height/8/4 - (y * self.height/8),
                                        text="(%d,%d)" % (x+1,y+1), font=("times", 12), fill = "black", tag = self.tag)

        # ------------------------------------------------------------------------        
        self.canvas.delete(oldtag)
        
    def destroy(self):
        self.done = 1 # stop processing requests, if handing
        self.quit = 1 # stop accept/bind toplevel
        self.root.quit() # kill the gui

def INIT():
    root = Tkinter.Tk()
    root.withdraw()
    return GUI(root, 600, 600)
