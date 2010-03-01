#include "VisionLib.h"
#include <stdlib.h>
#include <stdio.h>

Vision::Vision() {
  allocatedImage = 0;
  movieMode = 0;
}

Vision::Vision(int wi, int he, int de, int r, int g, int b) {
  allocatedImage = 0;
  movieMode = 0;
  initialize(wi, he, de, r, g, b);
}

Vision::Vision(int wi, int he, int de) {
  allocatedImage = 0;
  movieMode = 0;
  initialize(wi, he, de, 0, 1, 2);
}

Vision::~Vision() {
  if (allocatedImage)
    delete [] image;
}

PyObject *Vision::registerCameraDevice(void *dev) {
  Device *device = (Device *)dev;
  image = device->getImage();
  allocatedImage = 1;
  return initialize(device->getWidth(), device->getHeight(), device->getDepth(),
		    device->getRGB()[0],device->getRGB()[1],device->getRGB()[2]);
}

PyObject *Vision::getRGB() {
  return Py_BuildValue("iii", rgb[0], rgb[1], rgb[2] );
}

PyObject *Vision::setRGB(int r, int g, int b) {
  int rgb_order[MAXDEPTH] = {r, g, b};
  for (int d = 0; d < depth; d++)
    // set offsets for RGB
    rgb[d] = rgb_order[d];
  return getRGB();
}

PyObject *Vision::initialize(int wi, int he, int de, int r, int g, int b) {
  width = wi;
  height = he;
  depth = de;
  setRGB(r, g, b);
  filterList = PyList_New(0);
  // set the current image to:
  Image = image;
  // Make memory for motion capture:
  for (int i = 0; i < MAXMOTIONLEVELS; i++) {
    motionArray[i] = new unsigned char[width * height * depth];
  }
  return PyInt_FromLong(0L);
}

// set(): works on current image
// sets the depth R, G, or B at (w, h) to val.
// if d is RED, GREEN, or BLUE then set just that d; if
// d == ALL, then set all colors to val.

PyObject *Vision::set(int offset, int r, int g, int b) {
  if (offset < 0 || offset >= width * height) {
    PyErr_SetString(PyExc_ValueError, "offset, or value out-of-bounds in set()");
    return NULL;
  } else {
    int value[3] = {r, g, b};
    for (int deep = 0; deep < depth; deep++) {
      Image[offset * depth + deep] = value[deep];
    }
  }
  return Py_BuildValue("i", 1);
  
}

PyObject *Vision::set(int w, int h, int r, int g, int b) {
  setVal(w, h, rgb[0], r);
  setVal(w, h, rgb[1], g);
  setVal(w, h, rgb[2], b);
  return Py_BuildValue("i", 1);
}

PyObject *Vision::setVal(int w, int h, int d, int value) {
  if (w < 0 || w >= width ||
      h < 0 || h >= height ||
      value < 0 || value >= 256) {
    PyErr_SetString(PyExc_ValueError, "width, height, or value out-of-bounds in set()");
    return NULL;
  } else {
    if (d < MAXDEPTH)
      Image[(h * width + w) * depth + rgb[d]] = value;
    else if (d == ALL)
      for (int deep = 0; deep < depth; deep++)
	Image[(h * width + w) * depth + deep] = value;
    else {
      PyErr_SetString(PyExc_ValueError, "invalid color in set()");
      return NULL;
    }
  }
  return Py_BuildValue("i", value);
}

PyObject *Vision::setImage(PyObject *array) {
  if (PyList_Size(array) != width * height * depth) {
    PyErr_SetString(PyExc_ValueError, "wrong size of array in setImage()");
    return NULL;
  } else {
    for (int i = 0; i < PyList_Size(array); i++) {
      PyObject* value = PyList_GetItem(array, i);
      if (!PyInt_Check(value)) {
	PyErr_SetString(PyExc_ValueError, "all array items should be integers in setImage()");
	return NULL;
      }
      Image[i] = (unsigned char) PyInt_AsLong(value);
    }
  }
  return PyInt_FromLong(0L);
}

// same as set(), but for the entire color plane (depth)

PyObject *Vision::setPlane(int d, int value) {
  for (int w=0; w<width; w++) {
    for (int h=0; h<height; h++) {
      if (d < MAXDEPTH)
	Image[(h * width + w) * depth + rgb[d]] = value;
      else if (d == ALL)
	for (int deep = 0; deep < depth; deep++)
	  Image[(h * width + w) * depth + deep] = value;
      else {
	PyErr_SetString(PyExc_ValueError, "invalid color in set()");
	return NULL;
      }
    }
  }
  return Py_BuildValue("i", value);
}

PyObject *Vision::scale(float r, float g, float b) {
  for (int w=0; w<width; w++) {
    for (int h=0; h<height; h++) {
      for (int d=0; d<depth; d++) {
	Image[(h * width + w) * depth + rgb[0]] = (int)(MIN(MAX(r * Image[(h * width + w) * depth + rgb[0]],0),255));
	Image[(h * width + w) * depth + rgb[1]] = (int)(MIN(MAX(g * Image[(h * width + w) * depth + rgb[1]],0),255));
	Image[(h * width + w) * depth + rgb[2]] = (int)(MIN(MAX(b * Image[(h * width + w) * depth + rgb[2]],0),255));
      }
    }
  }
  return PyInt_FromLong(0L);
}

PyObject *Vision::getMMap() {
  PyObject *buffer;
  buffer = PyBuffer_FromMemory(Image, 
			       width * height * depth * sizeof(unsigned char));
  return Py_BuildValue("O", buffer);
}


PyObject *Vision::get(int w, int h) {
  if (w < 0 || w >= width ||
      h < 0 || h >= height) {
    PyErr_SetString(PyExc_ValueError, "width or height out-of-bounds in get");
    return NULL;
  }
  if (depth == 3) {
    return Py_BuildValue("iii", 
			 Image[(h * width + w) * depth + rgb[0]],
			 Image[(h * width + w) * depth + rgb[1]],
			 Image[(h * width + w) * depth + rgb[2]] );
  } else if (depth == 1) {
    return Py_BuildValue("i", Image[(h * width + w) * depth + 0]);
  } else {
    PyErr_SetString(PyExc_ValueError, "Invalid depth in get");
    return NULL;
  }
}

PyObject *Vision::superColor(float w1, float w2, float w3, 
			     int outChannel, int threshold) {
  float weight[3] = {w1, w2, w3};
  int count = 0;
  for (int w=0; w<width; w++) {
    for (int h=0; h<height; h++) {
      int brightness = 0;
      for (int d = 0; d < depth; d++) {
	// compute brightness as sum of values * weight
	brightness += (int) (Image[(h * width + w) * depth + rgb[d]] * weight[d]);
	// blacken all pixels:
	Image[(h * width + w) * depth + rgb[d]] = 0;
      }
      if (brightness > 0) {
	if (threshold) {
	  if (brightness > threshold) 
	    Image[(h * width + w) * depth + rgb[outChannel] ] = 255;
	} else {
	  // reset outChannel pixel to brightness level:
	  Image[(h * width + w) * depth + rgb[outChannel] ] = MAX(MIN(brightness,255),0); 
	}
	count++;
      }
    }
  }
  return PyInt_FromLong(count);
}  

// match() - match pixels by tolerance

PyObject *Vision::match(int r, int g, int b, int tolerance, 
			int outChannel) {
  return matchRange( r - tolerance, g - tolerance, b - tolerance,
		     r + tolerance, g + tolerance, b + tolerance,
		     outChannel);
}

// match() - match pixels by range
// outChannel can be RED, GREEN, BLUE, or ALL

PyObject *Vision::matchRange(int lr, int lg, int lb, 
			     int hr, int hg, int hb,
			     int outChannel) {
  int matches = 0;
  for(int h=0;h<height;h++) {
    for(int w=0;w<width;w++) {
      if (
	  (lr == -1 || 
	   (Image[(h * width + w) * depth + rgb[RED]] >= lr && 
	    Image[(h * width + w) * depth + rgb[RED]] <= hr))
	  &&
	  (lg == -1 || 
	   (Image[(h * width + w) * depth + rgb[GREEN]] >= lg && 
	    Image[(h * width + w) * depth + rgb[GREEN]] <= hg))
	  &&
	  (lb == -1 ||
	   (Image[(h * width + w) * depth + rgb[BLUE]] >=  lb && 
	    Image[(h * width + w) * depth + rgb[BLUE]] <= hb))
	  ) {
	/* maybe add a normalizer here so the outputs are 
	   between 100-255ish for more varied usage? */
	matches++;
	if (outChannel == ALL) {
	  for (int d = 0; d < depth; d++) {
	    Image[(h * width + w) * depth + d ] = 255;
	  }
	} else {
	  for (int d = 0; d < depth; d++) {
	    Image[(h * width + w) * depth + d ] = 0;
	  }
	  Image[(h * width + w) * depth + rgb[outChannel] ] = 255;
	}
      } else { // no match
	// leave alone for now
      }
    }
  }
  return Py_BuildValue("i", matches);
}

// [ (r1, g1, b1, r2, g2, b2, out), ...]

PyObject *Vision::matchList(PyObject *myList) {
  int matches = 0, matchOne = 0, lastOut = 0;
  int lr = 0, lg = 0, lb = 0, hr = 255, hg = 255, hb = 255, outChannel = 0;
  int ranges[100][7];
  for (int matchCount = 0; matchCount < PyList_Size(myList); matchCount++) {
    PyObject *tuple = PyList_GetItem(myList, matchCount);
    lr = -1, lg = -1, lb = -1, hr = 255, hg = 255, hb = 255, outChannel = 0;
    if (!PyArg_ParseTuple(tuple, "|iiiiiii", &lr, &lg, &lb, &hr, &hg, &hb, &outChannel)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: matchList");
      return NULL;
    }
    ranges[matchCount][0] = lr;
    ranges[matchCount][1] = lg;
    ranges[matchCount][2] = lb;
    ranges[matchCount][3] = hr;
    ranges[matchCount][4] = hg;
    ranges[matchCount][5] = hb;
    ranges[matchCount][6] = outChannel;
  }
  for(int h=0;h<height;h++) {
    for(int w=0;w<width;w++) {
      matchOne = 0;
      for (int matchCount = 0; matchCount < PyList_Size(myList); matchCount++) {
	lr = ranges[matchCount][0];
	lg = ranges[matchCount][1];
	lb = ranges[matchCount][2];
	hr = ranges[matchCount][3];
	hg = ranges[matchCount][4];
	hb = ranges[matchCount][5];
	outChannel = ranges[matchCount][6];
	if (
	    (lr == -1 || 
	     (Image[(h * width + w) * depth + rgb[RED]] >= lr && 
	      Image[(h * width + w) * depth + rgb[RED]] <= hr))
	    &&
	    (lg == -1 || 
	     (Image[(h * width + w) * depth + rgb[GREEN]] >= lg && 
	      Image[(h * width + w) * depth + rgb[GREEN]] <= hg))
	    &&
	    (lb == -1 ||
	     (Image[(h * width + w) * depth + rgb[BLUE]] >=  lb && 
	      Image[(h * width + w) * depth + rgb[BLUE]] <= hb))
	    ) {
	  /* maybe add a normalizer here so the outputs are 
	     between 100-255ish for more varied usage? */
	  matchOne++;
	  lastOut = outChannel; // last out channel to match
	}
      }
      if (matchOne) { // if at least one matched
	matches++;
	if (lastOut == ALL) {
	  for (int d = 0; d < depth; d++) {
	    Image[(h * width + w) * depth + d ] = 255;
	  }
	} else {
	  for (int d = 0; d < depth; d++) {
	    Image[(h * width + w) * depth + d ] = 0;
	  }
	  Image[(h * width + w) * depth + rgb[lastOut] ] = 255;
	}
      } else { // no match
	// leave alone for now
      }
    }
  }
  return Py_BuildValue("i", matches);
}

PyObject *Vision::continueMovie() {
  movieMode = 1;
  return PyInt_FromLong(0L);
}

PyObject *Vision::stopMovie() {
  movieMode = 0;
  return PyInt_FromLong(0L);
}

PyObject *Vision::startMovie(char *filename) {
  movieCounter = 0;
  strcpy(movieFilename, filename);
  movieMode = 1;
  return PyInt_FromLong(0L);
}

PyObject *Vision::saveImage(char *filename) {
  int i, j;
  FILE *fptr;
  if (0 != rgb[0])
    swapPlanes(0, rgb[0]);
  if ((fptr=fopen(filename, "wb+"))==NULL)
    {
      PyErr_SetString(PyExc_TypeError, 
		      "Unable to open file");
      return NULL;
    }
  else
    {
      fprintf(fptr, "P6\n%d %d\n 255\n", width, height);
      fwrite(Image, (width * height * depth), 1, fptr);
      fclose(fptr);
    }
  if (0 != rgb[0])
    swapPlanes(0, rgb[0]);
  return PyInt_FromLong(0L);
} 

PyObject *Vision::drawRect(int x1, int y1, int x2, int y2, 
			   int fill, int channel) {
  if (x1 > x2)
    SWAP(x1, x2);
  if (y1 > y2)
    SWAP(y1, y2);
  x2 = MAX(MIN(width - 1, x2),0);
  y2 = MAX(MIN(height - 1, y2),0);
  for(int w=x1; w<=x2; w++) {
      for(int h=y1; h<=y2; h++ ) {
	if (fill == 1 || ((h == y1) || (h == y2) ||
			  (w == x1) || (w == x2)))
	  if (channel == ALL)
	    for(int d=0; d<depth; d++) {
	      Image[(h * width + w) * depth + d] = 255;
	    }
	  else if (channel == BLACK)
	    for(int d=0; d<depth; d++) {
	      Image[(h * width + w) * depth + d] = 0;
	    }
	  else
	    Image[(h * width + w) * depth + rgb[channel]] = 255;
      }
  }
  return PyInt_FromLong(0L);
}

PyObject *Vision::drawCross(int x1, int y1, int length, int channel) {
  int startX = x1 - length/2;
  int startY = y1 - length/2;
  int stopX = x1 + length/2;
  int stopY = y1 + length/2;
  int pos = 0;
  for(int w=startX; w<=stopX; w++) {
    if (channel == ALL) {
      for(int d=0; d<depth; d++) {
	pos = (y1 * width + w) * depth + d;
	if (pos < (((height - 1) * width) + (width - 1)) * depth + 2) {
	  Image[pos] = 255;
	}
      }
    } else {
      pos = (y1 * width + w) * depth + rgb[channel];
      if (pos < (((height - 1) * width) + (width - 1)) * depth + 2) {
	Image[pos] = 255;
      }
    }
  }
  for(int h=startY; h<=stopY; h++ ) {
    if (channel == ALL) {
      for(int d=0; d<depth; d++) {
	pos = (h * width + x1) * depth + d;
	if (pos < (((height - 1) * width) + (width - 1)) * depth + 2) {
	  Image[pos] = 255;
	}
      }
    } else {
      pos = (h * width + x1) * depth + rgb[channel];
      if (pos < (((height - 1) * width) + (width - 1)) * depth + 2)
	Image[pos] = 255;
    }
  }
  return PyInt_FromLong(0L);
}

PyObject *Vision::histogram(int x1, int y1, int x2, int y2, int bins) {
  int b, d;
  long int **binCnt;
  long int **binAvg;
  long int *maxAvg;
  long int *maxCnt;
  // DON'T ASSUME THAT bin count won't change. Reallocate these.
  // OR make a maximum size, and just leave them here.
  binCnt = new long int *[depth];
  binAvg = new long int *[depth];
  maxAvg = new long int[depth];
  maxCnt = new long int[depth];
  for (d = 0; d < depth; d++) {
    binCnt[d] = new long int[bins];
    binAvg[d] = new long int[bins];
    maxAvg[d] = 0;
    maxCnt[d] = 0;
    for (b = 0; b < bins; b++) {
      binCnt[d][b] = 0;
      binAvg[d][b] = 0;
    }
  }
  // First, make a histogram:
  for (int w = x1; w <= x2; w++) {
    for (int h = y1; h <= y2; h++) {
      for (int d = 0; d < depth; d++) {
	int bin = int(Image[(h * width + w) * depth + d] / 256.0 * bins);
	binAvg[d][ bin ] += Image[(h * width + w) * depth + d];
	binCnt[d][ bin ]++;
      }
    }
  }
  // Compute avg, and remember best:
  for (d = 0; d < depth; d++) {
    for (b = 0; b < bins; b++) {
      if (binCnt[d][b]) {
	binAvg[d][b] /= binCnt[d][b];
      }
      if (binCnt[d][b] > maxCnt[d]) {
	maxAvg[d] = binAvg[d][b];
	maxCnt[d] = binCnt[d][b];
      }
    }
  }
  PyObject *histList = PyList_New( bins );
  for (int i = 0; i < bins; i++) {
    PyList_SetItem(histList, i, Py_BuildValue("(iii)(iii)", 
					      binAvg[rgb[0]][i], 
					      binAvg[rgb[1]][i], 
					      binAvg[rgb[2]][i],
					      binCnt[rgb[0]][i], 
					      binCnt[rgb[1]][i], 
					      binCnt[rgb[2]][i] ));
  }
  PyObject *retval = Py_BuildValue("O(iii)", 
				   histList,
				   maxAvg[rgb[0]],
				   maxAvg[rgb[1]],
				   maxAvg[rgb[2]] );
  // clean up
  for (d = 0; d < depth; d++) {
    delete [] binCnt[d];
    delete [] binAvg[d];
  }
  delete [] binCnt;
  delete [] binAvg;
  delete [] maxAvg;
  delete [] maxCnt;
  return retval;
}

PyObject *Vision::grayScale() {
  int x, y, d, value;
  for (y=0; y<height; y++)
    for(x=0; x<width; x++)
      {
	value = 0;
	for (d = 0; d < depth; d++) {
	  value += (int)Image[(x+y*width)*depth + d];
	}
	value /= depth;
	for (d = 0; d < depth; d++) {
	  Image[(x+y*width)*depth + d]= value;
	}
      }
  return PyInt_FromLong(0L);
}

PyObject *Vision::threshold(int channel, int value) {
  int x, y;
  for (y=0; y<height; y++)
    for(x=0; x<width; x++) {
      if (channel == ALL) { // white
	if ((Image[(x+y*width)*depth + 0] >= value) &&
	    (Image[(x+y*width)*depth + 1] >= value) &&
	    (Image[(x+y*width)*depth + 2] >= value)) {
	  Image[(x+y*width)*depth + 0] = 255;
	  Image[(x+y*width)*depth + 1] = 255;
	  Image[(x+y*width)*depth + 2] = 255;
	} else {
	  int sum = Image[(x+y*width)*depth + 0] + Image[(x+y*width)*depth + 1] + Image[(x+y*width)*depth + 2];
	  int avg = sum / 3;
	  if (((abs(Image[(x+y*width)*depth + 0] - avg) > 20) ||
	       (abs(Image[(x+y*width)*depth + 1] - avg) > 20) ||
	       (abs(Image[(x+y*width)*depth + 2] - avg) > 20) ||
	       (avg > 155))) {
	    Image[(x+y*width)*depth + 0] = 255;
	    Image[(x+y*width)*depth + 1] = 255;
	    Image[(x+y*width)*depth + 2] = 255;
	  } else {
	    Image[(x+y*width)*depth + 0] = 0;
	    Image[(x+y*width)*depth + 1] = 0;
	    Image[(x+y*width)*depth + 2] = 0;
	  }
	}
      } else if (channel == BLACK) { // black
	if ((Image[(x+y*width)*depth + 0] <= value) &&
	    (Image[(x+y*width)*depth + 1] <= value) &&
	    (Image[(x+y*width)*depth + 2] <= value)) {
	  //int sum = Image[(x+y*width)*depth + 0] + Image[(x+y*width)*depth + 1] + Image[(x+y*width)*depth + 2];
	  //int avg = sum / 3;
	  //if ((abs(Image[(x+y*width)*depth + 0] - avg) < 20) &&
	  //    (abs(Image[(x+y*width)*depth + 1] - avg) < 20) &&
	  //    (abs(Image[(x+y*width)*depth + 2] - avg) < 20)) {
	  Image[(x+y*width)*depth + 0] = 0;
	  Image[(x+y*width)*depth + 1] = 0;
	  Image[(x+y*width)*depth + 2] = 0;
	  //} else {
	  //Image[(x+y*width)*depth + 0] = 255;
	  //Image[(x+y*width)*depth + 1] = 255;
	  //Image[(x+y*width)*depth + 2] = 255;
	  //}
	} else {
	  Image[(x+y*width)*depth + 0] = 255;
	  Image[(x+y*width)*depth + 1] = 255;
	  Image[(x+y*width)*depth + 2] = 255;
	}
      } else {
	if (Image[(x+y*width)*depth + rgb[channel]] >= value) {
	  Image[(x+y*width)*depth + rgb[channel]] = 255;
	} else {
	  Image[(x+y*width)*depth + rgb[channel]] = 0;
	}
      }
    }
  return PyInt_FromLong(0L);
}

PyObject *Vision::inverse(int channel) {
  int x, y;
  for (y=0; y<height; y++)
    for(x=0; x<width; x++) {
      Image[(x+y*width)*depth + rgb[channel]] = 255 - Image[(x+y*width)*depth + rgb[channel]];
    }
  return PyInt_FromLong(0L);
}

PyObject *Vision::sobel(int thresh) {
  int i, j, offset;
  unsigned int tempx, tempy;
  unsigned char *ImagePtr;
  unsigned char *out;
  
  unsigned int a,b,d,f,g,z,c,e,h,gc, sobscale;
  int k, pos, index = 0, dis, count=0, pi = 0;
  int ps[width][2], p[4];

  out = (unsigned char *)malloc(sizeof(char)*width*height*depth);
    
  ImagePtr = Image;
  
  for (j=0;j<height*width*depth;j++)
    out[j]=0;

  offset = 0;
  sobscale = 1;

  i = j = 0;
  
  for (j=0;j<height-2;j++)
  {
    a = Image[(j*width+i)*depth];
    b = Image[(j*width+(i+1))*depth];
    d = Image[((j+1)*width+i)*depth];
    f = Image[((j+2)*width+i)*depth];
    g = Image[((j+2)*width+(i+1))*depth];
    z = Image[(j*width+i)*depth];
    
    for (i=0;i<width-2;i++) 
    {
      c = Image[(j*width+(i+2))*depth];
      e = Image[((j+1)*width+(i+2))*depth];
      h = Image[((j+2)*width+(i+2))*depth];

      tempx = (a+d+f) - (c+e+h);
      if( tempx < 0 ) tempx = -1*tempx;
      
      tempy = (a+b+c) - (f+g+h);
      if( tempy < 0 ) tempy = -1*tempy;

      gc = (unsigned int) (sobscale * sqrt(tempx*tempx+tempy*tempy));
      gc = offset+gc;
      gc = (gc>255)? 0 : 255 - gc;

      out[(j*width+i)*depth] = gc;
      out[(j*width+i)*depth+1] = gc;
      out[(j*width+i)*depth+2] = gc;

      a=b;
      b=c;
      d=z;
      f=g;
      g=h;
      z=e;

    }
    i=0;
  }

  ImagePtr = Image;
  for (j=0;j<height;j++)
    for (i=0;i<width;i++)
      for(offset=0;offset<depth;offset++)
	Image[(i+j*width)*depth+offset] = out[(i+j*width)*depth+offset] ;

  free(out);

  return PyInt_FromLong(0L);
}

int Vision::feql(int x, int y, double t){
  int dif = abs(x - y);

  if (dif < (x+y)/2*t)
    return 1;

  return 0;
}

PyObject *Vision::orientation(double current_height) {
  static unsigned char *orientmap = new unsigned char[width * height * depth];
  int x1, y1, x2, y2;
  double max_height = 1.75; // meters
  double percent = (current_height / max_height);
  int sum_count = 0;
  int threshold = 3;
  int pairs[MAX(width+1, height+1)][MAX(height/2, width/2)][2];
  int c_count[MAX(width+1, height+1)];
  x1 = (int)(width * (.1 + .25 * percent));  // between .1 and .35 percent off on each side
  y1 = (int)(height * (.1 + .25 * percent));
  x2 = (int)(width - width * (.1 + .25 * percent));
  y2 = (int)(height - height * (.1 + .25 * percent));
  drawRect(x1-2, y1-2, x2+2, y2+2, 0, BLACK); // 0 = fill, ALL=white
  drawRect(x1-1, y1-1, x2+1, y2+1, 0, ALL); // 0 = fill, ALL=white
  // --------------------------------------------------------------------------
  // Do across columns:
  pairs[0][0][0] = y1;
  pairs[0][0][1] = y2-1;
  c_count[0] = 1;
  for (int current = 0; current < x2-x1; current++) {
    c_count[current+1] = 0;
    for (int seg = 0; seg < c_count[current]; seg++){
      sum_count = 0;
      for(int y = pairs[current][seg][0]; y <= pairs[current][seg][1]; y++){
	if (Image[(y * width + current+x1) * depth + 0] < 100) {
	  Image[(y * width + current+x1) * depth + rgb[0]] = 255;
	  Image[(y * width + current+x1) * depth + rgb[1]] = 0;
	  Image[(y * width + current+x1) * depth + rgb[2]] = 0;
	  sum_count++;
	  if (sum_count == 1) {
	    pairs[current+1][c_count[current+1]][0] = MAX(y - 1, y1); // start
	    pairs[current+1][c_count[current+1]][1] = MIN(y + 1, y2); // end, might just be one pixel
	    c_count[current+1]++;
	  } else{
	    pairs[current+1][c_count[current+1]-1][1] = MIN(y + 1, y2); // overwrite end
	  }
	} else{ 
	  sum_count = 0;
	}
      }
      if (c_count[current+1] == 0 && current < (x2-x1)/2) { // none found
	// restart!
	pairs[current+1][c_count[current+1]][0] = y1; // start
	pairs[current+1][c_count[current+1]][1] = y2 - 1; // end, might just be one pixel
	c_count[current+1] = 1;
      } 
    }
  }
  // --------------------------------------------------------------------------
  // Do across rows:
  pairs[0][0][0] = x1;
  pairs[0][0][1] = x2-1;
  c_count[0] = 1;
  for (int current = 0; current < y2-y1; current++) {
    c_count[current+1] = 0;
    for (int seg = 0; seg < c_count[current]; seg++){
      sum_count = 0;
      for(int x = pairs[current][seg][0]; x <= pairs[current][seg][1]; x++){
	if (Image[((current + y1) * width + x) * depth + 0] < 100 || ((Image[((current + y1) * width + x) * depth + rgb[0]] == 255) &&
								      (Image[((current + y1) * width + x) * depth + rgb[1]] == 0) &&
								      (Image[((current + y1) * width + x) * depth + rgb[2]] == 0))) {
	  Image[((current + y1) * width + x) * depth + rgb[0]] = 255;
	  Image[((current + y1) * width + x) * depth + rgb[1]] = 0;
	  Image[((current + y1) * width + x) * depth + rgb[2]] = 0;
	  sum_count++;
	  if (sum_count == 1) {
	    pairs[current+1][c_count[current+1]][0] = MAX(x - 1, x1); // start
	    pairs[current+1][c_count[current+1]][1] = MIN(x + 1, x2); // end, might just be one pixel
	    c_count[current+1]++;
	  } else{
	    pairs[current+1][c_count[current+1]-1][1] = MIN(x + 1, x2); // overwrite end
	  }
	} else{ 
	  sum_count = 0;
	}
      }
      if (c_count[current+1] == 0 && current < (y2-y1)/2) { // none found
	// restart!
	pairs[current+1][c_count[current+1]][0] = x1; // start
	pairs[current+1][c_count[current+1]][1] = x2 - 1; // end, might just be one pixel
	c_count[current+1] = 1;
      } 
    }
  }
  return PyInt_FromLong(sum_count);
}

PyObject *Vision::fid(int thresh) {
  int i, j, offset;
  unsigned int tempx, tempy;
  unsigned char *ImagePtr;
  static unsigned char *out = (unsigned char *)malloc(sizeof(char)*width*height*depth);
  
  unsigned int a,b,d,f,g,z,c,e,h,gc, sobscale;

  ImagePtr = Image;
  
  for (j=0;j<height*width*depth;j++)
    out[j]=0;

  offset = 0;
  sobscale = 1;

  i = j = 0;
  
  for (j=0;j<height-2;j++)
  {
    a = Image[(j*width+i)*depth];
    b = Image[(j*width+(i+1))*depth];
    d = Image[((j+1)*width+i)*depth];
    f = Image[((j+2)*width+i)*depth];
    g = Image[((j+2)*width+(i+1))*depth];
    z = Image[(j*width+i)*depth];
    
    for (i=0;i<width-2;i++) 
    {
      c = Image[(j*width+(i+2))*depth];
      e = Image[((j+1)*width+(i+2))*depth];
      h = Image[((j+2)*width+(i+2))*depth];

      tempx = (a+d+f) - (c+e+h);
      if( tempx < 0 ) tempx = -1*tempx;
      
      tempy = (a+b+c) - (f+g+h);
      if( tempy < 0 ) tempy = -1*tempy;

      gc = (unsigned int) (sobscale * sqrt(tempx*tempx+tempy*tempy));
      gc = offset+gc;
      gc = (gc>255)? 0 : 255 - gc;

      out[(j*width+i)*depth] = gc;
      out[(j*width+i)*depth+1] = gc;
      out[(j*width+i)*depth+2] = gc;

      a=b;
      b=c;
      d=z;
      f=g;
      g=h;
      z=e;

    }
    i=0;

  }

  // center x, center y, and number of dots
  int cx=0, cy=0, numdots = 0;


  int k, pos, starti = -1;
  // array to hold pairs of positions that mark the start and end of a box
  int ps[width][2]; 
  // used to index the ps array, hope for 4, maybe less
  int index = 0;    

  // black level should be 0, but set to 20. Set higher if black appears to
  // be washed out
  // of is an offset for how many pixels I am skiping at each side, i.e.
  // for each line, I skip a certain number of pixels at the beginning and
  // the end.
  int black = 20, of = 20, white = 255;

  // min: minimum width of a box, set to width/12
  // max: maximum width of a box, set to width/2
  // multiply by 3 is necessary
  double min = width/12*3, max = width/2*3;

  int w, previous, maxwidth = 0, boxwidth = 0, maxboxwidth = 0;
  
  for (k=0; k<width; k++)
    ps[k][0] = ps[k][1] = -1;  

  for (i=0; i<height; i++) {
    if ((starti != -1) && (i-starti > maxboxwidth))
      break;
    
    for (k=0; k<index; k++)
      ps[k][0] = ps[k][1] = -1;  

    index = 0;
    boxwidth = 0;

    for (j=of; j<width-of; j++) {
      pos = (i*width+j)*depth;
      if (out[pos] < black && out[pos+1] < black && out[pos+2] < black) {
	if (ps[index][0] == -1)
	  ps[index][0] = pos;
	else if (ps[index][1] == -1) {
	  if ((pos - ps[index][0]) > min && 
	      (pos - ps[index][0]) < max ) {
	    ps[index][1] = pos;
	    ps[++index][0] = pos;

	  }
	  else
	    ps[index][0] = pos;
	}
      }
    }

    int colors[6][3] = {{0, 0, 255},             //blue
			{0, 255, 0},             //green
			{255, 0, 0},             //red
			{0, 255, 255},           //cyan
			{255, 0, 255},           //magenta
			{255, 255, 0}};          //yellow
    int ci = 0;

    if (index >2) {
      for (j=0; j<index; j++) {
	w = 0;
	previous = 0;
	if (ci > 5)
	  ci = 0;

	boxwidth += (ps[j][1] - ps[j][0])/3;

	for (k=ps[j][0]; k<=ps[j][1]; k=k+3) {
	  if (Image[k] != Image[k+1] || Image[k+1] != Image[k+2] ||
	    (Image[k]<white && Image[k+1]<white && Image[k+2]<white)) {
	    out[k] = colors[ci][0];
	    out[k+1] = colors[ci][1];
	    out[k+2] = colors[ci][2];
	    
	    if (k - previous == 3)
	      w++;
	    previous = k;
	  }
	}
	if (w > maxwidth)
	  maxwidth = w;
	ci++;
      }
      boxwidth /= index;
      if (boxwidth > maxboxwidth) {
	if (starti == -1)
	  starti = i;
	maxboxwidth = boxwidth;
	cy = i;
	cx = ((ps[index-1][1] - ps[0][0])/2 + ps[0][0])/3 - i*width;
      }
    }

  }

  int dotw = maxboxwidth/3;

  if (maxwidth > dotw*2 ) 
    numdots = 3;
  else if (maxwidth > dotw)
    numdots = 2;
  else if (maxwidth > dotw/2)
    numdots = 1;

  //printf("%d %d %d\n", cx, cy, numdots);



  ImagePtr = Image;
  for (j=0;j<height;j++)
    for (i=0;i<width;i++) {
      if (j == cy || i == cx) {
	Image[(i+j*width)*depth] = 0;
	Image[(i+j*width)*depth+1] = 255;
	Image[(i+j*width)*depth+2] = 255;
	continue;
      }
      for(offset=0;offset<depth;offset++)
	Image[(i+j*width)*depth+offset] = out[(i+j*width)*depth+offset] ;
    }
  //  free(out);
  
  PyObject *tuple = PyTuple_New(3);
  PyTuple_SetItem(tuple, 0, Py_BuildValue("i", cx));
  PyTuple_SetItem(tuple, 1, Py_BuildValue("i", cy));
  PyTuple_SetItem(tuple, 2, Py_BuildValue("i", numdots));
  return tuple; 
 
  return PyInt_FromLong(0L);
}

PyObject *Vision::medianBlur(int kernel) {
  int mid;
  int w,h,i,j,x, moveVal, offset, temp=0;
  int median[4][400] = {{-1}};  /*enough for 20x20(huge) Kernel */
  int intensity = 3;
  unsigned char *ptr, *outptr, *imagePtr;
  static unsigned char *out = new unsigned char[width * height * depth];

  if(kernel <= 0)
    kernel = 1;
  else if(kernel % 2 == 0) 
    kernel--;
  
  x=(int)kernel/2;
  
  moveVal = x*width+x;

  imagePtr = Image+(moveVal)*3;
  outptr = out+(moveVal)*3;
  
  for (j=0;j<height*width*depth;j++)
    out[j]=0;

  offset = 0;

  for(h=x;h<height-x;h++)
    {
      for(w=x;w<width-x;w++,imagePtr+=3,outptr+=3)
	{
	  ptr=imagePtr-(moveVal)*3;
	  temp=0;
	 
	  /* find middle color of surrouding pixels */
	  for(i=0;i<kernel;i++)
	    {
	      for(j=0;j<kernel;j++,ptr+=3,temp++)
		{
		  median[BLUE][temp]  = *(ptr);
		  median[GREEN][temp] = *(ptr+1);
		  median[RED][temp]  = *(ptr+2);
		  median[intensity][temp]=(int) (0.3*(*(ptr+2)) + 0.59*(*(ptr+1)) + 0.11*(*(ptr)));
		}
	      /* bring ptr to next row */
	      ptr=ptr-(kernel*3);
	      ptr=ptr+width*3; /* bring ptr to next row */
	    }
	  
	  /* get median intensity index */
	  mid=getMiddleIndex(median, kernel);

	  *outptr = median[BLUE][mid];
	  *(outptr+1) = median[GREEN][mid];
	  *(outptr+2) = median[RED][mid];

	}
    }

  imagePtr = Image;
  outptr = out;
  for (j=0;j<height;j++)
    for (i=0;i<width;i++)
      for(offset=0;offset<depth;offset++)
	Image[(i+j*width)*depth+offset] = outptr[(i+j*width)*depth+offset] ;

  return PyInt_FromLong(0L);
}

int Vision::getMiddleIndex(int median[4][400], int kernel) {
  int i,j;
  int rankTable[400];
  
  for(i=0; i<kernel*kernel; i++)
    rankTable[i] = i;
  
  for(i=0; i < kernel*kernel; i++)
    for(j=i+1; j< kernel*kernel; j++)
      if(median[3][rankTable[i]] > median[3][rankTable[j]])
	SWAP(rankTable[i],rankTable[j]);
  
  return(rankTable[(int)((kernel*kernel)/2)]);
}

PyObject *Vision::meanBlur(int kernel) {
  int w,h,i,j,side,d;
  unsigned int average[3]={0};
  
  if(kernel <= 0)
    kernel = 1;
  else if(kernel % 2 == 0) 
    kernel--;
  
  side=(int)kernel/2;
  
  for(h=side;h<height-side;h++)
    {
      for(w=side;w<width-side;w++)
	{
	  /* calculate average color of surrounding pixels*/
	  for(i=-side;i<=side;i++)
	    for(j=-side;j<=side;j++)
	      for(d=0;d<depth;d++)
		average[d] += Image[((h+i)* width + (w + j)) * depth + d];
	  
	  
	  for(d=0;d<depth;d++)
	    Image[(h * width + w) * depth + d] = average[d] / (kernel*kernel);
	  
	  average[0] = 0;
	  average[1] = 0;
	  average[2] = 0;
	}
    }
  return PyInt_FromLong(0L);
}

// ----------------------- Blob Functions ------------------

Blob *Vision::initBlob(Blob *b) {
  b->mass = 0;
  b->ul.x = 0;
  b->ul.y = 0;
  b->lr.x = 0;
  b->lr.y = 0;
  b->cm.x = 0;
  b->cm.y = 0;
  b->next = 0;  
  return(b);
}

Blob *Vision::initBlob( Blob *b, int y, int x )
{
  b->mass = 1;
  b->ul.x=x;
  b->ul.y=y;
  b->lr.x=x;
  b->lr.y=y;
  b->cm.x=x;
  b->cm.y=y;
  b->next = 0;
  return (b);
}

Blob *Vision::addPixel( Blob *b, int y,int x )
{
  if( x < b->ul.x )
    b->ul.x = x;  
  if( x > b->lr.x )
    b->lr.x = x;
  if( y < b->ul.y )
    b->ul.y = y;
  if( y > b->lr.y )
    b->lr.y = y;
  /* not correct */
  /*b->cm.x =( (float)(b->mass * b->cm.x + x) / (float)(b->mass+1) );
    b->cm.y =( (float)(b->mass * b->cm.y + y) / (float)(b->mass+1) );*/
  b->mass++;
  return (b);
}

void Vision::joinBlob( Blob *self, Blob *other )
{
  if(self->mass != 0 && other->mass != 0)
    {
      if( other->ul.x < self->ul.x )
	self->ul.x = other->ul.x;
      
      if( other->lr.x > self->lr.x )
	self->lr.x = other->lr.x ;
      
      if( other->ul.y < self->ul.y )
	self->ul.y = other->ul.y;
      
      if( other->lr.y > self->lr.y )
	self->lr.y = other->lr.y;
      
      /* Not Correct */
      /*
	self->cm.x=( (self->mass * self->cm.x + other->mass * other->cm.x )/
	(self->mass + other->mass));
	self->cm.y=( (self->mass * self->cm.y + other->mass * other->cm.y)/
	(self->mass + other->mass));
      */ 
      self->mass += other->mass;      
      other->mass = 0;
    }
}

void Vision::deleteBlob( Blob *b )
{
  
  b->cm.x = 0;
  b->cm.y = 0;
  b->ul.x = 0;
  b->ul.y = 0;
  b->lr.x = 0;
  b->lr.x = 0;
  b->mass = 0;
  
}

int Vision::getBlobWidth( Blob *b )
{
  return( b->lr.x - b->ul.x );
}

int Vision::getBlobHeight( Blob *b )
{
  return( b->lr.y - b->ul.y );
}

int Vision::getBlobArea( Blob *b )
{
  return( getBlobWidth( b ) * getBlobHeight( b ) );
}

/* not correct, 1 pixel is very dense.  */
/*
  float getBlobDensity( Blob *b )
  {
  return( (float)b->mass / (float)getBlobArea( b ) );
  }
*/


void Vision::sortBlobs(int sortMethod, Blob bloblist[], 
		       int indexes[], int size)
{
  int i,j;
  int rankTable[MAXBLOBS];
  
  
  for(i=0; i<MAXBLOBS; i++)
    rankTable[i] = i;
  
  switch(sortMethod)
    {
      
    case 0:/* Mass */
      for(i=1; i < size+1; i++)
	for(j=i+1; j< MAXBLOBS; j++)
	  if(bloblist[rankTable[i]].mass < bloblist[rankTable[j]].mass)
	    SWAP(rankTable[i],rankTable[j]);
      break;
      
    case 1: /* Area */
      for(i=1; i < size+1; i++)
	for(j=i+1; j< MAXBLOBS; j++)
	  /* automattically swap out 0 mass from i spot*/
	  if(bloblist[rankTable[i]].mass == 0 ||
	     (bloblist[rankTable[j]].mass != 0 &&
	      getBlobArea(&bloblist[rankTable[i]]) <
	      getBlobArea(&bloblist[rankTable[j]])))
	    SWAP(rankTable[i],rankTable[j]); 
      break;
    
    }
  
  for(i=1;i<size+1;i++)
    indexes[i-1]= rankTable[i];
  
}

PyObject *Vision::blobify(int inChannel, int low, int high, 
			  int sortmethod, 
			  int size, int drawBox, int super_color)
{
  /** 
      This code is a way to find the largest blob.  It will 
      combine blobs if there is more than one.  However, given
      the colors that we are using in the project, it is 
      unlikely that we'll have more than one blob with the 
      same color (unless the same object is split into multiple 
      regions by some other object)
      
      The function works by looking at the top and left pixel
      to see if there is already a blob there.  It joins or adds
      the pixel to the blob, and merges blobs if they are connected.
  **/
  
  Blob bloblist[MAXBLOBS];
  
  int w,h,n,m,i,j, k, l;
  int offset = 0, mark1 = 0, mark2 = 0;
  int count;
  int minBlobNum=0, maxBlobNum=0;

  int maxIndex[5]={0};
  static int **blobdata;
  static int initialized = 0;
  if (!initialized) {
    // ASSUMES height and width don't change!
    blobdata = new int*[width];
    for (i = 0; i < width; i++) {
      blobdata[i] = new int[height];
    }
    initialized = 1;
  }
  // Always need to initilize to zero
  for (i = 0; i < width; i++) {
    for (j = 0; j < height; j++)
      blobdata[i][j] = 0;
  }
  unsigned char *ImagePtr;
  
  if(inChannel == BLUE)
    {
      offset = rgb[2]; mark1 = rgb[0]; mark2 = rgb[1];
    }
  else if(inChannel == GREEN)
    {
      offset = rgb[1]; mark1 = rgb[0]; mark2 = rgb[2];
    }
  else if(inChannel == RED)
    {
      offset = rgb[0]; mark1 = rgb[1]; mark2 = rgb[2];
    }
  else
    perror("Invalid Channel\n");
  
  
  for(n=0;n<MAXBLOBS;n++)
    initBlob(&bloblist[n]);
  
  count = 1;
  
  ImagePtr = Image;

  /*build the blobmap and construct unjoined Blob objects*/
  for(h=0;h<height;h++)
    {
      for(w=0;w<width;w++,ImagePtr+=3)
	{
	  // either it is between low and high, or
	  if((!super_color && (*(ImagePtr+offset) >= low && *(ImagePtr+offset) <= high)) || 
	     (super_color && (*(ImagePtr+offset) - *(ImagePtr+mark1) - *(ImagePtr+mark2)) > 128))
	    {  
	      if(h == 0 && w == 0 && count < MAXBLOBS)
		{ /*in upper left corner - new blob */
		  initBlob(&bloblist[count],h,w);
		  blobdata[w][h]= count;
		  count++;
		}
	      else if(w == 0)/*if in first col */
		{
		  if( blobdata[w][h-1] != 0 )
		    {
		      addPixel(&bloblist[blobdata[w][h-1]],h,w);
		      blobdata[w][h]=blobdata[w][h-1];
		    }
		  else if (count < MAXBLOBS) /*above is off -- new blob*/
		    {
		      initBlob(&bloblist[count], h,w);		      
		      blobdata[w][h]=count;
		      count++;
		    }
		}
	      else if(h == 0) /* in first row */
		{
		  if( blobdata[w-1][h] != 0 )
		    {
		      addPixel(&bloblist[blobdata[w-1][h]],h,w);
		      blobdata[w][h]= blobdata[w-1][h];
		    }
		  else if (count < MAXBLOBS)  /* left is off -- new blob */
		    {
		      initBlob(&bloblist[count], h,w);
		      blobdata[w][h]=count;
		      count++;
		    }		    
		}
	      
	      else if( blobdata[w-1][h] != 0 && blobdata[w][h-1] != 0 )
		{
		  /*
		    see if the pixel to left and on the top are the same blob and add 
		    this new pixel to the blob if they are 
		  */
		  if(blobdata[w-1][h] == blobdata[w][h-1])
		    {
		      addPixel(&bloblist[blobdata[w-1][h]],h,w);
		      blobdata[w][h] = blobdata[w-1][h];
		    }
		  else 
		    {
		      addPixel(&bloblist[blobdata[w-1][h]],h,w);		      
		      joinBlob(&bloblist[blobdata[w-1][h]],&bloblist[blobdata[w][h-1]]);
		      blobdata[w][h] = blobdata[w-1][h];
		      
		      n = blobdata[w][h-1];		      
		      for(i=0;i<=h;i++)
			for(j=0;j<width;j++)
			  if(blobdata[j][i] == n)
			    blobdata[j][i] = blobdata[w-1][h];
		      
		      /*deleteBlob(&bloblist[blobdata[w][h-1]]);*/
		    }
		}
	      else
		{
		  if( blobdata[w-1][h] != 0 )
		    {
		      addPixel(&bloblist[blobdata[w-1][h]],h,w);		  
		      blobdata[w][h]=blobdata[w-1][h];		      
		    }
		  /*top is on -- old blob */
		  else if( blobdata[w][h-1] != 0 )
		    {		      
		      addPixel(&bloblist[blobdata[w][h-1]],h,w);
		      blobdata[w][h]=blobdata[w][h-1];
		    }
		  else if (count < MAXBLOBS) /* neither left or top on. -- new blob.*/
		    {
		      initBlob(&bloblist[count],h,w);		      
		      blobdata[w][h]=count;		      
		      count++;
		    }
		}
	    }
	}
    }

  sortBlobs(sortmethod, bloblist, maxIndex, size);

  if(drawBox)
    {
      for(i=0; i<height; i++ )
	for(j=0; j<width; j++)
	  for(k=0;k<size;k++) {
	    // change the color of the matching pixels:
	    //	    if(blobdata[j][i] == maxIndex[k]) {
	    //Image[(i * width + j) * depth + offset] = 0;
	    //Image[(i * width + j) * depth + mark1] = 255;
	    //Image[(i * width + j) * depth + mark2] = 0;
	    //}
	    if(bloblist[maxIndex[k]].mass > 0 )
	      if(((j >= bloblist[maxIndex[k]].ul.x && j <= bloblist[maxIndex[k]].lr.x) &&
		  (i == bloblist[maxIndex[k]].ul.y || i == bloblist[maxIndex[k]].lr.y)) ||
		 ((j == bloblist[maxIndex[k]].ul.x || j == bloblist[maxIndex[k]].lr.x) &&
		  (i >= bloblist[maxIndex[k]].ul.y && i <= bloblist[maxIndex[k]].lr.y)))
		{
		  Image[(i * width + j) * depth + offset] = 255;
		  Image[(i * width + j) * depth + mark1] = 255;
		  Image[(i * width + j) * depth + mark2] = 255;
		}
	  }
    }      
  
  PyObject *tuple = PyTuple_New( size );

  for (i = 0; i < size; i++) {
    PyTuple_SetItem(tuple, i, 
		    Py_BuildValue("iiiii",
				  bloblist[maxIndex[i]].ul.x,
				  bloblist[maxIndex[i]].ul.y,
				  bloblist[maxIndex[i]].lr.x,
				  bloblist[maxIndex[i]].lr.y,
				  bloblist[maxIndex[i]].mass));
  }
  return tuple; 
}  

PyObject *Vision::getFilterList() {
  Py_INCREF(filterList);
  return filterList;
}

PyObject *Vision::setFilterList(PyObject *newList) {
  if (!PyList_Check(newList)) {
    PyErr_SetString(PyExc_TypeError, "Invalid list to setFilters");
    return NULL;
  }
  Py_DECREF(filterList);
  filterList = newList;
  Py_INCREF(filterList);
  return PyInt_FromLong(0L);
}

PyObject *Vision::popFilterList() {
  int size = PyList_Size(filterList);
  if (size > 0) {
    PyObject *retval = PyList_GetItem(filterList, size - 1); 
    Py_INCREF(retval);
    PyList_SetSlice(filterList, size - 1, size, Py_BuildValue("[]"));
    return retval;
  } else {
    PyErr_SetString(PyExc_TypeError, "can't remove items from an empty list in popFilterList");
    return NULL;
  }
}

PyObject *Vision::addFilter(PyObject *newFilter) {
  //if (!PyList_Check(newFilter)) {
  //  PyErr_SetString(PyExc_TypeError, "Invalid filter to addFilter");
  //  return NULL;
  //}
  Py_INCREF(newFilter);
  PyList_Append(filterList, newFilter);
  return PyInt_FromLong(0L);
}

PyObject *Vision::gaussianBlur() {
  int offset,m1,m2;
  int x,y,temp;

  /******************************
    here it says image[(x-1)+(y+1)*width] 
    if it is changed to image[(x-depth+offset)+(y+depth)*width]
    it should work for rgb (or bgr as the case may be)
    -----------------------------------------------------
     this means we will probably need another for loop for
     offset, as we probably want to blur for all channels
     ---------------------------------------------------
       Get each of the surrounding pixels weighted value
       top, left, right, and bottom weighing 2x
       diagonals weighing 1x
       pixel itself weighing 4x
       and take the average
       --------------------------------------------
       I think *out is just the output buffer, which
       in this case we want to be *image, so I think all
       those parts can be omitted
  ******************************************/
  static unsigned char *out = new unsigned char [width * height * depth];
  for (y=1;y<height-1;y++)
    for (x=1;x<width-1;x++)
      for(offset=0;offset<depth;offset++)
      {
	temp=Image[(x-depth+offset+y*width)*depth+offset];
	temp+=2*Image[(x-depth+y*width)*depth+offset];
	temp+=Image[(x-depth+(y+1)*width)*depth+offset];
	temp+=2*Image[(x+(y-1)*width)*depth+offset];
	temp+=4*Image[(x+y*width)*depth+offset];
	temp+=2*Image[(x+(y+1)*width)*depth+offset];
	temp+=Image[(x+depth+offset+(y-1)*width)*depth+offset];
	temp+=2*Image[(x+depth+offset+y*width)*depth+offset];
	temp+=Image[(x+depth+offset+(y+1)*width)*depth+offset];
	temp/=16;
	out[(x+offset+y*width)*depth+offset] = temp;
      }

  for (y=1;y<height-1;y++)
    for (x=1;x<width-1;x++)
      for(offset=0;offset<depth;offset++)
      	Image[(x+y*width)*depth+offset] = out[(x+y*width)*depth+offset] ;
  
  return PyInt_FromLong(0L);
} 

PyObject *Vision::applyFilterList() {
  // This is called right after a call to camera.updateMMap()
  motionCount = 0;
  char buffer[50];
  PyObject *temp = applyFilters(filterList);
  if (movieMode) {
    sprintf(buffer, "%s-%05d.ppm", movieFilename, movieCounter);
    saveImage(&buffer[0]);
    movieCounter++;
  }
  return PyInt_FromLong(0L);
}

PyObject *Vision::backup() { 
  return copy(0, 0); // 0 backup, 1 restore
}

PyObject *Vision::restore() { 
  return copy(1, 0); // 0 backup, 1 restore
}

PyObject *Vision::motion(int threshold, int outChannel) { 
  static unsigned char *temp = new unsigned char[width * height * depth];
  int motionPixelCount = 0;
  if (motionCount >= MAXMOTIONLEVELS) {
    PyErr_SetString(PyExc_TypeError, "too many calls detecting motion; increase MAXMOTIONLEVELS in Vision.cpp");
    return NULL;
  }
  for (int w = 0; w < width; w++) {
    for (int h = 0; h < height; h++) {
      int totalDiff = 0;
      for (int d = 0; d < depth; d++) {
	totalDiff += abs(Image[(h * width + w) * depth + d] - motionArray[motionCount][(h * width + w) * depth + d]);
	// set it black:
	temp[(h * width + w) * depth + d] = 0;
      }
      // mark the outChannel bright if qualifies:
      if (totalDiff/3 > threshold) {
	temp[(h * width + w) * depth + rgb[outChannel]] = 255;
	motionPixelCount++;
      }
    }
  }
  // Copy current image to motion:
  memcpy(motionArray[motionCount], Image, width * height * depth);
  // Copy temp to current Image:
  memcpy(Image, temp, width * height * depth);
  // increase motion counter for next call:
  motionCount++;
  return PyInt_FromLong(motionPixelCount);
}

PyObject *Vision::hsv2rgb() {
  int R, G, B;
  double var_r, var_g, var_b;
  for (int w = 0; w < width; w++) {
    for (int h = 0; h < height; h++) {
      int H = Image[(h * width + w) * depth + rgb[0]];
      int S = Image[(h * width + w) * depth + rgb[1]];
      int V = Image[(h * width + w) * depth + rgb[2]];
      if (S == 0) {                      //HSV values = 0 ÷ 1
	R = int(V * 255.0);
	G = int(V * 255.0);
	B = int(V * 255.0);
      } else {
	double var_h = H * 6.0;
	double var_i = int( var_h );         //Or ... var_i = floor( var_h )
	double var_1 = V * ( 1.0 - S );
	double var_2 = V * ( 1.0 - S * ( var_h - var_i ) );
	double var_3 = V * ( 1.0 - S * ( 1 - ( var_h - var_i ) ) );
	if      (var_i == 0) { var_r = V    ; var_g = var_3; var_b = var_1; }
	else if (var_i == 1) { var_r = var_2; var_g = V    ; var_b = var_1; }
	else if (var_i == 2) { var_r = var_1; var_g = V    ; var_b = var_3; }
	else if (var_i == 3) { var_r = var_1; var_g = var_2; var_b = V;     }
	else if (var_i == 4) { var_r = var_3; var_g = var_1; var_b = V;     }
	else                 { var_r = V    ; var_g = var_1; var_b = var_2; }
	R = int(var_r * 255.0);                  //RGB results = 0 ÷ 255
	G = int(var_g * 255.0);
	B = int(var_b * 255.0);
	Image[(h * width + w) * depth + rgb[0]] = MAX(MIN(R,255),0);
	Image[(h * width + w) * depth + rgb[1]] = MAX(MIN(G,255),0);
	Image[(h * width + w) * depth + rgb[2]] = MAX(MIN(B,255),0);
      }
    }
  }
  return PyInt_FromLong(0L);
}

PyObject *Vision::rgb2hsv() {
  double H, S, V;
  for (int w = 0; w < width; w++) {
    for (int h = 0; h < height; h++) {
      H = 1; S = 1; V = 1;
      int R = Image[(h * width + w) * depth + rgb[0]];
      int G = Image[(h * width + w) * depth + rgb[1]];
      int B = Image[(h * width + w) * depth + rgb[2]];
      double var_R = (R / 255.0);   //RGB values = 0 ÷ 255
      double var_G = (G / 255.0);
      double var_B = (B / 255.0);
      double var_Min = MIN(MIN(var_R, var_G), var_B);    //Min. value of RGB
      double var_Max = MAX(MAX(var_R, var_G), var_B);    //Max. value of RGB
      double del_Max = var_Max - var_Min;             //Delta RGB value
      double V = var_Max;
      if (del_Max == 0) {                     //This is a gray, no chroma...
	H = 0;                                //HSV results = 0 ÷ 1
	S = 0;
      } else {                                   //Chromatic data...
	S = del_Max / var_Max;
	double del_R = (((var_Max - var_R) / 6.0) + (del_Max / 2.0))/del_Max;
	double del_G = (((var_Max - var_G) / 6.0) + (del_Max / 2.0))/del_Max;
	double del_B = (((var_Max - var_B) / 6.0) + (del_Max / 2.0))/del_Max;
	if      (var_R == var_Max) H = del_B - del_G;
	else if (var_G == var_Max) H = (1.0 / 3.0) + del_R - del_B;
	else if (var_B == var_Max) H = (2.0 / 3.0) + del_G - del_R;
	if ( H < 0 ) H += 1;
	if ( H > 1 ) H -= 1;
      }
      Image[(h * width + w) * depth + rgb[0]] = int(MAX(MIN(H * 255,255),0));
      Image[(h * width + w) * depth + rgb[1]] = int(MAX(MIN(S * 255,255),0));
      Image[(h * width + w) * depth + rgb[2]] = int(MAX(MIN(V * 255,255),0));
    }
  }
  return PyInt_FromLong(0L);
}

PyObject *Vision::rgb2yuv() {
  for (int w = 0; w < width; w++) {
    for (int h = 0; h < height; h++) {
      int R = Image[(h * width + w) * depth + rgb[0]];
      int G = Image[(h * width + w) * depth + rgb[1]];
      int B = Image[(h * width + w) * depth + rgb[2]];
      int Y = int(0.299 * R + 0.587 * G + 0.114 * B);
      int U = int(-0.169 * R - 0.332 * G + 0.500 * B + 128);
      int V = int( 0.500 * R - 0.419 * G - 0.0813 * B + 128);
      Image[(h * width + w) * depth + rgb[0]] = MAX(MIN(Y,255),0);
      Image[(h * width + w) * depth + rgb[1]] = MAX(MIN(U,255),0);
      Image[(h * width + w) * depth + rgb[2]] = MAX(MIN(V,255),0);
    }
  }
  return PyInt_FromLong(0L);
}

PyObject *Vision::yuv2rgb() {
  for (int w = 0; w < width; w++) {
    for (int h = 0; h < height; h++) {
      int Y = Image[(h * width + w) * depth + rgb[0]];
      int U = Image[(h * width + w) * depth + rgb[1]];
      int V = Image[(h * width + w) * depth + rgb[2]];

      int R = int(Y + (1.4075 * (V - 128)));
      int G = int(Y - (0.3455 * (U - 128)) - (0.7169 * (V - 128)));
      int B = int(Y + (1.7790 * (U - 128)));
      Image[(h * width + w) * depth + rgb[0]] = MAX(MIN(R,255),0);
      Image[(h * width + w) * depth + rgb[1]] = MAX(MIN(G,255),0);
      Image[(h * width + w) * depth + rgb[2]] = MAX(MIN(B,255),0);
    }
  }
  return PyInt_FromLong(0L);
}

PyObject *Vision::mask(int channel) { 
  return copy(2, channel);
}

PyObject *Vision::copy(int fromto, int channel) { // 0 backup, 1 restore
  static unsigned char *backup = new unsigned char[width * height * depth];
  if (fromto == 0) { // backup
    memcpy(backup, Image, width * height * depth);
  } else if (fromto == 1) { // restore
    memcpy(Image, backup, width * height * depth);
  } else if (fromto == 2) { // mask the backup, and restore
    for (int w = 0; w < width; w++) {
      for (int h = 0; h < height; h++) {
	if (Image[(h * width + w) * depth + rgb[channel]] == 255) {
	  for (int d = 0; d < depth; d++) {
	    Image[(h * width + w) * depth + d] = backup[(h * width + w) * depth + d];
	  }
	}
      }
    }
  } else {
    PyErr_SetString(PyExc_TypeError, "Invalid argument to copy()");
    return NULL;
  }
  return PyInt_FromLong(0L);
}

PyObject *Vision::applyFilters(PyObject *newList) {
  PyObject *filter;
  if (!PyList_Check(newList)) {
    PyErr_SetString(PyExc_TypeError, "Invalid list to applyFilters");
    return NULL;
  }
  PyObject *retvals = PyList_New( PyList_Size(newList) );
  for (int i = 0; i < PyList_Size(newList); i++) {
    filter = PyList_GetItem(newList, i);
    PyList_SetItem(retvals, i, applyFilter( filter ));
  }
  return retvals;
}

int randomize(int range) {
  int amt = int(rand()/float(RAND_MAX) * range);
  if ((rand() / float(RAND_MAX)) <.5)
    return amt;
  else
    return -amt;
}

PyObject *Vision::addNoise(float percent, int range) {
  // Used to add noise to an image
  unsigned int thisPos;
  int counter = 0;
  int r;
  for (int h = 0; h < height; h++) {
    for (int w = 0; w < width; w++) {
      if ((rand()/float(RAND_MAX)) < percent) {
	counter++;
	thisPos = (h * width + w) * depth;
	r = randomize(range);
	Image[thisPos + rgb[0]] = MIN(MAX( Image[thisPos + rgb[0]] + r, 0), 255);
	Image[thisPos + rgb[1]] = MIN(MAX( Image[thisPos + rgb[1]] + r, 0), 255);
	Image[thisPos + rgb[2]] = MIN(MAX( Image[thisPos + rgb[2]] + r, 0), 255);
      }
    }
  }
  return Py_BuildValue("i", counter);
}

// For upside down cameras:
PyObject *Vision::rotate() {
  unsigned int thisPos;
  unsigned int otherPos;
  unsigned int temp;
  for (int h = 0; h < height/2; h++) {
    for (int w = 0; w < width; w++) {
      thisPos = (h * width + w) * depth;
      otherPos = (height * width * depth) - thisPos;
      for (int d=0; d<depth; d++) {
	temp = Image[thisPos + d];
	Image[thisPos + d] = Image[otherPos - depth + d];
	Image[otherPos - depth + d] = temp;
      }
    }
  }
  if ((height % 2) == 1) { // if odd, do the middle row
    for (int w = 0; w < width/2; w++) {
      thisPos = ((height/2) * width + w) * depth;
      otherPos = (height * width * depth) - thisPos;
      for (int d=0; d<depth; d++) {
	temp = Image[thisPos + d];
	Image[thisPos + d] = Image[otherPos - depth + d];
	Image[otherPos - depth + d] = temp;
      }
    }
  }
  return PyInt_FromLong(0L);
}

PyObject *Vision::swapPlanes(int d1, int d2) {
  for (int h = 0; h < height; h++) {
    for (int w = 0; w < width; w++) {
      unsigned int temp = Image[(h * width + w) * depth + d1];
      Image[(h * width + w) * depth + d1] = Image[(h * width + w) * depth + d2];
      Image[(h * width + w) * depth + d2] = temp;
    }
  }
  return PyInt_FromLong(0L);
}

PyObject *Vision::getMenu() {
  PyObject *menu = PyList_New( 0 );
  PyList_Append(menu, Py_BuildValue("sss", "Blur", "meanBlur", "meanBlur"));
  PyList_Append(menu, Py_BuildValue("sss", "Blur", "gaussianBlur", "gaussianBlur"));
  PyList_Append(menu, Py_BuildValue("sss", "Blur", "medianBlur", "medianBlur"));
  PyList_Append(menu, Py_BuildValue("sssiiiiiii", "Blobify", "Red", "blobify", 0, 255, 255, 0, 1, 1, 1));
  PyList_Append(menu, Py_BuildValue("sssiiiiiii", "Blobify", "Green", "blobify", 1, 255, 255, 0, 1, 1, 1));
  PyList_Append(menu, Py_BuildValue("sssiiiiii", "Blobify", "Blue", "blobify", 2, 255, 255, 0, 1, 1, 1));
  PyList_Append(menu, Py_BuildValue("sssii", "Clear", "Red to   0", "setPlane", 0, 0));
  PyList_Append(menu, Py_BuildValue("sssii", "Clear", "Red to 128", "setPlane", 0, 128));
  PyList_Append(menu, Py_BuildValue("sssii", "Clear", "Red to 255", "setPlane", 0, 255));
  PyList_Append(menu, Py_BuildValue("sssii", "Clear", "Green to   0", "setPlane", 1, 0));
  PyList_Append(menu, Py_BuildValue("sssii", "Clear", "Green to 128", "setPlane", 1, 128));
  PyList_Append(menu, Py_BuildValue("sssii", "Clear", "Green to 255", "setPlane", 1, 255));
  PyList_Append(menu, Py_BuildValue("sssii", "Clear", "Blue to  0", "setPlane", 2, 0));
  PyList_Append(menu, Py_BuildValue("sssii", "Clear", "Blue to 128", "setPlane", 2, 128));
  PyList_Append(menu, Py_BuildValue("sssii", "Clear", "Blue to 255", "setPlane", 2, 255));
  PyList_Append(menu, Py_BuildValue("sssiiiii", "Supercolor", "Red", "superColor", 1, -1, -1, 0, 128));
  PyList_Append(menu, Py_BuildValue("sssiiiii", "Supercolor", "Green", "superColor", -1, 1, -1, 1, 128));
  PyList_Append(menu, Py_BuildValue("sssiiiii", "Supercolor", "Blue", "superColor", -1, -1, 1, 2, 128));
  PyList_Append(menu, Py_BuildValue("sssi", "Threshold", "Red", "threshold", 0));
  PyList_Append(menu, Py_BuildValue("sssi", "Threshold", "Green", "threshold", 1));
  PyList_Append(menu, Py_BuildValue("sssi", "Threshold", "Blue", "threshold", 2));
  PyList_Append(menu, Py_BuildValue("sssii", "Threshold", "White", "threshold", ALL, 200));
  PyList_Append(menu, Py_BuildValue("sssii", "Threshold", "Black", "threshold", BLACK, 20));
  PyList_Append(menu, Py_BuildValue("sssi", "Inverse", "Red", "inverse", 0));
  PyList_Append(menu, Py_BuildValue("sssi", "Inverse", "Green", "inverse", 1));
  PyList_Append(menu, Py_BuildValue("sssi", "Inverse", "Blue", "inverse", 2));
  PyList_Append(menu, Py_BuildValue("sss", "Copy", "Backup", "backup"));
  PyList_Append(menu, Py_BuildValue("sss", "Copy", "Restore", "restore"));
  PyList_Append(menu, Py_BuildValue("sss", "Detect", "Edges (sobel)", "sobel"));  
  PyList_Append(menu, Py_BuildValue("sss", "Detect", "Fiducials", "fid"));
  PyList_Append(menu, Py_BuildValue("sssf", "Detect", "Line orientation", "orientation", 1.0));
  PyList_Append(menu, Py_BuildValue("sssii", "Detect", "Motion", "motion", 30, 0));

  PyList_Append(menu, Py_BuildValue("sssiiiii", "Match", "By Tolerance", "match", 0, 0, 0, 30, 0));
  PyList_Append(menu, Py_BuildValue("sssiiiiiii", "Match", "By Range", "matchRange", 0, 0, 0, 255, 255, 255, 0));
  PyList_Append(menu, Py_BuildValue("sssiiiiiii", "Match", "By List of Ranges", "matchList", Py_BuildValue("[(iiiiiii)]", 0, 0, 0, 255, 255, 255, 0)));
  
  PyList_Append(menu, Py_BuildValue("sss", "Misc", "Gray scale", "grayScale"));
  PyList_Append(menu, Py_BuildValue("sss", "Misc", "Rotate", "rotate"));
  PyList_Append(menu, Py_BuildValue("sss", "Misc", "Swap planes", "swapPlanes", rgb[0], rgb[2]));
  PyList_Append(menu, Py_BuildValue("sssfi", "Misc", "Add noise", "addNoise", 0.05, 30));
  PyList_Append(menu, Py_BuildValue("sssi", "Misc", "Apply mask to backup", "mask", 0));
  PyList_Append(menu, Py_BuildValue("sss", "Misc", "RGB -> YUV", "rgb2yuv"));
  PyList_Append(menu, Py_BuildValue("sss", "Misc", "YUV -> RGB", "yuv2rgb"));
  //PyList_Append(menu, Py_BuildValue("sss", "Misc", "RGB -> HSV", "rgb2hsv"));
  //PyList_Append(menu, Py_BuildValue("sss", "Misc", "HSV -> RGB", "hsv2rgb"));
  PyList_Append(menu, Py_BuildValue("sssiiii", "Draw", "Box", "drawRect", 10, 10, 30, 30));
  PyList_Append(menu, Py_BuildValue("sssiii", "Draw", "Cross", "drawCross", 20, 20, 10));
  return menu;
}

PyObject *Vision::applyFilter(PyObject *filter) {
  int i1, i2, i3, i4, i5, i6, i7;
  float f1, f2, f3, f4, f5, f6, f7;
  PyObject *command, *list, *retval;
  if (!PyArg_ParseTuple(filter, "s|O", &command, &list)) {
    PyErr_SetString(PyExc_TypeError, "Invalid filter list name to applyFilters");
    return NULL;
  }
  // process filters here:
  if (strcmp((char *)command, "superColor") == 0) {
    f1 = 1.0, f2 = -1.0, f3 = -1.0, i1 = 0, i2 = 128;
    if (!PyArg_ParseTuple(list, "|fffii", &f1, &f2, &f3, &i1, &i2)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: superColor");
      return NULL;
    }
    retval = superColor(f1, f2, f3, i1, i2);
  } else if (strcmp((char *)command, "scale") == 0) {
    f1 = 1.0, f2 = 1.0, f3 = 1.0;
    if (!PyArg_ParseTuple(list, "|fff", &f1, &f2, &f3)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: scale");
      return NULL;
    }
    retval = scale(f1, f2, f3);
  } else if (strcmp((char *)command, "addNoise") == 0) {
    f1 = 0.05, i1 = 30;
    if (!PyArg_ParseTuple(list, "|fi", &f1, &i1)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: addNoise");
      return NULL;
    }
    retval = addNoise(f1, i1);
  } else if (strcmp((char *)command, "rotate") == 0) {
    retval = rotate();
  } else if (strcmp((char *)command, "meanBlur") == 0) {
    i1 = 3;
    if (!PyArg_ParseTuple(list, "|i", &i1)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: meanBlur");
      return NULL;
    }
    retval = meanBlur(i1);
  } else if (strcmp((char *)command, "medianBlur") == 0) {
    i1 = 3;
    if (!PyArg_ParseTuple(list, "|i", &i1)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: medianBlur");
      return NULL;
    }
    retval = medianBlur(i1);
  } else if (strcmp((char *)command, "gaussianBlur") == 0) {
    retval = gaussianBlur();
  } else if (strcmp((char *)command, "sobel") == 0) {
    i1 = 1;
    if (!PyArg_ParseTuple(list, "|i", &i1)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: sobel");
      return NULL;
    }
    retval = sobel(i1);
  } else if (strcmp((char *)command, "fid") == 0) {
    i1 = 1;
    if (!PyArg_ParseTuple(list, "|i", &i1)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: fid");
      return NULL;
    }
    retval = fid(i1);
  } else if (strcmp((char *)command, "orientation") == 0) {
    f1 = 1.0;
    if (!PyArg_ParseTuple(list, "|f", &f1)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: orientation");
      return NULL;
    }
    retval = orientation(f1);
  } else if (strcmp((char *)command, "setPlane") == 0) {
    i1 = 0; i2 = 0;
    if (!PyArg_ParseTuple(list, "|ii", &i1, &i2)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: setPlane");
      return NULL;
    }
    retval = setPlane(i1, i2);
  } else if (strcmp((char *)command, "set") == 0) {
    i1 = 0; i2 = 0, i3 = 255, i4 = 255, i5 = 255;
    if (!PyArg_ParseTuple(list, "|iiiii", &i1, &i2, &i3, &i4, &i5)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: set");
      return NULL;
    }
    retval = set(i1, i2, i3, i4, i5);
  } else if (strcmp((char *)command, "drawRect") == 0) {
    // x, y, x, y, fill, outChannel
    i1 = 10; i2 = 10; i3 = 30; i4 = 30; i5 = 0; i6 = ALL;
    if (!PyArg_ParseTuple(list, "|iiiiii", &i1, &i2, &i3, &i4, &i5, &i6)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: drawRect");
      return NULL;
    }
    retval = drawRect(i1, i2, i3, i4, i5, i6);
  } else if (strcmp((char *)command, "drawCross") == 0) {
    // x, y, size, outChannel
    i1 = 20; i2 = 20; i3 = 10; i4 = ALL;
    if (!PyArg_ParseTuple(list, "|iiii", &i1, &i2, &i3, &i4)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: drawCross");
      return NULL;
    }
    retval = drawCross(i1, i2, i3, i4);
  } else if (strcmp((char *)command, "swapPlanes") == 0) {
    // plane1, plane2 (red, blue)
    i1 = rgb[0]; i2 = rgb[2];
    if (!PyArg_ParseTuple(list, "|ii", &i1, &i2)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: swapPlanes");
      return NULL;
    }
    retval = swapPlanes(rgb[i1], rgb[i2]);
  } else if (strcmp((char *)command, "match") == 0) {
    i1 = 0; i2 = 0; i3 = 0; i4 = 30; i5 = 0;
    if (!PyArg_ParseTuple(list, "|iiiii", &i1, &i2, &i3, &i4, &i5)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: match");
      return NULL;
    }
    retval = match(i1, i2, i3, i4, i5);
  } else if (strcmp((char *)command, "matchRange") == 0) {
    // r1, g1, b1, r2, g2, b2, outChannel
    i1 = 0; i2 = 0; i3 = 0; i4 = 255; i5 = 255; i6 = 255, i7 = 0;
    if (!PyArg_ParseTuple(list, "|iiiiiii", &i1, &i2, &i3, &i4,&i5,&i6,&i7)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: matchRange");
      return NULL;
    }
    retval = matchRange(i1, i2, i3, i4, i5, i6, i7);
  } else if (strcmp((char *)command, "matchList") == 0) {
    PyObject *pyobj = NULL;
    if (!PyArg_ParseTuple(list, "O", &pyobj)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: matchList");
      return NULL;
    }
    retval = matchList(pyobj);
  } else if (strcmp((char *)command, "grayScale") == 0) {
    retval = grayScale();
  } else if (strcmp((char *)command, "rgb2yuv") == 0) {
    retval = rgb2yuv();
  } else if (strcmp((char *)command, "yuv2rgb") == 0) {
    retval = yuv2rgb();
  } else if (strcmp((char *)command, "rgb2hsv") == 0) {
    retval = rgb2hsv();
  } else if (strcmp((char *)command, "hsv2rgb") == 0) {
    retval = hsv2rgb();
  } else if (strcmp((char *)command, "mask") == 0) {
    i1 = 0;
    if (!PyArg_ParseTuple(list, "|i", &i1)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: mask");
      return NULL;
    }
    retval = mask(i1);
  } else if (strcmp((char *)command, "backup") == 0) {
    retval = backup();
  } else if (strcmp((char *)command, "restore") == 0) {
    retval = restore();
  } else if (strcmp((char *)command, "motion") == 0) {
    i1 = 30; 
    i2 = 0;
    if (!PyArg_ParseTuple(list, "|ii", &i1, &i2)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: motion");
      return NULL;
    }
    retval = motion(i1, i2);
  } else if (strcmp((char *)command, "threshold") == 0) {
    i1 = 0; i2 = 200;
    if (!PyArg_ParseTuple(list, "|ii", &i1, &i2)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: threshold");
      return NULL;
    }
    retval = threshold(i1, i2);
  } else if (strcmp((char *)command, "inverse") == 0) {
    i1 = 0;
    if (!PyArg_ParseTuple(list, "|i", &i1)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: inverse");
      return NULL;
    }
    retval = inverse(i1);
  } else if (strcmp((char *)command, "blobify") == 0) {
    i1 = 0; i2 = 200; i3 = 255; i4 = 0; i5 = 1; i6 = 1, i7 = 1;
    // inChannel, low, high, sortmethod 0 = mass, 1 = area, return blobs, 
    // drawBox, super_color
    if (!PyArg_ParseTuple(list, "|iiiiiii", &i1, &i2, &i3, &i4, &i5, &i6, &i7)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: blobify");
      return NULL;
    }
    retval = blobify(i1, i2, i3, i4, i5, i6, i7);
  } else if (strcmp((char *)command, "histogram") == 0) {
    i1 = 0; i2 = 0; i3 = width - 1; i4 = height - 1; i5 = 8;
    // x1, y1, x2, y2, bins
    if (!PyArg_ParseTuple(list, "|iiiii", &i1, &i2, &i3, &i4, &i5)) {
      PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: histogram");
      return NULL;
    }
    retval = histogram(i1, i2, i3, i4, i5);
  } else {
    PyErr_SetString(PyExc_TypeError, "Invalid command to applyFilter");
    return NULL;
  }
  return retval;
}

