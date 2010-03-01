import Gnuplot

class TreePlot:
    def __init__(self, filename, title = None, datatitle = None,
                 debug = 0):
        self.gp = Gnuplot.Gnuplot(debug = debug)
        fp = open(filename, "r")
        line = fp.readline()
        while line:
            line = line.strip()
            if line.find('"') >= 0:
                data = line.split(" ")
                label = line[line.find('"')+2:-1]
                self.gp('set label "%s" at %f,%f' %
                        (label, float(data[0]), float(data[1])))
            line = fp.readline()
        fp.close()
        self.file = Gnuplot.File(filename)
        self.gp('set data style lines')
        self.gp.title(title)
        self.file.set_option(title = datatitle)

    def plot(self):
        self.gp.plot(self.file)

    def replot(self):
        self.gp.replot()

    def hardcopy(self, output):
        self.gp.hardcopy(output)

if __name__ == '__main__':
    tree = TreePlot("data.tree", title = "Sample Tree Data")
    tree.plot()
    raw_input()
    tree.file.set_option(title = "Data Title")
    tree.replot()
    tree.hardcopy("/tmp/output.ps")
    raw_input()
