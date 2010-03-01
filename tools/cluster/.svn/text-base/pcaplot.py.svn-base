import Gnuplot

class PCAPlot:
    def __init__(self, eigenfile, namefile = None, debug = 0,
                 dimensions = 2, title = None, datatitle = None,
                 showpoints = 1, showlabels = 1, components = [0, 1, 2]):
        self.gp = Gnuplot.Gnuplot(debug = debug)
        self.dimensions = dimensions
        self.showpoints = showpoints
        self.showlabels = showlabels
        self.components = components
        # read in eigenvalues, names
        efp = open(eigenfile, "r")
        if namefile:
            nfp = open(namefile, "r")
        else:
            nfp = None
        eline = efp.readline()
        if nfp:
            nline = nfp.readline()
        else:
            nline = eline.split()[-1]
        dataset = []
        while eline:
            eline = eline.strip()
            if nfp:
                label = nline.strip()
            else:
                label = eline.split()[-1]
            data = eline.split(" ")
            if dimensions == 2:
                if label and showlabels:
                    self.gp('set label "%s" at %f,%f' %
                            (label, float(data[self.components[0]]), float(data[self.components[1]])))
                dataset.append( (float(data[self.components[0]]), float(data[self.components[1]])))
            elif dimensions == 3:
                if label and showlabels:
                    self.gp('set label "%s" at %f,%f,%f' %
                            (label, float(data[self.components[0]]),
                             float(data[self.components[1]]), float(data[self.components[2]])))
                dataset.append( (float(data[self.components[0]]), float(data[self.components[1]]),
                                     float(data[self.components[2]])))
            else:
                raise "DimensionError", \
                      "cannot handle dimensions of %d" % dimensions
            eline = efp.readline()
            if nfp:
                nline = nfp.readline()
        efp.close()
        if nfp:
            nfp.close()
        self.data = Gnuplot.Data(dataset)
        if showpoints:
            self.gp('set data style points')
        else:
            self.gp('set data style dots')
        self.gp.title(title)
        self.data.set_option(title = datatitle)

    def plot(self):
        if self.dimensions == 2:
            self.gp.plot(self.data)
        elif self.dimensions == 3:
            self.gp.splot(self.data)
        else:
            raise "DimensionError", \
                  "cannot handle dimensions of %d" % dimensions

    def replot(self):
        self.gp.replot()

    def hardcopy(self, output):
        self.gp.hardcopy(output)

if __name__ == '__main__':
    pca = PCAPlot("data.pca", "names", title = "Sample PCA Plot", showpoints = 0)
    pca.plot()
    raw_input()
    pca.data.set_option(title = "Data name")
    pca.replot()
    pca.hardcopy("/tmp/output.ps")
    raw_input()
