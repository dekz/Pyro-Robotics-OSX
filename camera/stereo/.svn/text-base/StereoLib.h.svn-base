#ifndef __STEREO_H__
#define __STEREO_H__

#include "Device.h"

#include <assert.h>
#include <memory.h>
#include <stdlib.h>
#include <string.h>

#define DEBUG 0

#define FIRST_MATCH 	65535   /* symbol for first match */
#define DEFAULT_COST  	  600   /* prevents costs from becoming negative */
#define NO_IG_PEN    	 1000   /* penalty for depth discontinuity  */
                                /* without intensity gradient */
#define INF              65535
#define DISCONTINUITY      255   /* symbol for a depth discontinuity */
#define NO_DISCONTINUITY     0   /* symbol for no depth discontinuity */

#define max(a,b)	((a) > (b) ? (a) : (b))
#define min(a,b)	((a) < (b) ? (a) : (b))
#define max3(a,b,c)	((a) > (b) ? max((a),(c)) : max((b),(c)))
#define min3(a,b,c)	((a) < (b) ? min((a),(c)) : min((b),(c)))
#define abs(x) ((x) > 0 ? (x) : -(x))

/* Special options for comparing our algorithm with other possibilities. */
/* For our algorithm, leave them all commented. */
/* #define USE_ABSOLUTE_DIFFERENCE */
/* #define USE_SYMMETRIC_GRADIENTS */
/* #define USE_HYPOTHETICAL_GRADIENTS */
/* #define BACKWARD_LOOKING */

class Stereo : public Device {

 public:
  unsigned char *leftimage;
  unsigned char *rightimage;
  int leftwidth;
  int leftheight;
  int leftdepth;
  int rightwidth;
  int rightheight;
  int rightdepth;

  Stereo(void *left, void *right);
  PyObject *updateMMap();

 private:
  unsigned char *disparity_map1;
  unsigned char *disparity_map2;
  unsigned char *depth_discontinuities1;
  unsigned char *depth_discontinuities2;
  unsigned short int *himgL, *himgR;
  unsigned short int *dimgL, *dimgR;

  int *newdis, *phi, *pie_y, *pie_d, *dis, *no_igL, *no_igR, 
    *xmin, *q_no_igL, *q_no_igR, *matches;

  /* These values are multiplied by two because of fillDissimilarityTable() */
  int occ_pen;	
  int reward;
  int g_maxdisp; // maximum disparity
  int g_slop;  /* expand arrays so we don't have to keep checking whether index is too large */

  /* If printing of details during propagation is desired, set this variable */
  /* to the column in which you are interested.  Otherwise, set it to a  */
  /* negative value. */
  int col_interest;
  int row_interest0, row_interest1;

  /* Thresholds for reliability */
  int th_reliable;
  double alpha;
  int th_moderately_reliable;
  int th_slightly_reliable;

  /* Threshold for max distance for aligning with gradient to handle  */
  /* nearly horizontal boundaries */
  int th_max_attraction;

  unsigned int *reliability_map;       /* reliabilities of pixels */
  unsigned char *igx, *igy; /* intensity gradients */
  int *igyd, *igxd; /* distance to nearest gradient */
  int *hist;   /* histogram */

  void setOcclusionPenalty(int op);
  int getOcclusionPenalty(void);
  void setReward(int r);
  int getReward(void);
  void computeIntensityGradientsX(unsigned char *imgL,
					  unsigned char *imgR,
					  int scanline,
					  int *no_igL,
					  int *no_igR);
  void fillDissimilarityTable(unsigned char *imgL, 
				      unsigned char *imgR,
				      int *dis,
				      int scanline);
  void normalize_phi(int scanline,
			     int *phi,
		     int scanline_interest);
  void conductDPBackward(int scanline,
			 int *phi,
			 int *pie_y,
			 int *pie_d,
			 int *dis,
			 int *no_igL,
			 int *no_igR,
			 int flag,
			 int scanline_interest);
  void conductDPFaster(int scanline,
		       int *phi,
		       int *pie_y,
		       int *pie_d,
		       int *dis,
		       int *no_igL,
		       int *no_igR,
		       int flag);
  void find_ending_match(int scanline,
			 int *phi,
			 int *pie_y_best,
			 int *pie_d_best);
  void compute_dm_and_dd(int scanline,
			 int pie_y_best,
			 int pie_d_best,
			 int *pie_y,
			 int *pie_d,
			 unsigned char *disparity_map,
			 unsigned char *depth_discontinuities);
  void matchScanlines(unsigned char *imgL,
		      unsigned char *imgR,
		      unsigned char *disparity_map,
		      unsigned char *depth_discontinuities);
  void print_phi(int *phi,
		 int scanline,
		 int y0,
		 int y1,
		 int d0,
		 int d1);
  void print_dis(int *dis,
		 int scanline,
		 int y0,
		 int y1,
		 int d0,
		 int d1);

  // -------------------------

  void setReliableThreshold(int th);
  void setAlpha(double a);
  void setMaxAttractionThreshold(int th);
  int getReliableThreshold(void);
  double getAlpha(void);
  int getMaxAttractionThreshold(void);
  void char_mat_by_scalar( unsigned char *mat_in, unsigned char *mat_out, int scalar);
  void ceil_uint_mat(unsigned int *mat_in, unsigned char *mat_out);
  void ceil_int_mat(int *mat_in, unsigned char *mat_out);
  void logical_or_mat(unsigned char *mat1, unsigned char *mat2, unsigned char *mato);
  void compute_igxy(unsigned char *imgL, unsigned char *igx, unsigned char *igy);
  void compute_igyd(unsigned char *igy, int *igyd);
  void compute_igxd(unsigned char *igx, int *igxd);
  void computeReliabilitiesY(unsigned char *disp_map, unsigned int *reliability_map);
  void computeReliabilitiesX(unsigned char *disp_map, unsigned int *reliability_map);
  void propagateY(unsigned char *disp_map, unsigned char *igy, int th_moderately_reliable, int th_slightly_reliable, unsigned int *reliability_map, int *igyd, int max_attraction);
  void propagateX(unsigned char *disp_map, unsigned char *igx, int th_moderately_reliable, int th_slightly_reliable, unsigned int *reliability_map, int *igxd, int max_attraction);
  void removeIsolatedPixelsX(unsigned char *array, int len);
  void removeIsolatedPixelsY(unsigned char *array, int len);
  void coerceSurroundedPixelsY(unsigned char *array);
  void modefilterY(unsigned char *array, int h);
  void modefilterX(unsigned char *array, int w);
  void computeDepthDiscontinuities(unsigned char *disp_map, unsigned char *dd_map);
  void postprocess(unsigned char *imgL, unsigned char *imgR, unsigned char *dm_orig, unsigned char *disp_map, unsigned char *dd_map);
};

#endif
