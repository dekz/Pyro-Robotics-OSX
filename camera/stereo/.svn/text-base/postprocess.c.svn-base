/********************************************************************* */
/* postprocess_column.c */
/* */
/* Postprocesses the disparity map using the column-wise method. */
/********************************************************************* */

/* Standard includes */
#include <assert.h>
#include <stdio.h>
#include <string.h>

/* Our includes */
#include "base.h"
#include "error.h"
#include "pnmio.h"
#include "p2p.h"

extern int g_rows, g_cols, g_maxdisp;

/* Special options for comparing our algorithm with other possibilities. */
/* For our algorithm, leave them all commented. */
/* #define HANDLE_NEARLY_HORIZONTAL_BORDERS */
/* #define ONLY_OVERWRITE_UNRELIABLE */


/* If printing of details during propagation is desired, set this variable */
/* to the column in which you are interested.  Otherwise, set it to a  */
/* negative value. */
static int col_interest = -1;
static int row_interest0 = 250, row_interest1 = 400;

/* Thresholds for reliability */
int th_reliable = 14;
double alpha = 0.15;
int th_moderately_reliable;
int th_slightly_reliable;

/* Threshold for max distance for aligning with gradient to handle  */
/* nearly horizontal boundaries */
int th_max_attraction = 10;

extern int writePostprocessingIntermediateResults;

static int verbose = 0;

#define abs(x) ((x) > 0 ? (x) : -(x))

/********************************************************************* */
/* setReliableThreshold */
/* setAlpha */
/* setMaxAttractionThreshold */
/* getReliableThreshold */
/* getAlpha */
/* getMaxAttractionThreshold */
/*  */
/* Provide an interface to the thresholds. */
/********************************************************************* */

void setReliableThreshold(int th)
{
  if (th < 0)  {
    warning("Reliable threshold must be nonnegative.  Setting to zero.");
    th = 0;
  }
  th_reliable = th;
}

void setAlpha(double a)
{
  if (a < 0)  {
    warning("Alpha must be nonnegative.  Setting to zero.");
    a = 0;
  }
  alpha = a;
}

void setMaxAttractionThreshold(int th)
{
  if (th < 0)  {
    warning("Max-attraction threshold must be nonnegative.  Setting to zero.");
    th = 0;
  }
  th_max_attraction = th;
}

int getReliableThreshold(void)
{
  return th_reliable;
}

double getAlpha(void)
{
  return alpha;
}

int getMaxAttractionThreshold(void)
{
  return th_max_attraction;
}

/********************************************************************* */
/* multiplay_uchar_mat_by_scalar */

void multiply_uchar_mat_by_scalar(
  uchar *mat_in,
  uchar *mat_out,
  int scalar)
{
  uchar *pi = mat_in;
  uchar *po = mat_out;
  int val;
  int i;
  
  for (i=g_rows*g_cols ; i>0 ; i--) {
    val = *pi++ * scalar;
    val = max(val, 0);
    val = min(val, 255);
    *po++ = (uchar) val;
  }
}


void ceil_uint_mat(
  uint *mat_in,
  uchar *mat_out)
{
  uint *pi = mat_in;
  uchar *po = mat_out;
  int val;
  int i;
  
  for (i=g_rows*g_cols ; i>0 ; i--) {
    val = *pi++;
    val = max(val, 0);
    val = min(val, 255);
    *po++ = (uchar) val;
  }
}

void ceil_int_mat(
  int *mat_in,
  uchar *mat_out)
{
  int *pi = mat_in;
  uchar *po = mat_out;
  int val;
  int i;
  
  for (i=g_rows*g_cols ; i>0 ; i--) {
    val = *pi++;
    val = max(val, 0);
    val = min(val, 255);
    *po++ = (uchar) val;
  }
}

void logical_or_mat(
  uchar *mat1,
  uchar *mat2,
  uchar *mato)
{
  uchar *pr1 = mat1;
  uchar *pr2 = mat2;
  uchar *pro = mato;
  int i;
  
  for (i=0 ; i<g_rows*g_cols ; i++) {
    *pro = *pr1 || *pr2;
    pro++;
    pr1++;
    pr2++;
  }
}

/********************************************************************* */
/* WriteDMToPGM */
/* */
/* Writes a disparity map to a PGM file. */

void WriteDMToPGM(uchar *dm)
{
  uchar *imgtmp;
  char fname_out[80];
  static int count=0;

  imgtmp = malloc(g_rows*g_cols*sizeof(uchar));
  if (imgtmp == NULL)  
    error("(WriteDMToPGM) Memory not allocated");
  
  multiply_uchar_mat_by_scalar(dm, imgtmp, 30);
  sprintf(fname_out, "output/dmt%04d.pgm", count);
  pgmWriteFile(fname_out, (uchar *) imgtmp, g_cols, g_rows);
  count++;
  free(imgtmp);
}

void WriteRMToPGM(uint *rm)
{
  uchar *imgtmp;
  char fname_out[80];
  static int count=0;
  
  imgtmp = malloc(g_rows*g_cols*sizeof(uchar));
  if (imgtmp == NULL)  
    error("(WriteRMToPGM) Memory not allocated");

  ceil_uint_mat(rm, imgtmp);
  sprintf(fname_out, "output/rmt%04d.pgm", count);
  pgmWriteFile(fname_out, (uchar *) imgtmp, g_cols, g_rows);
  count++;
  free(imgtmp);
}


void WriteLabelsToPGM(int *lab)
{
  uchar *imgtmp;
  char fname_out[80];
  static int count=0;
  
  imgtmp = malloc(g_rows*g_cols*sizeof(uchar));
  if (imgtmp == NULL)  
    error("(WriteLabelsToPGM) Memory not allocated");

  ceil_int_mat(lab, imgtmp);
  sprintf(fname_out, "output/labelst%04d.pgm", count);
  pgmWriteFile(fname_out, (uchar *) imgtmp, g_cols, g_rows);
  count++;
  free(imgtmp);
}

/********************************************************************* */
/* compute_igxy */
/* */
/* Computes intensity gradients.  For each window of pixels, declares  */
/* the pixels within the window to be intensity gradients if the  */
/* intensity variation w/i the window is greater than a threshold. */
/* Interpretation:  igx = 1  means that pixel is an ig in the x-direction */
/*                  igy = 1     "      "      "       "       y-direction */
/********************************************************************* */

static void compute_igxy(uchar *imgL, 
                         uchar *igx, 
                         uchar *igy)
{
  int th = 5;                /* minimum variation w/i window */
  int w = 3;                 /* window width */
  int maxx, minn;
  int i, j, k;
  
  /* Initialize arrays */
  for (i = 0 ; i < g_rows ; i++)  {
    for (j = 0 ; j < g_cols ; j++)  {
      igx[(g_cols)*i+j] = 0;
      igy[(g_cols)*i+j] = 0;
    }
  }
  
  /* Compute intensity gradients in x-direction */
  for (i = 0 ; i < g_rows ; i++)
    for (j = 0 ; j < g_cols - w + 1 ; j++)  {
      maxx = 0;      minn = INF;
      for (k = j ; k < j + w ; k++)  {
        if (imgL[(g_cols)*i+k] < minn)   minn = imgL[(g_cols)*i+k];
        if (imgL[(g_cols)*i+k] > maxx)   maxx = imgL[(g_cols)*i+k];
      }
      if (maxx - minn >= th)
        for (k = j ; k < j + w ; k++)
          igx[(g_cols)*i+k] = 1;
    }
  
  /* Compute intensity gradients in y-direction */
  for (j = 0 ; j < g_cols ; j++)
    for (i = 0 ; i < g_rows - w + 1 ; i++)  {
      maxx = 0;      minn = INF;
      for (k = i ; k < i + w ; k++)  {
        if (imgL[(g_cols)*k+j] < minn)   minn = imgL[(g_cols)*k+j];
        if (imgL[(g_cols)*k+j] > maxx)   maxx = imgL[(g_cols)*k+j];
      }
      if (maxx - minn >= th)
        for (k = i ; k < i + w ; k++)
          igy[(g_cols)*k+j] = 1;
    }
}


/********************************************************************* */
/* compute_igyd */
/*  */
/* Given igy (the boolean map of intensity gradients in the  */
/* y direction), computes igyd (the integer map of distances to ig's. */
/* Interpretation:  igyd = 0 means pixel is ig in y-direction */
/*                   "   = d means nearest ig is d pixels  below */
/*                   "   = -d   "     "     "       "      above */
/*                         (d is positive) */
/********************************************************************* */

static void compute_igyd(uchar *igy,
                         int *igyd)
{
  int i, j, curr_dist;
  
  for (j = 0 ; j < g_cols ; j++)  {
    
    /* Expand downward */
    curr_dist = - 1 * INF;
    for (i = 0 ; i < g_rows ; i++)  {
      if (igy[(g_cols)*i+j])  curr_dist = 0;
      else  curr_dist--;
      igyd[(g_cols)*i+j] = curr_dist;
    }
    
    /* Expand upward */
    curr_dist = INF;
    for (i = g_rows - 1 ; i >= 0 ; i--)  {
      if (igy[(g_cols)*i+j])  curr_dist = 0;
      else  curr_dist++;
      if (curr_dist < -1 * igyd[(g_cols)*i+j]) igyd[(g_cols)*i+j] = curr_dist;
    }
  }
  
}


/********************************************************************* */
/* compute_igxd */
/*  */
/* Given igx (the boolean map of intensity gradients in the  */
/* x direction), computes igxd (the integer map of distances to ig's). */
/* Interpretation:  igxd = 0 means pixel is ig in x-direction */
/*                   "   = d means nearest ig is d pixels to the right */
/*                   "   = -d   "     "     "       "     to the left  */
/*                         (d is positive) */
/********************************************************************* */

static void compute_igxd(uchar *igx,
                         int *igxd)
{
  int i, j, curr_dist;
  
  for (i = 0 ; i < g_rows ; i++)  {
    
    /* Expand rightward */
    curr_dist = - 1 * INF;
    for (j = 0 ; j < g_cols ; j++)  {
      if (igx[(g_cols)*i+j])  curr_dist = 0;
      else  curr_dist--;
      igxd[(g_cols)*i+j] = curr_dist;
    }
    
    /* Expand leftward */
    curr_dist = INF;
    for (j = g_cols - 1 ; j >= 0 ; j--)  {
      if (igx[(g_cols)*i+j])  curr_dist = 0;
      else  curr_dist++;
      if (curr_dist < -1 * igxd[(g_cols)*i+j]) igxd[(g_cols)*i+j] = curr_dist;
    }
  }
}


/********************************************************************* */
/* computeReliabilitiesY */
/*  */
/* Labels each pixel with its "reliability".  Reliability of a pixel P */
/* is defined as the number of pixels in P's region, where the region is */
/* the contiguous set of pixels (in the y direction) with the same  */
/* disparity as P. */
/********************************************************************* */

static void computeReliabilitiesY(uchar *disp_map,
                                  uint *reliability_map)
{
  int i, j, k, curr_disp, curr_length;
  
  for (j = 0 ; j < g_cols ; j++)  {
    curr_disp = -1;
    curr_length = 0;
    for (i = 0 ; i < g_rows ; i++)  {
      if (disp_map[(g_cols)*i+j] == curr_disp)  curr_length++;
      else  {
        for (k = i - curr_length ; k < i ; k++)
          reliability_map[(g_cols)*k+j] = curr_length;
        curr_disp = disp_map[(g_cols)*i+j];
        curr_length = 1;
      }
    }
    for (k = i - curr_length ; k < i ; k++)
      reliability_map[(g_cols)*k+j] = curr_length;
  }
}


/********************************************************************* */
/* computeReliabilitiesX */
/*  */
/* Same as computeReliabilitiesY, but in the x direction. */
/********************************************************************* */

static void computeReliabilitiesX(uchar *disp_map,
                                  uint *reliability_map)
{
  int i, j, k, curr_disp, curr_length;
  
  for (i = 0 ; i < g_rows ; i++)  {
    curr_disp = -1;
    curr_length = 0;
    for (j = 0 ; j < g_cols ; j++)  {
      if (disp_map[(g_cols)*i+j] == curr_disp)  curr_length++;
      else  {
        for (k = j - curr_length ; k < j ; k++)
          reliability_map[(g_cols)*i+k] = curr_length;
        curr_disp = disp_map[(g_cols)*i+j];
        curr_length = 1;
      }
    }
    for (k = j - curr_length ; k < j ; k++)
      reliability_map[(g_cols)*i+k] = curr_length;
  }
}

/********************************************************************* */
/* propagateY */
/*  */
/* Propagates each moderately reliable region in the y direction until  */
/* it hits an intensity gradient.  (? First checks whether border of  */
/* reliable region is just beyond an intensity gradient.  If so, then  */
/* the region has probably extended into an object by accident, */
/* so therefore it backs up to align its border with the intensity  */
/* gradient.?)  Propagation occurs as long as neighboring region is  */
/* either unreliable or has a disparity at least two greater than the */
/* current region. */

static void propagateY(uchar *disp_map, 
                       uchar *igy,
                       int th_moderately_reliable, 
                       int th_slightly_reliable, 
                       uint *reliability_map,
                       int *igyd, 
                       int max_attraction)
{
  int i, j, k, curr_disp;
  
  for (j = 0 ; j < g_cols ; j++)  {
    
    if (j==col_interest) {
      int oo;
      printf("Reliabilities of column %d\n", j);
      for (oo=row_interest0 ; oo<row_interest1 ; oo++) {
        printf("   Row %3d:  %3d\n", oo, reliability_map[(g_cols)*oo+j]);
      }
      printf("\n");
    }
    
    i = 0;
    while (i < g_rows)  {
      
      /* Find top of new stable region */
      while (i < g_rows && reliability_map[(g_cols)*i+j] < th_moderately_reliable)  i++;
      if (i >= g_rows)  break;
      curr_disp = disp_map[(g_cols)*i+j];
      if (j == col_interest)  
        printf("top is i = %d, curr_disp = %d\n", i, curr_disp);
      
#ifdef HANDLE_NEARLY_HORIZONTAL_BORDERS
      /* Unless ig just below, ... */
      if (!(i > 0 && (reliability_map[(g_cols)*(i - 1)+j] >= th_slightly_reliable)
          && igyd[(g_cols)*(i - 1)+j] > 0 && igyd[(g_cols)*(i - 1)+j] <= max_attraction))
#endif
      /* expand region upward */
        for (k = i - 1 ;
             k >= 0
               && !igy[(g_cols)*k+j]
               && (reliability_map[(g_cols)*k+j] < th_slightly_reliable 
                   || disp_map[(g_cols)*k+j] == curr_disp
#ifndef ONLY_OVERWRITE_UNRELIABLE
                   || disp_map[(g_cols)*k+j] >= curr_disp + 2
#endif
                   ) ;
             k-- )  {
          if (j == col_interest)  
            printf("prop up at [%d][%d] with disp = %d\n",  k, j, curr_disp);
          disp_map[(g_cols)*k+j] = curr_disp;
          reliability_map[(g_cols)*k+j] = th_moderately_reliable;
        }
    
      /* Find bottom of stable region */
      for (k = i + 1 ;
           k < g_rows && disp_map[(g_cols)*k+j] == curr_disp ;
           k++) ;
      i = k - 1;
      if (k >= g_rows)  break;
    
      if (j == col_interest)  
        printf("bottom is i = %d, k = %d, curr_disp = %d\n", i, k, curr_disp);
    
#ifdef HANDLE_NEARLY_HORIZONTAL_BORDERS
      /* Unless ig just above, ... */
      if (i < g_rows - 1 && (reliability_map[(g_cols)*(i + 1)+j] >= th_slightly_reliable)
          && igyd[(g_cols)*(i + 1)+j] < 0 && -1 * igyd[(g_cols)*(i + 1)+j] <= max_attraction) {
      }
      else
#endif
      {
        /* expand region downward */
        if (j==col_interest) printf("** k=%3d, curr_disp=%2d\n", k, curr_disp);
        
        for ( ;
              k < g_rows
                && !igy[(g_cols)*k+j]
                && (reliability_map[(g_cols)*k+j] < th_slightly_reliable 
                    || disp_map[(g_cols)*k+j] == curr_disp
#ifndef ONLY_OVERWRITE_UNRELIABLE
                    || disp_map[(g_cols)*k+j] >= curr_disp + 2
#endif
                    ) ;
              k++ )  {
          disp_map[(g_cols)*k+j] = curr_disp;
          reliability_map[(g_cols)*k+j] = th_moderately_reliable;
          if (j == col_interest) 
            printf("  propagating down into [%d][%d] with disp = %d\n", 
                   k, j, curr_disp);
        }
        i = k;
      } /* endelse */
    }  /* endwhile i */
  }  /* endfor j */
}
 

/********************************************************************* */
/* propagateX */
/*  */
/* Same as propagateY, except in the x direction. */

static void propagateX(uchar *disp_map, 
                       uchar *igx,
                       int th_moderately_reliable, 
                       int th_slightly_reliable, 
                       uint *reliability_map,
                       int *igxd,
                       int max_attraction)
{
  int i, j, k, curr_disp;

  for (i = 0 ; i < g_rows ; i++)  {

    if (i==col_interest) {
      int oo;
      printf("Reliabilities of row %d\n", i);
      for (oo=row_interest0 ; oo<row_interest1 ; oo++) {
        printf("   Column %3d:  %3d\n", oo, reliability_map[(g_cols)*i+oo]);
      }
      printf("\n");
    }
    
    j = 0;
    while (j < g_cols)  {

      /* Find left of new stable region */
      while (j < g_cols && reliability_map[(g_cols)*i+j] < th_moderately_reliable)  j++;
      if (j >= g_cols)  break;
      curr_disp = disp_map[(g_cols)*i+j];
      if (i == col_interest)  
         printf("left is j = %d, curr_disp = %d\n", j, curr_disp);

#ifdef HANDLE_NEARLY_HORIZONTAL_BORDERS
      /* Unless ig just to the right, ... */
      if (!(j > 0 && (reliability_map[(g_cols)*i+j - 1] >= th_slightly_reliable)
          && igxd[(g_cols)*i+j - 1] > 0 && igxd[(g_cols)*i+j - 1] <= max_attraction))
#endif
        /* expand region leftward */
        for (k = j - 1 ;
             k >= 0
             && !igx[(g_cols)*i+k]
             && (reliability_map[(g_cols)*i+k] < th_slightly_reliable 
                 || disp_map[(g_cols)*i+k] == curr_disp
#ifndef ONLY_OVERWRITE_UNRELIABLE
                 || disp_map[(g_cols)*i+k] >= curr_disp + 2
#endif
                 ) ;
             k-- )  {
            if (i == col_interest)  
               printf("prop left at [%d][%d] with disp = %d\n",  i, k, curr_disp);
            disp_map[(g_cols)*i+k] = curr_disp;
            reliability_map[(g_cols)*i+k] = th_moderately_reliable;
        }

      /* Find right of stable region */
      for (k = j + 1 ;
           k < g_cols && disp_map[(g_cols)*i+k] == curr_disp ;
           k++) ;
      j = k - 1;
      if (k >= g_cols)  break;

      if (i == col_interest)  
         printf("right is j = %d, k = %d, curr_disp = %d\n", j, k, curr_disp);

#ifdef HANDLE_NEARLY_HORIZONTAL_BORDERS
      /* Unless ig just to the left, ... */
      if (j < g_cols - 1 && (reliability_map[(g_cols)*i+j + 1] >= th_slightly_reliable)
          && igxd[(g_cols)*i+j + 1] < 0 && -1 * igxd[(g_cols)*i+j + 1] <= max_attraction) {
      }
      else
#endif
      {
        /* expand region rightward */
        for ( ;
              k < g_cols
                && !igx[(g_cols)*i+k]
                && (reliability_map[(g_cols)*i+k] < th_slightly_reliable
                    || disp_map[(g_cols)*i+k] == curr_disp
#ifndef ONLY_OVERWRITE_UNRELIABLE
                    || disp_map[(g_cols)*i+k] >= curr_disp + 2
#endif
                    ) ;
              k++ )  {
          disp_map[(g_cols)*i+k] = curr_disp;
          reliability_map[(g_cols)*i+k] = th_moderately_reliable;
          if (i == col_interest) 
            printf("  propagating right into [%d][%d] with disp = %d\n", 
                   i, k, curr_disp);
        }
        j = k;
      }
    }  /* endwhile j */
  } /* endfor i */
}


/********************************************************************* */
/* removeIsolatedPixelsX */
/*  */
/* Given a binary map, removes isolated 1's in the x direction. */
/* */
/* INPUTS */
/* array:  binary array */
/* len:  smallest # of 1's that is allowed to remain. */
/*       For example, if len = 3, then */
/*          0000011000011100000 becomes */
/*          0000000000011100000. */
/* */
/* OUTPUTS */
/* array is changed */
/********************************************************************* */

static void removeIsolatedPixelsX(uchar *array, int len)
{
  int i, j, k, curr_len;

  for (i = 0 ; i < g_rows ; i++)  {
    curr_len = 0;
    for (j = 0 ; j < g_cols ; j++)  {
      if (array[(g_cols)*i+j])  curr_len++;
      else if (curr_len < len)  {
        for (k = j - curr_len ; k < j ; k++)
          array[(g_cols)*i+k] = 0;
        curr_len = 0;
      }
      else  curr_len = 0;
    }  /* endfor j */
    if (curr_len < len)
      for (k = j - curr_len ; k < j ; k++)
        array[(g_cols)*i+k] = 0;
  }  /* endfor i */
}


/********************************************************************* */
/* removeIsolatedPixelsY */
/*  */
/* Same as removeIsolatedPixelsX, except in the y direction. */
/********************************************************************* */

static void removeIsolatedPixelsY(uchar *array, int len)
{
  int i, j, k, curr_len;

  for (j = 0 ; j < g_cols ; j++)  {
    curr_len = 0;
    for (i = 0 ; i < g_rows ; i++)  {
      if (array[(g_cols)*i+j])  curr_len++;
      else if (curr_len < len)  {
        for (k = i - curr_len ; k < i ; k++)
          array[(g_cols)*k+j] = 0;
        curr_len = 0;
      }
      else  curr_len = 0;
    }  /* endfor i */
    if (curr_len < len)
      for (k = i - curr_len ; k < i ; k++)
        array[(g_cols)*k+j] = 0;
  }  /* endfor j */
}


/********************************************************************* */
/* coerceSurroundedPixelsY */
/*  */
/* Given an array, surrounded pixels are coerced.  In other words,  */
/* given a pixel P in the array, if P's two immediate neighbors in the  */
/* y direction (the one above and the one below) have the same value, */
/* then P's value is changed to agree with theirs. */
/********************************************************************* */

static void coerceSurroundedPixelsY(uchar *array)
{
  int i, j;

  for (i = 1 ; i < g_rows - 1 ; i++)
    for (j = 0 ; j < g_cols ; j++)
      if (array[(g_cols)*(i-1)+j] == array[(g_cols)*(i+1)+j])
        array[(g_cols)*i+j] = array[(g_cols)*(i-1)+j];
}


/********************************************************************* */
/* modefilterY */
/*  */
/* Performs mode filtering in the y direction on an array whose  */
/* elements range from 0 to g_maxdisp. */
/*  */
/* INPUTS */
/* array:  an array whose elements range from 0 to g_maxdisp */
/* h:  filter height (must be odd) */
/*  */
/* NOTES */
/* This is an inefficient implementation, but it works. */
/********************************************************************* */

static void modefilterY(uchar *array, int h)
{
  int i, j, k, maxx, mode;
  int hh = h / 2;          /* filter half-height */
  int *hist;   /* histogram */
  int disp;
  int inertia;

  if (h % 2 == 0)
    error("modefilterY:  filter height must be odd\n");

  hist = malloc((g_maxdisp + 1)*sizeof(int));
  if (hist == NULL)  
    error("(modefilterY) Memory not allocated");

  for (j = 0 ; j < g_cols ; j++)
    for (i = 0 ; i < g_rows ; i++)  {
      for (k = 0 ; k <= g_maxdisp ; k++)
        hist[k] = 0;
      for (k = max(0,i-hh) ; k <= min(g_rows-1,i+hh) ; k++)  {
        disp = array[(g_cols)*k+j];
        (hist[ disp ])++;   
      }

      disp = array[(g_cols)*i+j];
      mode = disp;
      maxx = hist[disp];
/*      disp = array[i][j]; */
/*      maxx = hist[disp]; */
/*      if (disp>0) maxx += hist[disp-1]; */
/*      if (disp<g_maxdisp) maxx += hist[disp+1]; */
/*      mode = disp; */
      for (k = 0 ; k <= g_maxdisp ; k++)
        if (hist[k] > maxx)  {
          maxx = hist[k];
          mode = k;
        }
      inertia = hist[disp];
      if (disp>0) inertia += hist[disp-1];
      if (disp<g_maxdisp) inertia += hist[disp+1];
      if (maxx>inertia) {
        array[(g_cols)*i+j] = mode;
      } else {
        mode = disp;
        maxx = hist[disp];
        if (disp>0 && hist[disp-1]>maxx) {
          maxx = hist[disp-1];
          mode = disp-1;
        }
        if (disp<g_maxdisp && hist[disp+1]>maxx) {
          mode = disp+1;
        }
        array[(g_cols)*i+j] = mode;
      }
    }
    free(hist);
}


/********************************************************************* */
/* modefilterX */
/*  */
/* Same as modefilterY, but in the x direction. */
/********************************************************************* */

static void modefilterX(uchar *array, int w)
{
  int i, j, k, maxx, mode;
  int hw = w / 2;          /* filter half-width */
  int *hist;   /* histogram */
  int disp;
  int inertia;

  if (w % 2 == 0)
    error("modefilterX:  filter width must be odd\n");

  hist = malloc((g_maxdisp + 1)*sizeof(int));
  if (hist == NULL)  
    error("(modefilterX) Memory not allocated");

  for (i = 0 ; i < g_rows ; i++)
    for (j = 0 ; j < g_cols ; j++)  {
      for (k = 0 ; k <= g_maxdisp ; k++)
        hist[k] = 0;
      for (k = max(0,j-hw) ; k <= min(g_cols-1,j+hw) ; k++)  {
        disp = array[(g_cols)*i+k];
        (hist[ disp ])++;
      }

      disp = array[(g_cols)*i+j];
      mode = disp;
      maxx = hist[disp];
/*      disp = array[i][j]; */
/*      maxx = hist[disp]; */
/*      if (disp>0) maxx += hist[disp-1]; */
/*      if (disp<g_maxdisp) maxx += hist[disp+1]; */
/*      mode = disp; */
      for (k = 0 ; k <= g_maxdisp ; k++)
        if (hist[k] > maxx)  {
          maxx = hist[k];
          mode = k;
        }
      inertia = hist[disp];
      if (disp>0) inertia += hist[disp-1];
      if (disp<g_maxdisp) inertia += hist[disp+1];
      if (abs(mode-disp)<=1 || maxx>inertia) {
        array[(g_cols)*i+j] = mode;
      } else {
        mode = disp;
        maxx = hist[disp];
        if (disp>0 && hist[disp-1]>maxx) {
          maxx = hist[disp-1];
          mode = disp-1;
        }
        if (disp<g_maxdisp && hist[disp+1]>maxx) {
          mode = disp+1;
        }
        array[(g_cols)*i+j] = mode;
      }
    }
    free(hist);
}


/********************************************************************* */
/* computeDepthDiscontinuities */
/*  */
/* Given a disparity map, computes the depth discontinuities as those  */
/* pixels that border a change in disparity of at least two levels,  */
/* and that lie on the background.  (This latter condition is necessary */
/* to prevent two neighboring pixels from both being declared  */
/* discontinuities.) */
/********************************************************************* */

static void computeDepthDiscontinuities(uchar *disp_map,
                                        uchar *dd_map)
{
  int i, j;

  for (i = 1 ; i < g_rows - 1 ; i++)
    for (j = 1 ; j < g_cols - 1 ; j++)  {
      if (   disp_map[(g_cols)*i+j] < disp_map[(g_cols)*(i+1)+j] - 1
          || disp_map[(g_cols)*i+j] < disp_map[(g_cols)*(i-1)+j] - 1
          || disp_map[(g_cols)*i+j] < disp_map[(g_cols)*i+j+1] - 1
          || disp_map[(g_cols)*i+j] < disp_map[(g_cols)*i+j-1] - 1 )
        dd_map[(g_cols)*i+j] = DISCONTINUITY;
      else dd_map[(g_cols)*i+j] = NO_DISCONTINUITY;
    }

  for (i = 0 ; i < g_rows ; i++)  {
    dd_map[(g_cols)*i+0] = NO_DISCONTINUITY;
    dd_map[(g_cols)*i+g_cols-1] = NO_DISCONTINUITY;
  }
  for (j = 0 ; j < g_cols ; j++)  {
    dd_map[(g_cols)*0+j] = NO_DISCONTINUITY;
    dd_map[(g_cols)*(g_rows-1)+j] = NO_DISCONTINUITY;
  }
}


/********************************************************************* */
/* postprocess */
/* */
/* Version used in STAN-CS-TR-96-1573 and ICCV '98 */
/* */
/* Postprocess the disparity map.  The basic idea is to propagate */
/* reliable regions into unreliable regions, stopping at intensity  */
/* gradients.  (The actual rules are more complicated, of course.)   */
/* Further processing, like mode filtering, helps to clean up things. */
/*  */
/* INPUTS */
/* imgL:  original left intensity image */
/* dm_orig:  disparity map computed by matching the scanlines independently */
/*  */
/* OUTPUTS */
/* disp_map:  disparity map after postprocessing */
/* dd_map:  depth discontinuities after postprocessing */
/********************************************************************* */

void postprocess(uchar *imgL, 
                 uchar *imgR,   /* unused in this routine */
                 uchar *dm_orig, 
                 uchar *disp_map, 
                 uchar *dd_map)
{
  uint *reliability_map;       /* reliabilities of pixels */
  uchar *igx, *igy; /* intensity gradients */
  int *igyd, *igxd; /* distance to nearest gradient */

  reliability_map = malloc(g_rows*g_cols*sizeof(uint));
  if (reliability_map == NULL)  
    error("(postprocess) Memory not allocated");
  igx = malloc(g_rows*g_cols*sizeof(uchar));
  if (igx == NULL)  
    error("(postprocess) Memory not allocated");
  igy = malloc(g_rows*g_cols*sizeof(uchar));
  if (igy == NULL)  
    error("(postprocess) Memory not allocated");
  igyd = malloc(g_rows*g_cols*sizeof(int));
  if (igyd == NULL)  
    error("(postprocess) Memory not allocated");
  igxd = malloc(g_rows*g_cols*sizeof(int));
  if (igxd == NULL)  
    error("(postprocess) Memory not allocated");

  th_slightly_reliable = (int) (th_reliable*(1-alpha) + 0.5);
  th_moderately_reliable = (int) (th_reliable*(1+alpha) + 0.5);

  printf("Parameters:  sr=%d, mr=%d",
         th_slightly_reliable, th_moderately_reliable);
#ifdef HANDLE_NEARLY_HORIZONTAL_BORDERS
  printf(", ma=%d\n", th_max_attraction);
#else
  printf("\n");
#endif

  if ((th_slightly_reliable > th_moderately_reliable))
    error("postprocess:  Reliability thresholds do not obey monotonicity.");
  if (row_interest0 < 0 || row_interest0 >= g_rows ||
      row_interest1 < 0 || row_interest1 >= g_rows)
    row_interest1 = row_interest0 - 1;

  /* Copy original disparity map to new disparity map */
  memcpy((uchar *) disp_map, (uchar *) dm_orig, g_rows*g_cols);
  if (writePostprocessingIntermediateResults)
	pgmWriteFile("dm0.pgm", (uchar *) disp_map, g_cols, g_rows);

  /* Remove "obvious errors" in the disparity map */
  coerceSurroundedPixelsY(disp_map);
  if (writePostprocessingIntermediateResults)
	pgmWriteFile("dm1.pgm", (uchar *) disp_map, g_cols, g_rows);

  /* Compute intensity gradients */
  compute_igxy(imgL, igx, igy);
  if (writePostprocessingIntermediateResults)
	pgmWriteFile("igx0.pgm", (uchar *) igx, g_cols, g_rows);
  if (writePostprocessingIntermediateResults)
	pgmWriteFile("igy0.pgm", (uchar *) igy, g_cols, g_rows);

  /* Remove "isolated" intensity gradients in the y direction */
  removeIsolatedPixelsX(igy, 3);
  if (writePostprocessingIntermediateResults)
	pgmWriteFile("igy1.pgm", (uchar *) igy, g_cols, g_rows);

  /* Propagate reliable regions in the y direction */
  compute_igyd(igy, igyd);
  computeReliabilitiesY(disp_map, reliability_map);
  propagateY(disp_map, igy, th_moderately_reliable, th_slightly_reliable,
             reliability_map, igyd, th_max_attraction);
  if (writePostprocessingIntermediateResults)
	pgmWriteFile("dm2.pgm", (uchar *) disp_map, g_cols, g_rows);

  /* Remove "isolated" intensity gradients in the x direction */
  removeIsolatedPixelsY(igx, 3);
  if (writePostprocessingIntermediateResults)
	pgmWriteFile("igx1.pgm", (uchar *) igx, g_cols, g_rows);

  /* Propagate reliable regions in the x direction */
  compute_igxd(igx, igxd);
  computeReliabilitiesX(disp_map, reliability_map);
  propagateX(disp_map, igx, th_moderately_reliable, th_slightly_reliable,
             reliability_map, igxd, th_max_attraction);
  if (writePostprocessingIntermediateResults)
	pgmWriteFile("dm3.pgm", (uchar *) disp_map, g_cols, g_rows);

  /* Mode filter the disparity map */
  modefilterY(disp_map, 11);
  if (writePostprocessingIntermediateResults)
	pgmWriteFile("dm4.pgm", (uchar *) disp_map, g_cols, g_rows);
  modefilterX(disp_map, 11);
  if (writePostprocessingIntermediateResults)
	pgmWriteFile("dm5.pgm", (uchar *) disp_map, g_cols, g_rows);

  /* Find the depth discontinuities from the disparity map */
  computeDepthDiscontinuities(disp_map, dd_map);

  free(reliability_map);
  free(igx);
  free(igy);
  free(igyd);
  free(igxd);
}



