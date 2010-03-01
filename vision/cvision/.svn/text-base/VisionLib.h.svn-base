#ifndef __VISION_H__ 
#define __VISION_H__ 

#include <Python.h>
#include <Device.h>

typedef struct bitmap
{
  int height;
  int width;
  int depth;
  unsigned int data[384][240];
  int *equivList;
}Bitmap;

typedef struct point{
  int x;
  int y;
} Point;

typedef struct blob{

  Point ul;
  Point lr;
  Point cm;

  int mass;
  int next;
}Blob;


#define SWAP(a,b) { int itemp=(a);(a)=(b);(b)=itemp;}
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAXBLOBS 2000
#define MAXMOTIONLEVELS 3

class Vision {
public:
  static const int RED = 0;
  static const int GREEN = 1;
  static const int BLUE = 2;
  static const int ALL = 10;
  static const int BLACK = 11;

  static const int WORKSPACE = 50;
  static const int ORIGINAL = 60;
  static const int IMAGE = 70;

  static const int AND = 100;
  static const int OR = 101;
  static const int XOR = 102;
  static const int ACCUM = 103;
  
  Vision();
  Vision(int w, int h, int d, int r, int g, int b);
  Vision(int w, int h, int d);
  ~Vision();
  PyObject *initialize(int wi, int he, int de, int r, int g, int b);
  PyObject *registerCameraDevice(void *args);
  //PyObject *registerCameraDevice(Device device);
  PyObject *superColor(float w1, float w2, float w3,
		       int outChannel, int threshold);
  PyObject *matchRange(int lr, int lg, int lb,
		       int hr, int hg, int hb,
		       int outChannel);
  PyObject *match(int r, int g, int b, int tolerance,
		  int outChannel);
  PyObject *matchList(PyObject *myList);
  PyObject *get(int w, int h);
  PyObject *set(int offset, int r, int g, int b);
  PyObject *set(int w, int h, int r, int g, int b);
  PyObject *setVal(int w, int h, int d, int val);
  PyObject *setImage(PyObject *array);
  PyObject *drawRect(int x1, int y1, int x2, int y2, 
		int fill, int channel);
  PyObject *drawCross(int x1, int y1, int length, int channel);
  PyObject *scale(float r, float g, float b);
  PyObject *meanBlur(int kernel);
  PyObject *gaussianBlur();
  PyObject *medianBlur(int kernel);
  PyObject *threshold(int channel, int value);
  int getMiddleIndex(int median[4][400], int kernel);
  PyObject *inverse(int channel);
  int getWidth() { return width; }
  int getHeight() { return height; }
  int getDepth() { return depth; }
  PyObject *saveImage(char *filename);
  PyObject *startMovie(char *filename);
  PyObject *stopMovie();
  PyObject *continueMovie();
  PyObject *getMMap();

  PyObject *histogram(int x1, int y1, int x2, int y2, int bins);
  PyObject *grayScale();
  PyObject *sobel(int val);
  PyObject *orientation(double current_height);
  PyObject *fid(int val);
  PyObject *setPlane(int d, int value);
  PyObject *blobify(int inChannel, int low, int high, 
			    int sortmethod, 
		    int size, int drawBox, int super_color);
  PyObject *applyFilter(PyObject *filter);
  PyObject *applyFilters(PyObject *filterList);
  PyObject *addFilter(PyObject *newFilter);
  PyObject *applyFilterList();
  PyObject *setFilterList(PyObject *filterList);
  PyObject *getFilterList();
  PyObject *popFilterList();

  int getCopyMode() { return copyMode; }
  void setCopyMode(int value) {copyMode = value;}
  PyObject *getRGB();
  PyObject *setRGB(int r, int g, int b); 

  PyObject *mask(int channel);
  PyObject *backup();
  PyObject *restore();
  PyObject *motion(int threshold, int outChannel);
  PyObject *rotate();
  PyObject *addNoise(float percent, int range);
  PyObject *getMenu();
  PyObject *swapPlanes(int d1, int d2);
  PyObject *rgb2yuv();
  PyObject *yuv2rgb();
  PyObject *rgb2hsv();
  PyObject *hsv2rgb();

  int feql(int x, int y, double t);

 protected:
  unsigned char *Image; // current image (currently only image is available)
  unsigned char *image;
  unsigned char *motionArray[MAXMOTIONLEVELS];
  int motionCount;
  int copyMode;
  int allocatedImage;
  int movieMode;
  int movieCounter;
  char movieFilename[50];

  PyObject *filterList;
  int width;
  int height;
  int depth;
  int rgb[3];

  Blob *initBlob(Blob *b);
  Blob *initBlob( Blob *b, int y, int x );
  Blob *addPixel( Blob *b, int y,int x );
  void joinBlob( Blob *self, Blob *other );
  void deleteBlob( Blob *b );
  int getBlobWidth( Blob *b );
  int getBlobHeight( Blob *b );
  int getBlobArea( Blob *b );
  void sortBlobs(int sortMethod, Blob bloblist[], int indexes[], int size);
  PyObject *copy(int,int);
};

#endif
