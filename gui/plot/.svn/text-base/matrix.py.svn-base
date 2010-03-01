# -------------------------------------------------------
# Matrix Plot (Images)
# -------------------------------------------------------

from Tkinter import *
import os

class Matrix: # Plot
   def __init__(self, cols = 1, rows = 1, title = None, width = 275,
                height = 275, maxvalue = 255.0, data = None, type = 'grid'):
      """
      Arguments:

      """
      self.type = type
      self.app = Tk()
      self.app.wm_state('withdrawn')
      self.win = Toplevel()
      self.maxvalue=maxvalue
      self.width=width
      self.height = height
      self.cols = cols
      self.rows = rows
      if title == None:
         self.win.wm_title("matrix@%s:"%os.getenv('HOSTNAME'))
      else:
         self.win.wm_title(title)
      self.canvas = Canvas(self.win,width=width,height=height)
      self.win.bind("<Configure>", self.changeSize)
      self.canvas.pack({'fill':'both', 'expand':1, 'side': 'left'})
      self.even = 0
      if data:
         self.update(data)
      else:
         self.update([1.0] * cols * rows)
        
   def setTitle(self, title):
      self.win.wm_title(title)

   def changeSize(self, event):
      self.width = self.win.winfo_width() - 2
      self.height = self.win.winfo_height() - 2
      self.update(self.last)
      
   def update(self, vec):
      self.last = vec[:]
      if self.even:
         label = 'even'
         last = 'odd'
      else:
         label = 'odd'
         last = 'even'
      self.even = not self.even
      if self.type == 'som':
         x_blocksize = int(self.width / float(self.cols + .5))
      else:
         x_blocksize = int(self.width / float(self.cols))
      y_blocksize = int(self.height / float(self.rows))
      x_b = x_blocksize / 2.0
      y_b = y_blocksize / 2.0
      for r in range (self.rows):
         for c in range (self.cols):
            v = r * self.cols + c
            color = "gray%d" % int((vec[v] / self.maxvalue) * 100.0) 
            x = x_blocksize * c + x_b
            y = y_blocksize * r + y_b
            try:
               if self.type == 'grid':
                  self.canvas.create_rectangle(x - x_b,
                                               y - y_b,
                                               x + x_b,
                                               y + y_b,
                                               width = 0,
                                               tag = label,
                                               fill = color)
               else: # som
                  if r % 2 == 1:
                     x += x_b
                  self.canvas.create_oval(x - x_b,
                                          y - y_b,
                                          x + x_b,
                                          y + y_b,
                                          width = 0,
                                          tag = label,
                                          fill = color)
            except:
               pass
      try:
         self.canvas.delete(last)
      except:
         pass
      while self.win.tk.dooneevent(2): pass

   def destroy(self):
      self.win.destroy()

if __name__ == '__main__':
   matrix1 = Matrix(3, 2, type = 'grid', maxvalue = 1)
   matrix3 = Matrix(3, 2, type = 'som', maxvalue = 1)
   matrix1.update([0.0, 1.0, .5, 0.0, .74, .5])
   matrix3.update([0.0, 1.0, .5, 0.0, .74, .5])
   matrix2 = Matrix(4, 2, type = 'som', maxvalue = 5)
   v = [1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 5.0, 5.0]
   matrix2.update(v)
   matrix1.win.mainloop()
