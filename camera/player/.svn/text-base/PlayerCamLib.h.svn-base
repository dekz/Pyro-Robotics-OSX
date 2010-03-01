// why is this __AIBO_H__ ???
#ifndef __AIBO_H__
#define __AIBO_H__

#include "Device.h"
#include "libplayerc/playerc.h"

class PlayerCam : public Device {
 public:
  PlayerCam(char *hostname, int port);
  PyObject *updateMMap(int load);
  int index;
  playerc_client_t *client;
  playerc_camera_t *camDevice;
};

#endif
