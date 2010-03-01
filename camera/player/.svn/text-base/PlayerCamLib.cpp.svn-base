#include "PlayerCamLib.h"

PyObject *PlayerCam::updateMMap(int load) {
  void *rdevice = playerc_client_read(client);
  //playerc_camera_decompress(camDevice);
  width = camDevice->width;
  height = camDevice->height;
  // data is in camDevice->image[i]
  if (load)
    memcpy(image, camDevice->image, width * height * depth);
  return PyInt_FromLong(0);
}

PlayerCam::PlayerCam(char *hostname, int port) {
  index = 0;
  client = playerc_client_create(NULL, hostname, port);
  playerc_client_connect(client);
  camDevice = playerc_camera_create(client, index);
  if (playerc_camera_subscribe(camDevice, PLAYER_OPEN_MODE) != 0) {
    printf("PlayerCam: subscribe failed\n");
  } else {
    printf("PlayerCam: subscribe succeeded\n");
  }
  // get image details
  depth = 3;
  // set width, height 0 to trigger automatically:
  width = 0;
  height = 0;
  updateMMap(0); // this will set height and width automatically
  initialize(width, height, depth, 0, 1, 2); // create some space
}
