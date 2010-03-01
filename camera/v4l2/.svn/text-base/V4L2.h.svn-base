#ifndef __V4L2_H
#define __V4L2_H

#include "Device.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <fcntl.h>              /* low-level i/o */
#include <unistd.h>
#include <errno.h>
#include <malloc.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <asm/types.h>          /* for videodev2.h */
#include <linux/videodev2.h>
#include "jpeg.h"

#define CLEAR(x) memset (&(x), 0, sizeof (x))

typedef enum {
	IO_METHOD_READ,
	IO_METHOD_MMAP,
	IO_METHOD_USERPTR,
} io_method;

struct buffer {
        void *                  start;
        size_t                  length;
};

class V4L2 : public Device
{
 public:
  V4L2 ( char *device_name, int wi, int he, int de, int ch);
  ~V4L2();

 public:

  PyObject *updateMMap(void);
  void init(void);
  void swap_rgb24(char *mem, int n); 
  void uninit_device();
  void start_capturing(void);
  void init_read(unsigned int);
  void init_mmap(int nbufs);
  void init_userp(unsigned int);
  void init_device();
  void close_device();
  void open_device();
  void stop_capturing(void);
  void errno_exit(char*);
  int xioctl(int, int, void*);
  void process_image(void*, int);
  int read_frame();

  char device[255];
  int channel;
  char *device_name;
  char *           dev_name;
  io_method	  io;
  int              fd;
  buffer *         buffers;
  unsigned int     n_buffers;
  int              format;
};

#endif // __V4L2_H
