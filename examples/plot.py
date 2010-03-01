import sys
import Tkinter

def cleanup(line):
    line = line.replace(",", "")
    line = line.replace("(", "")
    line = line.replace("=>", "")
    line = line.replace(")", "")
    line = line.replace(";", "")
    return map(float, line.strip().split())

def cleanup2(line):
    line = line.replace(",", "")
    line = line.replace("=>", "")
    line = line.replace(";", "")
    return line.strip().split()

class Display(Tkinter.Toplevel):
    def __init__(self, root = None):
        if not root:
            root = Tkinter.Tk()
            root.withdraw()
        Tkinter.Toplevel.__init__(self, root)
        self.protocol('WM_DELETE_WINDOW',self.destroy)
        self.title("Two Spirals Results")
        self.frame = Tkinter.Frame(self)
        self.canvas = Tkinter.Canvas(self.frame, width = 500, height = 500)
        self.canvas.bind("<Button-1>", self.click)
        self.frame.pack()
        self.canvas.pack()
    def destroy(self):
        Tkinter.Toplevel.destroy(self)
        sys.exit()
    def click(self, event):
        pass
    def drawLine(self, points):
        lastx, lasty = None, None
        for (x,y) in points:
            if (lastx, lasty) == (None, None):
                lastx, lasty = x, y
            else:
                self.canvas.create_line(lastx, lasty, x, y)
                lastx, lasty = x, y
    def drawPixel(self, x, y, color):
        resolution = .1
        maxRadius = 6.5
        area = 500 * resolution
        px = ((x / maxRadius) + 1.0)/2 * 500
        py = ((y / maxRadius) + 1.0)/2 * 500
        pc = int((color + .5) * 255)
        pc = "#%02x%02x%02x" % (pc, pc, pc)
        self.canvas.create_rectangle(px, py, px + area, py + area,
                                     fill=pc, width=0)
    def drawSymbol(self, x, y, sym):
        resolution = .1
        maxRadius = 6.5
        area = 500 * resolution
        px = ((x / maxRadius) + 1.0)/2 * 500
        py = ((y / maxRadius) + 1.0)/2 * 500
        if sym == "+":
            color = "green"
        else:
            color = "red"
        self.canvas.create_oval(px, py,
                                px + area/10, py + area/10,
                                fill=color, width= 1)

if __name__ == "__main__":
    trainfile = sys.argv[1]
    testfile = sys.argv[2]
    fp = open(testfile, "r")
    display = Display()
    for line in fp:
        data = cleanup(line)
        display.drawPixel(data[0], data[1], data[3])
    fp = open(trainfile, "r")
    process = 0
    line = fp.readline().strip()
    while 1:
        if "$TRAIN" in line[:6]:
            line = fp.readline().strip() # blank line
            process = 1
        elif process:
            if not line:
                break
            else:
               data = cleanup2(line)
               display.drawSymbol(float(data[0]), float(data[1]), data[2])
        line = fp.readline().strip()
    display.mainloop()
