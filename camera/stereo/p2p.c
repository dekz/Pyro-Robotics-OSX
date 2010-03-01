/********************************************************************* */
/* p2p.c */
/* */
/* Implements Pixel-to-Pixel stereo algorithm, as explained in the  */
/* technical report "Depth Discontinuities by Pixel-to-Pixel Stereo", */
/* STAN-CS-TR-96-1573, Stanford University, July 1996. */
/* */
/* Version ?? */
/* */
/* Author:  Stan Birchfield, birchfield@cs.stanford.edu */
/* Date:  November 8, A.D. 1996 */
/********************************************************************* */

/* Standard includes */
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <stdlib.h>

/* Our includes */
#include "base.h"
#include "pnmio.h"
#include "error.h"
#include "p2p.h"

int g_rows, g_cols, g_maxdisp;

int g_slop;  /* expand arrays so we don't have to keep checking whether index is too large */

/* Whether to write the results after independent scanline matching */
BOOL writeIntermediateResults = FALSE;

/* Filenames of images and output */
char dir_in[100] = ".";
char basenameL[100];
char basenameR[100];
char basename_dm_in[100];
char basename_ig[100];
char fnameL[100];
char fnameR[100];
char fname_dm_in[100];
char fname_dm[] = "dm.pgm";
char fname_dd[] = "dd.pgm";
char fname_dd_intermediate[] = "dd_inter.pgm";
char fname_dm_intermediate[] = "dm_inter.pgm";

/* Functions in other files */
void setOcclusionPenalty(int op);
void setReward(int r);
int getOcclusionPenalty(void);
int getReward(void);
void setReliableThreshold(int th);
void setAlpha(double a);
void setMaxAttractionThreshold(int th);
int getReliableThreshold(void);
double getAlpha(void);
int getMaxAttractionThreshold(void);
void matchScanlines(uchar *imgL,
                    uchar *imgR,
                    uchar *disparity_map,
                    uchar *depth_discontinuities,
                    char *ptr_ig);
void postprocess(uchar *imgL,
                 uchar *imgR,
                 uchar *dm_orig,
                 uchar *disp_map,
                 uchar *dd_map);

int writePostprocessingIntermediateResults = FALSE;



/********************************************************************* */
/* usage */
/********************************************************************* */

static void usage(char *command)
{
  fprintf(stderr,
          "\nPixel-to-pixel stereo algorithm.\n\n"
          "usage:  %s [options] file1 file2 maxdisparity [file_dm]\n\n"
          "Files 'file1' and 'file2' are read, the stereo algorithm (including\n"
          "postprocessing) is run, and the resulting disparity map and depth\n"
          "discontinuities are saved in files '%s' and '%s'.  Note that maxdisp\n"
          "must lie between 14 and 50.  The original images must be in PGM file\n"
          "format.  If the -b option is selected, then the results after processing\n"
          "the scanlines independently are also saved, in '%s' and '%s'.  All results\n"
          "are written to the current directory.  Options:\n\n"
          "        [-h]     displays this help message\n"
          "        [-o n]   sets the occlusion penalty to 'n' (default: %d)\n"
          "        [-r n]   sets the reward to 'n' (default: %d)\n"
          "        [-d dir] looks for input files in directory 'dir'\n"
          "                 (default: current directory)\n"
          "        [-b]     also writes out the results after independent matching\n"
          "        [-rel n]  sets the reliable threshold to n (default: %d)\n"
          "        [-alpha f]  sets alpha (for reliability) to f (default: %f)\n"
          "        [-ma n]  sets the max-attraction threshold to n (default: %d)\n\n"
          "        [-wpi]   writes the intermediate results during postprocessing\n"
          "                 (default:  off)\n"
          "        [-np]    do not postprocess disparity map\n"
          "        [-jp]    just postprocess disparity map\n"
          "                 (i.e., 'file_dm' is taken to be a disparity map to\n"
          "                 postprocess.  'file2' is ignored).\n"
          "        [-ig f]  for matching, uses intensity gradients specified\n"
          "                 in 'f' (E.g., f='ig%%c.pgm'). x & y go into '%%c'\n"
          "Example:  %s -o 15 -hr 30 -d ~/images img1.pgm img2.pgm 20\n\n",
          command, fname_dm, fname_dd, fname_dm_intermediate, fname_dd_intermediate,
          getOcclusionPenalty(), getReward(), 
          getReliableThreshold(), getAlpha(), 
          getMaxAttractionThreshold(),
          command);
  exit(1);
}


static void size_error(int ncols, int nrows)
{
  error("Wrong number of columns or rows.\n"
        "     Image is of size %d by %d, but\n"
        "     expecting %d by %d.\n",
        ncols, nrows, g_cols, g_rows);
}


/********************************************************************* */
/* main */
/* */
/* Main routine for running the pixel-to-pixel stereo algorithm. */
/********************************************************************* */

int main(int argc, char *argv[]) {
  BOOL leftImageHasBeenRead = FALSE;
  BOOL rightImageHasBeenRead = FALSE;
  BOOL disparityMapHasBeenRead = FALSE;
  BOOL do_matching = TRUE;
  BOOL do_postprocessing = TRUE;
  int tempCols, tempRows;
  clock_t time1, time2, time3, time4;
  char *ptr_ig = NULL;
  int i;
  /* Left and right images */
  uchar *imgL, *imgR;
  /* Results after matching the scanlines independently */
  uchar *disparity_map1, *depth_discontinuities1;
  /* Results after postprocessing the first disparity map */
  uchar *disparity_map2, *depth_discontinuities2;

  g_maxdisp = -1;
  /* Parse command line */
  for (i = 1 ; i < argc ; i++)  {
    if (strcmp(argv[i], "-h") == 0)  usage(argv[0]);
    else if (strcmp(argv[i], "-o") == 0)  {
      i++;
      if (i == argc)  error("Missing argument.");
      setOcclusionPenalty(atoi(argv[i]));
    }
    else if (strcmp(argv[i], "-r") == 0)  {
      i++;
      if (i == argc)  error("Missing argument.");
      setReward(atoi(argv[i]));
    }
    else if (strcmp(argv[i], "-d") == 0)  {
      i++;
      if (i == argc)  error("Missing argument.");
      strcpy(dir_in, argv[i]);
    }
    else if (strcmp(argv[i], "-rel") == 0)  {
      i++;
      if (i == argc)  error("Missing argument.");
      setReliableThreshold(atoi(argv[i]));
    }
    else if (strcmp(argv[i], "-alpha") == 0)  {
      i++;
      if (i == argc)  error("Missing argument.");
      setAlpha(atof(argv[i]));
    }
    else if (strcmp(argv[i], "-ma") == 0)  {
      i++;
      if (i == argc)  error("Missing argument.");
      setMaxAttractionThreshold(atoi(argv[i]));
    }
    else if (strcmp(argv[i], "-b") == 0)
      writeIntermediateResults = TRUE;
    else if (strcmp(argv[i], "-np") == 0)
      do_postprocessing = FALSE;
    else if (strcmp(argv[i], "-jp") == 0)
      do_matching = FALSE;
    else if (strcmp(argv[i], "-wpi") == 0)
      writePostprocessingIntermediateResults = TRUE;
    else if (!leftImageHasBeenRead)  {
      strcpy(basenameL, argv[i]);
      leftImageHasBeenRead = TRUE;
    }
    else if (strcmp(argv[i], "-ig") == 0)  {
      i++;
      if (i == argc)  error("Missing argument.");
      strcpy(basename_ig, argv[i]);
      ptr_ig = (char *) basename_ig;
    }
    else if (rightImageHasBeenRead)  {
        g_maxdisp = atoi((argv[i]));
        g_slop = g_maxdisp + 1;
    }
    else if (!rightImageHasBeenRead)  {
      strcpy(basenameR, argv[i]);
      rightImageHasBeenRead = TRUE;
    }
    else if (!disparityMapHasBeenRead)  {
      strcpy(basename_dm_in, argv[i]);
      disparityMapHasBeenRead = TRUE;
    }
    else warning("Unknown argument.");
  }
  if (!leftImageHasBeenRead || !rightImageHasBeenRead ||
      (!do_matching && !disparityMapHasBeenRead) || 
      (g_maxdisp == -1) || (g_maxdisp < 14) || (g_maxdisp > 50))
    usage(argv[0]);

  sprintf(fnameL, "%s/%s", dir_in, basenameL);
  sprintf(fnameR, "%s/%s", dir_in, basenameR);

  /* Read images (and maybe disparity map and intensity gradients) */
  printf("Attempting to read %s and\n"
         "                   %s\n", fnameL, fnameR);
  imgL = pgmReadFile(fnameL, &g_cols, &g_rows);

  disparity_map1 = malloc(g_rows*g_cols*sizeof(uchar));
  if (disparity_map1 == NULL)  
    error("(main) Memory not allocated");
  depth_discontinuities1 = malloc(g_rows*g_cols*sizeof(uchar));
  if (depth_discontinuities1 == NULL)  
    error("(main) Memory not allocated");
  disparity_map2 = malloc(g_rows*g_cols*sizeof(uchar));
  if (disparity_map2 == NULL)  
    error("(main) Memory not allocated");
  depth_discontinuities2 = malloc(g_rows*g_cols*sizeof(uchar));
  if (depth_discontinuities2 == NULL)  
    error("(main) Memory not allocated");

  imgR = pgmReadFile(fnameR, &tempCols, &tempRows);
  if (tempCols != g_cols || tempRows != g_rows) size_error(tempCols, tempRows);
  printf("Images successfully read. Their size is %3d by %3d\n", g_cols, g_rows);
  if (!do_matching) {
    printf("Attempting to read %s\n", basename_dm_in);
    disparity_map1 = pgmReadFile(basename_dm_in, &tempCols, &tempRows);
    if (tempCols != g_cols || tempRows != g_rows) size_error(tempCols, tempRows);
  }

  printf("Using maximum disparity of %d\n", g_maxdisp);

  if (do_matching) {
    time1 = clock();

    /* Match scanlines using dynamic programming */
    printf("Matching scanlines independently ...\n");
    matchScanlines(imgL, imgR, disparity_map1, depth_discontinuities1, ptr_ig);

    /* Check the time */
    time2 = clock();
    printf("Done.  Independent processing took %4.1f seconds "
           "of processor time.\n", (((float) time2 - time1)/ CLOCKS_PER_SEC)); 
  }

  if (do_postprocessing) {
    time3 = clock();

    /* Postprocess disparity map */
    printf("Postprocessing disparity map ...\n");
    postprocess(imgL, imgR, disparity_map1, disparity_map2, 
                depth_discontinuities2);

    /* Check the time */
    time4 = clock();
    printf("Done.  Postprocessing took %4.1f seconds of processor time.\n", 
           (((float) time4 - time3)/ CLOCKS_PER_SEC)); 
  }

  if (do_matching && do_postprocessing) {
    printf("Total processor time was %4.1f seconds.\n", 
           (((float) time4 - time1)/ CLOCKS_PER_SEC)); 
  }

  /* Write results */
  if (do_matching && writeIntermediateResults)  {
    printf("Writing to %s and %s\n", fname_dm_intermediate, 
           fname_dd_intermediate);
    pgmWriteFile(fname_dm_intermediate, 
                 (unsigned char *) disparity_map1, g_cols, g_rows);
    pgmWriteFile(fname_dd_intermediate, 
                 (unsigned char *) depth_discontinuities1, g_cols, g_rows);
  }

  if (do_postprocessing) {
    printf("Writing to %s and %s\n", fname_dm, fname_dd);
    pgmWriteFile(fname_dm, (unsigned char *) disparity_map2, g_cols, g_rows);
    pgmWriteFile(fname_dd, (unsigned char *) depth_discontinuities2, g_cols, g_rows);
  }
  printf("\n");

  free(imgL);
  free(imgR);
  free(disparity_map1);
  free(depth_discontinuities1);
  free(disparity_map2);
  free(depth_discontinuities2);
}

