#include "RobocupLib.h"

Robocup::Robocup(int w, int h, int d) {
  initialize(w, h, 3, 0, 1, 2);
  clear();
}

void Robocup::setPixel(int x, int y, int r, int g, int b) {
  image[(y * width + x) * depth + rgb[0]] = r;
  image[(y * width + x) * depth + rgb[1]] = g;
  image[(y * width + x) * depth + rgb[2]] = b;
}

void Robocup::drawLine(long int x0, long int y0, 
		       long int x1, long int y1, 
		       long int r, long int g, long int b) {
  // keep in range
  x1 = MAX(MIN(width - 1, x1),0);
  y1 = MAX(MIN(height - 1, y1),0);
  x0 = MAX(MIN(width - 1, x0),0);
  y0 = MAX(MIN(height - 1, y0),0);
  int dy = y1 - y0;
  int dx = x1 - x0;
  int stepx, stepy;
  if (dy < 0) { dy = -dy;  stepy = -1; } else { stepy = 1; }
  if (dx < 0) { dx = -dx;  stepx = -1; } else { stepx = 1; }
  dy <<= 1;                                                  // dy is now 2*dy
  dx <<= 1;                                                  // dx is now 2*dx
  setPixel(x0, y0, r, g, b);
  if (dx > dy) {
    int fraction = dy - (dx >> 1);                         // same as 2*dy - dx
    while (x0 != x1) {
      if (fraction >= 0) {
	y0 += stepy;
	fraction -= dx;                                // same as fraction -= 2*dx
      }
      x0 += stepx;
      fraction += dy;                                    // same as fraction -= 2*dy
      setPixel(x0, y0, r, g, b);
    }
  } else {
    int fraction = dx - (dy >> 1);
    while (y0 != y1) {
      if (fraction >= 0) {
	x0 += stepx;
	fraction -= dy;
      }
      y0 += stepy;
      fraction += dx;
      setPixel(x0, y0, r, g, b);
    }
  }
}

void Robocup::drawRect(long int x1, long int y1, 
		       long int x2, long int y2, 
		       long int r, long int g, long int b) {
  if (x1 > x2)
    SWAP(x1, x2);
  if (y1 > y2)
    SWAP(y1, y2);
  // keep in range
  x1 = MAX(MIN(width - 1, x1),0);
  y1 = MAX(MIN(height - 1, y1),0);
  x2 = MAX(MIN(width - 1, x2),0);
  y2 = MAX(MIN(height - 1, y2),0);
  for(int w=x1; w<=x2; w++) {
    for(int h=y1; h<=y2; h++ ) {
      setPixel(w, h, r, g, b);
    }
  }
}

void Robocup::clear() {
  for(int w=0; w<width; w++) {
    for(int h=0; h<height; h++ ) {
      image[(h * width + w) * depth + rgb[0]] = 0;
      image[(h * width + w) * depth + rgb[1]] = 153;
      image[(h * width + w) * depth + rgb[2]] = 0;
    }
  }
}

PyObject *Robocup::updateMMap(PyObject *points, PyObject *lines) {
  PyObject *pylist;
  int r, g, b;
  int i, x, y;
  char *name;
  clear();
  // Takes a dict and a list
  // [{'right': [(4, 12), (31, 12), (15, 12), (20, 12)], 
  //   'center': [(17, 28)], 
  //   'Bottom': [(33, 13), (33, 16), (33, 19)], 
  //   '1pleft': [], 'Left': [], 'Top': [(2, 13), (2, 16)], 'left': []},
  //  [['b', 7.4000000000000004, -44.0, 0, 0]]
  // ]
  // draw points
  PyObject *key, *value;
  Py_ssize_t *next = 0;
  int lastX, lastY;
  while (PyDict_Next(points, next, &key, &value)) { // for each line
    // key is the name of the line
    // value is the list of points
    lastX = -1, lastY = -1;
    if (!PyArg_Parse(key, "s", &name)) {
      PyErr_SetString(PyExc_TypeError, "Invalid name in updateMMap((DICT,LIST)) where DICT is {name: (x, y)...}");
      return NULL;
    }
    for(i = 0; i < PyList_Size(value); i++) { // for each point in value
      PyObject *pytuple = PyList_GetItem(value, i);
      if (!PyArg_ParseTuple(pytuple, "ii", &x, &y)) {
	PyErr_SetString(PyExc_TypeError, "Invalid (x,y) in updateMMap((DICT,LIST)) where DICT is {name: (x, y)...}");
	return NULL;
      }
      switch (name[0]) {
      case 't':
      case 'l':
      case 'b':
      case 'r':
	drawRect(x, y, x, y, 128, 128, 128);
	if (lastX != -1 && lastY != -1) {
	  drawLine(lastX, lastY, x, y, 128, 128, 128);
	}
	break;
      case 'T':
      case 'L':
      case 'B':
      case 'R':
	// boundaries
	drawRect(x, y, x, y, 0, 0, 0);
	if (lastX != -1 && lastY != -1) {
	  drawLine(lastX, lastY, x, y, 0, 0, 0);
	}
	break;
      case 'c':
      case '1':
      case '2':
      case 'a':
      case 'z':
      case 'A':
      case 'Z':
	drawRect(x, y, x, y, 255, 0, 0);
	if (lastX != -1 && lastY != -1) {
	  drawLine(lastX, lastY, x, y, 255, 0, 0);
	}
	break;
      }
      lastX = x, lastY = y;
    }
  }
  // draw objects
  for (i = 0; i < PyList_Size(lines); i++) {
    PyObject *obj = PyList_GetItem(lines, i);
    if (!PyArg_ParseTuple(obj, "sii", &name, &x, &y)) {
      PyErr_SetString(PyExc_TypeError, "Invalid list item to updateMMap((DICT,LIST)) where LIST is ((name, x, y)...)");
      return NULL;
    }
    if (name[0] ==  'b') // ball
      drawRect(x - 1, y, x + 1, y - 2, 255, 255, 255);
    else if (name[0] ==  'p') // player
      drawRect(x - 1, y, x + 1, y - 2, 255, 255, 0);
    else if ((strncmp(name,"fg", 2) == 0) || (name[0] == 'g'))
      drawRect(x, y, x, y - 5, 255, 153, 255); // goal WHICH IS MINE?
  }
  return PyInt_FromLong(0L);
}
