#include "V4L2.h"

V4L2::V4L2 ( char *device_name, int wi, int he, int de, int ch) :
     Device(wi, he, de) {
  int size = 0;
  snprintf(device, 255, device_name);
  width = wi;
  height = he;
  depth = de;
  channel = ch;
  fprintf(stderr, "V4L2 constructor '%s' (%d x %d) x %d ch = %d\n",
	  device, width, height, depth, channel);
  size = width * height * depth;
  image = new unsigned char [size];
  init();
}

V4L2::~V4L2 ()
{
  stop_capturing();
  uninit_device();
  close_device();
  delete [] image;
}

void V4L2::errno_exit(char *s)
{
        fprintf (stderr, "%s error %d, %s\n",
                 s, errno, strerror (errno));
        exit (EXIT_FAILURE);
}

int V4L2::xioctl(int fd, int request, void *arg)
{
        int r;
        do r = ioctl (fd, request, arg);
        while (-1 == r && EINTR == errno);
        return r;
}

#define CLIP(color) (unsigned char)(((color)>0xFF)?0xff:(((color)<0)?0:(color))) 
void convert_yuyv_to_bgr24(const unsigned char *src, unsigned char *dest,
  int width, int height)
{
  int j;

  while (--height >= 0) {
    for (j = 0; j < width; j += 2) {
      int u = src[1];
      int v = src[3];
      int u1 = (((u - 128) << 7) +  (u - 128)) >> 6;
      int rg = (((u - 128) << 1) +  (u - 128) +
                ((v - 128) << 2) + ((v - 128) << 1)) >> 3;
      int v1 = (((v - 128) << 1) +  (v - 128)) >> 1;

      *dest++ = CLIP(src[0] + u1);
      *dest++ = CLIP(src[0] - rg);
      *dest++ = CLIP(src[0] + v1);

      *dest++ = CLIP(src[2] + u1);
      *dest++ = CLIP(src[2] - rg);
      *dest++ = CLIP(src[2] + v1);
      src += 4;
    }
  }
} 

#define LIMIT(x) ((x)>0xffffff?0xff: ((x)<=0xffff?0:((x)>>16)))

static inline void move_420_block(int yTL, int yTR, int yBL, int yBR, 
				  int u, int v, int rowPixels, 
				  unsigned char * rgb)
{
    const int rvScale = 91881;
    const int guScale = -22553;
    const int gvScale = -46801;
    const int buScale = 116129;
    const int yScale  = 65536;
    int r, g, b;

    g = guScale * u + gvScale * v;
    r = rvScale * v;
    b = buScale * u;

    yTL *= yScale; yTR *= yScale;
    yBL *= yScale; yBR *= yScale;

    /* Write out top two pixels */
    rgb[0] = LIMIT(b+yTL); rgb[1] = LIMIT(g+yTL);
    rgb[2] = LIMIT(r+yTL);

    rgb[3] = LIMIT(b+yTR); rgb[4] = LIMIT(g+yTR);
    rgb[5] = LIMIT(r+yTR);

    /* Skip down to next line to write out bottom two pixels */
    rgb += 3 * rowPixels;
    rgb[0] = LIMIT(b+yBL); rgb[1] = LIMIT(g+yBL);
    rgb[2] = LIMIT(r+yBL);

    rgb[3] = LIMIT(b+yBR); rgb[4] = LIMIT(g+yBR);
    rgb[5] = LIMIT(r+yBR);
}

static void yuv420p_to_rgb24(int width, int height, unsigned char *pIn0, 
			     unsigned char *pOut0)
{
    const int numpix = width * height;
    const int bytes = 24 >> 3;
    int i, j, y00, y01, y10, y11, u, v;
    unsigned char *pY = pIn0;
    unsigned char *pU = pY + numpix;
    unsigned char *pV = pU + numpix / 4;
    unsigned char *pOut = pOut0;

    for (j = 0; j <= height - 2; j += 2) {
        for (i = 0; i <= width - 2; i += 2) {
            y00 = *pY;
            y01 = *(pY + 1);
            y10 = *(pY + width);
            y11 = *(pY + width + 1);
            u = (*pU++) - 128;
            v = (*pV++) - 128;

            move_420_block(y00, y01, y10, y11, u, v,
                       width, pOut);
    
            pY += 2;
            pOut += 2 * bytes;

        }
        pY += width;
        pOut += width * bytes;
    }
}

#define u32 uint32_t

#define R(x,y,width) pRGB24[0 + 3 * ((x) + width * (y))]
#define G(x,y,width) pRGB24[1 + 3 * ((x) + width * (y))]
#define B(x,y,width) pRGB24[2 + 3 * ((x) + width * (y))]

#define Bay(x,y,width) pBay[(x) + width * (y)]

static void bayer_copy(unsigned char *pBay, unsigned char *pRGB24, int x, int y, int width)
{

  G(x + 0, y + 0,width) = Bay(x + 0, y + 0,width);
  G(x + 1, y + 1,width) = Bay(x + 1, y + 1,width);
  G(x + 0, y + 1,width) = G(x + 1, y + 0,width) = ((u32)Bay(x + 0, y + 0,width) + (u32)Bay(x + 1, y + 1, width)) / 2;
  R(x + 0, y + 0,width) = R(x + 1, y + 0,width) = R(x + 1, y + 1,width) = R(x + 0, y + 1,width) = Bay(x + 0, y + 1,width);
  B(x + 1, y + 1,width) = B(x + 0, y + 0, width) = B(x + 0, y + 1,width) = B(x + 1, y + 0,width) = Bay(x + 1, y + 0,width);
}

static void bayer_bilinear(unsigned char *pBay, unsigned char *pRGB24, int x, int y, int width)
{
  R(x + 0, y + 0, width) = ((u32)Bay(x + 0, y + 1, width) + (u32)Bay(x + 0, y - 1, width)) / 2;
  G(x + 0, y + 0, width) = Bay(x + 0, y + 0, width);
  B(x + 0, y + 0, width) = ((u32)Bay(x - 1, y + 0, width) + (u32)Bay(x + 1, y + 0, width)) / 2;

  R(x + 0, y + 1, width) = Bay(x + 0, y + 1, width);
  G(x + 0, y + 1, width) = ((u32)Bay(x + 0, y + 0, width) + (u32)Bay(x + 0, y + 2, width)
      + (u32)Bay(x - 1, y + 1, width) + (u32)Bay(x + 1, y + 1, width)) / 4;
  B(x + 0, y + 1, width) = ((u32)Bay(x + 1, y + 0, width) + (u32)Bay(x - 1, y + 0, width)
      + (u32)Bay(x + 1, y + 2, width) + (u32)Bay(x - 1, y + 2, width)) / 4;

  R(x + 1, y + 0, width) = ((u32)Bay(x + 0, y + 1, width) + (u32)Bay(x + 2, y + 1, width)
      + (u32)Bay(x + 0, y - 1, width) + (u32)Bay(x + 2, y - 1, width)) / 4;
  G(x + 1, y + 0, width) = ((u32)Bay(x + 0, y + 0, width) + (u32)Bay(x + 2, y + 0, width)
      + (u32)Bay(x + 1, y - 1, width) + (u32)Bay(x + 1, y + 1, width)) / 4;
  B(x + 1, y + 0, width) = Bay(x + 1, y + 0, width);

  R(x + 1, y + 1, width) = ((u32)Bay(x + 0, y + 1, width) + (u32)Bay(x + 2, y + 1, width)) / 2;
  G(x + 1, y + 1, width) = Bay(x + 1, y + 1, width);
  B(x + 1, y + 1, width) = ((u32)Bay(x + 1, y + 0, width) + (u32)Bay(x + 1, y + 2, width)) / 2;
}


static void bayer_to_rgb24(unsigned char *pBay, unsigned char *pRGB24, int width)
{
  int i, j;
  for (i = 0; i < 640; i += 2)
    for (j = 0; j < 480; j += 2)
      if (i == 0 || j == 0 || i == 640 - 2 || j == 480 - 2)
	bayer_copy(pBay, pRGB24, i, j, width);
      else
	bayer_bilinear(pBay, pRGB24, i, j, width);
}

void V4L2::process_image(void *p, int length)
{
  switch(format){
  case V4L2_PIX_FMT_JPEG: 
    jpeg_decompress((unsigned char *)image, (width * height * depth), 
		    (unsigned char *)p, (int) length);
    swap_rgb24((char *)image, width * height);
    break;
  case V4L2_PIX_FMT_RGB32: 
    image = (unsigned char*)p;
    break;
  case V4L2_PIX_FMT_YUYV:
    convert_yuyv_to_bgr24((unsigned char *)p, image, width, height);
    break;
    //case 1196573255: // GBRG
  case V4L2_PIX_FMT_SPCA561:
    bayer_to_rgb24((unsigned char *)p, image, width);
    break;
    //case V4L2_PIX_FMT_UYVY: 
    //break;
    //case V4L2_PIX_FMT_GREY:
    //break;
    //case V4L2_PIX_FMT_YUV420: 
    //break;
  default: 
    fprintf(stderr, "ERROR: Unknown V4L2 format '%c%c%c%c'\n",
	    (char)(format),
	    (char)(format>>8),
	    (char)(format>>16),
	    (char)(format>>24));
    errno_exit("process_image");
  }
}

int V4L2:: read_frame(void)
{
        struct v4l2_buffer buf;
	unsigned int i;
	switch (io) {
	case IO_METHOD_READ:
    		if (-1 == read (fd, buffers[0].start, buffers[0].length)) {
            		switch (errno) {
            		case EAGAIN:
                    		return 0;
			case EIO:
				/* Could ignore EIO, see spec. */
				/* fall through */
			default:
				errno_exit ("read");
			}
		}
    		process_image(buffers[0].start,
			      buffers[0].length);
		break;
	case IO_METHOD_MMAP:
		CLEAR (buf);
            	buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            	buf.memory = V4L2_MEMORY_MMAP;
    		if (-1 == xioctl (fd, VIDIOC_DQBUF, &buf)) {
            		switch (errno) {
            		case EAGAIN:
                    		return 0;
			case EIO:
				/* Could ignore EIO, see spec. */
				/* fall through */
			default:
				errno_exit ("VIDIOC_DQBUF");
			}
		}
                assert (buf.index < n_buffers);
	        process_image(buffers[buf.index].start, 
			      buffers[buf.index].length);
		if (-1 == xioctl (fd, VIDIOC_QBUF, &buf))
			errno_exit ("VIDIOC_QBUF");
		break;
	case IO_METHOD_USERPTR:
		CLEAR (buf);
    		buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    		buf.memory = V4L2_MEMORY_USERPTR;
		if (-1 == xioctl (fd, VIDIOC_DQBUF, &buf)) {
			switch (errno) {
			case EAGAIN:
				return 0;
			case EIO:
				/* Could ignore EIO, see spec. */
				/* fall through */
			default:
				errno_exit ("VIDIOC_DQBUF");
			}
		}
		for (i = 0; i < n_buffers; ++i)
			if (buf.m.userptr == (unsigned long) buffers[i].start
			    && buf.length == buffers[i].length)
				break;
		assert (i < n_buffers);
    		process_image ((void *) buf.m.userptr,
			       buf.length);
		if (-1 == xioctl (fd, VIDIOC_QBUF, &buf))
			errno_exit ("VIDIOC_QBUF");
		break;
	}
	return 1;
}

void V4L2::stop_capturing(void)
{
        enum v4l2_buf_type type;
	switch (io) {
	case IO_METHOD_READ:
		/* Nothing to do. */
		break;
	case IO_METHOD_MMAP:
	case IO_METHOD_USERPTR:
		type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
		if (-1 == xioctl (fd, VIDIOC_STREAMOFF, &type))
			errno_exit ("VIDIOC_STREAMOFF");
		break;
	}
}

void V4L2::start_capturing(void)
{
        unsigned int i;
        enum v4l2_buf_type type;
	switch (io) {
	case IO_METHOD_READ:
		/* Nothing to do. */
		break;
	case IO_METHOD_MMAP:
		for (i = 0; i < n_buffers; ++i) {
            		struct v4l2_buffer buf;
        		CLEAR (buf);
        		buf.type        = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        		buf.memory      = V4L2_MEMORY_MMAP;
        		buf.index       = i;
        		if (-1 == xioctl (fd, VIDIOC_QBUF, &buf))
                    		errno_exit ("VIDIOC_QBUF");
		}

		type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
		if (-1 == xioctl (fd, VIDIOC_STREAMON, &type))
			errno_exit ("VIDIOC_STREAMON");

		break;
	case IO_METHOD_USERPTR:
		for (i = 0; i < n_buffers; ++i) {
            		struct v4l2_buffer buf;
        		CLEAR (buf);
        		buf.type        = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        		buf.memory      = V4L2_MEMORY_USERPTR;
			buf.index       = i;
			buf.m.userptr	= (unsigned long) buffers[i].start;
			buf.length      = buffers[i].length;
			if (-1 == xioctl (fd, VIDIOC_QBUF, &buf))
                    		errno_exit ("VIDIOC_QBUF");
		}
		type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
		if (-1 == xioctl (fd, VIDIOC_STREAMON, &type))
			errno_exit ("VIDIOC_STREAMON");
		break;
	}
}

void V4L2::uninit_device(void)
{
        unsigned int i;
	switch (io) {
	case IO_METHOD_READ:
		free (buffers[0].start);
		break;
	case IO_METHOD_MMAP:
		for (i = 0; i < n_buffers; ++i)
			if (-1 == munmap (buffers[i].start, buffers[i].length))
				errno_exit ("munmap");
		break;
	case IO_METHOD_USERPTR:
		for (i = 0; i < n_buffers; ++i)
			free (buffers[i].start);
		break;
	}
	free (buffers);
}

void V4L2::init_read(unsigned int buffer_size)
{
  buffers = (buffer*) calloc (1, sizeof (*buffers));
  if (!buffers) {
    fprintf (stderr, "Out of memory\n");
    exit (EXIT_FAILURE);
  }
  buffers[0].length = buffer_size;
  buffers[0].start = malloc (buffer_size);
  if (!buffers[0].start) {
    fprintf (stderr, "Out of memory\n");
    exit (EXIT_FAILURE);
  }
}

void V4L2::init_mmap(int nbufs)
{
	struct v4l2_requestbuffers req;
        CLEAR (req);
        req.count               = nbufs; 
        req.type                = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        req.memory              = V4L2_MEMORY_MMAP;
	if (-1 == xioctl (fd, VIDIOC_REQBUFS, &req)) {
                if (EINVAL == errno) {
                        fprintf (stderr, "%s does not support "
                                 "memory mapping\n", device);
                        exit (EXIT_FAILURE);
                } else {
                        errno_exit ("VIDIOC_REQBUFS");
                }
        }
	/*
        if (req.count < 2) {
                fprintf (stderr, "Insufficient buffer memory on %s\n",
                         device);
                exit (EXIT_FAILURE);
        }
	*/
        buffers = (buffer*) calloc (req.count, sizeof (*buffers));
        if (!buffers) {
                fprintf (stderr, "Out of memory\n");
                exit (EXIT_FAILURE);
        }
        for (n_buffers = 0; n_buffers < req.count; ++n_buffers) {
                struct v4l2_buffer buf;
                CLEAR (buf);
                buf.type        = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                buf.memory      = V4L2_MEMORY_MMAP;
                buf.index       = n_buffers;
                if (-1 == xioctl (fd, VIDIOC_QUERYBUF, &buf))
                        errno_exit ("VIDIOC_QUERYBUF");
                buffers[n_buffers].length = buf.length;
		buffers[n_buffers].start =
		  mmap (NULL /* start anywhere */,
			buf.length,
			PROT_READ | PROT_WRITE /* required */,
			MAP_SHARED /* recommended */,
			fd, buf.m.offset);
                if (MAP_FAILED == buffers[n_buffers].start)
                        errno_exit ("mmap");
        }
}

void V4L2::init_userp(unsigned int buffer_size)
{
	struct v4l2_requestbuffers req;
        unsigned int page_size;
        page_size = getpagesize ();
        buffer_size = (buffer_size + page_size - 1) & ~(page_size - 1);
        CLEAR (req);
        req.count               = 4;
        req.type                = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        req.memory              = V4L2_MEMORY_USERPTR;
        if (-1 == xioctl (fd, VIDIOC_REQBUFS, &req)) {
                if (EINVAL == errno) {
                        fprintf (stderr, "%s does not support "
                                 "user pointer i/o\n", device);
                        exit (EXIT_FAILURE);
                } else {
                        errno_exit ("VIDIOC_REQBUFS");
                }
        }
        buffers = (buffer*) calloc (4, sizeof (*buffers));
        if (!buffers) {
                fprintf (stderr, "Out of memory\n");
                exit (EXIT_FAILURE);
        }
        for (n_buffers = 0; n_buffers < 4; ++n_buffers) {
                buffers[n_buffers].length = buffer_size;
                buffers[n_buffers].start = memalign (/* boundary */ page_size,
                                                     buffer_size);
                if (!buffers[n_buffers].start) {
    			fprintf (stderr, "Out of memory\n");
            		exit (EXIT_FAILURE);
		}
        }
}

void V4L2::init_device(void)
{
        struct v4l2_capability cap;
        struct v4l2_cropcap cropcap;
        struct v4l2_crop crop;
        struct v4l2_format fmt;
	unsigned int min;
        if (-1 == xioctl (fd, VIDIOC_QUERYCAP, &cap)) {
                if (EINVAL == errno) {
                        fprintf (stderr, "%s is no V4L2 device\n",
                                 device);
                        exit (EXIT_FAILURE);
                } else {
                        errno_exit ("VIDIOC_QUERYCAP");
                }
        }
        if (!(cap.capabilities & V4L2_CAP_VIDEO_CAPTURE)) {
                fprintf (stderr, "%s is no video capture device\n",
                         device);
                exit (EXIT_FAILURE);
        }
	switch (io) {
	case IO_METHOD_READ:
		if (!(cap.capabilities & V4L2_CAP_READWRITE)) {
			fprintf (stderr, "%s does not support read i/o\n",
				 device);
			exit (EXIT_FAILURE);
		}
		break;
	case IO_METHOD_MMAP:
	case IO_METHOD_USERPTR:
		if (!(cap.capabilities & V4L2_CAP_STREAMING)) {
			fprintf (stderr, "%s does not support streaming i/o\n",
				 device);
			exit (EXIT_FAILURE);
		}
		break;
	}

        /* Select video input, video standard and tune here. */

	CLEAR (cropcap);
        cropcap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        if (0 == xioctl (fd, VIDIOC_CROPCAP, &cropcap)) {
                crop.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
                crop.c = cropcap.defrect; /* reset to default */
                if (-1 == xioctl (fd, VIDIOC_S_CROP, &crop)) {
                        switch (errno) {
                        case EINVAL:
                                /* Cropping not supported. */
                                break;
                        default:
                                /* Errors ignored. */
                                break;
                        }
                }
        } else {	
                /* Errors ignored. */
        }

        CLEAR (fmt);
        fmt.type                = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        fmt.fmt.pix.width       = width; 
        fmt.fmt.pix.height      = height;
        fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
        fmt.fmt.pix.field       = V4L2_FIELD_INTERLACED;
        if (-1 == xioctl (fd, VIDIOC_S_FMT, &fmt))
	  errno_exit ("VIDIOC_S_FMT");

	if (-1 == xioctl (fd, VIDIOC_G_FMT, &fmt))
	  errno_exit("VIDIOC_G_FMT");
	
	format = fmt.fmt.pix.pixelformat;
	switch(fmt.fmt.pix.pixelformat){
	case V4L2_PIX_FMT_JPEG: 
	  printf("v4l2 format: JPEG\n");
	  break;
	case V4L2_PIX_FMT_RGB32: 
	  printf("v4l2 format: RGBA\n");
	  break;
	case V4L2_PIX_FMT_UYVY: 
	  printf("v4l2 format: YUV\n");
	  break;
	case V4L2_PIX_FMT_YUYV: 
	  printf("v4l2 format: YUYV\n");
	  break;
	case V4L2_PIX_FMT_GREY: 
	  printf("v4l2 format: GREY\n");
	  break;
	case V4L2_PIX_FMT_YUV420: 
	  printf("v4l2 format: YUV 4:2:0\n");
	  break;
	case V4L2_PIX_FMT_SPCA561:
	  //case 1196573255: // GBRG
	  printf("v4l2 format: GBRG\n"); // a Bayer pattern
	  break;
	default: 
	  char format_name[5] = {'\0'};
	  for (int i = 0; i < 4; i++) {
	    format_name[i] = (char)(fmt.fmt.pix.pixelformat >> (i * 8));
	  }
	  fprintf(stderr, "compute: %d\n", 
	      ((long)'G') + 
	      ((long)'B') << 8 + 
	      ((long)'R') << 16 + 
	      ((long)'G') << 24);
	  fprintf(stderr, " actual: %d\n", fmt.fmt.pix.pixelformat);
	  fprintf(stderr, "ERROR: Unknown V4L2 init_device format '%s'\n",
	      format_name);
	  errno_exit("unknown v4l2 format");
	}
  
        /* Note VIDIOC_S_FMT may change width and height. */
	/* Buggy driver paranoia. */
	min = fmt.fmt.pix.width * 2;
	if (fmt.fmt.pix.bytesperline < min)
		fmt.fmt.pix.bytesperline = min;
	min = fmt.fmt.pix.bytesperline * fmt.fmt.pix.height;
	if (fmt.fmt.pix.sizeimage < min)
		fmt.fmt.pix.sizeimage = min;
	switch (io) {
	case IO_METHOD_READ:
		init_read (fmt.fmt.pix.sizeimage);
		break;
	case IO_METHOD_MMAP:
		init_mmap(1);
		break;
	case IO_METHOD_USERPTR:
		init_userp (fmt.fmt.pix.sizeimage);
		break;
	}
}

void V4L2::close_device(void)
{
        if (-1 == close (fd))
	        errno_exit ("close");
        fd = -1;
}

void V4L2:: open_device(void)
{
        struct stat st; 
        if (-1 == stat (device, &st)) {
                fprintf (stderr, "Cannot identify '%s': %d, %s\n",
                         device, errno, strerror (errno));
                exit (EXIT_FAILURE);
        }
        if (!S_ISCHR (st.st_mode)) {
                fprintf (stderr, "%s is no device\n", device);
                exit (EXIT_FAILURE);
        }
        fd = open (device, O_RDWR /* required */ | O_NONBLOCK, 0);
        if (-1 == fd) {
                fprintf (stderr, "Cannot open '%s': %d, %s\n",
                         device, errno, strerror (errno));
                exit (EXIT_FAILURE);
        }
}

PyObject *V4L2:: updateMMap( )
{
  for (;;) {
    fd_set fds;
    struct timeval tv;
    int r;
    FD_ZERO (&fds);
    FD_SET (fd, &fds);
    // Timeout. 
    tv.tv_sec = 2;
    tv.tv_usec = 0;
    r = select (fd + 1, &fds, NULL, NULL, &tv);
    if (-1 == r) {
      if (EINTR == errno)
	continue;
      errno_exit ("select");
    }
    if (0 == r) {
      fprintf (stderr, "select timeout\n");
      exit (EXIT_FAILURE);
    }
    if (read_frame())
      break;
    
    // EAGAIN - continue select loop.
    sleep(1); 
    // force context switch to avoid giant sucking sound
    // this is a millisec
  }
  return PyInt_FromLong(0L);
}

void V4L2::init(void) {
  fprintf(stderr,"Init-ing Video under Querycap-V4L2\n");
  io		= IO_METHOD_MMAP;
  fd              = -1;
  buffers         = NULL;
  n_buffers       = 0;
  fprintf(stderr,"open_device...\n");
  open_device();
  fprintf(stderr,"init_device...\n");
  init_device();
  fprintf(stderr,"start_capture...\n");
  start_capturing();
  fprintf(stderr,"Done Init Video under Querycap-V4L2\n");
}

void V4L2::swap_rgb24(char *mem, int n) {
  char  c;
  char *p = mem;
  int   i = n;
  while (--i) {
    c = p[0]; p[0] = p[2]; p[2] = c;
    p += 3;
  }
}
