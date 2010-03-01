#ifndef __DEVICE_H__ 
#define __DEVICE_H__ 

#include <Python.h>
#define MAXDEPTH 3

class Device {

public:
  Device();
  Device(int w, int h, int d, int r, int g, int b);
  Device(int w, int h, int d);
  ~Device();
  PyObject *initialize(int wi, int he, int de, int r, int g, int b);
  int *getRGB() {return rgb;}
  void setRGB(int r, int g, int b);
  int getWidth() {return width;}
  int getHeight() {return height;}
  int getDepth() {return depth;}
  unsigned char *getImage() {return image;}
  unsigned char getByte(int position);

 protected:
  unsigned char *image;
  int width;
  int height;
  int depth;
  int rgb[3];
};

#endif
