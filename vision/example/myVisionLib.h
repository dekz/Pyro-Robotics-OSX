#ifndef __MYVISION_H__ 
#define __MYVISION_H__ 

#include <Python.h>
#include <Device.h>

#define SWAP(a,b) { int itemp=(a);(a)=(b);(b)=itemp;}
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))

class myVision {
public:
  static const int RED = 0;
  static const int GREEN = 1;
  static const int BLUE = 2;
  static const int ALL = 10;

  static const int WORKSPACE = 50;
  static const int ORIGINAL = 60;
  static const int IMAGE = 70;

  static const int AND = 100;
  static const int OR = 101;
  static const int XOR = 102;
  static const int ACCUM = 103;
  
  myVision();
  myVision(int w, int h, int d, int r, int g, int b);
  myVision(int w, int h, int d);
  ~myVision();
  PyObject *initialize(int wi, int he, int de, int r, int g, int b);
  PyObject *registerCameraDevice(void *args);
  PyObject *matchRange(int lr, int lg, int lb,
		       int hr, int hg, int hb,
		       int outChannel);
  PyObject *match(int r, int g, int b, int tolerance,
		  int outChannel);
  PyObject *get(int w, int h);
  PyObject *set(int w, int h, int r, int g, int b);
  PyObject *set(int w, int h, int d, int val);
  PyObject *drawRect(int x1, int y1, int x2, int y2, 
		int fill, int channel);
  void swapPlanes(int d1, int d2);
  int getWidth() { return width; }
  int getHeight() { return height; }
  int getDepth() { return depth; }
  PyObject *saveImage(char *filename);
  PyObject *getMMap();

  PyObject *applyFilter(PyObject *filter);
  PyObject *applyFilters(PyObject *filterList);
  PyObject *addFilter(PyObject *newFilter);
  PyObject *applyFilterList();
  PyObject *setFilterList(PyObject *filterList);
  PyObject *getFilterList();
  PyObject *popFilterList();

  PyObject *getRGB();
  PyObject *setRGB(int r, int g, int b); 

  PyObject *getMenu();

 protected:
  unsigned char *Image; // current image (image, original, workspace)
  unsigned char *image;
  int allocatedImage;

  PyObject *filterList;
  int width;
  int height;
  int depth;
  int rgb[3];
};

#endif
