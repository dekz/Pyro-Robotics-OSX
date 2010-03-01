import Tkinter

class Joystick(Tkinter.Toplevel):

   def __init__(self, parent = None, hasZ = 0):
      Tkinter.Toplevel.__init__(self, parent)
      self.debug = 0
      self.wm_title('Joystick')
      self.protocol('WM_DELETE_WINDOW',self.destroy)
      self.springBack = 0
      self.hasZ = hasZ
      self.mBar = Tkinter.Frame(self, relief=Tkinter.RAISED, borderwidth=2)
      self.mBar.pack(fill=Tkinter.X)
      self.goButtons = {}
      self.menuButtons = {}
      self.heightScaleValue = 0
      menu = [('Options',[['Toggle spring-back to center', self.toggleSpringBack],
                          ]),
              ]
      for entry in menu:
         self.mBar.tk_menuBar(self.makeMenu(self.mBar, entry[0], entry[1]))
      if self.hasZ: # has a 3rd dimension, height
         self.mainFrame = Tkinter.Frame(self)
         self.topFrame = Tkinter.Frame(self.mainFrame)
         self.rightFrame = Tkinter.Frame(self.topFrame)
         ticks = 10
         resolution = .1
         label = Tkinter.Label(self.rightFrame, text = "Height")
         label.pack(side = "top")
         self.heightScale = Tkinter.Scale(self.rightFrame, orient=Tkinter.VERTICAL,
                                          length = 220, from_=1, to=-1,
                                          tickinterval=ticks, command = self.setHeightScale,
                                          resolution = resolution)
         self.heightScale.set(0)
         self.heightScale.pack(side = 'bottom', expand = "yes", anchor = "e", fill = 'y')
         self.rightFrame.pack(side='right')
         self.topFrame.pack()
         self.frame = Tkinter.Frame(self.topFrame)
      else:
         self.mainFrame = Tkinter.Frame(self)
         self.frame = Tkinter.Frame(self.mainFrame)
      label = Tkinter.Label(self.frame, text = "Forward")
      label.pack(side = "top")
      label = Tkinter.Label(self.frame, text = "Reverse")
      label.pack(side = "bottom")
      label = Tkinter.Label(self.frame, text = "Turn\nLeft")
      label.pack(side = "left")
      label = Tkinter.Label(self.frame, text = "Turn\nRight")
      label.pack(side = "right")
      self.canvas = Tkinter.Canvas(self.frame,
                                   width = 220,
                                   height = 220,
                                   bg = 'white')
      self.initHandlers()
      self.canvas.pack(side=Tkinter.BOTTOM)
      self.circle_dim = (10, 10, 210, 210) #x0, y0, x1, y1
      self.circle = self.canvas.create_oval(self.circle_dim, fill = 'white')
      self.canvas.create_oval(105, 105, 115, 115, fill='black')
      self.frame.pack(side='left')
      self.goButtons["Stop"] = Tkinter.Button(self,text="Stop",command=self.stop)
      self.goButtons["Stop"].pack(side=Tkinter.BOTTOM,padx=2,pady=2,fill=Tkinter.X, expand = "yes", anchor="s")
      self.mainFrame.pack()
      self.translate = 0.0
      self.rotate = 0.0
      self.threshold = 0.10
   def toggleSpringBack(self):
      self.springBack = not self.springBack
   def makeMenu(self, bar, name, commands):
      """ Assumes self.menuButtons exists """
      menu = Tkinter.Menubutton(bar,text=name,underline=0)
      self.menuButtons[name] = menu
      menu.pack(side=Tkinter.LEFT,padx="2m")
      menu.filemenu = Tkinter.Menu(menu)
      for cmd in commands:
         if cmd:
            menu.filemenu.add_command(label=cmd[0],command=cmd[1])
         else:
            menu.filemenu.add_separator()
      menu['menu'] = menu.filemenu
      return menu

   def setHeightScale(self, event = None):
      self.heightScaleValue = self.heightScale.get()
      if self.hasZ:
         self.move(self.translate, self.rotate, self.heightScaleValue)
      else:
         self.move(self.translate, self.rotate)

   def initHandlers(self):
      self.canvas.bind("<ButtonRelease-1>", self.canvas_clicked_up)
      self.canvas.bind("<Button-1>", self.canvas_clicked_down)
      self.canvas.bind("<B1-Motion>", self.canvas_moved)

   def getValue(self, event = None):
      return self.translate, self.rotate

   def _move(self, translate, rotate):
      self.translate = translate
      self.rotate = rotate
      if self.hasZ:
         self.move(self.translate, self.rotate, self.heightScaleValue)
      else:
         self.move(self.translate, self.rotate)

   def move(self, x, y, z = 0):
      if self.debug:
         print x, y, z

   def canvas_clicked_up(self, event):
      if not self.springBack:
         self.canvas.delete("lines")
         self._move(0.0, 0.0)

   def drawArrows(self, x, y, trans, rotate):
      if trans == 0:
         self.canvas.create_line(110, 110, 110, y, width=3, fill="blue", tag="lines")
      else:
         self.canvas.create_line(110, 110, 110, y, width=3, fill="blue", tag="lines", arrowshape = (10, 10, 3), arrow = "last")
      if rotate == 0:
         self.canvas.create_line(110, 110, x, 110, width=3, fill="red", tag="lines")
      else:
         self.canvas.create_line(110, 110, x, 110, width=3, fill="red", tag="lines", arrowshape = (10, 10, 3), arrow = "last")

   def canvas_clicked_down(self, event):
      if self.in_circle(event.x, event.y):
         self.canvas.delete("lines")
         trans, rotate = self.calc_tr(event.x, event.y)
         self.drawArrows(event.x, event.y, trans, rotate)
         self._move(trans, rotate)

   def canvas_moved(self, event):
      if self.in_circle(event.x, event.y):
         self.canvas.delete("lines")
         trans, rotate = self.calc_tr(event.x, event.y)
         self.drawArrows(event.x, event.y, trans, rotate)         
         self._move(trans, rotate)

   def stop(self, event = None):
      if self.hasZ:
         self.heightScale.set(0)
      self.canvas.delete("lines")
      self._move(0.0, 0.0)

   def in_circle(self, x, y):
      return 1
##       r2 = ((self.circle_dim[2] - self.circle_dim[0])/2)**2
           
##       center = ((self.circle_dim[2] + self.circle_dim[0])/2,
##                 (self.circle_dim[3] + self.circle_dim[1])/2)
##       #x in?
##       dist2 = (center[0] - x)**2 + (center[1] - y)**2
##       if (dist2 < r2):
##          return 1
##       else:
##          return 0

   def calc_tr(self, x, y):
      #right is negative
      center = ((self.circle_dim[2] + self.circle_dim[0])/2,
                (self.circle_dim[3] + self.circle_dim[1])/2)
      rot = float(center[0] - x) / float(center[0] - self.circle_dim[0])
      trans = float(center[1] - y) / float(center[1] - self.circle_dim[1])
      if abs(rot) < self.threshold:
         rot = 0.0
      if abs(trans) < self.threshold:
         trans = 0.0
      return (trans, rot)

if __name__ == '__main__':
   app = Tkinter.Tk()
   app.withdraw()
   joystick = Joystick(parent = app, hasZ = 1)
   #app.mainloop()
