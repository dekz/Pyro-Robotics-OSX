#ifndef __BT848_H
#define __BT848_H

#include "Device.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/fcntl.h>
#include <sys/signal.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <errno.h>              /* errno */

#include "ioctl_meteor.h"
#include "ioctl_bt848.h" // dsb

class BT848: public Device
{
 public:
  BT848 ( const char* dname, int w, int h, int d);
  ~BT848();
  PyObject *updateMMap( );

 private:
  int size;
  void init(void);
  int fd;
  int icontrol;
  struct meteor_counts cnt;
  char *VIDEO_DEV;
  unsigned char *buffer;
};

#endif // __BT848_H



