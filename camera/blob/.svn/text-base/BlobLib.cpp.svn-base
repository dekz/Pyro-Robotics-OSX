#include "BlobLib.h"

Blob::Blob(int w, int h, int d) {
  initialize(w, h, 3, 0, 1, 2);
}

void Blob::drawRect(long int left, long int right, 
		    long int top, long int bottom, 
		    long int r, long int g, long int b) {
  for(int w=left; w<=right; w++) {
    for(int h=top; h<=bottom; h++ ) {
      image[(h * width + w) * depth + rgb[0]] = r;
      image[(h * width + w) * depth + rgb[1]] = g;
      image[(h * width + w) * depth + rgb[2]] = b;
    }
  }
}

void Blob::clear() {
  for(int w=0; w<width; w++) {
    for(int h=0; h<height; h++ ) {
      image[(h * width + w) * depth + rgb[0]] = 128;
      image[(h * width + w) * depth + rgb[1]] = 128;
      image[(h * width + w) * depth + rgb[2]] = 128;
    }
  }
}

PyObject *Blob::updateMMap(PyObject *blobData) {
  int r, g, b;
  PyObject *blob;
  clear();
  if (!PyList_Check(blobData)) {
    PyErr_SetString(PyExc_TypeError, "Invalid list to updateMMap()");
    return NULL;
  }
  int left, right, top, bottom;
  long int packedcolor;
  // for each blob:
  for (int i = 0; i < PyList_Size(blobData); i++) {
    PyObject *blob = PyList_GetItem(blobData, i);
    if (!PyArg_ParseTuple(blob, "iiiil", 
			  &left, &top, &right, &bottom, &packedcolor)) {
      PyErr_SetString(PyExc_TypeError, "Invalid items to updateMMap()");
      return NULL;
    }
    // process data
    // draw rectangle
    r = packedcolor >> 16;
    g = packedcolor >>  8 & 0x0000FF;
    b = packedcolor       & 0x0000FF;
    drawRect(left, right, top, bottom, r, g, b);
  }
  return PyInt_FromLong(0L);
}
