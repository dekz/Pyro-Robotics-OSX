import struct
from pyrobot.system import file_exists
from pyrobot import pyrobotdir

# Standard convolution matrices:

laplace  = ([-1, -1, -1, -1,  8, -1, -1, -1, -1], 1)
hipass   = ([-1, -1, -1, -1,  9, -1, -1, -1, -1], 1)
topedge  = ([ 1,  1,  1,  1, -2,  1, -1, -1, -1], 1)
sharpen  = ([-1, -1, -1, -1, 16, -1, -1, -1, -1], 8)
sharpen2 = ([-1, -2, -1, -1, 19, -2, -1, -2, -1], 7)
edge     = ([ 0, -1,  0, -1,  5, -1,  0, -1,  0], 1)
emboss   = ([ 1,  0,  1,  0,  0,  0,  1,  0, -2], 1)
soften   = ([ 2,  2,  2,  2,  0,  2,  2,  2,  2], 16)
blur     = ([ 3,  3,  3,  3,  8,  3,  3,  3,  3], 32)
softest  = ([ 0,  1,  0,  1,  2,  1,  0,  1,  0], 6)
fill     = ([ 1,  1,  1,  1,  1,  1,  1,  1,  1], 5)
smooth   = ([ 1,  2,  1,  2,  4,  2,  1,  2,  1], 16)
bw       = ([ 0,  0,  0,  0,  1,  0,  0,  0,  0], 1)

class PyrobotImage:
   """
   A Basic Image class. 
   """
   def __init__(self, width = 0, height = 0, depth = 3, init_val = 0,
                r=0,g=0,b=0):
      """
      Constructor. Depth is bytes per pixel.
      """
      self.width = width
      self.height = height
      self.depth = depth
      self.rgb = (0, 1, 2)[0:self.depth] # offsets to red, green, blue
      if self.depth == 1:  # initialize grayScale image to initial brightness
         self.data = [init_val] * height * width * depth
      else:   # initialize color image to initial color
         self.data = [r] * height * width * depth
         if r != 0 or g != 0 or b != 0:
            for h in range(self.height):
               for w in range(self.width):
                  self.set(w,h,g,1)
                  self.set(w,h,b,2)

   def loadFromFile(self, filename):
      """
      Method to load image from file. Currently must be in PBM P6 Format
      (color binary).
      """
      fp = open(filename, "r")
      type = fp.readline().strip() # P6
      if type == 'P6':
         self.depth = 3
      elif type == 'P5':
         self.depth = 1
      else:
         raise 'Unknown PPM mode: %s' % type
      (width, height) = fp.readline().split(' ')
      self.width = int(width)
      self.height = int(height)
      self.data = [0] * self.height * self.width * self.depth
      irange = int(fp.readline())
      x = 0
      while (x < self.width * self.height):
         for i in range(self.depth):
            c = fp.read(1)
            r = float(struct.unpack('h', c + '\x00')[0]) #/ float(irange)
            self.data[x * self.depth + i] = int(r)
         x += 1

   def saveToFile(self, filename):
      """
      Method to save image to a file. Currently will save PBM P5/P6 Format.
      """
      fp = open(filename, "w")
      if self.depth == 3:
         fp.writelines("P6\n") # P6
      else:
         fp.writelines("P5\n") # P5
      fp.writelines("%d %d\n" % (self.width, self.height))
      fp.writelines("255\n")
      x = 0
      while (x < self.width * self.height):
         for i in range(self.depth):
            c = int(self.data[x * self.depth + i])
            r = struct.pack('h', c)[0]
            fp.writelines(r)
         x += 1

   def getScaledImage(self, xscale=0.5, yscale='unset', mode='sample'):
      """
      return a scaled version of the current image
      if used without arguments, will return a 1/2 scale image
      if yscale is unspecified, the image is uniformly scaled
      currently you get wacky results unless you use scale values that
      fit evenly into 1.0 (i recommend 0.5, 0.333, 0.25, 0.125 ...)
      """
      if yscale=='unset':
         yscale = xscale
      newImage = PyrobotImage(int(xscale*self.width), int(yscale*self.height), 
                           self.depth)
      xpixels = int(1/xscale)
      ypixels = int(1/yscale)
      for y in range(newImage.height):
         for x in range(newImage.width):
            if(mode == 'average'):
               for y1 in range(y*ypixels,(y+1)*ypixels):
                  for x1 in range(x*xpixels,(x+1)*xpixels):
                     val1 = self.getVal(x1,y1)
                     val2 = newImage.getVal(x,y)
                     newval = tuple(map(lambda x,y: x+y, val1, val2))
                     newImage.setVal(x,y,newval)
               val = newImage.getVal(x,y)
               newval = tuple(map(lambda x,xp=xpixels,yp=ypixels: x/(xp*yp), val))
            elif(mode == 'sample'):
               newval=self.getVal(x*xpixels,y*ypixels)
            else:
               raise "unrecognized mode '" + mode + "'"
            newImage.setVal(x,y,newval)
      return newImage

   def getGrayScale(self):
      """
      Method to convert depth 3 color into depth 1 grayscale
      """
      if self.depth == 1:
         return self.data
      data = [0] * self.width * self.height
      for h in range(self.height):
         for w in range(self.width):
            r = self.data[(w + h * self.width) * self.depth + 0]
            g = self.data[(w + h * self.width) * self.depth + 1]
            b = self.data[(w + h * self.width) * self.depth + 2]
            data[w + h * self.width] = int((r + g + b) / 3.0)
      return data

   def getColorFilter(self, r, g, b):
      """
      returns a filtered image
      r,g,b values indicate percentage of each color to keep
      eg. self.getColorFilter(0.0,1.0,1.0) filters out all the red
      eg. self.getColorFilter(1.0,0.5,0.0) creates an orange image
      """
      if self.depth==1:
         raise "cannot apply a colour filter to greyscale image"
      newimage = PyrobotImage(self.width,self.height)
      for h in range(self.height):
         for w in range(self.width):
            red = self.get(w,h,0)*r
            newimage.set(w,h,red,0)
            green = self.get(w,h,1)*g
            newimage.set(w,h,green,1)
            blue = self.get(w,h,2)*b
            newimage.set(w,h,blue,2)
      return newimage

   def display(self):
      """
      Display PyrobotImage in ASCII Art.
      """
      if self.depth == 3:
         line = ''
         for h in range(self.height):
            for w in range(self.width):
               r = self.data[(w + h * self.width) * self.depth + self.rgb[0]]
               g = self.data[(w + h * self.width) * self.depth + self.rgb[1]]
               b = self.data[(w + h * self.width) * self.depth + self.rgb[2]]               
               if int(((r + g + b) / 3 )/255.0 * 9):
                  line += "%d" % int(((r + g + b) / 3 )/255.0 * 9)
               else:
                  line += '.'
            print line; line = ''
         print line; line = ''
      else:
         line = ''
         for h in range(self.height):
            for w in range(self.width):
               c = self.data[(w + h * self.width) * self.depth + 0]
               if int(c/255.0 * 9):
                  line += "%d" % int(c * 9)
               else:
                  line += '.'
            print line; line = ''
         print line; line = ''

   def get(self, x, y, offset = 0):
      """
      Get a pixel value. offset is r, g, b = 0, 1, 2.
      """
      return self.data[(x + y * self.width) * self.depth + offset]

   def getRow(self, y):
      """ Get the entire row, in tuples """
      retval = [0] * self.width
      for x in range(self.width):
         retval[x] = self.getVal(x, y)
      return retval

   def getDim(self):
      return self.width, self.height

   def getCol(self, x):
      """ Get the entire col, in tuples """
      retval = [0] * self.height
      for y in range(self.height):
         retval[y] = self.getVal(x, y)
      return retval

   def getVal(self, x, y):
      """
      Get the entire color value of the pixel in quetion, returned as a tuple.
      If this is an RGB image, it will be of the form (r, g, b).
      """
      start = (x + y * self.width) * self.depth
      end = start + self.depth
      rgb = self.data[start:end]
      return tuple( (rgb[self.rgb[0]], rgb[self.rgb[1]], rgb[self.rgb[2]] ))

   def setVal(self, x, y, val):
      """
      Method to set the entire RGB value of a pixel.
      val should be an n-tuple (or length n list), where n is the depth of the
      image.  For RGB, it should be of the form (r, g, b)
      """
      if len(val) != self.depth:
         print "Error in setVal: val is not the same length as depth"
         return

      for offset in range(self.depth):
         self.data[(x + y * self.width) * self.depth + offset] = val[offset]
         
   def reset(self, vector):
      """
      Reset an image to a vector.
      """
      for v in range(len(vector)):
         self.data[v] = vector[v]

   def resetToColor(self,r,g,b):
      """
      reset the image to a specified color
      """
      if self.depth == 1:
         raise "cannot set color for a depth 1 image"
      for h in range(self.height):
         for w in range(self.width):
            self.set(w,h,r,0)
            self.set(w,h,g,1)
            self.set(w,h,b,2)

   def incr(self, x, y, offset = 0):
      """
      Method to increment a pixel value. offset is r, g, b (0, 1, 2)
      """
      self.data[(x + y * self.width) * self.depth + offset] += 1

   def cropPixels(self, l, t='unset', r='unset', b='unset'):
      """
      cropPixels()
      ------------
      crops pixels in the amount specified from left, top, right, and bottom
      if unspecified, right is assumed to be the same as left and bottom the
      same as top.  if top is unspecified it is assumed to be the same as left
      """
      if t == 'unset':
         t = l
      if r == 'unset':
         r = l
      if b == 'unset':
         b = t
      for h in range(t):
         for w in range(self.width):
            if self.depth == 1:
               self.set(w,h,0)
            else:
               self.set(w,h,0,0)
               self.set(w,h,0,1)
               self.set(w,h,0,2)
      for h in range(self.height - b, self.height):
         for w in range(self.width):
            if self.depth == 1:
               self.set(w,h,0)
            else:
               self.set(w,h,0,0)
               self.set(w,h,0,1)
               self.set(w,h,0,2)
      for w in range(l):
         for h in range(self.height):
            if self.depth == 1:
               self.set(w,h,0)
            else:
               self.set(w,h,0,0)
               self.set(w,h,0,1)
               self.set(w,h,0,2)
      for w in range(self.width - r, self.width):
         for h in range(self.height):
            if self.depth == 1:
               self.set(w,h,0)
            else:
               self.set(w,h,0,0)
               self.set(w,h,0,1)
               self.set(w,h,0,2)                              

   def getBitmap(self, cutoff, cutoff2='unset', mode='brightness'):
      """
      getBitmap()
      -----------
      constructs a bitmap from the image based on one of four modes
      ----------------------
      the default mode is 'brightness', which only keeps pixels of the
      brightness specified by cutoff (here cutoff2 is ignored)
      ----------------------
      the remaining modes construct bitmaps based on ratioing
      ('rg/b', 'rb/g', and 'gb/r', with support for the reverse permutation of
      the first two letters)
      this is most easily explained with an example, take 'rg/b':
      at each pixel, we keep it only if r/b > cutoff and if g/b > cutoff2
      if cutoff2 is unspecified, it is set to cutoff
      cutoff always applies to the first color and cutoff2 to the second
      (so if you do 'gr/b' cutoff applies to g and cutoff2 to r)
      """
      if cutoff2 == 'unset':
         cutoff2 = cutoff

      # set alternate mode permutations to usable modes
      if mode == 'gr/b' or mode == 'br/g' or mode == 'bg/r':
         cutoff, cutoff2 = cutoff2, cutoff
         if mode == 'gr/b':
            mode = 'rg/b'
         elif mode == 'br/g':
            mode = 'rb/g'
         else:
            mode = 'gb/r'
            
      if mode == 'brightness':
         grayImage = PyrobotImage(self.width,self.height,depth=1)
         grayImage.data = self.getGrayScale()
         bitmap = Bitmap(grayImage.width, grayImage.height)
         for h in range(bitmap.height):
            for w in range(bitmap.width):
               if grayImage.get(w, h) > cutoff:
                  bitmap.set(w, h, 255)
               else:
                  bitmap.set(w, h, 0)
      elif mode == 'rg/b' or mode == 'rb/g' or mode == 'gb/r':
         if mode == 'rg/b':
            o_n1 = 0  # first numerator offset
            o_n2 = 1  # second numerator offset            
            o_d  = 2  # denominator offset
         elif mode == 'rb/g':
            o_n1 = 0
            o_n2 = 2
            o_d  = 1
         else:
            o_n1 = 1
            o_n2 = 2
            o_d  = 0
         bitmap = Bitmap(self.width,self.height)
         for h in range(bitmap.height):
            for w in range(bitmap.width):
               d = float(self.get(w,h,o_d))   # denominator
               if d == 0:
                  d = 0.01
               if self.get(w,h,o_n1)/d > cutoff and self.get(w,h,o_n2)/d > cutoff2:
                  bitmap.set(w, h, 255)
               else:
                  bitmap.set(w, h, 0)
      else:
         raise "unrecognized mode", mode
      return bitmap

   def histogram(self, cols = 20, rows = 20, initvals = 0):
      """
      Creates a histogram.
      """
      if not initvals:
         histogram = Histogram(cols, rows)
      else:
         histogram = initvals
      for h in range(self.height):
         for w in range(self.width):
            r = self.get(w, h, 0)
            g = self.get(w, h, 1)
            b = self.get(w, h, 2)
            if r == 0: r = 1.0
            br = min(int(b/float(r + g + b) * float(cols - 1)), cols - 1)
            gr = min(int(g/float(r + g + b) * float(rows - 1)), rows - 1)
            histogram.incr(br, gr)
      return histogram
   
   def convolve(self, convmask, bit = 0, threshold = 0):
      (mask, z) = convmask
      data = PyrobotImage(self.width, self.height, self.depth)
      for x in range(1, self.width-2):
         for y in range(1, self.height-2):
            for c in range(self.depth):
               val = (self.get(x - 1, y - 1, c) * mask[0] + \
                      self.get(x    , y - 1, c) * mask[1] + \
                      self.get(x + 1, y - 1, c) * mask[2] + \
                      self.get(x - 1, y    , c) * mask[3] + \
                      self.get(x    , y    , c) * mask[4] + \
                      self.get(x + 1, y    , c) * mask[5] + \
                      self.get(x - 1, y + 1, c) * mask[6] + \
                      self.get(x    , y + 1, c) * mask[7] + \
                      self.get(x + 1, y + 1, c) * mask[8] ) / float(z)
               val = min(max(val, 0), 255)
               if val > threshold:
                  if bit:
                     data.set(x,y,255,c)
                  else:
                     data.set(x,y,val,c)
      return data

   def getPlane(self, colorPlane): # 0, 1, 2
      data = [0 for x in range(self.width * self.height)]
      for h in range(self.height):
         for w in range(self.width):
            data[h * self.width + w] = self.get(w, h, self.rgb[colorPlane])
      return data
   
   def swapPlanes(self, plane1, plane2):
      for h in range(self.height):
         for w in range(self.width):
            c2 = self.get(w, h, plane2)
            c1 = self.get(w, h, plane1)
            self.set(w, h, c2, plane1)
            self.set(w, h, c1, plane2)

class Histogram(PyrobotImage):
   """
   Histogram class. Based on Image, but has methods for display.
   """
   def __init__(self, width, height, init_val = 0):
      PyrobotImage.__init__(self, width, height, 1, init_val) # 1 bit depth

   def display(self):
      """
      Display bitmap ASCII art.
      """
      maxval = 0
      for h in range(self.height):
         for w in range(self.width):
            maxval = max(maxval, self.get(w, h))
      for h in range(self.height):
         for w in range(self.width):
            if maxval:
               print "%5d" % self.get(w, h),
            else:
               print ' ',
         print ''
      print ''

   def compare(self, hist):
      sum = 0
      for h in range(self.height):
         for w in range(self.width):
            sum += min(self.get(w, h), hist.get(w, h))
      return sum

class Bitmap(PyrobotImage):
   """
   Bitmap class. Based on Image, but has methods for blobs, etc.
   """
   def __init__(self, width, height, init_val = 0):
      PyrobotImage.__init__(self, width, height, 1, init_val) # 1 bit depth
      self.equivList = [0] * 2000
      for n in range(2000):
         self.equivList[n] = n

   def display(self):
      """
      Display bitmap ASCII art.
      """
      for h in range(self.height):
         for w in range(self.width):
            if self.data[w + h * self.width]:
               try:
                  print self.equivList[self.data[w + h * self.width]],
               except:
                  print ">",
            else:
               print '.',
         print ''
      print ''

   def avgColor(self, img):
      """
      Return an n-tuple of the average color of the image where the bitmap is true,
      where n is the depth of img.  That is, using the bitmap as a mask, find the average color of img.
      img and self should have the same dimensions.
      """

      if not (self.width == img.width and self.height == img.height):
         print "Error in avgColor: Bitmap and Image do not have the same dimensions"
         return
      
      avg = []
      n = 0
      for i in range(img.depth):
         avg.append(0) #an n-array of zeros
         
      for x in range(self.width):
         for y in range(self.height):
            if (self.get(x, y)): #if the bitmap is on at this point
               for i in range(img.depth):
                  avg[i] += img.get(x, y, i)
                  n += 1

      if n == 0:
         return tuple(avg)
      else:
         for i in range(img.depth):
            avg[i] /= n
         return tuple(avg)
               
"""
assume that we are starting our x,y coordinates from the upper-left,
and starting at (0,0), such that (0,0) represents the upper-left-most
pixel
"""
class Point:
   def __init__(self, x=0, y=0):
      self.x = x
      self.y = y
   def set(self, x, y):
      self.x = x
      self.y = y
   def setx(self, x):
      self.x = x
   def sety(self, y):
      self.y = y
   def clear(self):
      self.x = 0
      self.y = 0

class Blob:
   def __init__(self, pixel):
      self.mass = 1
      self.ul = Point(pixel.x, pixel.y)
      self.lr = Point(pixel.x, pixel.y)
      self.cm = Point(pixel.x, pixel.y)
      self.next = 0

   def addpixel(self, pixel):
      if pixel.x < self.ul.x:
         self.ul.x = pixel.x
      elif pixel.x > self.lr.x:
         self.lr.x = pixel.x
      if pixel.y < self.ul.y:
         self.ul.y = pixel.y
      elif pixel.y > self.lr.y:
         self.lr.y = pixel.y
      self.cm.x = float(self.mass * self.cm.x + pixel.x)/float(self.mass + 1)
      self.cm.y = float(self.mass * self.cm.y + pixel.y)/float(self.mass + 1)
      self.mass += 1

   def joinblob(self, other):
      if other.ul.x < self.ul.x:
         self.ul.x = other.ul.x
      elif other.lr.x > self.lr.x:
         self.lr.x = other.lr.x
      if other.ul.y < self.ul.y:
         self.ul.y = other.ul.y
      elif other.lr.y > self.lr.y:
         self.lr.y = other.lr.y
      self.cm.x = float(self.mass * self.cm.x + other.mass * other.cm.x) \
                  /float(self.mass + other.mass)
      self.cm.y = float(self.mass * self.cm.y + other.mass * other.cm.y) \
                  /float(self.mass + other.mass)
      self.mass += other.mass   
         
   def width(self):
      return self.lr.x - self.ul.x + 1
   def height(self):
      return self.lr.y - self.ul.y + 1
   def area(self):
      return self.width() * self.height()
   def density(self):
      return float(self.mass)/float(self.area())
   def display(self):
      print "mass:", self.mass
      print "area:", self.area()
      print "density:", self.density()
      print "center of mass:", self.cm.x, ",", self.cm.y
      print "upper-left bound:", self.ul.x, ",", self.ul.y
      print "lower-right bound:", self.lr.x, ",", self.lr.y



class Blobdata:
   def __init__(self, bitmap):
      self.blobmap = Bitmap(bitmap.width, bitmap.height)
      self.bloblist = [0] * 2000
      count = 1

      # build the blobmap and construct unjoined Blob objects
      for w in range(bitmap.width):
         for h in range(bitmap.height):
            if bitmap.get(w, h):
               if h == 0 and w == 0: # in upper left corner -- new blob
                  self.bloblist[count] = Blob(Point(w,h))
                  self.blobmap.set(w, h, count)
                  count += 1
               elif w == 0:  # if in first col 
                  if bitmap.get(w, h - 1): # pixel above is on -- old blob
                     self.bloblist[self.blobmap.get(w,h-1)].addpixel(Point(w,h))
                     self.blobmap.set(w, h, self.blobmap.get(w, h - 1))
                  else: # above is off -- new blob
                     self.bloblist[count] = Blob(Point(w,h))
                     self.blobmap.set(w, h, count)
                     count += 1
               elif h == 0: # in first row
                  if bitmap.get(w - 1, h): # pixel to left is on -- old blob
                     self.bloblist[self.blobmap.get(w-1,h)].addpixel(Point(w,h))
                     self.blobmap.set(w, h, self.blobmap.get(w - 1, h))
                  else: # left is off -- new blob
                     self.bloblist[count] = Blob(Point(w,h))
                     self.blobmap.set(w, h, count)
                     count += 1
               elif bitmap.get(w - 1, h) and bitmap.get(w, h - 1): # both on
                  if self.blobmap.get(w - 1, h) == self.blobmap.get(w, h - 1):
                     self.bloblist[self.blobmap.get(w-1,h)].addpixel(Point(w,h))
                     self.blobmap.set(w, h, self.blobmap.get(w - 1, h))
                  else: # intersection of two blobs
                     minBlobNum = min( \
                        self.blobmap.equivList[self.blobmap.get(w - 1, h)],
                        self.blobmap.equivList[self.blobmap.get(w, h - 1)])
                     maxBlobNum = max( \
                        self.blobmap.equivList[self.blobmap.get(w - 1, h)],
                        self.blobmap.equivList[self.blobmap.get(w, h - 1)])
                     self.bloblist[minBlobNum].addpixel(Point(w,h))
                     self.blobmap.set(w, h, minBlobNum)
                     for n in range(2000):
                        if self.blobmap.equivList[n] == maxBlobNum:
                           self.blobmap.equivList[n] = minBlobNum
               else:
                  if bitmap.get(w - 1, h): # left is on -- old blob
                     self.bloblist[self.blobmap.get(w-1,h)].addpixel(Point(w,h))
                     self.blobmap.set(w, h, self.blobmap.get(w - 1, h))
                  elif bitmap.get(w, h - 1): # above is on -- old blob
                     self.bloblist[self.blobmap.get(w,h-1)].addpixel(Point(w,h))
                     self.blobmap.set(w, h, self.blobmap.get(w, h - 1))
                  else: # left is off, above is off -- new blob
                     self.bloblist[count] = Blob(Point(w,h))
                     self.blobmap.set(w, h, count)
                     count += 1

      # count the number of blobs and join the actual blob objects
      self.nblobs = 0
      for n in range(1,count):
         if self.blobmap.equivList[n] == n:
            for m in range(n+1,count):
               if self.blobmap.equivList[m] == n:
                  self.bloblist[n].joinblob(self.bloblist[m])
                  self.bloblist[m] = 0
            self.nblobs += 1

      # shift the elements of bloblist[] so that the first Blob is at
      # bloblist[0] and the rest follow consecutively
      for n in range(1,count):
         m = n-1
         while self.bloblist[m] == 0:
            self.bloblist[m] = self.bloblist[m+1]
            self.bloblist[m+1] = 0
            if m == 0:
               break
            m -= 1


   # sort based on mass, area, or density
   def sort(self, mode="mass"):
      newlist = [0] * self.nblobs
      if mode == "mass":
         for i in range(0,self.nblobs):
            max = 0
            m = 0
            for n in range(0,self.nblobs):
               if self.bloblist[n] == 0:
                  pass
               elif self.bloblist[n].mass > max:
                  max = self.bloblist[n].mass
                  m = n
            newlist[i] = self.bloblist[m]
            self.bloblist[m] = 0
         self.bloblist = newlist
      elif mode == "area":
         for i in range(0,self.nblobs):
            max = 0
            m = 0
            for n in range(0,self.nblobs):
               if self.bloblist[n] == 0:
                  pass
               elif self.bloblist[n].area() > max:
                  max = self.bloblist[n].area()
                  m = n
            newlist[i] = self.bloblist[m]
            self.bloblist[m] = 0
         self.bloblist = newlist
      elif mode == "density":
         for i in range(0,self.nblobs):
            max = 0
            m = 0
            for n in range(0,self.nblobs):
               if self.bloblist[n] == 0:
                  pass
               elif self.bloblist[n].density() > max:
                  max = self.bloblist[n].density()
                  m = n
            newlist[i] = self.bloblist[m]
            self.bloblist[m] = 0
         self.bloblist = newlist
      elif mode == "wacky":
         for i in range(0,self.nblobs):
            max = 0
            m = 0
            for n in range(0,self.nblobs):
               if self.bloblist[n] == 0:
                  pass
               else:
                  blob = self.bloblist[n]
                  center = Point(float(self.blobmap.width)/2.0, \
                                 float(self.blobmap.height)/2.0)
                  dx = blob.cm.x - center.x
                  dy = blob.cm.y - center.y
                  dist = dx*dx + dy*dy
                  if dist == 0:
                     dist = 0.5
                  val = blob.density() * blob.mass * blob.mass / dist
                  if val > max:
                     max = val
                     m = n
            newlist[i] = self.bloblist[m]
            self.bloblist[m] = 0
         self.bloblist = newlist      
      else:
         print "unknown sorting parameter:", mode

   def display(self):
      self.blobmap.display()
      print "Total number of blobs:", self.nblobs
      print ""
      for n in range(0,self.nblobs):
         print "Blob", n, ":"
         self.bloblist[n].display()            
         print ""

if __name__ == '__main__':
   from os import getenv
   import sys
   
   bitmap = Bitmap(20, 15)
   bitmap.reset([1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 
                 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 
                 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 
                 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 
                 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 
                 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 
                 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 
                 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1])
   print "Do you want to run test 1: create bitmap, blobify, and display results? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      bitmap.display()
      myblobdata = Blobdata(bitmap)
      myblobdata.sort("area")
      myblobdata.display()
      print "Done!"
   else:
      print "skipping..."
   print "Do you want to run test 2: create image from file, save it back out? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      image = PyrobotImage(0, 0)
      image.loadFromFile(pyrobotdir() + "/vision/snaps/som-1.ppm")
      image.saveToFile("test2.ppm")
      print "Done! To see output, use 'xv test2.ppm'"
   else:
      print "skipping..."
   print "Do you want to run test 2.25: image shrinking? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      from time import clock
      tavg = clock()
      newimage = image.getShrunkenImage(mode='average')
      tavg = clock() - tavg
      newimage.saveToFile("test2.25_avg.ppm")
      tsmp = clock()
      newimage = image.getShrunkenImage(mode='sample')
      tsmp = clock() - tsmp
      newimage.saveToFile("test2.25_smp.ppm")
      print "calc time for mode 'average': %f" %(tavg)
      print "calc time for mode 'sample': %f" %(tsmp)
      print "Done! To see output, use 'xv test2.25_*.ppm'"
   else:
      print "skipping..."
   print "Do you want to run test 2.5: create a filtered image, save to file? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      newimage = image.getColorFilter(1,.5,0)
      newimage.saveToFile("test2.5.ppm")
      print "Done! To see output, use 'xv test2.5.ppm'"
   else:
      print "skipping..."
   print "Do you want to run test 2.75: reset to a solid color, save to file? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      newimage.resetToColor(0,128,255)
      newimage.saveToFile("test2.75.ppm")
      print "Done! To see output, use 'xv test2.75.ppm'"
   else:
      print "skipping..."      
   print "Do you want to run test 3: create a grayscale image, save to file? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      image = PyrobotImage(0, 0)
      image.loadFromFile(pyrobotdir() + "/vision/snaps/som-21.ppm")
      image.grayScale()
      image.saveToFile("test3.ppm")
      #image.display()
      print "Done! To see output, use 'xv test3.ppm'"
   else:
      print "skipping..."

   print "Do you want to run test 3.01: recognize a yellow object? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      image = PyrobotImage(0, 0)
      image.loadFromFile(pyrobotdir() + "/vision/snaps/som-21.ppm")
      image.saveToFile("test3.01a.ppm")
      mybitmap = image.getBitmap(4.0, mode='rg/b')
      mybitmap.saveToFile("test3.01b.ppm")
      mybitmap = image.getBitmap(70, mode='brightness')
      mybitmap.saveToFile("test3.01c.ppm")
      myblobdata = Blobdata(mybitmap)
      myblobdata.sort("wacky")
      print "original image: test3.01a.ppm"
      print "bitmapped image: test3.01b.ppm"
      print "dominant blob:"
      myblobdata.bloblist[0].display()
      print ""
   else:
      print "skipping..."      

   
   
   print "Do you want to run test 4: convert PyrobotImage to PIL image, and display it using xv? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      try:
         image.loadFromFile(pyrobotdir() + "/vision/snaps/som-1.ppm")
         import PIL.PpmImagePlugin
         from struct import *
         c = ''
         for x in range(len(image.data)):
            #c += pack('h', image.data[x] * 255.0)[0]
            c += pack('h', image.data[x])[0]
         i = PIL.PpmImagePlugin.Image.fromstring('RGB', (image.width, image.height),c)
         if getenv('DISPLAY'): i.show()
         else: print "set DISPLAY to see"
         print "Done!"
      except:
         print "Failed! Probably you don't have PIL installed"
   else:
      print "skipping..."
   print "Do you want to run test 5: convert Bitmap to PIL image, and display it using xv? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      import PIL.PpmImagePlugin
      from struct import *
      c = ''
      for x in range(len(bitmap.data)):
         c += pack('h', bitmap.data[x] * 255.0)[0]
         #c += pack('h', bitmap.data[x])[0]
      i = PIL.PpmImagePlugin.Image.fromstring('L', (bitmap.width, bitmap.height),c)
      if getenv('DISPLAY'): i.show()
      print "Done!"
   else:
      print "skipping..."
   print "Do you want to run test 6: create a TK window, and display PPM from file or PyrobotImage? ",
   if getenv('DISPLAY') and sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      try:
         import Tkinter
         import Image, ImageTk
         class UI(Tkinter.Label):
            def __init__(self, master, im):
               if im.mode == "1":
                  # bitmap image
                  self.image = ImageTk.BitmapImage(im, foreground="white")
                  Label.__init__(self, master, image=self.image, bg="black", bd=0)
               else:
                  # photo image
                  self.image = ImageTk.PhotoImage(im)
                  Tkinter.Label.__init__(self, master, image=self.image, bd=0)
         root = Tkinter.Toplevel()
         filename = pyrobotdir() + "/vision/snaps/som-1.ppm"
         root.title(filename)
         im = Image.open(filename)
         #im = i
         UI(root, im).pack()
         root.mainloop()
         print "Done!"
      except:
         print "Failed! Probably you don't have Tkinter or ImageTk installed"
   else:
      print "skipping..."
   print "Do you want to run test 7: create a camera view, and display 10 frames in ASCII? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      from pyrobot.camera.fake import FakeCamera
      image = FakeCamera()
      for x in range(10):
         image.update()
         image.display()
      print "Done!"
   else:
      print "skipping..."
   print "Do you want to run test 8: create a histogram of the image? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      from pyrobot.camera.fake import FakeCamera
      image = FakeCamera()
      image.update()
      histogram = image.histogram(15, 20)
      histogram.display()
      #for x in range(99):
      #   image.update()
      #   histogram = image.histogram(15, 20, histogram)
      #   histogram.display()
      print "Done!"
   else:
      print "skipping..."

   print "Do you want to run test 9: find motion in 10 frames? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      from pyrobot.camera.fake import FakeCamera
      camera = FakeCamera()
      camera.update()
      for x in range(10):
         camera.update(1)
         camera.motion.display()
         print "avg color of motion:", camera.motion.avgColor(camera)
      print "Done!"
   else:
      print "skipping..."
   print "Do you want to run test 10: find edges in bitmap? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      image = PyrobotImage(0,0)
      image.loadFromFile(pyrobotdir() + '/vision/snaps/som-16.ppm')
      image.grayScale()
      mask = image.convolve(edge, 1, 128)
      #mask = mask.convolve(fill, 1)
      print "Your final image is in test10.ppm"
      mask.saveToFile('test10.ppm')
   else:
      print "skipping..."
   print "Do you want to run test 11: do person ID test with histograms? ",
   if sys.stdin.readline().lower()[0] == 'y':
      print "Running..."
      hists = [0] * 8
      files = [0] * 8
      imgs = [0] * 8
      files[0] = "/vision/snaps/som-andrew1.ppm"
      files[1] = "/vision/snaps/som-doug1.ppm"
      files[2] = "/vision/snaps/som-evan1.ppm"
      files[3] = "/vision/snaps/som-katie1.ppm"
      files[4] = "/vision/snaps/som-maria1.ppm"
      files[5] = "/vision/snaps/som-ry1.ppm"
      files[6] = "/vision/snaps/som-sharonrose1.ppm"
      files[7] = "/vision/snaps/som-dsb1.ppm"

      for x in range( len(files)):
         print "Loading " + files[x] + "..."
         imgs[x] = PyrobotImage(0,0)
         imgs[x].loadFromFile(pyrobotdir() + files[x])
         hists[x] = imgs[x].histogram(20, 20)

      f = "/vision/snaps/som-dsb4.ppm"
      print "========================= Testing " + f
      i = PyrobotImage(0,0)
      i.loadFromFile(pyrobotdir() + f)
      h = i.histogram(20,20)
      maxcomp = 0
      for x in range( len(files)):
         print "Comparing to " + files[x] + "=",
         comp = hists[x].compare(h)
         print comp
         if comp > maxcomp:
            maxfile = files[x]
            maxcomp = comp
      print "=========================="
      print "I found the closest histogram to be:" + maxfile

   else:
      print "skipping..."
      
   print "All done!"
