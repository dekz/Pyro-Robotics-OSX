/********************************************************************* */
/* match_scanlines.c */
/* */
/* Implements the ``Faster Algorithm'', which matches two scanlines */
/* using dynamic programming, with pruning.  Depth discontinuities */
/* are required to be aligned with intensity gradients, which allows */
/* the algorithm to handle large untextured regions. */
/********************************************************************* */

#include <assert.h>
#include <memory.h>
#include <stdlib.h>
#include <string.h>
#include "base.h"
#include "error.h"
#include "pnmio.h"
#include "p2p.h"

extern int g_rows, g_cols, g_maxdisp, g_slop;

#define FIRST_MATCH 	65535   /* symbol for first match */
#define DEFAULT_COST  	  600   /* prevents costs from becoming negative */
#define NO_IG_PEN    	 1000   /* penalty for depth discontinuity  */
                                /* without intensity gradient */

/* Special options for comparing our algorithm with other possibilities. */
/* For our algorithm, leave them all commented. */
/* #define USE_ABSOLUTE_DIFFERENCE */
/* #define USE_SYMMETRIC_GRADIENTS */
/* #define USE_HYPOTHETICAL_GRADIENTS */
/* #define BACKWARD_LOOKING */


/* These values are multiplied by two because of fillDissimilarityTable() */
static int occ_pen = 25 * 2;	
static int reward = 5 * 2;


/********************************************************************* */
/* setOcclusionPenalty */
/* getOcclusionPenalty */
/* setReward */
/* getReward */
/* */
/* Provides an interface to the occlusion penalty and match reward.   */
/* Recall that the value stored in the variable is double the actual  */
/* value, since fillDissimilarityTable() doubles the dissimilarities  */
/* in an effort to keep everything integers. */
/********************************************************************* */

void setOcclusionPenalty(int op)
{
   if (op < 0)  {
      warning("Occlusion penalty must be nonnegative.  Setting to zero.");
      op = 0;
   }
	occ_pen = op * 2;
}

int getOcclusionPenalty(void)
{
  if (occ_pen%2!=0) {
    error("Low-level problem:  Someone must have manually set occ_pen incorrectly\n");
    exit(-1);
  }
  return (occ_pen/2);
}

void setReward(int r)
{
   if (r < 0)  {
      warning("Reward must be nonnegative.  Setting to zero.");
      r = 0;
   }
   reward = r*2;
}

int getReward(void)
{
  if (occ_pen%2!=0) {
    error("Low-level problem:  Someone must have manually set reward incorrectly\n");
    exit(-1);
  }
   return (reward/2);
}


/********************************************************************* */
/* computeIntensityGradientsX */
/*  */
/* This function determines which pixels lie beside intensity  */
/* gradients.  A pixel in the {left} scanline lies to the {left} of  */
/* an intensity gradient if there is some intensity variation to its  */
/* right.  Likewise, a pixel in the {right} scanline lies to the  */
/* {right} of an intensity gradient if there is some intensity  */
/* variation to its left.   */
/*  */
/* A pixel which lies beside an intensity gradient is labelled with 0; */
/* all other pixels are labelled with NO_IG_PEN.  This label is used  */
/* as a penalty to enforce the constraint that depth discontinuities  */
/* must occur at intensity gradients.  That is, a value of 0 has no  */
/* effect on the cost function, whereas a value of NO_IG_PEN prohibits  */
/* depth discontinuities. */
/*  */
/* NOTE:  Because NO_IG_PEN is so large, this computation prohibits */
/* depth discontinuities that are not accompanied by intensity  */
/* gradients, just like the ``if'' statements in the paper.  This  */
/* method is chosen for computational speed. */
/********************************************************************* */

void computeIntensityGradientsX(uchar *imgL,
                                uchar *imgR,
                                int scanline,
                                int *no_igL,
                                int *no_igR)
{
   int th = 5;                /* minimum intensity variation within window */
   int w = 3;                 /* width of window  */
   int max1, min1, max2, min2;
   int i, j;
   
   /* Initially, declare all pixels to be NOT intensity gradients */
   for (i = 0 ; i < g_cols ; i++)  {
      no_igL[i] = NO_IG_PEN;
      no_igR[i] = NO_IG_PEN;
   }

   /* Find intensity gradients in the left scanline */
   for (i = 0 ; i < g_cols - w + 1 ; i++)  {
      max1 = 0;      min1 = INF;
      for (j = i ; j < i + w ; j++)  {
         if (imgL[g_cols*scanline+j] < min1)   min1 = imgL[g_cols*scanline+j];
         if (imgL[g_cols*scanline+j] > max1)   max1 = imgL[g_cols*scanline+j];
      }
      if (max1 - min1 >= th)
         no_igL[i] = 0;
   }

   /* Find intensity gradients in the right scanline */
   for (i = w - 1 ; i < g_cols ; i++)  {
      max2 = 0;      min2 = INF;
      for (j = i - w + 1 ; j <= i ; j++)  {
         if (imgR[g_cols*scanline+j] < min2)   min2 = imgR[g_cols*scanline+j];
         if (imgR[g_cols*scanline+j] > max2)   max2 = imgR[g_cols*scanline+j];
      }
      if (max2 - min2 >= th)
         no_igR[i] = 0;
   }

#ifdef USE_SYMMETRIC_GRADIENTS

   /* Shift left scanline to the right */
   for (i = g_cols - 1 ; i >= 2 ; i--)  {
      no_igL[i] = NO_IG_PEN * (no_igL[i-1] && no_igL[i-2]);
   }

   /* Shift right scanline to the left */
   for (i = 0 ; i < g_cols - 2 ; i++)  {
      no_igR[i] = NO_IG_PEN * (no_igR[i+1] && no_igR[i+2]);
   }

#elif defined(USE_HYPOTHETICAL_GRADIENTS)

   /* Shift left scanline to the right */
   for (i = g_cols - 1 ; i >= 1 ; i--)  {
      no_igL[i] = no_igL[i-1];
   }

   /* Shift right scanline to the left */
   for (i = 0 ; i < g_cols - 1 ; i++)  {
      no_igR[i] = no_igR[i+1];
   }

   /* Shift left scanline to the right */
   for (i = g_cols - 1 ; i >= 1 ; i--)  {
      no_igL[i] = no_igL[i-1];
   }

   /* Shift right scanline to the left */
   for (i = 0 ; i < g_cols - 1 ; i++)  {
      no_igR[i] = no_igR[i+1];
   }

   /* Shift left scanline to the right */
   for (i = g_cols - 1 ; i >= 1 ; i--)  {
      no_igL[i] = no_igL[i-1];
   }

   /* Shift right scanline to the left */
   for (i = 0 ; i < g_cols - 1 ; i++)  {
      no_igR[i] = no_igR[i+1];
   }


#endif

}

/********************************************************************* */
/* fillDissimilarityTable */
/*  */
/* Precomputes the dissimilarity values between each pair of pixels. */
/* The dissimilarity is defined as the minimum of: */
/*        min{ |I_1(x1) - I_2'(z)|, |I_1'(z) - I_2(x2)| }, */
/* where the prime denotes the linearly interpolated image. */
/* Actually returns twice the dissimilarity, to keep everything integers. */
/*  */
/* dimgL[x] = 2 * imgL[x]; */
/* himgL[x] = imgL[x - 1] + imgL[x]; */
/* himgL[x + 1] = imgL[x] + imgL[x + 1]; */
/********************************************************************* */

void fillDissimilarityTable(uchar *imgL, 
					   uchar *imgR,
					   int *dis,
					   int scanline)
{

#ifndef USE_ABSOLUTE_DIFFERENCE

   unsigned short int *himgL, *himgR;
   unsigned short int *dimgL, *dimgR;
   unsigned short int p0, p1, p2, q0, q1, q2;
   unsigned short int pmin, pmax, qmin, qmax;
   unsigned short int x, y, alpha, minn;

   himgL = malloc((g_cols + 1)*sizeof(unsigned short int));
   if (himgL == NULL)  
      error("(fillDissimilarityTable) Memory not allocated");
   himgR = malloc((g_cols + 1)*sizeof(unsigned short int));
   if (himgR == NULL)  
      error("(fillDissimilarityTable) Memory not allocated");
   dimgL = malloc((g_cols )*sizeof(unsigned short int));
   if (dimgL == NULL)  
      error("(fillDissimilarityTable) Memory not allocated");
   dimgR = malloc((g_cols)*sizeof(unsigned short int));
   if (dimgR == NULL)  
      error("(fillDissimilarityTable) Memory not allocated");
   
   p1 = imgL[g_cols*scanline+0];
   q1 = imgR[g_cols*scanline+0];
   himgL[0] = 2 * p1;
   himgR[0] = 2 * q1;
   himgL[g_cols] = 2 * imgL[g_cols*scanline+g_cols - 1];
   himgR[g_cols] = 2 * imgR[g_cols*scanline+g_cols - 1];
   dimgL[0] = 2 * p1;
   dimgR[0] = 2 * q1;

   for (y = 1 ; y < g_cols ; y++)  {
      p0 = p1;
      p1 = imgL[g_cols*scanline+y];
      q0 = q1;
      q1 = imgR[g_cols*scanline+y];
      himgL[y] = p0 + p1;
      dimgL[y] = 2 * p1;
      himgR[y] = q0 + q1;
      dimgR[y] = 2 * q1;
   }

   for (y = 0 ; y < g_cols ; y++)
      for (alpha = 0 ; alpha <= g_maxdisp ; alpha++)  {
         x = y + alpha;
         if (x < g_cols)  {
            p0 = dimgL[x];
            p1 = himgL[x];
            p2 = himgL[x + 1];
            q0 = dimgR[y];
            q1 = himgR[y];
            q2 = himgR[y + 1];
            minn = INF;
  
            pmax = max3(p0, p1, p2);
            pmin = min3(p0, p1, p2);
            qmax = max3(q0, q1, q2);
            qmin = min3(q0, q1, q2);
      
            if (p0 >= qmin)  { 
               if (p0 <= qmax) 
                  minn = 0;
               else
                  minn = p0 - qmax;
            }
            else  {
               minn = qmin - p0;
            }
            if (minn > 0)  {
               if (q0 >= pmin)  {
                  if (q0 <= pmax) 
                     minn = 0;
                  else
                     minn = min(minn, q0 - pmax);
               }
               else
                  minn = min(minn, pmin - q0);
            }
  
            dis[(g_maxdisp + 1)*y+alpha] = minn;
         }
      }

#else

   unsigned short int y, alpha;

   for (y = 0 ; y < g_cols ; y++)
      for (alpha = 0 ; alpha <= g_maxdisp ; alpha++)  {
         if (y+alpha < g_cols)  {
            dis[(g_maxdisp + 1)*y+alpha] = 2 * abs(imgL[g_cols*scanline+y+alpha] - imgR[g_cols*scanline+y]);
         }
      }

#endif

   free(himgL);
   free(himgR);
   free(dimgL);
   free(dimgR);
}


/********************************************************************* */
/* print_phi */
/* */

void print_phi(int *phi,
               int scanline,
               int y0,
               int y1,
               int d0,
               int d1)
{
   int y, d;
   
   if (y0<0)  y0=0;
   if (y0>=g_cols) y0=g_cols-1;
   if (y1<y0) y1=y0;
   if (y1>=g_cols) y1=g_cols-1;
   if (d0<0)  d0=0;
   if (d0>g_maxdisp)  d0=g_maxdisp;
   if (d1<d0) d1=d0;
   if (d1>g_maxdisp)  d1=g_maxdisp;
   if (scanline<0) scanline=0;
   if (scanline>=g_rows) scanline=g_rows-1;

   printf("\n(PRINT_PHI)\n");
   fflush(stdout);
   printf("\nSCANLINE %3d\n", scanline);
   printf("Disp: ");
   for (d=d0 ; d<=d1 ; d++) {
      printf("%3d ", d);
   }
   printf("\n-----------------------------------\n");
   for (y=y0 ; y<=y1 ; y++) {
      printf("%3d: ", y);
      for (d=d0 ; d<=d1 ; d++) {
         printf("%3d ", phi[(g_cols+g_slop)*scanline +(g_maxdisp + 1)*y+d]);
      }
      printf("\n");
   }
}


/********************************************************************* */
/* print_dis */
/* */

void print_dis(int *dis,
               int scanline,
               int y0,
               int y1,
               int d0,
               int d1)
{
   int y, d;
   
   if (y0<0)  y0=0;
   if (y0>=g_cols) y0=g_cols-1;
   if (y1<y0) y1=y0;
   if (y1>=g_cols) y1=g_cols-1;
   if (d0<0)  d0=0;
   if (d0>g_maxdisp)  d0=g_maxdisp;
   if (d1<d0) d1=d0;
   if (d1>g_maxdisp)  d1=g_maxdisp;
   if (scanline<0) scanline=0;
   if (scanline>=g_rows) scanline=g_rows-1;

   printf("\n(PRINT_DIS)\n");
   printf("\nSCANLINE %3d\n", scanline);
   printf("Disp: ");
   for (d=d0 ; d<=d1 ; d++) {
      printf("%3d ", d);
   }
   printf("\n-----------------------------------\n");
   for (y=y0 ; y<=y1 ; y++) {
      printf("%3d: ", y);
      for (d=d0 ; d<=d1 ; d++) {
         printf("%3d ", dis[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+d]);
      }
      printf("\n");
   }
}


/********************************************************************* */
/* normalize_phi */
/* */

void normalize_phi(int scanline,
                   int *phi,
                   int scanline_interest)
{
   int minn;
   int y, deltaa;

   minn = INF;
   for (y=0 ; y<g_cols ; y++)
      for (deltaa=0 ; deltaa<=g_maxdisp ; deltaa++)
         if (phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa]<minn)
            minn = phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa];
   if (scanline==scanline_interest) printf("minn=%d\n", minn);
   for (y=0 ; y<g_cols ; y++)
      for (deltaa=0 ; deltaa<=g_maxdisp ; deltaa++)
         phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] -= minn;
}


/********************************************************************* */
/* conductDPBackward */
/* */
/* Does dynamic programming using the Backward-Looking Algorithm. */
/* Fills the phi, pie_y, and pie_d tables. */
/* */
/* flag: 0 means each scanline independent */
/*       1 means use phi table in scanline above */
/*       2 means, in addition to 1, also using the values in */
/*         phi table in scanline below. */

void conductDPBackward(int scanline,
                       int *phi,
                       int *pie_y,
                       int *pie_d,
                       int *dis,
                       int *no_igL,
                       int *no_igR,
                       int flag,
                       int scanline_interest)
{
   int y, deltaa;                   /* the match following (y_p, delta_p) */
   int y_p, delta_p;                /* the current match */
   int phi_new, phi_best;
   int pie_y_best, pie_d_best;
/*      printf("Starting...\n");  fflush(stdout); */

   for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {
      phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p] = DEFAULT_COST + dis[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p];
      pie_y[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p] = FIRST_MATCH;
      pie_d[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p] = FIRST_MATCH;
   }

   for (y = 1 ; y < g_cols ; y++)  {
      /* printf("y=%d\n", y);  fflush(stdout); */
      for (deltaa = 0 ; deltaa <= g_maxdisp ; deltaa++)  {

         phi_best = INF;

         for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {
            y_p = y - max(1, delta_p - deltaa + 1);
            if (y_p>=0) {
               if (deltaa==delta_p ||
                   (deltaa>delta_p && !no_igL[(g_cols+g_slop)*scanline+y+deltaa-1]) ||
                   (deltaa<delta_p && !no_igR[(g_cols+g_slop)*scanline+y_p+1])) {
                  phi_new = 
                     occ_pen * (deltaa != delta_p);
                     if (scanline==scanline_interest && y==12) {
                        printf("## phi_new=%d\n", phi_new);
                     }
                  if (flag>0 && scanline>0) {
                     int s = phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p] +
                        phi[(g_cols+g_slop)*(scanline-1)+(g_maxdisp + 1)*y+deltaa];
                     if (scanline==scanline_interest && y==12) {
                        printf("## s=%d\n", s);
                     }
/*                     int n = 2; */
                     if (0 && deltaa>delta_p) {
                        int yy = y_p+1;
                        while (yy+delta_p<y+deltaa) {
                           if (yy<0 || yy>=g_cols+g_slop) printf("****yy=%d\n", yy);
                           assert(yy>=0 && yy<g_cols+g_slop);
                           assert(delta_p>=0 && delta_p<=g_maxdisp);
                           s += phi[(g_cols+g_slop)*(scanline-1)+(g_maxdisp + 1)*yy+delta_p];
                           /*                          n++; */
                           yy++;
                        }
                     } else if (0 && deltaa<delta_p) {
                        int yy = y_p+1;
                        while (yy<y) {
                           assert(yy>=0 && yy<g_cols+g_slop);
                           assert(delta_p>=0 && delta_p<=g_maxdisp);
                           s += phi[(g_cols+g_slop)*(scanline-1)+(g_maxdisp + 1)*yy+deltaa];
                           /* n++; */
                           yy++;
                        }                           
                           
/*                     while (d<delta_p) { */
                        /*                      d++; */
                        /*s += phi[scanline-1][y][d]; */
                        /*n++; */
                     }
/*                     phi_new += (phi[scanline][y_p][delta_p] + */
/*                         phi[scanline-1][y][deltaa])/2; */
                     phi_new += s;
                  } else {
                     phi_new += phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p];
                  }
/*                  if (scanline==scanline_interest && y==549) printf("## delta=%2d, delta_p=%2d, phi_new=%d\n", deltaa, delta_p, phi_new); */
                     if (scanline==scanline_interest && y==12) {
                        printf("## phi_new=%d\n", phi_new);
                     }
                  if (phi_new < phi_best) {
         if (scanline==scanline_interest && y==12) printf("!! New Phi_best !!\n");
                     phi_best = phi_new;
                     pie_y_best = y_p;
                     pie_d_best = delta_p;
                  }
               }
            }
         }
         if (scanline==scanline_interest && y==12) printf("--## delta=%2d, phi_best=%d\n", deltaa, phi_best);
         phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = phi_best +
            dis[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] - reward;

         /*     if (scanline == scanline_interest && y<15 && deltaa==4) { */
         /* printf("[%3d][%3d][%2d]:  phi=%d\n", */
         /*        scanline, y, deltaa, phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa]); */
         /*} */
         pie_y[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = pie_y_best;
         pie_d[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = pie_d_best;
      }
   }
   
   if (scanline>0) {
      for (y=0 ; y<g_cols ; y++)
         for (deltaa=0 ; deltaa<=g_maxdisp ; deltaa++)
            phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] /= ((scanline-1)*g_cols+y);
   }
   
   if (scanline==scanline_interest) {
/*      print_phi(phi, scanline, 0, 50, 0, 14); */
      print_phi(phi, scanline, 0, 150, 0, 5);
   }
   
/*   normalize_phi(scanline, phi, scanline_interest); */
   
/*   if (scanline==scanline_interest) { */
/*      print_phi(phi, scanline, 0, 50, 0, 14); */
/*      print_phi(phi, scanline, 0, 150, 0, 5); */
/*   } */
   
/*      printf("Ending...\n");  fflush(stdout); */
}


/********************************************************************* */
/* conductDPFaster */
/* */
/* Does dynamic programming using the Faster Algorithm. */
/* Fills the phi, pie_y, and pie_d tables. */

void conductDPFaster(int scanline,
                     int *phi,
                     int *pie_y,
                     int *pie_d,
                     int *dis,
                     int *no_igL,
                     int *no_igR,
                     int flag)
{
   int y, deltaa;                   /* the match following (y_p, delta_p) */
   int y_p, delta_p;                /* the current match */
   int ymin, *xmin;     /* used to prune bad nodes */
   int phi_new;

   xmin = malloc((g_cols + g_slop)*sizeof(int));
   if (xmin == NULL)  
      error("(conductDPFaster) Memory not allocated");

   /* Initialize arrays */
   for (y_p = 1 ; y_p < g_cols ; y_p++)  {
      xmin[y_p] = INF;
      for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)
         phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p] = INF;
   }

   for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {
      phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p] = DEFAULT_COST + dis[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p];
      pie_y[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p] = FIRST_MATCH;
      pie_d[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p] = FIRST_MATCH;
      xmin[0] = phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p];
   }

   for (y_p = 0 ; y_p < g_cols ; y_p++)  {

      /* Determine ymin */
      ymin = INF;
      for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {
         ymin = min(ymin, phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p]);
      }

      for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {

         /* Expand good y nodes */
         if ( phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p] <= ymin )  {
            y = y_p + 1;
            for (deltaa = delta_p + 1 ; deltaa <= g_maxdisp ; deltaa++)  {
               phi_new = phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p] +
                  dis[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] - reward + occ_pen
                  + no_igL[(g_cols+g_slop)*scanline+y + deltaa];
               if (phi_new < phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa])  {
                  phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = phi_new;
                  pie_y[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = y_p;
                  pie_d[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = delta_p;
                  xmin[y+deltaa] = min(xmin[y+deltaa], phi_new);
               }  /* end if(phi_new) */
            }  /* end for(deltaa) */
         }  /* end if(phi[][] <= ymin) */

         /* Expand good x nodes */
         if ( phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p] <= xmin[y_p+delta_p] ) {
            for (deltaa = 0 ; deltaa < delta_p ; deltaa++)  {
               y = y_p + delta_p - deltaa + 1;
               phi_new = phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p] +
                  dis[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] - reward + occ_pen
                  + no_igR[(g_cols+g_slop)*scanline+y_p];
               if (phi_new < phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa])  {
                  phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = phi_new;
                  pie_y[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = y_p;
                  pie_d[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = delta_p;
                  xmin[y+deltaa] = min(xmin[y+deltaa], phi_new);
               }  /* end if(phi_new) */
            }  /* end for(deltaa) */
         }  /* end if(phi[][] <= xmin[]) */

         /* Expand all nodes */
         phi_new = phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p] +
            dis[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y_p+1+delta_p] - reward;
         if ( phi_new < phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y_p+1+delta_p] )  {
            phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y_p+1+delta_p] = phi_new;
            pie_y[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y_p+1+delta_p] = y_p;
            pie_d[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y_p+1+delta_p] = delta_p;
            xmin[y_p+1+delta_p] = min(xmin[y_p+1+delta_p], phi_new);
         }  /* end(if) */
      }  /* end for(delta_p) */
   }  /* end for(y_p) */

   free(xmin);
}


/********************************************************************* */
/* find_ending_match */
/* */
/* finds ending match $m_{N_m}$ */

void find_ending_match(int scanline,
                       int *phi,
                       int *pie_y_best,
                       int *pie_d_best)
{
   int phi_best;
   int deltaa, y;
   
   phi_best = INF;
   for (deltaa = 0 ; deltaa <= g_maxdisp ; deltaa++)  {
      y = g_cols - 1 - deltaa;
      if (phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] <= phi_best)  {
         phi_best = phi[(g_cols+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa];
         *pie_y_best = y;
         *pie_d_best = deltaa;
      }
   }
}


/********************************************************************* */
/* extract_matches */
/* */
/* This code extracts matches from phi and pie tables.   */
/* It is only included for debugging purposes, and its */
/* results are used by no one. */
/*
extract_matches(int scanline,
                int *pie_y,
                int *pie_d)
{
#if 0   
   int matches[2][g_cols];
   int num_matches;
   int tmp_y, tmp_d;
   int zz = 0;
   
   y_p = pie_y_best;
   delta_p = pie_d_best;
   while (y_p != FIRST_MATCH && delta_p != FIRST_MATCH)  {
      matches[0][zz] = y_p + delta_p;
      matches[1][zz] = y_p;
      tmp_y = pie_y[y_p][delta_p];
      tmp_d = pie_d[y_p][delta_p];
      y_p = tmp_y;
      delta_p = tmp_d;
      zz++;
   }
   num_matches = y;
#endif  
}
*/


/********************************************************************* */
/* compute_dm_and_dd */
/* */
/* Computes disparity map and depth discontinuities */

void compute_dm_and_dd(int scanline,
                       int pie_y_best,
                       int pie_d_best,
                       int *pie_y,
                       int *pie_d,
                       uchar *disparity_map,
                       uchar *depth_discontinuities)
{
   int x, x1, x2, y1, y2, deltaa1, deltaa2;
   
   y1 = pie_y_best;         deltaa1 = pie_d_best;         x1 = y1 + deltaa1;
   y2 = pie_y[(g_maxdisp + 1)*y1+deltaa1]; deltaa2 = pie_d[(g_maxdisp + 1)*y1+deltaa1]; x2 = y2 + deltaa2;
   
   for (x = g_cols - 1 ; x >= x1 ; x--)  {
      disparity_map[g_cols*scanline+x] = deltaa1;
      depth_discontinuities[g_cols*scanline+x] = NO_DISCONTINUITY;
   }
   
   while (y2 != FIRST_MATCH)  {
      if (deltaa1 == deltaa2)  {
         disparity_map[g_cols*scanline+x2] = deltaa2;
         depth_discontinuities[g_cols*scanline+x2] = NO_DISCONTINUITY;
      }
      else if (deltaa2 > deltaa1)  {
         disparity_map[g_cols*scanline+x2] = deltaa2;
         depth_discontinuities[g_cols*scanline+x2] = DISCONTINUITY;
      }
      else {
         disparity_map[g_cols*scanline+x1 - 1] = deltaa2;
         depth_discontinuities[g_cols*scanline+x1 - 1] = DISCONTINUITY;
         for (x = x1 - 2 ; x >= x2 ; x--)  {
            disparity_map[g_cols*scanline+x] = deltaa2;
            depth_discontinuities[g_cols*scanline+x] = NO_DISCONTINUITY;
         }
      }
      y1 = y2;                 deltaa1 = deltaa2;             x1 = y1 + deltaa1;
      y2 = pie_y[(g_maxdisp + 1)*y1+deltaa1]; deltaa2 = pie_d[(g_maxdisp + 1)*y1+deltaa1]; x2 = y2 + deltaa2;
   }
   
   for (x = y1 + deltaa1 - 1 ; x >= 0 ; x--)  {
      disparity_map[g_cols*scanline+x] = deltaa1;
      depth_discontinuities[g_cols*scanline+x] = NO_DISCONTINUITY;
   }
}


/********************************************************************* */
/* joinDissimilarites */

void joinDissimilarities(int *dis,
                         int height)
{
   int hh = height/2;
   int *newdis;
   int x, y, disp;
   int yy;
   int dsum, n;

   newdis = malloc(g_rows*(g_cols+g_slop)*(g_maxdisp + 1)*sizeof(int));
   if (newdis == NULL)  
      error("(joinDissimilarities) Memory not allocated");

   assert(height % 2 == 1);

   memcpy((int *) newdis, (int *) dis, g_rows * (g_cols+g_slop) * (g_maxdisp+1) * sizeof(int));

   for (x=0 ; x<g_cols+g_slop ; x++) {
      for (y=0 ; y<g_rows ; y++) {
         for (disp=0 ; disp<=g_maxdisp ; disp++) {
            dsum = dis[(g_cols+g_slop)*y+(g_maxdisp + 1)*x+disp];
            n = 1;
            yy = max(0, y-hh);
            while (yy<y) {
               if (x>490) 
                  dsum += dis[(g_cols+g_slop)*yy+(g_maxdisp + 1)*x+disp];
               else
                  dsum += dis[(g_cols+g_slop)*y+(g_maxdisp + 1)*x+disp];
               n++;
               yy++;
            }
            yy = min(g_rows-1, y+hh);
            while (yy>y) {
               if (x>490) 
                  dsum += dis[(g_cols+g_slop)*yy+(g_maxdisp + 1)*x+disp];
               else
                  dsum += dis[(g_cols+g_slop)*y+(g_maxdisp + 1)*x+disp];
               n++;
               yy--;
            }
            newdis[(g_cols+g_slop)*y+(g_maxdisp + 1)*x+disp] = dsum;
         }
      }
   }

   memcpy((int *) dis, (int *) newdis, g_rows * (g_cols+g_slop) * (g_maxdisp+1) * sizeof(int));
   free(newdis);
}


/********************************************************************* */
void countDis(int *dis)
{
   int x, y, d;
   int sum;

   for (d=0 ; d<=g_maxdisp ; d++) {
      sum = 0;
      for (x=490 ; x<g_cols ; x++) {
         for (y=123 ; y<131 ; y++) {
            sum += dis[(g_cols+g_slop)*y+(g_maxdisp+1)*x+d];
         }
      }
      printf("   %%%%  dis=%2d,  count=%d\n", d, sum);
   }
}


/********************************************************************* */
/* */

void saveIGtoPGM(int *no_igL, char *fname)
{
   uchar *tmp;
   int val;
   int tx, ty;

   tmp = malloc(g_rows*(g_cols+g_slop)*sizeof(uchar));
   if (tmp == NULL)  
      error("(saveIGtoPGM) Memory not allocated");

   for (ty=0 ; ty<g_rows ; ty++) {
      for (tx=0 ; tx<g_cols+g_slop ; tx++) {
         val = no_igL[(g_cols+g_slop)*ty+tx];
         if (val<0) val=0;
         if (val>255) val=255;
         tmp[(g_cols+g_slop)*ty+tx] = (uchar) val;
      }
   }
   pgmWriteFile(fname, (uchar *) tmp, g_cols+g_slop, g_rows);
   free(tmp);
}


/********************************************************************* */
/* */

static void _readIGXFileHelper(char *ptr_ig,
                               int *q_no_ig,
                               char c)
{
   int magic, ncols, nrows, maxval;
   char fname[80];
   uchar *tmp;
   uchar *pri;
   int *pro;
   int i;

   
   sprintf(fname, ptr_ig, c);
   pgmReadHeaderFile(fname, &magic, &ncols, &nrows, &maxval);
   if (ncols!=g_cols+g_slop || nrows!=g_rows)
      error("IG File '%s' is of the wrong size.", ptr_ig);
   tmp = (uchar*)pgmReadFile(fname, &ncols, &nrows);
   pri=(uchar *) tmp;
   pro=(int *) q_no_ig;
   for (i=g_rows*(g_cols+g_slop) ; i>0 ; i--)  *pro++ = (int) *pri++;
   free(tmp);
}


/********************************************************************* */
/* */

void readIGXFiles(char *ptr_ig,
                  int *q_no_igL,
                  int *q_no_igR)
{   
   if (strstr(ptr_ig, "%c")==NULL)
      error("IG File '%s' is invalid.  Must contain '%%c'.", ptr_ig);

   _readIGXFileHelper(ptr_ig, q_no_igL, 'L');
   _readIGXFileHelper(ptr_ig, q_no_igR, 'R');
}


/********************************************************************* */
/* matchScanlines */
/* */
/* Used in STAN-CS-TR96-1573 and ICCV'98 */
/* */
/* Matches each pair of scanlines independently from the other pairs, */
/* using the Faster Algorithm, which is dynamic programming with */
/* pruning. */
/* */
/* NOTES */
/* On indexing the matrices, phi(y,deltaa) is the total cost of the */
/* match sequence ending with the match (y+deltaa,y).  In other */
/* words, y is the index into the right scanline and deltaa is the */
/* disparity.  For the sake of efficiency, these matrices are */
/* transposed from those in the paper. */
/********************************************************************* */

void matchScanlines(uchar *imgL,
                    uchar *imgR,
                    uchar *disparity_map,
                    uchar *depth_discontinuities,
                    char *ptr_ig)
{
  int *phi;      /* cost of a match sequence */
  int *pie_y;    /* points to the immediately */
  int *pie_d;    /*    preceding match */
  int *dis;      /* dissimilarity b/w two pixels */
  int *no_igL;                /* indicates no intensity gradient */
  int *no_igR;
  int scanline;                         /* the current scanline */
  int y, deltaa;                        /* the match following (y_p, delta_p) */
  int y_p, delta_p;                     /* the current match */
  int ymin, *xmin;          /* used to prune bad nodes */
  int phi_new;
  int phi_best, pie_y_best, pie_d_best;
  int *q_no_igL;          /* indicates no intensity gradient */
  int *q_no_igR;

  
  phi = malloc((g_cols+g_slop)*(g_maxdisp + 1)*sizeof(int));
  if (phi == NULL)
     error("(matchScanlines) Memory not allocated");
  pie_y = malloc((g_cols+g_slop)*(g_maxdisp + 1)*sizeof(int));
  if (pie_y == NULL)
     error("(matchScanlines) Memory not allocated");
  pie_d = malloc((g_cols+g_slop)*(g_maxdisp + 1)*sizeof(int));
  if (pie_d == NULL)
     error("(matchScanlines) Memory not allocated");
  dis = malloc((g_cols+g_slop)*(g_maxdisp + 1)*sizeof(int));
  if (dis == NULL)
     error("(matchScanlines) Memory not allocated");
  no_igL = malloc((g_cols+g_slop)*sizeof(int));
  if (no_igL == NULL)
     error("(matchScanlines) Memory not allocated");
  no_igR = malloc((g_cols+g_slop)*sizeof(int));
  if (no_igR == NULL)
     error("(matchScanlines) Memory not allocated");
  xmin = malloc((g_cols+g_slop)*sizeof(int));
  if (xmin == NULL)
     error("(matchScanlines) Memory not allocated");
  q_no_igL = malloc((g_rows)*(g_cols+g_slop)*sizeof(int));
  if (q_no_igL == NULL)
     error("(matchScanlines) Memory not allocated");
  q_no_igR = malloc((g_rows)*(g_cols+g_slop)*sizeof(int));
  if (q_no_igR == NULL)
     error("(matchScanlines) Memory not allocated");
  
  printf("Parameters:  occ=%d, rew=%d, ptr_ig='%s'\n", 
         getOcclusionPenalty(), getReward(), ptr_ig ? ptr_ig : "NULL");
  
  if (ptr_ig != NULL) {
    readIGXFiles(ptr_ig, q_no_igL, q_no_igR);
  }
  
  for (scanline = 0 ; scanline < g_rows ; scanline++)  {
    if (scanline % 50 == 0 && g_rows > 200)  printf("     scanline %d\n", scanline);
    
    /* Fill tables */
    fillDissimilarityTable(imgL, imgR, dis, scanline);
    if (ptr_ig == NULL)
      computeIntensityGradientsX(imgL, imgR, scanline, no_igL, no_igR);
    else {
      memcpy(no_igL, (void *)q_no_igL[scanline], (g_cols+g_slop)*sizeof(int));
      memcpy(no_igR, (void *)q_no_igR[scanline], (g_cols+g_slop)*sizeof(int));
    }
    
#ifdef BACKWARD_LOOKING
    
    for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {
      phi[(g_maxdisp + 1)*0+delta_p] = DEFAULT_COST + dis[(g_maxdisp + 1)*0+delta_p];
      pie_y[(g_maxdisp + 1)*0+delta_p] = FIRST_MATCH;
      pie_d[(g_maxdisp + 1)*0+delta_p] = FIRST_MATCH;
    }
    
    for (y = 1 ; y < g_cols ; y++)  {
      /* printf("y=%d\n", y);  fflush(stdout); */
      for (deltaa = 0 ; deltaa <= g_maxdisp ; deltaa++)  {
        
        phi_best = INF;
        
        for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {
          y_p = y - max(1, delta_p - deltaa + 1);
          if (y_p>=0) {
            if (deltaa==delta_p ||
                (deltaa>delta_p && !no_igL[y+deltaa-1]) ||
                (deltaa<delta_p && !no_igR[y_p+1])) {
              phi_new = phi[(g_maxdisp + 1)*y_p+delta_p] + occ_pen * (deltaa != delta_p);
              if (phi_new < phi_best) {
                phi_best = phi_new;
                pie_y_best = y_p;
                pie_d_best = delta_p;
              }
            }
          }
        }
        phi[(g_maxdisp + 1)*y+deltaa] = phi_best + dis[(g_maxdisp + 1)*y+deltaa]-reward;
        pie_y[(g_maxdisp + 1)*y+deltaa] = pie_y_best;
        pie_d[(g_maxdisp + 1)*y+deltaa] = pie_d_best;
      }
    }
    
#else
    /* Initialize arrays */
    for (y_p = 1 ; y_p < g_cols ; y_p++)  {
      xmin[y_p] = INF;
      for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)
        phi[(g_maxdisp + 1)*y_p+delta_p] = INF;
    }
    
    for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {
      phi[(g_maxdisp + 1)*0+delta_p] = DEFAULT_COST + dis[(g_maxdisp + 1)*0+delta_p];
      pie_y[(g_maxdisp + 1)*0+delta_p] = FIRST_MATCH;
      pie_d[(g_maxdisp + 1)*0+delta_p] = FIRST_MATCH;
      xmin[0] = phi[(g_maxdisp + 1)*0+delta_p];
    }
    
    for (y_p = 0 ; y_p < g_cols ; y_p++)  {
      
      /* Determine ymin */
      ymin = INF;
      for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {
        ymin = min(ymin, phi[(g_maxdisp + 1)*y_p+delta_p]);
      }
      
      for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {
        
        /* Expand good y nodes */
        if ( phi[(g_maxdisp + 1)*y_p+delta_p] <= ymin )  {
          y = y_p + 1;
          for (deltaa = delta_p + 1 ; deltaa <= g_maxdisp ; deltaa++)  {
            phi_new = phi[(g_maxdisp + 1)*y_p+delta_p] + dis[(g_maxdisp + 1)*y+deltaa] - reward + occ_pen
              + no_igL[y + deltaa];
            if (phi_new < phi[(g_maxdisp + 1)*y+deltaa])  {
              phi[(g_maxdisp + 1)*y+deltaa] = phi_new;
              pie_y[(g_maxdisp + 1)*y+deltaa] = y_p;
              pie_d[(g_maxdisp + 1)*y+deltaa] = delta_p;
              xmin[y+deltaa] = min(xmin[y+deltaa], phi_new);
            }  /* end if(phi_new) */
          }  /* end for(deltaa) */
        }  /* end if(phi[][] <= ymin) */
        
        /* Expand good x nodes */
        if ( phi[(g_maxdisp + 1)*y_p+delta_p] <= xmin[y_p+delta_p] ) {
          for (deltaa = 0 ; deltaa < delta_p ; deltaa++)  {
            y = y_p + delta_p - deltaa + 1;
            phi_new = phi[(g_maxdisp + 1)*y_p+delta_p] + dis[(g_maxdisp + 1)*y+deltaa] - reward + occ_pen
              + no_igR[y_p];
            if (phi_new < phi[(g_maxdisp + 1)*y+deltaa])  {
              phi[(g_maxdisp + 1)*y+deltaa] = phi_new;
              pie_y[(g_maxdisp + 1)*y+deltaa] = y_p;
              pie_d[(g_maxdisp + 1)*y+deltaa] = delta_p;
              xmin[y+deltaa] = min(xmin[y+deltaa], phi_new);
            }  /* end if(phi_new) */
          }  /* end for(deltaa) */
        }  /* end if(phi[][] <= xmin[]) */
        
        /* Expand all nodes */
        phi_new = phi[(g_maxdisp + 1)*y_p+delta_p] + dis[(g_maxdisp + 1)*(y_p+1)+delta_p] - reward;
        if ( phi_new < phi[(g_maxdisp + 1)*(y_p+1)+delta_p] )  {
          phi[(g_maxdisp + 1)*(y_p+1)+delta_p] = phi_new;
          pie_y[(g_maxdisp + 1)*(y_p+1)+delta_p] = y_p;
          pie_d[(g_maxdisp + 1)*(y_p+1)+delta_p] = delta_p;
          xmin[y_p+1+delta_p] = min(xmin[y_p+1+delta_p], phi_new);
        }  /* end(if) */
      }  /* end for(delta_p) */
    }  /* end for(y_p) */
    
#endif  /* BACKWARD_LOOKING */
    
    
    /* find ending match $m_k$ */
    
    phi_best = INF;
    for (deltaa = 0 ; deltaa <= g_maxdisp ; deltaa++)  {
      y = g_cols - 1 - deltaa;
      if (phi[(g_maxdisp + 1)*y+deltaa] <= phi_best)  {
        phi_best = phi[(g_maxdisp + 1)*y+deltaa];
        pie_y_best = y;
        pie_d_best = deltaa;
      }
    }
    
    
/******** */
#if 0 
    /* This code extracts matches from phi and pie tables. */
    /* It is only included for debugging purposes, and its */
    /* results are used by no one. */
    
    {
      int *matches;
      int num_matches;
      int tmp_y, tmp_d;
      int zz = 0;

      matches = malloc(2*g_cols*sizeof(int)];
      if (matches == NULL)
        error("(matchScanlines) Memory not allocated");
      
      y_p = pie_y_best;
      delta_p = pie_d_best;
      while (y_p != FIRST_MATCH && delta_p != FIRST_MATCH)  {
        matches[(g_cols)*0+zz] = y_p + delta_p;
        matches[(g_cols)1+zz] = y_p;
        tmp_y = pie_y[(g_maxdisp + 1)*y_p+delta_p];
        tmp_d = pie_d[(g_maxdisp + 1)*y_p+delta_p];
        y_p = tmp_y;
        delta_p = tmp_d;
        zz++;
      }
      num_matches = y;

      free(matches);
    }
#endif
/******** */
    
    
    
    /* Compute disparity map and depth discontinuities */
    {
      int x, x1, x2, y1, y2, deltaa1, deltaa2;
      
      y1 = pie_y_best;         deltaa1 = pie_d_best;         x1 = y1 + deltaa1;
      y2 = pie_y[(g_maxdisp + 1)*y1+deltaa1]; deltaa2 = pie_d[(g_maxdisp + 1)*y1+deltaa1]; x2 = y2 + deltaa2;
      
      for (x = g_cols - 1 ; x >= x1 ; x--)  {
        disparity_map[(g_cols)*scanline+x] = deltaa1;
        depth_discontinuities[(g_cols)*scanline+x] = NO_DISCONTINUITY;
      }
      
      while (y2 != FIRST_MATCH)  {
        if (deltaa1 == deltaa2)  {
          disparity_map[(g_cols)*scanline+x2] = deltaa2;
          depth_discontinuities[(g_cols)*scanline+x2] = NO_DISCONTINUITY;
        }
        else if (deltaa2 > deltaa1)  {
          disparity_map[(g_cols)*scanline+x2] = deltaa2;
          depth_discontinuities[(g_cols)*scanline+x2] = DISCONTINUITY;
        }
        else {
          disparity_map[(g_cols)*scanline+x1 - 1] = deltaa2;
          depth_discontinuities[(g_cols)*scanline+x1 - 1] = DISCONTINUITY;
          for (x = x1 - 2 ; x >= x2 ; x--)  {
            disparity_map[(g_cols)*scanline+x] = deltaa2;
            depth_discontinuities[(g_cols)*scanline+x] = NO_DISCONTINUITY;
          }
        }
        y1 = y2;                 deltaa1 = deltaa2;            x1 = y1 + deltaa1;
        y2 = pie_y[(g_maxdisp + 1)*y1+deltaa1]; deltaa2 = pie_d[(g_maxdisp + 1)*y1+deltaa1]; x2 = y2 + deltaa2;
      }
      
      for (x = y1 + deltaa1 - 1 ; x >= 0 ; x--)  {
        disparity_map[(g_cols)*scanline+x] = deltaa1;
        depth_discontinuities[(g_cols)*scanline+x] = NO_DISCONTINUITY;
      }
    }
    
  }  /* endfor -- scanline */
  
  free(phi);
  free(pie_y);
  free(pie_d);
  free(dis);
  free(no_igL);
  free(no_igR);
  free(xmin);
  free(q_no_igL);
  free(q_no_igR);
}







