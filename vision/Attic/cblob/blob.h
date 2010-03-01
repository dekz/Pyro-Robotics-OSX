#ifndef __BLOB_H__
#define __BLOB_H__

#include "config.h"

#include "v4lcap.h"
#include <stdint.h>

#ifdef HAVE_PLAYER_H
#include <player.h>
#endif

#define BLOBLIST_SIZE 10000
#define BITMAP_CUTOFF 0.5
#define PLAYERBLOB_MAX_CHANNELS 8
#define min(X, Y)  ((X) < (Y) ? (X) : (Y))
#define max(X, Y)  ((X) > (Y) ? (X) : (Y))

//Given a bitmap, computes an (x,y) offset (row-major)
//#define bm_offset(bm, x, y)  x*bm->width + y

typedef uint8_t* cbuf_t;

struct point{
  int x;
  int y;
};

struct bitmap{
  int width;
  int height;
  uint16_t* data;
};

struct blob{
  int mass;
  struct point ul;
  struct point lr;
  double cm_x;
  double cm_y;
};

struct blobdata{
  int width;
  int height;
  int nblobs;
  struct bitmap* blobmap;
  int* equivList;
  struct blob** bloblist;
};


/*Very similar to a really player_blobfinder_data_t, but
  the size of the array is set at runtime.
*/
#ifdef HAVE_PLAYER_H
typedef struct player_blobfinder_data_varsize{
  uint16_t width, height;
  int n_channels;
  player_blobfinder_header_elt_t* header;
  player_blobfinder_blob_elt_t* blobs;
} playerblob_t;
#endif

/*----------- Blob manipulation functions -----------
  Mostly for internal use by the Blobdata functions
*/
void Blob_init(struct blob* theBlob, struct point* pixel);
void Blob_init_xy(struct blob* theBlob, int x, int y); 
void Blob_addpixel(struct blob* theBlob, struct point* pixel);
void Blob_addpixel_xy(struct blob* theBlob, int x, int y);
void Blob_joinblob(struct blob* theBlob, struct blob* other);

/*----------- Bitmap Manipulation functions --------
 */
void Bitmap_init(struct bitmap* map, int w, int h);
void Bitmap_set(struct bitmap* map, int x, int y, uint16_t in);
uint16_t Bitmap_get(struct bitmap* map, int x, int y);
void Bitmap_del(struct bitmap* map);
int Bitmap_write_to_pgm(struct bitmap* map, char* filename, int levels);
struct bitmap* Bitmap_invert_and_copy(struct bitmap* thebitmap);
void Bitmap_invert(struct bitmap* thebitmap);
//void Bitmap_swap_colors(struct bitmap* image, int color1, int color2, int color3);
void Bitmap_or(struct bitmap* bmp1, struct bitmap* bmp2);
void Bitmap_and(struct bitmap* bmp1, struct bitmap* bmp2);

/*----------- Blobdata functions ----------
 */

struct blobdata* Blobdata_init(struct bitmap* theBitmap);
//void Blobdata_init(struct blobdata* data, struct bitmap* theBitmap);
void Blobdata_del(struct blobdata* data);
//SWIG support


/*---------- transducer functions -------------
     These functions should take image data in some format, filter
     it, and return a bitmap pointer.  They should utilize one of the
     filter_* callbacks in order to return an appropirately filtered
     bitmap.
*/

//Take image data from a live v4l feed
struct bitmap* bitmap_from_cap(struct image_cap* image, int width, int height,
			       double (*filter)(double, double, double),
			       double threshold);
//Import a ppm
struct bitmap* bitmap_from_ppm(char* filename,
			       double (*filter)(double, double, double),
			       double threshold);
//Import a pgm (grayscale ppm)
struct bitmap* bitmap_from_pgm(char* filename,
			       double (*filter)(double, double, double),
			       double threshold);
//Import a 1D array of 8-bit gray pixels
struct bitmap* bitmap_from_8bitGrayArray(uint8_t* array, int width, int height,
					 double (*filter)(double, double, double),
					 double threshold);
//Import a 1D array of 8-bit RGB values
//i.e., array = RGBRGBRGB...
struct bitmap* bitmap_from_8bitRGBArray(uint8_t* array, int width, int height,
					 double (*filter)(double, double, double),
					 double threshold);
struct bitmap* bitmap_from_8bitBGRArray(cbuf_t array, int width, int height,
					double (*filter)(double, double, double),
					double threshold);
//Import a 1D array of packed 32-bit RGB values,
//i.e., array[0] = 0x00RRGGBB
struct bitmap* bitmap_from_32bitPackedRGBArray(uint32_t* array, int width, int height,
					       double (*filter)(double, double, double),
					       double threshold);


/*--------- filter functions -----------
    Must conform to the prototype double func(double r, double g, double b).
    They Are expected to take an rgb value, with each element in the range
    [0.0, 1.0], and returns a value in the same range. */


double filter_red (double r, double g, double b);
double filter_green (double r, double g, double b);
double filter_blue (double r, double g, double b);
double filter_hue (double r, double g, double b);
double filter_saturation (double r, double g, double b);
double filter_brightness (double r, double g, double b);


/*------------- Player/Stage blob functions -------
  These functions will take an array of blobdata pointers
  and transform them into a Player/Stage-style stucture
  with multiple channels of blob data.

  make_player_blob  returns a pointer to an actual
  Player/Stage struct, which has limits on the number of
  channels allowed and the number of blobs per channel.

  make_player_blob_varsize returns a pointer to a struct that
  is similar to the real Player/Stage struct, but with no limit
  on blobs per channel or number of channels.  The struct cannot
  be dynamically resized, however.
*/
#ifdef HAVE_PLAYER_H
player_blobfinder_data_t* make_player_blob_default(struct blobdata** blobs);
player_blobfinder_data_t* make_player_blob(struct blobdata** blobs, uint32_t* channels, int n_channels);
playerblob_t* make_player_blob_varsize(struct blobdata** blobs, uint32_t* channels, int n_channels);
void playerblob_del(playerblob_t* blobs);
#endif //HAVE_PLAYER_H

#endif
