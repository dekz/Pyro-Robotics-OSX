#include "v4lcap.h"
#include "blob.h"
#include <stdio.h>

#define WIDTH 768
#define HEIGHT  480
#define PBMHEADER "P5\n768\n480\n255\n"
#define PGMHEADER_F "P5\n%d\n%d\n%d\n"
#define PPMHEADER "P6\n768\n480\n255\n"

#define USE_V4L

int main(int argc, char** argv){
  struct image_cap* camera;
  struct bitmap* bmp;
  struct blobdata* thedata;
  FILE* out;
  int i, j;

#ifdef USE_V4L
  camera = Cgrab_image("/dev/video0", WIDTH, HEIGHT, 1, 1);
  printf("Opened device\n");
  printf("bpp: %d\n", camera->bpp);
  Crefresh_image(camera, WIDTH, HEIGHT);
  out = fopen("cap.ppm", "w");
  fprintf(out, PPMHEADER);
  // swap colors to write out fast:
  swap_colors(camera, 2, 1, 0);
  fwrite(camera->data, 1, camera->size, out);
  // swap back:
  swap_colors(camera, 2, 1, 0);
  bmp = bitmap_from_cap(camera, WIDTH, HEIGHT, filter_red, 0.3);
  printf("Got bitmap_from_cap\n");
#else
  bmp = bitmap_from_ppm("cap.ppm", filter_red, 0.3);
  printf("Got bitmap_from_ppm('cap.ppm')\n");
#endif

  Bitmap_write_to_pgm(bmp, "bmp.pgm", 1);
  printf("Wrote bmp\n");

  thedata = Blobdata_init(bmp);
  printf("Blobdata_init\n");

  if (!Bitmap_write_to_pgm(thedata->blobmap, "blob.pgm", thedata->nblobs)){
    printf("Error");
  }
  
  Blobdata_del(thedata);
  free(thedata);
  Bitmap_del(bmp);
  free(bmp);
#ifdef USE_V4L
  Cfree_image(camera);
#endif
  return 0;
}
