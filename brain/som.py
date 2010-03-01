__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision: 2020 $"

import math, os

class SOM:

   def __init__(self, filename):
      self.mapfile = filename
      fp = open(filename, "r")
      #1548 hexa 12 8 bubble
      line = fp.readline()
      (length, ntype, cols, rows, kernel) = line.split(' ')
      self.cols = int(cols)
      self.rows = int(rows)
      self.vector_size = int(length)
      self.grid_type = ntype
      self.kernel_type = kernel
      self.cell = {}
      line = fp.readline()
      linecnt = 0
      print "Initializing SOM..."
      while (line):
         line = line.replace("\n", "")
         self.cell[linecnt] = {}
         vals = line.split(' ')
         x = 0
         for v in vals:
            try:
               self.cell[linecnt][x] = float(v)
               x += 1
            except:
               pass # nevermind
         line = fp.readline()
         linecnt += 1
      print "SOM initialized at", linecnt, x
      fp.close()
      self.max_translate = 0.2
      self.min_translate = 0.05
      self.max_rotate = 0.909091
      self.min_rotate = -0.909091
      self.max_speed = 18
      self.min_speed = -13
      self.max_ir = 100 # 980
      self.min_ir = 16


   def getCategory(self, vector):
      print "Finding a model..."
      of = open("/tmp/temp.dat", "w")
      # make som.dat from vector
      of.writelines("%d\n" % len(vector))

      translate = vector[0]
      rotate = vector[1]

      of.write( "%f %f " % (min((float(translate) - self.min_translate) / (self.max_translate - self.min_translate), 1.0), min((float(rotate) - self.min_rotate) / (self.max_rotate - self.min_rotate), 1.0)))
      left = vector[2]
      right = vector[3]
      
      of.write( "%f %f " % ((float(left) - self.min_speed) / (self.max_speed - self.min_speed), (float(right) - self.min_speed) / (self.max_speed - self.min_speed)))

      i = 0
      while (i < 8): # ir count
         ir_i = min((int(vector[i + 4]) - self.min_ir) / (self.max_ir - self.min_ir), 1.0)
         of.write( "%f " % ir_i)
         i += 1

      i = 12 # start at (sensor + motor count)
      while (i < len(vector)):
         of.write("%f " % vector[i])
         i += 1
      of.write("\n")
      of.close()

      # make som.cat
      os.system("/home/dblank/html/som_pak-3.1/visual -din /tmp/temp.dat -cin %s -dout /tmp/temp.cat" % self.mapfile)
      # read som.cat
      ifp = open("/tmp/temp.cat", "r")
      ifp.readline()
      line = ifp.readline()
      ifp.close()
      line = line.replace("\n", "")
      #11 3 4.30274
      (mycol, myrow, myerror, trash) = line.split(' ')
      mycol = int(mycol)
      myrow = int(myrow)
      myerror = float(myerror)
      print "Category found: cell[%d][%d] (error %f)" % (mycol, myrow, myerror)
      return (mycol, myrow, myerror)

   def getCategoryPlain(self, vector):
      print "Finding a model..."
      of = open("/tmp/temp.dat", "w")
      # make som.dat from vector
      of.writelines("%d\n" % len(vector))

      i = 0
      while (i < len(vector)):
         of.write("%f " % vector[i])
         i += 1
      of.write("\n")
      of.close()

      # make som.cat
      os.system("/home/dblank/html/som_pak-3.1/visual -din /tmp/temp.dat -cin %s -dout /tmp/temp.cat" % self.mapfile)
      # read som.cat
      ifp = open("/tmp/temp.cat", "r")
      ifp.readline()
      line = ifp.readline()
      ifp.close()
      line = line.replace("\n", "")
      #11 3 4.30274
      (mycol, myrow, myerror, trash) = line.split(' ')
      mycol = int(mycol)
      myrow = int(myrow)
      myerror = float(myerror)
      print "Category found: cell[%d][%d] (error %f)" % (mycol, myrow, myerror)
      return (mycol, myrow, myerror)

   def findModel(self, vector):
      (mycol, myrow, myerror) = self.getCategory(vector)
      return self.cell[int(myrow) * self.cols + int(mycol)]

   def activateSOM(self, x, y):
      # print x, y
      matrix = [0.0] * self.rows * self.cols
      matrix[x + y * self.cols] = 1.0
      for delta_x in (-1, 0, 1):
         for delta_y in (-1, 0, 1):
            if (delta_x == 0 and delta_y == 0) or \
               (delta_x + x >= self.cols) or \
               (delta_x + x < 0) or \
               (delta_y + y >= self.rows) or \
               (delta_y + y < 0):
               pass
            else:
               matrix[(x + delta_x) + ((y + delta_y) * self.cols)] = 0.5
      #for y in range(self.rows):
      #   for x in range(self.cols):
      #      print matrix[x + y * self.cols],
      #   print ''
      return matrix

   def findModelSlow(self, vector):
      print "Finding a model..."
      min_diff = 10000000
      min_pos = 0
      n = 0
      while (n < len(self.cell)):
         i = 0
         diff = 0
         while (i < len( self.cell[n])):
            # this appears to be what som-pak uses:
            diff += (vector[i] - self.cell[n][i]) * (vector[i] - self.cell[n][i])
            i += 1
         if diff < min_diff:
            min_diff = diff
            min_pos = n
         n += 1
      print "Category found: cell[%d][%d]" % (min_pos % self.cols, int(min_pos / self.cols))
      return self.cell[min_pos]
