#include "V4L.h"

V4L::V4L ( char *device_name, int wi, int he, int de, int ch) :
     Device(wi, he, de) {
  int size = 0;

  snprintf(device, 255, device_name);
  width = wi;
  height = he;
  depth = de;
  channel = ch;

  fprintf(stderr, "V4L constructor '%s' (%d x %d) x %d ch = %d\n",
	  device, width, height, depth, channel);

#ifdef VIDIOCGCAP
  size = width * height * depth;
#endif
  image = new unsigned char [size];
  init();
}

V4L::~V4L ()
{
  delete [] image;
}

PyObject *V4L:: updateMMap( )
{
  for (;;) {
    if (-1 >= ioctl(grab_fd,VIDIOCMCAPTURE,&grab_map)) {
      fprintf(stderr,"Error: ioctl cmcapture");
      perror("ioctl VIDIOCMCAPTURE");
    } else {
      if (-1 >= ioctl(grab_fd,VIDIOCSYNC,&grab_map)) {
	fprintf(stderr,"Error: VivioCsync");
	perror("ioctl VIDIOCSYNC");
      } else {
	//swap_rgb24((char *)image,grab_map.width*grab_map.height);
	width  = grab_map.width;
	height = grab_map.height;
	return PyInt_FromLong(0L);
      }
    }
    sleep(1); 
    // force context switch to avoid giant sucking sound
    // this is a millisec
  }
}

// Two methods: v4l, or v4l2

#ifdef DUMMY_VIDIOC_QUERYCAP

void V4L::init(void) {
  fprintf(stderr,"Init-ing Video under Querycap-V4L2\n");
  if (-1 >= (grab_fd = open(device,O_RDWR))) {
    fprintf(stderr,"Error opening video device");
    perror(device);
    exit(1);
  }
  if (-1 >= ioctl(grab_fd,VIDIOC_QUERYCAP,&grab_cap)) {
    fprintf(stderr,"wrong device\n");
    exit(1);
  }
  if (-1 >= ioctl(grab_fd, VIDIOC_G_FMT, &grab_pix)) {
    fprintf(stderr,"Error: ioctl 1");
    perror("ioctl VIDIOC_G_FMT");
    exit(1);
  }
  grab_pix.pixelformat = V4L2_PIX_FMT_BGR24;
  grab_pix.depth  = depth * 8;
  grab_pix.width  = cols;
  grab_pix.height = rows;
  if (-1 >= ioctl(grab_fd, VIDIOC_S_FMT, &grab_pix)) {
    fprintf(stderr,"Error: ioctl 2");
    perror("ioctl VIDIOC_S_FMT");
    exit(1);
  }
  grab_size = grab_pix.width * grab_pix.height * ((grab_pix.depth+7)/8);
  fprintf(stderr,"grabber: using %dx%dx%d => %d byte\n",
	  grab_pix.width,grab_pix.height,grab_pix.depth,grab_size);
  if (NULL == (image = malloc(grab_size))) {
    fprintf(stderr,"out of virtual memory\n");
    exit(1);
  }
  fprintf(stderr,"Done Init Video under Querycap-V4L2\n");
}

#endif


/* ---------------------------------------------------------------------- */
/* capture stuff  -  old v4l (bttv)                                       */

#ifdef VIDIOCGCAP

void V4L::init(void) {
  fprintf(stderr,"Initializing Video4Linux %s..", device);
  if (-1 >= (grab_fd = open(device,O_RDWR))) {
    fprintf(stderr,"Error: opening video device");
    perror(device);
    exit(1);
  }
  if (-1 >= ioctl(grab_fd,VIDIOCGCAP,&grab_cap)) {
    fprintf(stderr,"wrong device\n");
    exit(1);
  }
  
  /* set image source and TV norm */
  grab_chan.channel = channel;
  if (-1 >= ioctl(grab_fd,VIDIOCGCHAN,&grab_chan)) {
    fprintf(stderr,"Error: with Videochannel");
    perror("ioctl VIDIOCGCHAN");
    exit(1);
  }
  grab_chan.channel = channel;    
  grab_chan.norm    = GRAB_NORM;
  if (-1 >= ioctl(grab_fd,VIDIOCSCHAN,&grab_chan)) {
    fprintf(stderr,"Error: videochannel 2");
    perror("ioctl VIDIOCSCHAN");
    exit(1);
  }
  
  grab_map.format = VIDEO_PALETTE_RGB24;
  grab_map.frame  = 0;
  grab_map.width  = width;
  grab_map.height = height;
  if (-1 == ioctl(grab_fd, VIDIOCGMBUF, &grab_buf)) {
    perror("ioctl VIDIOCGMBUF");
  }
  grab_size = grab_buf.size; 
  image = (unsigned char *)mmap(NULL, 
				grab_size, 
				PROT_READ | PROT_WRITE, 
				MAP_SHARED, 
				grab_fd, 
				0); 
  if ((int)image == -1) {
    fprintf(stderr,"Error ");
    perror("mmap");
    exit(1);
  }
  fprintf(stderr,"..Done\n");
}

void V4L::swap_rgb24(char *mem, int n) {
  char  c;
  char *p = mem;
  int   i = n;
  
  while (--i) {
    c = p[0]; p[0] = p[2]; p[2] = c;
    p += 3;
  }
}

#endif 
