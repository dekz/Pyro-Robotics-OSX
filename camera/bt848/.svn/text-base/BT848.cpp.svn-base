/*
 * Adapted from the standard BT848 continuous example for the PXC200 pc104 framegrabber
 *
 *     Needs:
 *       - bt848 driver ver. 011598 by Brad Parker
 *            (ftp://ftp.parker.boston.ma.us/pub/mbone/bt848/bt848-011598.tar.gz)
 *       - bt848-cont.p1 patch by Luca Iocchi
 *            (ftp://ftp.dis.uniroma1.it/~iocchi/Linux/drivers/bt848/bt848-cont.p1)
 */

#include "BT848.h"

BT848::BT848 ( const char* dname, int wi, int hi, int de):
  Device(wi, hi, de) {
  size = wi * hi * 4; // size of raw buffer
  int msize = wi * hi * de; // size of image buffer
  VIDEO_DEV = new char[strlen(dname)+1];
  strcpy(VIDEO_DEV, dname);
  buffer = new unsigned char [size];
  image = new unsigned char [msize];
  init();
}

BT848::~BT848() {
 close (fd);
 delete [] buffer;
 delete [] image;
}

PyObject *BT848::updateMMap( ) {
  unsigned char *mmptr;
  if (read(fd, buffer, size) != size) {
    perror("read");
    close(fd);
    exit(1);
  }
  /* get error counts */
  if (ioctl(fd, METEORGCOUNT, &cnt)) {
      perror("ioctl GetCount failed");
      exit (1);
  }
  if (0) {
    printf ("Captured:\n  frames: %ld\n  even fields: %ld\n  odd fields: %ld\n",
	    cnt.frames_captured,
	    cnt.even_fields_captured,
	    cnt.odd_fields_captured);
    printf ("Fifo errors: %ld\n", cnt.fifo_errors);
    printf ("DMA errors:  %ld\n", cnt.dma_errors);   
  }
  mmptr = buffer;
  int pos = 0;
  for (int j=0; j<height; j++) {
    for (int k=0; k<width; k++) {
      image[pos + 0] = *mmptr++;            /* blue */
      image[pos + 1] = *mmptr++;            /* green */
      image[pos + 2] = *mmptr++;            /* red */
      *mmptr++;                     /* NULL byte */
      pos += 3;
     }
  }        
  return PyInt_FromLong(0L);
}

void BT848::init(void) {
  fprintf(stderr,"Init-ing Video under BT848\n");
  struct meteor_geomet geo;
  char rgb[3], header[16], *p;
  int j, k;
  /* open the device */
  if ((fd = open(VIDEO_DEV, O_RDWR)) <= 0) {
    perror (VIDEO_DEV);
    exit (1);
  }

  /* initialize the Imagenation PXC200.
   *
   * WARNING: this function may hang Linux if the board is not a PXC200!!!
   */
  printf ("initializing PXC200\n");
  if (ioctl (fd, BT848_INITPXC200, &icontrol) < 0) {
    perror ("BT848_INITPXC200 ioctl\n");
    exit (1);
  }

  /* set capture geometry */
  geo.rows = height;              /* # of lines in output image */
  geo.columns = width;           /* # of pixels in a row in output image */
  geo.frames = 1;               /* # of frames in a buffer */
  geo.oformat = METEOR_GEO_RGB24 ; /* RGB 24 in 4 bytes: NULL,R,G,B */
  if (ioctl (fd, METEORSETGEO, &geo) < 0) {
    perror ("METEORSETGEO ioctl\n");
    exit (1);
  }                             
  /* set input video format */
  icontrol = METEOR_FMT_NTSC;
  if (ioctl (fd, METEORSFMT, &icontrol) < 0) {
    perror ("METEORSFMT ioctl\n");
    exit (1);
  }
  /* set input port */
#ifdef USE_SVIDEO_INPUT
  icontrol = METEOR_INPUT_DEV0;        /* PXC200 S-video connector */
#else
  icontrol = METEOR_INPUT_DEV1;        /* PXC200 BNC composite video connector */
#endif
  if (ioctl (fd, METEORSINPUT, &icontrol) < 0) {
    printf ("METEORSINPUT ioctl failed: %d\n", errno);
    exit (1);
  }                          
}



