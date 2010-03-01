from pyrobot.brain.psom import *
from pyrobot.brain.psom.visvector import *
from pyrobot import pyrobotdir
from Tkinter import *

ACT_MAX   = 5
GRAY_STEP = 20

class VisPsom(psom):
   """
   A vizualized psom class.
   Takes all the same arguments as the psom class, with the following added
   keyword arguments:

   vis_radius:  The radius (in pixels) of the som cells.  Defaults to 15

   vis_padding: The amount of space (in pixels) on each side of each cell.
      Defaults to 2

   vis_vectortype:  The type of VisVector vizualier to use to display the
      model vectors.  Defaults to 'generic'.  See visvector.py.
   """

   def __init__(self, *args, **keys):
      self.last_x = 0
      self.last_y = 0
      self.fontsize = 8 # starting font size
      #get Vis-specific keyword arguements out
      if 'vis_radius' in keys.keys():
         self.vis_radius = keys['vis_radius']
         del keys['vis_radius']
      else:
         self.vis_radius = 15
      if 'vis_padding' in keys.keys():
         self.vis_padding = keys['vis_padding']
         del keys['vis_padding']
      else:
         self.vis_padding = 2
      if 'vis_vectortype' in keys.keys():
         self.vectortype = keys['vis_vectortype']
         del keys['vis_vectortype']
      else:
         self.vectortype = "Generic"
      if 'title' in keys.keys():
         title = keys['title']
         del keys['title']
      else:
         title = "VisPsom"
      if 'opts' in keys.keys():
         self.opts = keys['opts']
         del keys['opts']
      else:
         self.opts = None

      psom.__init__(self, *args, **keys)
      self.app = Tk()
      self.app.wm_state('withdrawn')
      self.win = Toplevel()
      self.win.wm_title(title)

      self.cellwidth = (self.vis_padding + self.vis_radius) * 2
      #offset to set off the rows for a hexagonal topology
      if self.topol == 'hexa':
         self.offset = self.cellwidth/2
      else: #topol = 'rect'
         self.offset = 0
      self.width = self.xdim*(2*self.vis_radius+2*self.vis_padding) + self.offset
      self.height = self.ydim*(2*self.vis_radius+2*self.vis_padding)
      self.canvas = Canvas(self.win,
                           width=self.width,
                           height=self.height,
                           bg='white')
      self.canvas.bind("<ButtonRelease-1>", self.canvas_clicked_up)
      self.canvas.bind("<Button-1>", self.canvas_clicked_down)
      self.win.bind("<Configure>", self.changeSize)
      self.canvas.pack(side=TOP, expand="yes", fill="both")
      self.lastMapped = (-1,-1)
      self.history = {}
      self.drawCells(init=1)
      # Set labels
      for y in range(self.ydim):
         for x in range(self.xdim):
            self._setcell_label(x, y)

      # menu bar with File and Show options
      menuBar = Menu(self.win)
      self.win.config(menu=menuBar)
      FileBtn = Menu(menuBar)
      menuBar.add_cascade(label='File', menu=FileBtn)
      FileBtn.add_command(label='Exit', command=sys.exit)

      ShowBtn = Menu(menuBar)
      menuBar.add_cascade(label='Show', menu=ShowBtn)
      ShowBtn.add_radiobutton(label='Train Count',
                              command=self.show_train_count)
      ShowBtn.add_radiobutton(label='Map Count',
                              command=self.show_map_count)
      ShowBtn.add_radiobutton(label='Labels',
                              command=self.show_labels)
      # show train count by default
      ShowBtn.invoke(ShowBtn.index('Train Count')) 
      # end menu bar
      #print self.width, self.height
      self.win.aspect(self.width, self.height + 32, self.width, self.height + 32)

   def drawCells(self, init=0):
      # draw connection lines first:
      if init:
         self.cells = []
      self.cellhash = {}
      self.canvas.delete("cell")
      for y in range(self.ydim):
         for x in range(self.xdim):
            x0 = (self.cellwidth * x) + self.vis_padding + (self.offset * (y % 2))
            y0 = (self.cellwidth * y) + self.vis_padding
            x1 = x0 + (self.vis_radius * 2)
            y1 = y0 + (self.vis_radius * 2)
            #    1    2
            #     \  /
            #   0 -  - 3
            #     /  \
            #    5    4
            connection = [1] * 6
            if y == 0:               # top row
               connection[1] = 0; connection[2] = 0
            if x == 0:               # left row
               connection[0] = 0;
            if y % 2 == 0 and x == 0:
               connection[1] = 0
            if y % 2 == 1 and x == self.xdim - 1:
               connection[2] = 0
            if connection[0]: self.canvas.create_line(x0 + self.cellwidth / 2,
                                                      y0 + self.cellwidth / 2,
                                                      x0 - self.cellwidth / 2,
                                                      y0 + self.cellwidth / 2,
                                                      tags = 'cell')
            if connection[1]: self.canvas.create_line(x0 + self.cellwidth / 2,
                                                      y0 + self.cellwidth / 2,
                                                      x0,
                                                      y0 - self.cellwidth / 2,
                                                      tags = 'cell')
            if connection[2]: self.canvas.create_line(x0 + self.cellwidth / 2,
                                                      y0 + self.cellwidth / 2,
                                                      x0 + self.cellwidth,
                                                      y0 - self.cellwidth / 2,
                                                      tags = 'cell')

      for y in range(self.ydim):
         if init:
            self.cells.append([])
         for x in range(self.xdim):
            x0 = (self.cellwidth * x) + self.vis_padding + (self.offset * (y % 2))
            y0 = (self.cellwidth * y) + self.vis_padding
            x1 = x0 + (self.vis_radius * 2)
            y1 = y0 + (self.vis_radius * 2)
            cell = self.canvas.create_oval(x0, y0, x1, y1, fill='white',
                                           tags = 'cell')
            center = ((x0 + x1)/2, (y0 + y1)/2)
            
            # display settings for train count
            traintext = self.canvas.create_text(center[0], center[1],
                                                text = "",
                                                fill = 'red',
                                                tags = 'traincount')
            # display settings for map count
            maptext = self.canvas.create_text(center[0], center[1],
                                              text = "",
                                              fill = 'blue',
                                              tags = 'mapcount')
            # display settings for label
            labeltext = self.canvas.create_text(center[0], center[1],
                                                text = "",
                                                fill = 'purple',
                                                tags = 'label')
            # dictionary associated with each cell
            pt = point(x, y)
            if init:
               self.cells[y].append({"cell": cell,
                                     "traintext": traintext,
                                     "maptext": maptext,
                                     "labeltext": labeltext})
            else:
               self.cells[y][x]["cell"] = cell
               px,py = map(int, self.canvas.coords(self.cells[y][x]["traintext"]))
               self.canvas.move(self.cells[y][x]["traintext"],center[0] - px, center[1] - py)
               self.canvas.move(self.cells[y][x]["maptext"],center[0] - px, center[1] - py)
               self.canvas.move(self.cells[y][x]["labeltext"],center[0] - px, center[1] - py)
               self.fontsize = self.cellwidth / 8
               self.canvas.itemconfigure(self.cells[y][x]["traintext"], font=(('MS', 'Sans', 'Serif'), self.fontsize))
               self.canvas.itemconfigure(self.cells[y][x]["maptext"], font=(('MS', 'Sans', 'Serif'), self.fontsize))
               self.canvas.itemconfigure(self.cells[y][x]["labeltext"], font=(('MS', 'Sans', 'Serif'), self.fontsize))

            self.cellhash[cell] = (x, y)

      self.canvas.tag_lower('cell', 'traincount')
      self.canvas.tag_lower('mapcount', 'cell')
      self.canvas.tag_lower('label', 'cell')

   def changeSize(self, event):
      #print self.width, self.height
      #print self.vis_padding, self.vis_radius
      #print self.offset, self.cellwidth
      #return
      self.vis_padding = 2
      self.width = self.win.winfo_width() - 2
      self.vis_radius = ((self.width - self.offset) / (2 * self.xdim)) - self.vis_padding
      self.cellwidth = (self.vis_padding + self.vis_radius) * 2
      if self.topol == 'hexa':
         self.offset = self.cellwidth/2
      else: #topol = 'rect'
         self.offset = 0
      self.height = self.ydim*(2*self.vis_radius+2*self.vis_padding)
      self.drawCells()

   def destroy(self):
      self.win.destroy()
      
   def canvas_clicked_up(self, event):
      celllist = self.canvas.find_overlapping(event.x, event.y,
                                              event.x, event.y)
      cell = None
      for item in celllist:
         if item in self.cellhash.keys():
            cell = item
            break
      
      if cell:
         x, y = self.cellhash[cell]
         vec = self.get_model_vector(point(x,y))
         
         label = self.get_model_vector(point(x,y)).get_label_asString()
         if label == "": label = "No Label"
            
         if x == self.last_x and y == self.last_y:
            visclass = getVisVectorByName(self.vectortype)
            if self.opts: # override defaults
               visclass(vec, title="(%d,%d):%s" % (x, y, label),
                        opts = self.opts)
            else:
               visclass(vec, title="(%d,%d):%s" % (x, y, label))
         else:
            # show difference
            vec2 = self.get_model_vector(point(self.last_x, self.last_y))
            diffvec = []
            for v in range(len(vec2)):
               diffvec.append( vec[v] - vec2[v] )
            myvector = vector( diffvec )
            visclass = getVisVectorByName(self.vectortype)
            if self.opts:
               visclass(myvector, title="(%d,%d) diff (%d,%d)"
                        % (x, y, self.last_x, self.last_y), opts = self.opts)
            else:
               visclass(myvector, title="(%d,%d) diff (%d,%d)"
                        % (x, y, self.last_x, self.last_y))

   def canvas_clicked_down(self, event):
      celllist = self.canvas.find_overlapping(event.x, event.y,
                                              event.x, event.y)
      cell = None
      for item in celllist:
         if item in self.cellhash.keys():
            cell = item
            break

      if cell:
         self.last_x, self.last_y = self.cellhash[cell]

   def _setcell_color(self, x, y, color, level='unset'):
      if level == 'unset':
         self.canvas.itemconfigure(self.cells[y][x]['cell'],
                                   fill=color)
      else:
         self.canvas.itemconfigure(self.cells[y][x]['cell'],
                                   fill=color + str(level))

   def _train_updatefill(self, curr_pt):
      self.history[curr_pt] = ACT_MAX
      
      for pt in self.history.keys():
         act = self.history[pt]
         self._setcell_color(pt[0], pt[1],
                             'gray', (ACT_MAX - act) * GRAY_STEP)
         #decrease activation by 1
         if act == 0:
            del self.history[pt]
         else:
            self.history[pt] -= 1
   
   def _map_updatefill(self, curr_pt):
      if self.lastMapped[0] != -1 and self.lastMapped[1] != -1:
         self._setcell_color(self.lastMapped[0], self.lastMapped[1],
                             'gray', 100)
      self._setcell_color(curr_pt[0], curr_pt[1], 'green')

   def _setcell_count(self, x, y, count, which):
      """
      Updates the hit counter of a cell.  Counters are displayed
      only if their values are > 0.
      """
      if count != 0:
         self.canvas.itemconfigure(self.cells[y][x][which+"text"],
                                   text=str(count))
                                
   def _setcell_label(self, x, y):
      """
      Given x, y coordinates, this function labels the corresponding cell
      """
      label = self.get_model_vector(point(x,y)).get_label_asString()
      self.canvas.itemconfigure(self.cells[y][x]['labeltext'],
                                text = label,
                                font=(('MS', 'Sans', 'Serif'), self.fontsize))

   def clearfill(self):
      """
      Clears the markers, the count printout, and resets the count to 0
      for all cells.
      """
      for y in range(self.ydim):
         for x in range(self.xdim):
            self._setcell_color(x, y, 100)
            #self.cells[x][y]['count'] = 0
      self.canvas.delete('traincount')
      self.canvas.delete('mapcount')
      self.update()
   
   def map(self, vector):
      """
      Maps the given vector, updates the fill, counter, label (if any)
      of the node that was mapped.  Returns the winning model vector.
      """
      model = psom.map(self, vector)
      pt    = model.point.x, model.point.y

      # update cell fill
      self._map_updatefill(pt)
      # update counter
      self._setcell_count(pt[0], pt[1],
                          self.get_reg_counter(model.point, 'map'),
                          'map')
      self._setcell_label(pt[0], pt[1])
      self.lastMapped = pt
      self.update()
      return model

   def train(self, vector):
      """
      Trains the SOM on the given vector.  Updates the fill and counter
      of the node that was mapped to.  Returns the winning model vector.
      """
      model = psom.train(self, vector)
      pt   = model.point.x, model.point.y

      # update cell fill
      self._train_updatefill(pt)
      # update counter
      self._setcell_count(pt[0], pt[1],
                          self.get_reg_counter(model.point, 'train'),
                          'train')
      self.update()
      return model
   
   def train_from_dataset(self, dataset, mode='cyclic'):
      """
      Trains the SOM on the given dataset in either 'cyclic' or 'rand'
      mode.  See train_from_dataset() in __init__.py for more info.
      Updates the fill of the last mapped node and the counters of
      all nodes that were mapped during training.  Returns the model
      vector of the last node that was mapped.
      """
      model = psom.train_from_dataset(self, dataset, mode)
      pt = model.point.x, model.point.y

      # update cell fill for last point
      self._train_updatefill(pt)
      # update counters
      for x in range(self.xdim):
         for y in range(self.ydim):
            self._setcell_count(x, y,
                                self.get_reg_counter(point(x,y), 'train'),
                                'train')
      self.update()
      return model

   def map_from_dataset(self, dataset):
      """
      Maps the dataset to the SOM.  See map_from_dataset() in
      __init__.py for more info.  Updates the fill of the last mapped
      node and the counters of all nodes that were mapped.  Returns
      the model vector of the last node that was mapped to.
      """
      model = psom.map_from_dataset(self, dataset)
      pt = model.point.x, model.point.y

      # update cell fill for last point
      self._map_updatefill(pt)
      # update counters
      for x in range(self.xdim):
         for y in range(self.ydim):
            self._setcell_count(x, y,
                           self.get_reg_counter(point(x,y), 'map'),
                           'map')
            self._setcell_label(x, y)
      
      self.lastMapped = pt
      self.update()
      return model
      
   def add_label(self, x, y, label=[]):
      """
      Given a label list, this function adds the label to the cell/model vector
      at the specified x,y position.  Previous label associations are preserved. 
      """
      vec = self.get_model_vector(point(x, y))
      vec.add_label(label)
      self._setcell_label(x, y)

   def clear_label(self, x, y):
      """
      Removes all labels associated with the cell/model vector at the given
      x,y position.
      """
      vec = self.get_model_vector(point(x, y))
      vec.clear_label()
      self._setcell_label(x, y)
      
   def update(self):
      while self.win.tk.dooneevent(2): pass

   def show_train_count(self):
      self.canvas.tag_raise('traincount', 'cell')
      self.canvas.tag_lower('mapcount', 'cell')
      self.canvas.tag_lower('label', 'cell')
      self.canvas.update()

   def show_map_count(self):
      self.canvas.tag_raise('mapcount', 'cell')
      self.canvas.tag_lower('traincount', 'cell')
      self.canvas.tag_lower('label', 'cell')
      self.canvas.update()

   def show_labels(self):
      self.canvas.tag_raise('label', 'cell')
      self.canvas.tag_lower('traincount', 'cell')
      self.canvas.tag_lower('mapcount', 'cell')
      self.canvas.update()

   
if __name__ == "__main__":
   def pause():
      print "Press [Enter] to continue...",
      raw_input();
   #mysom = VisPsom(file='ex.cod', vis_vectortype="Hinton")
   mysom = VisPsom(file=pyrobotdir() + '/brain/psom/ex.cod')
   mydataset = dataset(file=pyrobotdir() + '/brain/psom/ex.dat')
   mysom.init_training(0.02,4.0,5005)
   print "---> Begin training from dataset..."
   mysom.timing_start()
   mysom.train_from_dataset(mydataset)
   mysom.timing_stop()
   ttime = mysom.get_training_time()
   print "---> 5000 Training steps complete: %s seconds" % ttime
   pause()
   print "---> Training..."
   mysom.train(vector([30.0, 20.0, -.3, -.8, 400.0]))
   pause()
   print "---> Training..."
   mysom.train(vector([14.0, 10.0, .3, -.8, 400.0]))
   pause()
   print "---> Training..."
   mysom.train(vector([24.48, 29.45, -0.54, 0.16, 402.9]))
   pause()
   print "---> Training..."
   mysom.train(vector([27.0, 35.69, -0.45, -1.7, 401.7]))
   pause()
   print "---> Training..."
   mysom.train(vector([17.7, 18.89, -1.24, -0.84, 400.10]))
   pause()
   print "---> Mapping..."
   mysom.map(vector([10.0, 30.0, -.3, .8, 375.0]))
   pause()
   print "---> Mapping..."
   mysom.map(vector([30.0, 20.0, -.3, -.8, 400.0]))
   pause()
   print "---> Mapping..."
   mysom.map(vector([30.0, 20.0, -.3, -.8, 400.0]))
   pause()
   print "---> Mapping..."
   mysom.map(vector([30.0, 20.0, -.3, -.8, 400.0]))
   pause()
   print "---> Mapping..."
   mysom.map(vector([30.0, 20.0, -.3, -.8, 400.0]))
   pause()
   print "---> Mapping..."
   mysom.map(vector([30.0, 20.0, -.3, -.8, 400.0]))
   pause()
   print "---> Mapping..."
   mysom.map(vector([30.0, 20.0, -.3, -.8, 400.0]))

   print "---> Adding 1 to the label at 0,0..."
   pause()
   mysom.add_label(0, 0, [1])

   print "---> Adding 'zc' to the label at 5,5..."
   pause()
   mysom.add_label(5, 5, ['zc'])

   print "---> Clearing label '' at 0,1..."
   pause()
   mysom.clear_label(0, 1)

   print "---> Clearing label 'B' at 1,0..."
   pause()
   mysom.clear_label(1, 0)

   print "---> Displaying dataset"
   pause()
   mysom.display()

   #print "---> DONE. Please close window (use exit menu option)."
   #mysom.win.mainloop()

   #mysom.destroy()

