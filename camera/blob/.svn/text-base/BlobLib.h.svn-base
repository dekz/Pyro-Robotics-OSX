#ifndef __BLOB_H__
#define __BLOB_H__

#include "Device.h"

class Blob : public Device {

 public:
  Blob(int w, int h, int d);
  void clear();
  PyObject *updateMMap(PyObject *blobData);
  void drawRect(long int left, long int right, 
		long int top, long int bottom, 
		long int r, long int g, long int b);
};

#endif
