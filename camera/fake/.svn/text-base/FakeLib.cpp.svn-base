#include "FakeLib.h"

Fake::Fake(char filename[], int width, int height, int depth) {
  int limit, w, h, num, maxval, color;
  PyObject *buffer, *tuple;
  FILE* theFile;
  if (width != 0 && height != 0 && depth != 0) { // no filename, just the mmap
    if (depth == 3) 
      initialize(width, height, 3, 0, 1, 2);
    else if (depth == 1)
      initialize(width, height, 1, 0, 0, 0);
    return;
  }
  theFile = fopen(filename, "rb");
  if (!theFile){
    printf("Fake: Error loading file '%s'\n", filename);
    PyErr_SetString(PyExc_IOError, "Fake: Error loading file");
    initialize(0, 0, 1, 0, 0, 0);
    return;
  }
  fscanf(theFile, "P%d\n%d %d\n%3d%*c", &num, &w, &h, &maxval);
  fclose(theFile);
  switch(num){
  case 5:
    color = 0;
    break;
  case 6:
    color = 1;
    break;
  default:
    color = 1;
  }
  if (maxval > 255){
    PyErr_SetString(PyExc_TypeError, "Fake: Invalid PPM, must be 3 bytes per pixel");
  }
  if (color){
    initialize(w, h, 3, 0, 1, 2);
  } else{
    initialize(w, h, 1, 0, 0, 0);
  }
  updateMMap(filename);
}

PyObject *Fake::updateMMap(char filename[]) {
  int w, h, num, maxval, retval;
  FILE *theFile;
  theFile = fopen(filename, "rb");
  if (!theFile){
    //printf("Fake camera: error loading file\n");
    return PyInt_FromLong(0);
  }
  fscanf(theFile, "P%d\n%d %d\n%3d\n", &num, &w, &h, &maxval);
  //printf("P%d\n%d %d\n%d\n", num, w, h, maxval);
  if (w != width || h != height || 
      (num == 5 && depth != 1) ||
      (num == 6 && depth != 3)){
    PyErr_SetString(PyExc_IOError, "Fake: can't change image type or size");
    fclose(theFile);
    return NULL;
  }
  if (num == 5) {
    retval = fread(image, 1, w * h, theFile);
  } else {
    retval = fread(image, 1, w * h * 3, theFile);
  }
  width = w;
  height = h;
  fclose(theFile);
  return PyInt_FromLong(retval);
}

