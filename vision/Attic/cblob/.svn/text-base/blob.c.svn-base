#include <string.h>
#include "blob.h"
#include "hsbrgb.h"
#include <stdio.h>
#include <errno.h>

/*********************************
 * All init operations expect the pointer to already have been malloced,
 * and all the del operations do not free the structure.  These operations
 * allocate and free memory used within the structures.  Therefore, to
 * use them correctly, your code should look like this:
 *
 *  struct bitmap* map;
 *  map = (struct bitmap*)malloc(sizeof(struct bitmap));
 *  Bitmap_init(map, 100, 100);
 *
 *  //use the bitmap
 *
 *  Bitmap_del(map);
 *  free(map);
 *
 * The factory methods which return pointers, on the other hand, such
 * as bitmap_from_ppm(), return an already-malloced structure
 * which must be freed by the user.  E.g.:
 *
 *  struct bitmap* map;
 *  map = bitmap_from_cap(camera, 76, 48);
 *
 *  //use the image
 *
 *  Bitmap_del(map);
 *  free(map);
 *
 **********************************/

/* ------------- Blob operations ------------
    Largely copied from pyro.vision.Blob
*/

void Blob_init(struct blob* theBlob, struct point* pixel){
  Blob_init_xy(theBlob, pixel->x, pixel->y);
}

void Blob_init_xy(struct blob* theBlob, int x, int y){
  theBlob->mass = 1;
  theBlob->ul.x = theBlob->lr.x = x;
  theBlob->ul.y = theBlob->lr.y = y;
  theBlob->cm_x = (double)x;
  theBlob->cm_y = (double)y;
}

void Blob_addpixel(struct blob* theBlob, struct point* pixel){
  Blob_addpixel_xy(theBlob, pixel->x, pixel->y);
}

void Blob_addpixel_xy(struct blob* theBlob, int x, int y){
  if (x < theBlob->ul.x)
    theBlob->ul.x = x;
  else if (x > theBlob->lr.x)
    theBlob->lr.x = x;
  if (y < theBlob->ul.y)
    theBlob->ul.y = y;
  else if (y > theBlob->lr.y)
    theBlob->lr.y = y;
  theBlob->cm_x = (double)(theBlob->mass * theBlob->cm_x + x)/
    (double)(theBlob->mass + 1);
  theBlob->cm_y = (double)(theBlob->mass * theBlob->cm_y + y)/
    (double)(theBlob->mass + 1);
  theBlob->mass++;
}

void Blob_joinblob(struct blob* theBlob, struct blob* other){
  if (other->ul.x < theBlob->ul.x)
    theBlob->ul.x = other->ul.x;
  else if (other->lr.x > theBlob->lr.x)
    theBlob->lr.x = other->lr.x;
  if (other->ul.y < theBlob->ul.y)
    theBlob->ul.y = other->ul.y;
  else if (other->lr.y > theBlob->lr.y)
    theBlob->lr.y = other->lr.y;
  theBlob->cm_x = (double)(theBlob->mass * theBlob->cm_x + other->mass * other->cm_x) /
    (double)(theBlob->mass + other->mass);
  theBlob->cm_y = (double)(theBlob->mass * theBlob->cm_y + other->mass * other->cm_y) /
    (double)(theBlob->mass + other->mass);
  theBlob->mass += other->mass;
}

/* -------------- Bitmap ops ------------------*/

void Bitmap_init(struct bitmap* map, int w, int h){
  int i;
  map->width = w;
  map->height = h;
  map->data = (uint16_t *) calloc(w*h, sizeof(uint16_t));
}

void Bitmap_set(struct bitmap* map, int x, int y, uint16_t in){
  if (x >= 0 && x < map->width && y >= 0 && y < map->height){
    map->data[y*map->width + x] = in;
  }
}

uint16_t Bitmap_get(struct bitmap* map, int x, int y){
  if (x >= 0 && x < map->width && y >= 0 && y < map->height){
    return map->data[y*map->width + x];
  }
}

void Bitmap_del(struct bitmap* map){
  free(map->data);
}

/*
  Write a bitmap to a pgm file.  Levels is the number of gray levels.
  If levels is 0, it will defaul to the maximum, 65535.
  Warning:  if levels is less than 255, every pixel will have to be truncated
  to one byte from two; this will take much longer. Returns 1 on success
  and 0 on failure*/
int Bitmap_write_to_pgm(struct bitmap* map, char* filename, int levels){
  FILE* out;
  int maxval = 0;
  int i, w;
  uint8_t temp;
  
  out = fopen(filename, "w");
  if (out == NULL){
    perror("Bitmap_write_to_pgm: Error opening file for write");
    return 0;
  }

  if (levels <= 0 || levels > 65535){
    //default to the maximum
    fprintf(out, "P5\n%d %d\n65535\n", map->width, map->height);
    maxval = 1;
  } else{
    fprintf(out, "P5\n%d %d\n%d\n", map->width, map->height, levels);
  }
  if (maxval || levels > 255){
    i = fwrite(map->data, 2, map->width * map->height, out);
    if (i == 0 && map->width * map->height != 0){
      perror("Bitmap_write_to_pgm: error writing to file");
      return 0;
    }
  } else{
    //We have to write single-bytes instead of double-bytes
    for (i = 0; i < map->width * map->height; i++){
      //This could definately be optimized by doing some pointer math
      temp = (uint8_t)(map->data[i] & 0xFF);
      w = fwrite(&temp, 1, 1, out);
      if (w == 0){
	perror("Bitmap_write_to_pgm: error writing to file");
	return 0;
      }
    }
  }
  fclose(out);
  return 1;
}
/*
void Bitmap_swap_colors(struct bitmap* image, int color1, int color2, int color3) {
  // used to swap color positions
  // swap_colors(im, 2, 1, 0) will swap 1st and 3rd colors
  int i;
  int c1, c2, c3;
  for (i = 0; i < image->width*image->height; i += 3) {
    c1 = ((uint8_t *)image->data)[i + 0];
    c2 = ((uint8_t *)image->data)[i + 1];
    c3 = ((uint8_t *)image->data)[i + 2];
    ((uint8_t *)image->data)[i + color1] = c1;
    ((uint8_t *)image->data)[i + color2] = c2;
    ((uint8_t *)image->data)[i + color3] = c3;
  }
  }*/

struct bitmap* Bitmap_invert_and_copy(struct bitmap* thebitmap) {
  int i;
  struct bitmap * bmp;
  bmp = (struct bitmap*)malloc(sizeof(struct bitmap));
  Bitmap_init(bmp, thebitmap->width, thebitmap->height);
  for (i = 0; i < thebitmap->width * thebitmap->height; i++){
    bmp->data[i] = ! thebitmap->data[i];
  }
  return bmp;
}  

void Bitmap_invert(struct bitmap* thebitmap) {
  int i;
  for (i = 0; i < thebitmap->width * thebitmap->height; i++){
    thebitmap->data[i] = ! thebitmap->data[i];
  }
}  

void Bitmap_or(struct bitmap* bmp1, struct bitmap* bmp2) {
  int i;
  for (i = 0; i < bmp1->width * bmp1->height; i++){
    bmp1->data[i] = bmp1->data[i] || bmp2->data[i];
  }
}  

void Bitmap_and(struct bitmap* bmp1, struct bitmap* bmp2) {
  int i;
  for (i = 0; i < bmp1->width * bmp1->height; i++){
    bmp1->data[i] = bmp1->data[i] && bmp2->data[i];
  }
}

  
/* -------------- Blobdata operations ---------------*/

struct blobdata* Blobdata_init(struct bitmap* theBitmap){
  int count = 0;
  int w, h, n, m, minBlobNum, maxBlobNum, i;
  struct blob* tempBlob;
  struct blobdata *data = (struct blobdata*)malloc(sizeof(struct blobdata));
  /*--------------------
    This is a traslation into C of Doug's Blob code from
    pyro.camera.Blobdata.__init__.  It's pretty much exactly
    the same algorithm.
    -------------------*/
  data->blobmap = (struct bitmap*)malloc(sizeof(struct bitmap));
  Bitmap_init(data->blobmap, theBitmap->width, theBitmap->height);
  data->equivList = (int *) malloc(sizeof(int) * BLOBLIST_SIZE);
  for (i = 0; i < BLOBLIST_SIZE; i++){
    data->equivList[i] = i;
  }
  data->bloblist = (struct blob**) calloc(BLOBLIST_SIZE, sizeof(struct blob*));

  for (w = 0; w < theBitmap->width; w++){
    for (h = 0; h < theBitmap->height; h++){
      if (Bitmap_get(theBitmap, w, h)){
	if (h == 0 && w == 0){
	  tempBlob = (struct blob*) malloc(sizeof(struct blob));
	  Blob_init_xy(tempBlob, w, h);
	  data->bloblist[count] = tempBlob;
	  Bitmap_set(data->blobmap, w, h, count++);
	}
	else if (w == 0){
	  if (Bitmap_get(theBitmap, w, h - 1)){
	    Blob_addpixel_xy(data->bloblist[Bitmap_get(data->blobmap, w, h-1)],
			  w, h);
	    Bitmap_set(data->blobmap, w, h, Bitmap_get(data->blobmap, w, h-1));
	  } else {
	    tempBlob = (struct blob*) malloc(sizeof(struct blob));
	    Blob_init_xy(tempBlob, w, h);
	    data->bloblist[count] = tempBlob;
	    Bitmap_set(data->blobmap, w, h, count++);
	  }
	}
	else if (h == 0){
	  if (Bitmap_get(theBitmap, w-1, h)){
	    Blob_addpixel_xy(data->bloblist[Bitmap_get(data->blobmap, w-1, h)],
			  w, h);
	    Bitmap_set(data->blobmap, w, h, Bitmap_get(data->blobmap, w-1, h));
	  } else {
	    tempBlob = (struct blob*) malloc(sizeof(struct blob));
	    Blob_init_xy(tempBlob, w, h);
	    data->bloblist[count] = tempBlob;
	    Bitmap_set(data->blobmap, w, h, count++);
	  }
	}
	else if (Bitmap_get(theBitmap, w-1, h) &&
		 Bitmap_get(theBitmap, w, h-1)){
	  if (Bitmap_get(data->blobmap, w-1, h) ==
	      Bitmap_get(data->blobmap, w, h-1)){
	    Blob_addpixel_xy(data->bloblist[Bitmap_get(data->blobmap, w-1, h)],
			  w, h);
	    Bitmap_set(data->blobmap, w, h, Bitmap_get(data->blobmap, w-1, h));
	  }
	  else {
	    minBlobNum = min(data->equivList[Bitmap_get(data->blobmap,
								w-1, h)],
			     data->equivList[Bitmap_get(data->blobmap,
								w, h-1)]);
	    maxBlobNum = max(data->equivList[Bitmap_get(data->blobmap,
								w-1, h)],
			     data->equivList[Bitmap_get(data->blobmap,
								w, h-1)]);
	    Blob_addpixel_xy(data->bloblist[minBlobNum], w, h);
	    Bitmap_set(data->blobmap, w, h, minBlobNum);
	    for (n = 0; n < BLOBLIST_SIZE; n++){
	      if (data->equivList[n] == maxBlobNum)
		data->equivList[n] = minBlobNum;
	    }
	  }
	}
	else{
	  if (Bitmap_get(theBitmap, w-1, h)){
	    Blob_addpixel_xy(data->bloblist[Bitmap_get(data->blobmap, w-1, h)],
			  w, h);
	    Bitmap_set(data->blobmap, w, h, Bitmap_get(data->blobmap, w-1, h));
	  }
	  else if (Bitmap_get(theBitmap, w, h-1)){
	    Blob_addpixel_xy(data->bloblist[Bitmap_get(data->blobmap, w, h-1)],
			  w, h);
	    Bitmap_set(data->blobmap, w, h, Bitmap_get(data->blobmap, w, h-1));
	  }
	  else {
	    tempBlob = (struct blob*)malloc(sizeof(struct blob));
	    Blob_init_xy(tempBlob, w, h);
	    data->bloblist[count] = tempBlob;
	    Bitmap_set(data->blobmap, w, h, count++);
	  }
	}
      }
    }
  }

  data->nblobs = 0;
  for (n = 1; n < count; n++){
    if (data->equivList[n] == n){
      for (m = n+1; m < count; m++){
	if (data->equivList[m] == n){
	  Blob_joinblob(data->bloblist[n], data->bloblist[m]);
	  free(data->bloblist[m]);
	  data->bloblist[m] = NULL;
	}
      }
      data->nblobs++;
    }
  }

  for (n = 1; n < count; n++){
    m = n-1;
    while(data->bloblist[m] == NULL){
      data->bloblist[m] = data->bloblist[m+1];
      data->bloblist[m+1] = NULL;
      if (m == 0)
	break;
      m--;
    }
  }
  //Shrink bloblist to the size of the list blobs
  data->bloblist = (struct blob**)realloc(data->bloblist,
					   sizeof(struct blob*)*data->nblobs);
  return data;
}

void Blobdata_del(struct blobdata* data){
  int i;
  if (data->bloblist){
    for (i = 0; i < data->nblobs; i++){
      if (data->bloblist[i] != NULL){
	free(data->bloblist[i]);
      }
    }
    free(data->bloblist);
  }
  free(data->equivList);
  Bitmap_del(data->blobmap);
  free(data->blobmap);
}


/* --------------- transducers -----------------
   These functions take image data of some form and return a bitmap
   that can be used with the blob functions.
*/

struct bitmap* bitmap_from_cap(struct image_cap* image, int width, int height,
			       double (*filter)(double, double, double),
			       double threshold){
  int i;
  float h, s, v;
  double temp;
  int red, green, blue;
  struct bitmap* bmp = (struct bitmap*) malloc(sizeof(struct bitmap));
  Bitmap_init(bmp, width, height);
  if (image->bpp == 24){
    for (i = 0; i < image->size; i += 3) {
      // FIX: check on ordering of rgb
      red  = ((uint8_t *)image->data)[i + 2]/255.0;
      green= ((uint8_t *)image->data)[i + 1]/255.0;
      blue = ((uint8_t *)image->data)[i + 0]/255.0;
      bmp->data[i/3] = ((*filter)(red, green, blue) > threshold);
    }
  } else if (image->bpp == 8){
    for (i = 0; i < image->size; i++){
      temp = ((uint8_t*)image->data)[i]/255.0;
      bmp->data[i] = ((*filter)(temp, temp, temp) > threshold);
    }
  } else {
    perror("bitmap_from_cap: bpp not supported.");
  }
  return bmp;
}

struct bitmap* bitmap_from_ppm(char* filename,
			       double (*filter)(double, double, double),
			       double threshold){
  int rows, cols, maxval;
  FILE* theFile;
  uint8_t* rgb;
  uint16_t*  RGB;
  struct bitmap* bmp;
  int i;
  double red, green, blue;
  float h, s, v;
  

  theFile = fopen(filename, "r");
  if (!theFile){
    perror("bitmap_from_ppm: Error opening file for read.");
  }
  bmp = (struct bitmap*)malloc(sizeof(struct bitmap));
  fscanf(theFile, "%*2c\n%d %d\n%d", &cols, &rows, &maxval);
  Bitmap_init(bmp, cols, rows);
  /*
    If there are fewer than 255 colors in a pgm, each color value
    is represented by one byte.  Otherwise, two bytes are used.
    Thus, we need to treat the file differently depending on the
    maxval.
  */
  if (maxval <= 255){
    rgb = (uint8_t*)calloc(rows*cols*3, 1);
    fread(rgb, 1, rows*cols*3, theFile);
    for (i = 0; i < rows*cols*3; i += 3) {
      red  = rgb[i + 0]/(double)maxval;
      green= rgb[i + 1]/(double)maxval;
      blue = rgb[i + 2]/(double)maxval;
      bmp->data[i/3] = ((*filter)(red, green, blue) > threshold);
    }
    free(rgb);
  }
  else{
    RGB = (uint16_t*)calloc(rows*cols*3, 2);
    fread(RGB, 2, rows*cols*3, theFile);
    for (i = 0; i < rows*cols*3; i += 3) {
      red  = RGB[i]/(double)maxval;
      green= RGB[i + 1]/(double)maxval;
      blue = RGB[i + 2]/(double)maxval;
      bmp->data[i/3] = ((*filter)(red, green, blue) > threshold);
    }
    free(RGB);
  }
  fclose(theFile);
  
  return bmp;
}
  
struct bitmap* bitmap_from_pgm(char* filename,
			       double (*filter)(double, double, double),
			       double threshold){
  unsigned int rows, cols, maxval;
  FILE* theFile;
  unsigned char* gray;
  struct bitmap* bmp;
  double temp;
  int i;

  theFile = fopen(filename, "r");
  if (!theFile){
    perror("bitmap_from_pgm: Error openeing file for read");
  }

  fscanf(theFile, "%*s%d%d%d", &cols, &rows, &maxval);
  gray = (unsigned char*)calloc(rows*cols, 1);
  bmp = (struct bitmap*)malloc(sizeof(struct bitmap));
  Bitmap_init(bmp, cols, rows);
  fread(gray, 1, rows*cols, theFile);
  fclose(theFile);
  for (i = 0; i < rows*cols; i++) {
    //Calculate once here, so we don't have
    //to write it three times on the next line.
    temp = gray[i]/(double)maxval;
    bmp->data[i] = ((*filter)(temp, temp, temp) > threshold);
  }
  free(gray);
  return bmp;
}

/* array should be a 1D, width*height element array. */
struct bitmap* bitmap_from_8bitGrayArray(uint8_t* array, int width, int height,
					 double (*filter)(double, double, double),
					 double threshold){
  int i;
  double temp;
  struct bitmap* bmp;

  bmp = (struct bitmap*)malloc(sizeof(struct bitmap));
  Bitmap_init(bmp, width, height);
  for (i = 0; i < width*height; i++){
    temp = array[i]/255.0;
    bmp->data[i] = ((*filter)(temp, temp, temp) > threshold);
  }
  return bmp;
}

/* array should be a 1D, width*height*3 length array of RGB values,
   i.e., array[0] = R_1, array[1] = G_1. array[2] = B_1, array[3] = R_2, etc*/
struct bitmap* bitmap_from_8bitRGBArray(uint8_t* array, int width, int height,
					 double (*filter)(double, double, double),
					double threshold){
  int i;
  double r, g, b;
  struct bitmap* bmp;
  bmp = (struct bitmap*)malloc(sizeof(struct bitmap));
  Bitmap_init(bmp, width, height);
  for (i = 0; i < width*height*3; i += 3){
    r = array[i]/255.0;
    g = array[i+1]/255.0;
    b = array[i+2]/255.0;
    bmp->data[i/3] = ((*filter)(r, g, b) > threshold);
  }
  return bmp;
}
struct bitmap* bitmap_from_8bitBGRArray(cbuf_t pyarray, int width, int height,
					double (*filter)(double, double, double),
					double threshold){
  int i;
  double r, g, b;
  struct bitmap* bmp;
  uint8_t* array = (uint8_t*)pyarray;
  bmp = (struct bitmap*)malloc(sizeof(struct bitmap));
  Bitmap_init(bmp, width, height);
  for (i = 0; i < width*height*3; i += 3){
    r = array[i+2]/255.0;
    g = array[i+1]/255.0;
    b = array[i]/255.0;
    bmp->data[i/3] = ((*filter)(r, g, b) > threshold);
  }
  return bmp;
}
/* array should be a 1D, width*height length array of packed 32-bit RGB values,
   i.e., array[0] = 0x00RRGGBB */
struct bitmap* bitmap_from_32bitPackedRGBArray(uint32_t* array, int width, int height,
					       double (*filter)(double, double, double),
					       double threshold){
  int i;
  double r, g, b;
  struct bitmap* bmp;
  bmp = (struct bitmap*)malloc(sizeof(struct bitmap));
  Bitmap_init(bmp, width, height);
  for (i = 0; i < width*height; i++){
    r = ((array[i] & 0x00FF0000) >> 16)/255.0;
    g = ((array[i] & 0x0000FF00) >> 8)/255.0;
    b = (array[i] & 0x000000FF)/255.0;
    bmp->data[i] = ((*filter)(r, g, b) > threshold);
  }
  return bmp;
}
   

//---------- Filter functions ------------------

double filter_red (double r, double g, double b){
  return r;
}

double filter_green (double r, double g, double b){
  return g;
}

double filter_blue (double r, double g, double b){
  return b;
}

double filter_hue (double r, double g, double b){
  float h, s, v;
  rmRGBtoHSV(r, g, b, &h, &s, &v);
  return h;
}

double filter_saturation (double r, double g, double b){
  float h, s, v;
  rmRGBtoHSV(r, g, b, &h, &s, &v);
  return s;
}

double filter_brightness (double r, double g, double b){
  float h, s, v;
  rmRGBtoHSV(r, g, b, &h, &s, &v);
  return v;
}

/* ------- Blob output ---------
   Given an array of blobdata pointers, an array of ints (packed
   RGB color values for the channel colors), and an int
   representing the length of the previous two arrays (which much be equal),
   return a struct that looks like the player-stage blob struct
*/
#ifdef HAVE_PLAYER_H
player_blobfinder_data_t* make_player_blob_default(struct blobdata** blobs) {
  int channel_data[] = {255, 255, 255, 
			255, 0, 0,   
			0, 255, 0,   
			0, 0, 255,   
			0, 255, 255, 
			255, 255, 0,  
			255, 0, 255,  
			0, 0, 0 };
  int n_channels = 8;
  uint32_t channels[8];
  int i;
  for(i = 0; i < n_channels; i++) {
    channels[i] = ((channel_data[i * 3 + 0] << 16) ||
		   (channel_data[i * 3 + 1] << 8) ||
		   (channel_data[i * 3 + 2]));
  }
  return make_player_blob(blobs, channels, n_channels);
}

player_blobfinder_data_t* make_player_blob(struct blobdata** blobs,
						 uint32_t* channels,
						 int n_channels){
  player_blobfinder_data_t* data;
  player_blobfinder_header_elt_t header;
  player_blobfinder_blob_elt_t blob;
  struct blob* currblob;
  int maxn, maxb, i, j, lastj;

  data = (player_blobfinder_data_t*)malloc(sizeof(player_blobfinder_data_t));
  data->width = blobs[0]->width;
  data->height = blobs[0]->height;

  //If there are more channels than P._B._MAX_CHANNELS, we are just
  //going to ignore the rest of them.
  maxn = min(n_channels, PLAYER_BLOBFINDER_MAX_CHANNELS);
  
  lastj = 0;
  for (i = 0; i < maxn; i++){
    header.index = lastj;
    //If there are more blobs in this channel than P._B._MAX_B._P._CHANNEL
    //we will ignore them.
    maxb = min(blobs[i]->nblobs, PLAYER_BLOBFINDER_MAX_BLOBS_PER_CHANNEL);
    header.num = maxb;
    data->header[i] = header;

    for (j = 0; j < maxb; j++){
      currblob = blobs[i]->bloblist[j];
      //The ints in the channels list ought to be the
      //color of the channel that the blob data came from, although
      //I suppose you could use any int you wanted.
      blob.color = channels[i];
      blob.area = (currblob->lr.x - currblob->ul.x) * (currblob->lr.y - currblob->ul.y);
      blob.x = (uint16_t)currblob->cm_x;
      blob.y = (uint16_t)currblob->cm_y;
      blob.left = currblob->ul.x;
      blob.top = currblob->ul.y;
      blob.right = currblob->lr.x;
      blob.bottom = currblob->lr.y;
      //range can only be calcuated in the simulator.
      blob.range = 0;

      //The blobs are packed in this array, indexed by the
      //header struct.
      data->blobs[lastj+j] = blob;
    }

    lastj += maxb;
  }
  return data;
}

/*
  This function is almost identical to the one above, but it
  does not truncate the blob or channels lists to conform to
  Player/Stage's size limits.  It returns a playerblob_t pointer,
  which is nearly compatible with the Player/Statge struct, but not
  exactly.
*/
playerblob_t* make_player_blob_varsize(struct blobdata** blobs,
				       uint32_t* channels,
				       int n_channels){
  playerblob_t* data;
  player_blobfinder_header_elt_t header;
  player_blobfinder_blob_elt_t blob;
  struct blob* currblob;
  int i, j, lastj, totalblobs;

  data = (playerblob_t*)malloc(sizeof(playerblob_t));
  data->width = blobs[0]->width;
  data->height = blobs[0]->height;
  data->n_channels = n_channels;
  //Allocate enough space for the array of headers
  data->header = (player_blobfinder_header_elt_t*)malloc(sizeof(player_blobfinder_header_elt_t)*n_channels);
  totalblobs = 0;
  for (i = 0; i < n_channels; i++){
    totalblobs += blobs[i]->nblobs;
  }
  data->blobs = (player_blobfinder_blob_elt_t*)malloc(sizeof(player_blobfinder_blob_elt_t)*totalblobs);
  
    
  lastj = 0;
  for (i = 0; i < n_channels; i++){
    header.index = lastj;
    header.num = blobs[i]->nblobs;
    data->header[i] = header;

    for (j = 0; j < blobs[i]->nblobs; j++){
      currblob = blobs[i]->bloblist[j];
      blob.color = channels[i];
      blob.area = (currblob->lr.x - currblob->ul.x) * (currblob->lr.y - currblob->ul.y);
      blob.x = (uint16_t)currblob->cm_x;
      blob.y = (uint16_t)currblob->cm_y;
      blob.left = currblob->ul.x;
      blob.top = currblob->ul.y;
      blob.right = currblob->lr.x;
      blob.bottom = currblob->lr.y;
      blob.range = 0;
      data->blobs[lastj+j] = blob;
    }

    lastj += blobs[i]->nblobs;
  }
  return data;
}   

void playerblob_del(playerblob_t* blobs){
  free(blobs->header);
  free(blobs->blobs);
}
#endif
