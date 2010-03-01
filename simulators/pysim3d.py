"""
A Pure Python 3D Robot Simulator in Tkinter

(c) 2005, PyroRobotics.org. Licensed under the GNU GPL.
"""
import Tkinter, time, math, random
from pyrobot.geometry.matrix import *
from pyrobot.simulators.pysim import *

class Tk3DSimulator(TkSimulator):
    def __init__(self, dimensions, offsets, s, root = None, run = 1):
        TkSimulator.__init__(self, dimensions, offsets, s, root, run)
        self.centerx = self._width/2
        self.centery = self._height/2
        self.rotateMatrixWorld = translate(-self.centerx + self.offset_x,
                                           -self.centery, 0) * rotateYDeg(15) * rotateZDeg(15) * rotateXDeg(-60)
        self.matrix = Matrix() * scale(self.scale,self.scale,self.scale)
        self.primitives = []
        self.maxTrailSize = 40
    def click_b2_up(self, event):
        self.click_stop = event.x, event.y
        if self.click_stop == self.click_start:
            # center on this position:
            center = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2
            x_diff = self.click_stop[0] - center[0]
            y_diff = self.click_stop[1] - center[1]
        else: # move this much
            x_diff = self.click_start[0] - self.click_stop[0]
            y_diff = self.click_start[1] - self.click_stop[1]
        self.offset_x -= x_diff
        self.offset_y -= y_diff
        self.rotateMatrixWorld *= translate(-x_diff, y_diff, 0) 
        self.redraw()
    def simToggle(self, key):
        self.display[key] = (self.display[key] + 1) % 3
        self.redraw()
    def drawOval(self, x1, y1, x2, y2, **args):
        x1, y1, z1 = self.getPoint3D(x1, y1, 0)
        x2, y2, z2 = self.getPoint3D(x2, y2, 0)
        self.primitives.append(("oval", (z1 + z2)/2.0, x1, y1, x2, y2, args))
        return 0

    def drawLine(self, x0, y0, x1, y1, fill, tag, **args):
        return self.drawLine3D(x0, y0, 0, x1, y1, 0, fill = fill, tag = tag, **args)

    def drawLine3D(self, x0, y0, z0, x1, y1, z1, **args):
        VertsIn = [0, 0]
        VertsIn[0] = (self.matrix *
                      Vertex3D(x0, y0, z0 ))
        VertsIn[1] = (self.matrix *
                      Vertex3D(x1, y1, z1 ))
        self.primitives.append( ("line", (VertsIn[0].data[2]+VertsIn[1].data[2])/2.0,
                                 self.centerx + VertsIn[0].data[0],
                                 self.centery - VertsIn[0].data[1],
                                 self.centerx + VertsIn[1].data[0],
                                 self.centery - VertsIn[1].data[1],
                                 args))
        return 0

    def getPoint3Dxy(self, x, y, z):
        return self.getPoint3D(x, y, z)[0:2]
    def getPoint3Dz(self, x, y, z):
        return self.getPoint3D(x, y, z)[2]
    def getPoint3D(self, x, y, z):
        VertsIn = (self.matrix *
                   Vertex3D(x, y, z ))
        return self.centerx + VertsIn.data[0], self.centery - VertsIn.data[1], VertsIn.data[2]

    def drawPolygon(self, points, fill="", outline="black", tag = None, **args):
        if len(points[0]) == 3:
            all = map(lambda pt: self.getPoint3D(pt[0],pt[1],pt[2]), points)
        elif len(points[0]) == 2:
            all = map(lambda pt: self.getPoint3D(pt[0],pt[1],0), points)            
        xy = map(lambda pt: (pt[0], pt[1]), all)
        zs = map(lambda pt: pt[2], all)
        z = max(zs)
        args["fill"] = fill
        args["outline"] = outline
        args["tag"] = tag
        self.primitives.append( ("polygon", z, xy, args))
        return 0
    def rotateWorld(self, x, y, z):
        self.rotateMatrixWorld *= rotate(x, y, z)
        self.redraw()
    def translateWorld(self, x, y, z):
        self.rotateMatrixWorld *= translate(x, y, z)
        self.redraw()
    def step(self, run = 1):
        self.primitives = []
        TkSimulator.step(self, run)
        if self.display["wireframe"] < 2:
            self.redraw()
        self.drawObjects()

    def drawObjects(self):
        # sort them, based on Z buffer
        if self.display["wireframe"] < 2:
            self.primitives.sort(lambda x,y: cmp(x[1], y[1])) # 1st item is Z
            self.canvas.delete('all')
        for p in self.primitives:
            if p[0] == "oval":
                name, z, x1, y1, x2, y2, args = p
                self.canvas.create_oval(x1, y1, x2, y2, **args)
            elif p[0] == "line":
                name, z, x1, y1, x2, y2, args = p
                self.canvas.create_line(x1, y1, x2, y2, **args)
            elif p[0] == "polygon":
                name, z, points, args = p
                if self.display["wireframe"] == 2:
                    if "fill" in args:
                        if args["fill"] != "white":
                            args["outline"] = args["fill"]
                    else:
                        args["outline"] = "black"
                    args["fill"] = ""
                elif self.display["wireframe"] == 1:
                    if "fill" in args and args["fill"] == "white":
                        args["fill"] = ""
                self.canvas.create_polygon(points, **args)
            else:
                print "need renderer for type:", p[0]
        
    def redraw(self):
        if self.display["wireframe"] == 2:
            self.primitives = []
        matrix = (
            self.rotateMatrixWorld *
            scale(self.scale,self.scale,self.scale)
            )
        self.matrix = matrix
        
        for segment in self.world:
            (x1, y1), (x2, y2) = segment.start, segment.end
            id = self.drawLine3D(x1, y1, 0, x2, y2, 0, tag="line")
            segment.id = id

        for shape in self.shapes:
            if shape[0] == "box":
                name, ulx, uly, lrx, lry, color = shape
                # wall 3:
                points = []
                points.append((lrx, lry, 0))
                points.append((lrx, uly, 0))
                points.append((lrx, uly, 1))
                points.append((lrx, lry, 1))
                self.drawPolygon(points, tag="line", fill=color, outline="black")
                # wall 4:
                points = []
                points.append((lrx, lry, 0))
                points.append((ulx, lry, 0))
                points.append((ulx, lry, 1))
                points.append((lrx, lry, 1))
                self.drawPolygon(points, tag="line", fill=color, outline="black")
                # wall 2:
                points = []
                points.append((ulx, uly, 0))
                points.append((lrx, uly, 0))
                points.append((lrx, uly, 1))
                points.append((ulx, uly, 1))
                self.drawPolygon(points, tag="line", fill=color, outline="black")
                # wall 1:
                points = []
                points.append((ulx, uly, 0))
                points.append((ulx, lry, 0))
                points.append((ulx, lry, 1))
                points.append((ulx, uly, 1))
                self.drawPolygon(points, tag="line", fill=color, outline="black")

        for light in self.lights:
            if light.type != "fixed": continue # skip those on robots
            x, y, brightness, color = light.x, light.y, light.brightness, light.color
            self.drawOval((x - brightness), (y - brightness),
                          (x + brightness), (y + brightness),
                          tag="line", fill=color, outline="orange")
        i = 0
        for path in self.trail:
            if self.robots[i].subscribed and self.robots[i].display["trail"] == 1:
                if path[self.trailStart] != None:
                    lastX, lastY, lastA = path[self.trailStart]
                    color = self.robots[i].color
                    for p in range(self.trailStart, self.trailStart + self.maxTrailSize):
                        xya = path[p % self.maxTrailSize]
                        if xya == None: break
                        x, y = xya[0], xya[1]
                        self.drawLine(lastX, lastY, x, y, fill=color, tag="trail")
                        lastX, lastY = x, y
            i += 1
        if self.display["wireframe"] == 2:
            self.canvas.delete('all')
        self.drawObjects()
        for robot in self.robots:
            robot._last_pose = (-1, -1, -1)
    

if __name__ == "__main__":
    sim = Tk3DSimulator((446,491),(21,451),80.517190)
    sim.addBox(0, 0, 5, 5)
    sim.addBox(0, 4, 1, 5, "blue", wallcolor="blue")
    sim.addBox(2.5, 0, 2.6, 2.5, "green", wallcolor="green")
    sim.addBox(2.5, 2.5, 3.9, 2.6, "green", wallcolor="green")
    sim.mainloop()

