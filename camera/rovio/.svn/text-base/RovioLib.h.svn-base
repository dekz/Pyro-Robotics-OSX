#ifndef __ROVIO_H__
#define __ROVIO_H__

#include "Device.h"
#include "Socket.h"
#include "RWLock.h"

class RovioCam : public Device {
 public:
  RovioCam(char *hostname, int port, int tcp);
  PyObject *updateMMap(int decompress);
  Socket *sock;
  RWLock lock;
  int tcp;
};

#endif
