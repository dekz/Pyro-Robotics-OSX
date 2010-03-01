#include "myVisionLib.h"

myVision::myVision() {
  allocatedImage = 0;
}

myVision::myVision(int wi, int he, int de, int r, int g, int b) {
  allocatedImage = 0;
  initialize(wi, he, de, r, g, b);
}

myVision::myVision(int wi, int he, int de) {
  allocatedImage = 0;
  initialize(wi, he, de, 0, 1, 2);
}

myVision::~myVision() {
  if (allocatedImage)
    delete [] image;
}

PyObject *myVision::initialize(int wi, int he, int de, int r, int g, int b) {
  width = wi;
  height = he;
  depth = de;
  setRGB(r, g, b);
  filterList = PyList_New(0);
  // set the current image to:
  Image = image;
  return PyInt_FromLong(0L);
}

PyObject *myVision::registerCameraDevice(void *dev) {
  Device *device = (Device *)dev;
  image = device->getImage();
  allocatedImage = 1;
  return initialize(device->getWidth(), device->getHeight(), device->getDepth(),
		    device->getRGB()[0],device->getRGB()[1],device->getRGB()[2]);
}

PyObject *myVision::getRGB() {
  return Py_BuildValue("iii", rgb[0], rgb[1], rgb[2] );
}


PyObject *myVision::setRGB(int r, int g, int b) {
  int rgb_order[MAXDEPTH] = {r, g, b};
  for (int d = 0; d < depth; d++)
    // set offsets for RGB
    rgb[d] = rgb_order[d];
  return getRGB();
}

PyObject *myVision::set(int w, int h, int r, int g, int b) {
  set(w, h, rgb[0], r);
  set(w, h, rgb[1], g);
  set(w, h, rgb[2], b);
  return Py_BuildValue("i", 0);
}

PyObject *myVision::set(int w, int h, int d, int value) {
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

PyObject *myVision::getMMap() {
  PyObject *buffer;
  buffer = PyBuffer_FromMemory(Image, 
			       width * height * depth * sizeof(unsigned char));
  return Py_BuildValue("O", buffer);
}

PyObject *myVision::get(int w, int h) {
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

PyObject *myVision::match(int r, int g, int b, int tolerance, 
			int outChannel) {
  return matchRange( r - tolerance, g - tolerance, b - tolerance,
		     r + tolerance, g + tolerance, b + tolerance,
		     outChannel);
}

PyObject *myVision::matchRange(int lr, int lg, int lb, 
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

PyObject *myVision::saveImage(char *filename) {
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
  return Py_BuildValue("");
} 

void myVision::swapPlanes(int d1, int d2) {
  for (int h = 0; h < height; h++) {
    for (int w = 0; w < width; w++) {
      unsigned int temp = Image[(h * width + w) * depth + d1];
      Image[(h * width + w) * depth + d1] = Image[(h * width + w) * depth + d2];
      Image[(h * width + w) * depth + d2] = temp;
    }
  }
}

PyObject *myVision::drawRect(int x1, int y1, int x2, int y2, 
			     int fill, int channel) {
  if (x1 > x2)
    SWAP(x1, x2);
  if (y1 > y2)
    SWAP(y1, y2);
  x2 = MAX(MIN(width - 1, x2),0);
  y2 = MAX(MIN(height - 1, y2),0);
  for(int w=x1; w<=x2; w++) {
      for(int h=y1; h<=y2; h++ ) {
	if (fill == 1 || 
	    (h == x1 || h == x2) ||
	    (w == y1 || w == y2))
	  if (channel == ALL)
	    for(int d=0; d<depth; d++) {
	      Image[(h * width + w) * depth + d] = 255;
	    }
	  else
	    Image[(h * width + w) * depth + rgb[channel]] = 255;
      }
  }
  return PyInt_FromLong(0L);
}

PyObject *myVision::getFilterList() {
  Py_INCREF(filterList);
  return filterList;
}

PyObject *myVision::setFilterList(PyObject *newList) {
  if (!PyList_Check(newList)) {
    PyErr_SetString(PyExc_TypeError, "Invalid list to setFilters");
    return NULL;
  }
  Py_DECREF(filterList);
  filterList = newList;
  Py_INCREF(filterList);
  return Py_BuildValue("");
}

PyObject *myVision::popFilterList() {
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

PyObject *myVision::addFilter(PyObject *newFilter) {
  //if (!PyList_Check(newFilter)) {
  //  PyErr_SetString(PyExc_TypeError, "Invalid filter to addFilter");
  //  return NULL;
  //}
  Py_INCREF(newFilter);
  PyList_Append(filterList, newFilter);
  return Py_BuildValue("");
}

PyObject *myVision::applyFilterList() {
  return applyFilters(filterList);
}

PyObject *myVision::applyFilters(PyObject *newList) {
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

// ---------------------------------------------------------
// Add your commands here:
// ---------------------------------------------------------

PyObject *myVision::getMenu() {
  PyObject *menu = PyList_New( 0 );
  PyList_Append(menu, Py_BuildValue("sssiiiii", "myFilters", "Match pixel", "match", 0, 0, 0, 30, 0));
  PyList_Append(menu, Py_BuildValue("sssiiii", "myFilters", "Draw box", "drawRect", 10, 10, 30, 30));
  return menu;
}

PyObject *myVision::applyFilter(PyObject *filter) {
  int i1, i2, i3, i4, i5, i6, i7;
  float f1, f2, f3, f4, f5, f6, f7;
  PyObject *command, *list, *retval;
    if (!PyArg_ParseTuple(filter, "s|O", &command, &list)) {
      PyErr_SetString(PyExc_TypeError, "Invalid filter list name to applyFilters");
      return NULL;
    }
    // process filters here:
    if (strcmp((char *)command, "match") == 0) {
      i1 = 0; i2 = 0; i3 = 0; i4 = 30; i5 = 0;
      if (!PyArg_ParseTuple(list, "|iiiii", &i1, &i2, &i3, &i4, &i5)) {
	PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: match()");
	return NULL;
      }
      retval = match(i1, i2, i3, i4, i5);
      // add new commands here!
    } else if(strcmp((char *)command, "drawRect") == 0) {
      //int x1, int y1, int x2, int y2, 
      //int fill, int channel) {
      i1 = 20, i2 = 30, i3 = 50, i4 = 70, i5 = 0, i6 = 0;
      if (!PyArg_ParseTuple(list, "|iiiiii", &i1, &i2, &i3, &i4, &i5, &i6)) {
	PyErr_SetString(PyExc_TypeError, "Invalid applyFilters: drawRect()");
	return NULL;
      }
      retval = drawRect(i1, i2, i3, i4, i5, i6);
    } else {
      PyErr_SetString(PyExc_TypeError, "Invalid command to applyFilter");
      return NULL;
    }
    return retval;
}

