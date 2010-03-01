# -------------------------------------------------------
# Simple Map
# -------------------------------------------------------

import Tkinter

class Map(Tkinter.Tk): 
    COLORS = ['blue', 'red', 'tan', 'yellow', 'orange', 'black',
              'azure', 'beige', 'brown', 'coral', 'gold', 'ivory',
              'moccasin', 'navy', 'salmon', 'tan', 'ivory']
    def __init__(self, robot, name):
        Tkinter.Tk.__init__(self)
        self.robot = robot
        self.name = name
        self.title("Map: %s" % name)
        self.canvas = Tkinter.Canvas(self,width=400,height=400)
        self.canvas.pack()
        self.update_idletasks()
        self.protocol('WM_DELETE_WINDOW',self.close)
    def close(self):
        self.withdraw()
        self.update_idletasks()
        self.destroy()
    def redraw(self, options = {}):
        # do something to draw yourself
        self.update_idletasks()

if __name__ == '__main__':
    map = Map(0, '2D Map')
    map.mainloop()
