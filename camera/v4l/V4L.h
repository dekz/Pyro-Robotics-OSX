#ifndef __V4L_H
#define __V4L_H

#include "Device.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/fcntl.h>
#include <sys/mman.h>
#include <sys/ioctl.h>

#include <errno.h>
#include <sys/time.h>
#include <asm/types.h>
#include <linux/videodev.h>	/* change this to "videodev2.h" for v4l2 */
#include "jpeglib.h"
// #define GRAB_DEVICE       "/dev/video1"
// #define GRAB_WIDTH        320
// #define GRAB_HEIGHT       240
// #define GRAB_TEXT         "v4lgrab %d.%m.%Y %H:%M:%S"        /* strftime */

#ifdef VIDIOCGCAP
/* these work for v4l only, not v4l2 */
//  # define GRAB_SOURCE      1
  # define GRAB_NORM        VIDEO_MODE_NTSC
#endif

//extern int errno;

class V4L : public Device
{
 public:
  V4L ( char *device_name, int wi, int he, int de, int ch);
  ~V4L();

 public:

  PyObject *updateMMap(void);
  void init(void);
  void swap_rgb24(char *mem, int n); 

  /*
  //#ifdef VIDIOC_QUERYCAP

  struct v4l2_capability    grab_cap;
  struct v4l2_format        grab_pix;
  int                       grab_fd, grab_size;
  //unsigned char            *grab_data;

//#endif
*/

#ifdef VIDIOCGCAP

  struct video_capability   grab_cap;
  struct video_mmap         grab_map;
  struct video_mbuf         grab_buf;
  struct video_channel	    grab_chan;
  int                       grab_fd, grab_size;
  //unsigned char            *grab_data;

#endif

  char device[255];
  int channel;

};

#endif // __V4L_H
