#ifndef __AIBO_H__
#define __AIBO_H__

#include "Device.h"
#include "Socket.h"
#include "RWLock.h"

class AiboCam : public Device {
 public:
  AiboCam(char *hostname, int port, int tcp);
  PyObject *updateMMap(int decompress);
  Socket *sock;
  RWLock lock;
  int tcp;
};

#endif
