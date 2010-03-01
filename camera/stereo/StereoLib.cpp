#include "StereoLib.h"

#include <math.h>

/* Functions in other files */

Stereo::Stereo(void *left, void *right) {
  // other image:
  Device *leftdevice = (Device *)left;
  Device *rightdevice = (Device *)right;
  leftimage = leftdevice->getImage();
  leftwidth = leftdevice->getWidth();
  leftheight = leftdevice->getHeight();
  leftdepth = leftdevice->getDepth();
  rightimage = rightdevice->getImage();
  rightwidth = rightdevice->getWidth();
  rightheight = rightdevice->getHeight();
  rightdepth = rightdevice->getDepth();
  // this image:
  width = leftwidth;
  height = leftheight;
  depth = leftdepth;
  initialize(width, height, depth, 0, 1, 2);
  
  g_maxdisp = 14; // maximum disparity
  g_slop = g_maxdisp + 1;  /* expand arrays so we don't have to keep checking whether index is too large */
  occ_pen = 25 * 2;	
  reward = 5 * 2;
  col_interest = -1;
  row_interest0 = 250; 
  row_interest1 = 400;

  /* Thresholds for reliability */
  th_reliable = 14;
  alpha = 0.15;
  th_max_attraction = 10;

  // Memory:
  disparity_map1 = new unsigned char [height * width];
  disparity_map2 = new unsigned char [height * width];
  depth_discontinuities1 = new unsigned char [height * width];
  depth_discontinuities2 = new unsigned char [height * width];

  himgL = new unsigned short int[width + 1];
  himgR = new unsigned short int[width + 1];
  dimgL = new unsigned short int[width + 1];
  dimgR = new unsigned short int[width + 1];

  xmin = new int [width + g_slop];
  newdis = new int [height * (width + g_slop)*(g_maxdisp + 1)];

  phi = new int [(width + g_slop)*(g_maxdisp + 1)];
  pie_y = new int [(width + g_slop)*(g_maxdisp + 1)];
  pie_d = new int [(width + g_slop)*(g_maxdisp + 1)];
  dis = new int [(width + g_slop)*(g_maxdisp + 1)];
  no_igL = new int [(width + g_slop)];
  no_igR = new int [(width + g_slop)];
  q_no_igL = new int [(height)*(width + g_slop)];
  q_no_igR = new int [(height)*(width + g_slop)];
  matches = new int [2*width];

  reliability_map = new unsigned int [height*width];
  igx = new unsigned char[height*width];
  igy = new unsigned char [height*width];
  igyd = new int [height*width];
  igxd = new int[height*width];
  hist = new int [g_maxdisp + 1];

  updateMMap();
}

PyObject *Stereo::updateMMap() {
  /* Match scanlines using dynamic programming */
  if (DEBUG) printf("Matching scanlines independently ...\n");
  matchScanlines(leftimage, rightimage, 
		 disparity_map1, 
		 depth_discontinuities1);
  /* Postprocess disparity map */
  if (DEBUG) printf("Postprocessing disparity map ...\n");
  postprocess(leftimage, rightimage, 
	      disparity_map1, 
	      disparity_map2, 
	      depth_discontinuities2);
  for (int h = 0; h < height; h++) {
    for (int w = 0; w < width; w++) {
      image[(h * width + w) * depth + 0] = disparity_map2[(h * width + w)] * 255 / g_maxdisp;
      image[(h * width + w) * depth + 1] = disparity_map2[(h * width + w)] * 255 / g_maxdisp;
      image[(h * width + w) * depth + 2] = disparity_map2[(h * width + w)] * 255 / g_maxdisp;
    }
  }
  return PyInt_FromLong(0);
}

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

void Stereo::setOcclusionPenalty(int op)
{
  if (op < 0)  {
    printf("Occlusion penalty must be nonnegative.  Setting to zero.");
    op = 0;
  }
  occ_pen = op * 2;
}

int Stereo::getOcclusionPenalty(void)
{
  if (occ_pen%2!=0) {
    printf("Low-level problem:  Someone must have manually set occ_pen incorrectly\n");
    exit(-1);
  }
  return (occ_pen/2);
}

void Stereo::setReward(int r)
{
  if (r < 0)  {
    printf("Reward must be nonnegative.  Setting to zero.");
    r = 0;
  }
  reward = r*2;
}

int Stereo::getReward(void)
{
  if (occ_pen%2!=0) {
    printf("Low-level problem:  Someone must have manually set reward incorrectly\n");
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

void Stereo::computeIntensityGradientsX(unsigned char *imgL,
					unsigned char *imgR,
					int scanline,
					int *no_igL,
					int *no_igR)
{
  int th = 5;                /* minimum intensity variation within window */
  int w = 3;                 /* width of window  */
  int max1, min1, max2, min2;
  int i, j;
  
  /* Initially, declare all pixels to be NOT intensity gradients */
  for (i = 0 ; i < width ; i++)  {
    no_igL[i] = NO_IG_PEN;
    no_igR[i] = NO_IG_PEN;
  }
  
  /* Find intensity gradients in the left scanline */
  for (i = 0 ; i < width - w + 1 ; i++)  {
    max1 = 0;      min1 = INF;
    for (j = i ; j < i + w ; j++)  {
      if (imgL[width*depth*scanline+j*depth] < min1)   min1 = imgL[width*depth*scanline+j*depth];
      if (imgL[width*depth*scanline+j*depth] > max1)   max1 = imgL[width*depth*scanline+j*depth];
    }
    if (max1 - min1 >= th)
      no_igL[i] = 0;
  }
  
  /* Find intensity gradients in the right scanline */
  for (i = w - 1 ; i < width ; i++)  {
    max2 = 0;      min2 = INF;
    for (j = i - w + 1 ; j <= i ; j++)  {
      if (imgR[width*depth*scanline+j*depth] < min2)   min2 = imgR[width*depth*scanline+j*depth];
      if (imgR[width*depth*scanline+j*depth] > max2)   max2 = imgR[width*depth*scanline+j*depth];
    }
    if (max2 - min2 >= th)
      no_igR[i] = 0;
  }
  
#ifdef USE_SYMMETRIC_GRADIENTS
  
  /* Shift left scanline to the right */
  for (i = width - 1 ; i >= 2 ; i--)  {
    no_igL[i] = NO_IG_PEN * (no_igL[i-1] && no_igL[i-2]);
  }
  
  /* Shift right scanline to the left */
  for (i = 0 ; i < width - 2 ; i++)  {
    no_igR[i] = NO_IG_PEN * (no_igR[i+1] && no_igR[i+2]);
  }
  
#elif defined(USE_HYPOTHETICAL_GRADIENTS)
  
  /* Shift left scanline to the right */
  for (i = width - 1 ; i >= 1 ; i--)  {
    no_igL[i] = no_igL[i-1];
  }
  
  /* Shift right scanline to the left */
  for (i = 0 ; i < width - 1 ; i++)  {
    no_igR[i] = no_igR[i+1];
  }
  
  /* Shift left scanline to the right */
  for (i = width - 1 ; i >= 1 ; i--)  {
    no_igL[i] = no_igL[i-1];
  }
  
  /* Shift right scanline to the left */
  for (i = 0 ; i < width - 1 ; i++)  {
    no_igR[i] = no_igR[i+1];
  }
  
  /* Shift left scanline to the right */
  for (i = width - 1 ; i >= 1 ; i--)  {
    no_igL[i] = no_igL[i-1];
  }
  
  /* Shift right scanline to the left */
  for (i = 0 ; i < width - 1 ; i++)  {
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

void Stereo::fillDissimilarityTable(unsigned char *imgL, 
				    unsigned char *imgR,
				    int *dis,
				    int scanline)
{
  
  if (DEBUG) printf("starting fillDissimilarityTable\n");
  
#ifndef USE_ABSOLUTE_DIFFERENCE
  
  unsigned short int p0, p1, p2, q0, q1, q2;
  unsigned short int pmin, pmax, qmin, qmax;
  unsigned short int x, y, alpha, minn;
  
  p1 = imgL[width*depth*scanline+0];
  q1 = imgR[width*depth*scanline+0];
  himgL[0] = 2 * p1;
  himgR[0] = 2 * q1;
  himgL[width] = 2 * imgL[width*depth*scanline+width*depth - 1]; // or - 3
  himgR[width] = 2 * imgR[width*depth*scanline+width*depth - 1]; // or - 3
  dimgL[0] = 2 * p1;
  dimgR[0] = 2 * q1;

  for (y = 1 ; y < width ; y++)  {
    p0 = p1;
    p1 = imgL[width*depth*scanline+y*depth];
    q0 = q1;
    q1 = imgR[width*depth*scanline+y*depth];
    himgL[y] = p0 + p1;
    dimgL[y] = 2 * p1;
    himgR[y] = q0 + q1;
    dimgR[y] = 2 * q1;
  }
  
  for (y = 0 ; y < width ; y++)
    for (alpha = 0 ; alpha <= g_maxdisp ; alpha++)  {
      x = y + alpha;
      if (x < width)  {
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
  
  for (y = 0 ; y < width ; y++)
    for (alpha = 0 ; alpha <= g_maxdisp ; alpha++)  {
      if (y+alpha < width)  {
	dis[(g_maxdisp + 1)*y+alpha] = 2 * abs(imgL[width*depth*scanline+y*depth+alpha*depth] - imgR[width*depth*scanline+y*depth]);
      }
    }
#endif
  if (DEBUG) printf("end fillDissimilarityTable\n");
  
}

void Stereo::normalize_phi(int scanline,
			   int *phi,
			   int scanline_interest)
{
  int minn;
  int y, deltaa;
  
  minn = INF;
  for (y=0 ; y<width ; y++)
    for (deltaa=0 ; deltaa<=g_maxdisp ; deltaa++)
      if (phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa]<minn)
	minn = phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa];
  if (scanline==scanline_interest) printf("minn=%d\n", minn);
  for (y=0 ; y<width ; y++)
    for (deltaa=0 ; deltaa<=g_maxdisp ; deltaa++)
      phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] -= minn;
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

void Stereo::conductDPBackward(int scanline,
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
  int pie_y_best = 0, pie_d_best = 0;
  /*      printf("Starting...\n");  fflush(stdout); */
  
  for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {
    phi[(width+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p] = DEFAULT_COST + dis[(width+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p];
    pie_y[(width+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p] = FIRST_MATCH;
    pie_d[(width+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p] = FIRST_MATCH;
  }
  
  for (y = 1 ; y < width ; y++)  {
    /* printf("y=%d\n", y);  fflush(stdout); */
    for (deltaa = 0 ; deltaa <= g_maxdisp ; deltaa++)  {
      
      phi_best = INF;
      
      for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {
	y_p = y - max(1, delta_p - deltaa + 1);
	if (y_p>=0) {
	  if (deltaa==delta_p ||
	      (deltaa>delta_p && !no_igL[(width+g_slop)*scanline+y+deltaa-1]) ||
	      (deltaa<delta_p && !no_igR[(width+g_slop)*scanline+y_p+1])) {
	    phi_new = 
	      occ_pen * (deltaa != delta_p);
	    if (scanline==scanline_interest && y==12) {
	      printf("## phi_new=%d\n", phi_new);
	    }
	    if (flag>0 && scanline>0) {
	      int s = phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p] +
		phi[(width+g_slop)*(scanline-1)+(g_maxdisp + 1)*y+deltaa];
	      if (scanline==scanline_interest && y==12) {
		printf("## s=%d\n", s);
	      }
	      /*                     int n = 2; */
	      if (0 && deltaa>delta_p) {
		int yy = y_p+1;
		while (yy+delta_p<y+deltaa) {
		  if (yy<0 || yy>=width+g_slop) printf("****yy=%d\n", yy);
		  assert(yy>=0 && yy<width+g_slop);
		  assert(delta_p>=0 && delta_p<=g_maxdisp);
		  s += phi[(width+g_slop)*(scanline-1)+(g_maxdisp + 1)*yy+delta_p];
		  /*                          n++; */
		  yy++;
		}
	      } else if (0 && deltaa<delta_p) {
		int yy = y_p+1;
		while (yy<y) {
		  assert(yy>=0 && yy<width+g_slop);
		  assert(delta_p>=0 && delta_p<=g_maxdisp);
		  s += phi[(width+g_slop)*(scanline-1)+(g_maxdisp + 1)*yy+deltaa];
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
	      phi_new += phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p];
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
      phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = phi_best +
	dis[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] - reward;
      
      /*     if (scanline == scanline_interest && y<15 && deltaa==4) { */
      /* printf("[%3d][%3d][%2d]:  phi=%d\n", */
      /*        scanline, y, deltaa, phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa]); */
      /*} */
      pie_y[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = pie_y_best;
      pie_d[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = pie_d_best;
    }
  }
  
  if (scanline>0) {
    for (y=0 ; y<width ; y++)
      for (deltaa=0 ; deltaa<=g_maxdisp ; deltaa++)
	phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] /= ((scanline-1)*width+y);
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

void Stereo::conductDPFaster(int scanline,
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
  int ymin;     /* used to prune bad nodes */
  int phi_new;
  
  /* Initialize arrays */
  for (y_p = 1 ; y_p < width ; y_p++)  {
    xmin[y_p] = INF;
    for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)
      phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p] = INF;
  }
  
  for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {
    phi[(width+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p] = DEFAULT_COST + dis[(width+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p];
    pie_y[(width+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p] = FIRST_MATCH;
    pie_d[(width+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p] = FIRST_MATCH;
    xmin[0] = phi[(width+g_slop)*scanline+(g_maxdisp + 1)*0+delta_p];
  }
  
  for (y_p = 0 ; y_p < width ; y_p++)  {
    
    /* Determine ymin */
    ymin = INF;
    for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {
      ymin = min(ymin, phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p]);
    }
    
    for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {
      
      /* Expand good y nodes */
      if ( phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p] <= ymin )  {
	y = y_p + 1;
	for (deltaa = delta_p + 1 ; deltaa <= g_maxdisp ; deltaa++)  {
	  phi_new = phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p] +
	    dis[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] - reward + occ_pen
	    + no_igL[(width+g_slop)*scanline+y + deltaa];
	  if (phi_new < phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa])  {
	    phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = phi_new;
	    pie_y[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = y_p;
	    pie_d[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = delta_p;
	    xmin[y+deltaa] = min(xmin[y+deltaa], phi_new);
	  }  /* end if(phi_new) */
	}  /* end for(deltaa) */
      }  /* end if(phi[][] <= ymin) */
      
         /* Expand good x nodes */
      if ( phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p] <= xmin[y_p+delta_p] ) {
	for (deltaa = 0 ; deltaa < delta_p ; deltaa++)  {
	  y = y_p + delta_p - deltaa + 1;
	  phi_new = phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p] +
	    dis[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] - reward + occ_pen
	    + no_igR[(width+g_slop)*scanline+y_p];
	  if (phi_new < phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa])  {
	    phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = phi_new;
	    pie_y[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = y_p;
	    pie_d[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] = delta_p;
	    xmin[y+deltaa] = min(xmin[y+deltaa], phi_new);
	  }  /* end if(phi_new) */
	}  /* end for(deltaa) */
      }  /* end if(phi[][] <= xmin[]) */
      
         /* Expand all nodes */
      phi_new = phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y_p+delta_p] +
	dis[(width+g_slop)*scanline+(g_maxdisp + 1)*y_p+1+delta_p] - reward;
      if ( phi_new < phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y_p+1+delta_p] )  {
	phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y_p+1+delta_p] = phi_new;
	pie_y[(width+g_slop)*scanline+(g_maxdisp + 1)*y_p+1+delta_p] = y_p;
	pie_d[(width+g_slop)*scanline+(g_maxdisp + 1)*y_p+1+delta_p] = delta_p;
	xmin[y_p+1+delta_p] = min(xmin[y_p+1+delta_p], phi_new);
      }  /* end(if) */
    }  /* end for(delta_p) */
  }  /* end for(y_p) */
}


/********************************************************************* */
/* find_ending_match */
/* */
/* finds ending match $m_{N_m}$ */

void Stereo::find_ending_match(int scanline,
			       int *phi,
			       int *pie_y_best,
			       int *pie_d_best)
{
  int phi_best;
  int deltaa, y;
  
  phi_best = INF;
  for (deltaa = 0 ; deltaa <= g_maxdisp ; deltaa++)  {
    y = width - 1 - deltaa;
    if (phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa] <= phi_best)  {
      phi_best = phi[(width+g_slop)*scanline+(g_maxdisp + 1)*y+deltaa];
      *pie_y_best = y;
      *pie_d_best = deltaa;
    }
  }
}

/********************************************************************* */
/* compute_dm_and_dd */
/* */
/* Computes disparity map and depth discontinuities */

void Stereo::compute_dm_and_dd(int scanline,
			       int pie_y_best,
			       int pie_d_best,
			       int *pie_y,
			       int *pie_d,
			       unsigned char *disparity_map,
			       unsigned char *depth_discontinuities)
{
  int x, x1, x2, y1, y2, deltaa1, deltaa2;
  
  y1 = pie_y_best;         deltaa1 = pie_d_best;         x1 = y1 + deltaa1;
  y2 = pie_y[(g_maxdisp + 1)*y1+deltaa1]; deltaa2 = pie_d[(g_maxdisp + 1)*y1+deltaa1]; x2 = y2 + deltaa2;
  
  for (x = width - 1 ; x >= x1 ; x--)  {
    disparity_map[width*scanline+x] = deltaa1;
    depth_discontinuities[width*scanline+x] = NO_DISCONTINUITY;
  }
  
  while (y2 != FIRST_MATCH)  {
    if (deltaa1 == deltaa2)  {
      disparity_map[width*scanline+x2] = deltaa2;
      depth_discontinuities[width*scanline+x2] = NO_DISCONTINUITY;
    }
    else if (deltaa2 > deltaa1)  {
      disparity_map[width*scanline+x2] = deltaa2;
      depth_discontinuities[width*scanline+x2] = DISCONTINUITY;
    }
    else {
      disparity_map[width*scanline+x1 - 1] = deltaa2;
      depth_discontinuities[width*scanline+x1 - 1] = DISCONTINUITY;
      for (x = x1 - 2 ; x >= x2 ; x--)  {
	disparity_map[width*scanline+x] = deltaa2;
	depth_discontinuities[width*scanline+x] = NO_DISCONTINUITY;
      }
    }
    y1 = y2;                 deltaa1 = deltaa2;             x1 = y1 + deltaa1;
    y2 = pie_y[(g_maxdisp + 1)*y1+deltaa1]; deltaa2 = pie_d[(g_maxdisp + 1)*y1+deltaa1]; x2 = y2 + deltaa2;
  }
  
  for (x = y1 + deltaa1 - 1 ; x >= 0 ; x--)  {
    disparity_map[width*scanline+x] = deltaa1;
    depth_discontinuities[width*scanline+x] = NO_DISCONTINUITY;
  }
}

/********************************************************************* */
/* */

void Stereo::matchScanlines(unsigned char *imgL,
			    unsigned char *imgR,
			    unsigned char *disparity_map,
			    unsigned char *depth_discontinuities) 
{
  int scanline;                         /* the current scanline */
  int y, deltaa;                        /* the match following (y_p, delta_p) */
  int y_p, delta_p;                     /* the current match */
  int ymin;          /* used to prune bad nodes */
  int phi_new;
  int phi_best = 0, pie_y_best = 0, pie_d_best = 0;

  if (DEBUG) printf("Parameters:  occ=%d, rew=%d\n", getOcclusionPenalty(), getReward());
  
  for (scanline = 0 ; scanline < height ; scanline++)  {
    if (scanline % 50 == 0 && height > 200)  if (DEBUG) printf("     scanline %d\n", scanline);
    
    /* Fill tables */
    fillDissimilarityTable(imgL, imgR, dis, scanline);
    for (int i = 0; i < width + g_slop; i++) {
      no_igL[i] = q_no_igL[scanline + i];
      no_igR[i] = q_no_igR[scanline + i];
    }
    //memcpy(no_igL, (int *)q_no_igL[scanline], (width + g_slop));
    //memcpy(no_igR, (int *)q_no_igR[scanline], (width + g_slop));
    
#ifdef BACKWARD_LOOKING
    
    for (delta_p = 0 ; delta_p <= g_maxdisp ; delta_p++)  {
      phi[(g_maxdisp + 1)*0+delta_p] = DEFAULT_COST + dis[(g_maxdisp + 1)*0+delta_p];
      pie_y[(g_maxdisp + 1)*0+delta_p] = FIRST_MATCH;
      pie_d[(g_maxdisp + 1)*0+delta_p] = FIRST_MATCH;
    }
    
    for (y = 1 ; y < width ; y++)  {
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
    if (DEBUG) printf("Initialize arrays\n");
    for (y_p = 1 ; y_p < width ; y_p++)  {
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
    
    for (y_p = 0 ; y_p < width ; y_p++)  {
      
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
    
    if (DEBUG) printf("find ending match\n");
    phi_best = INF;
    for (deltaa = 0 ; deltaa <= g_maxdisp ; deltaa++)  {
      y = width - 1 - deltaa;
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
      int num_matches;
      int tmp_y, tmp_d;
      int zz = 0;

      y_p = pie_y_best;
      delta_p = pie_d_best;
      while (y_p != FIRST_MATCH && delta_p != FIRST_MATCH)  {
        matches[(width)*0+zz] = y_p + delta_p;
        matches[(width)1+zz] = y_p;
        tmp_y = pie_y[(g_maxdisp + 1)*y_p+delta_p];
        tmp_d = pie_d[(g_maxdisp + 1)*y_p+delta_p];
        y_p = tmp_y;
        delta_p = tmp_d;
        zz++;
      }
      num_matches = y;
    }
#endif
/******** */
    
    if (DEBUG) printf("Compute disparity map and depth discontinuities\n");
    {
      int x, x1, x2, y1, y2, deltaa1, deltaa2;
      
      y1 = pie_y_best;         deltaa1 = pie_d_best;         x1 = y1 + deltaa1;
      y2 = pie_y[(g_maxdisp + 1)*y1+deltaa1]; deltaa2 = pie_d[(g_maxdisp + 1)*y1+deltaa1]; x2 = y2 + deltaa2;
      
      for (x = width - 1 ; x >= x1 ; x--)  {
        disparity_map[(width)*scanline+x] = deltaa1;
        depth_discontinuities[(width)*scanline+x] = NO_DISCONTINUITY;
      }
      
      while (y2 != FIRST_MATCH)  {
        if (deltaa1 == deltaa2)  {
          disparity_map[(width)*scanline+x2] = deltaa2;
          depth_discontinuities[(width)*scanline+x2] = NO_DISCONTINUITY;
        }
        else if (deltaa2 > deltaa1)  {
          disparity_map[(width)*scanline+x2] = deltaa2;
          depth_discontinuities[(width)*scanline+x2] = DISCONTINUITY;
        }
        else {
          disparity_map[(width)*scanline+x1 - 1] = deltaa2;
          depth_discontinuities[(width)*scanline+x1 - 1] = DISCONTINUITY;
          for (x = x1 - 2 ; x >= x2 ; x--)  {
            disparity_map[(width)*scanline+x] = deltaa2;
            depth_discontinuities[(width)*scanline+x] = NO_DISCONTINUITY;
          }
        }
        y1 = y2;                 deltaa1 = deltaa2;            x1 = y1 + deltaa1;
        y2 = pie_y[(g_maxdisp + 1)*y1+deltaa1]; deltaa2 = pie_d[(g_maxdisp + 1)*y1+deltaa1]; x2 = y2 + deltaa2;
      }
      
      for (x = y1 + deltaa1 - 1 ; x >= 0 ; x--)  {
        disparity_map[(width)*scanline+x] = deltaa1;
        depth_discontinuities[(width)*scanline+x] = NO_DISCONTINUITY;
      }
    }
  }  /* endfor -- scanline */
  if (DEBUG) printf("end matchScanlines\n");
}

void Stereo::print_phi(int *phi,
		       int scanline,
		       int y0,
		       int y1,
		       int d0,
		       int d1)
{
   int y, d;
   
   if (y0<0)  y0=0;
   if (y0>=width) y0=width-1;
   if (y1<y0) y1=y0;
   if (y1>=width) y1=width-1;
   if (d0<0)  d0=0;
   if (d0>g_maxdisp)  d0=g_maxdisp;
   if (d1<d0) d1=d0;
   if (d1>g_maxdisp)  d1=g_maxdisp;
   if (scanline<0) scanline=0;
   if (scanline>=height) scanline=height-1;

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
         printf("%3d ", phi[(width+g_slop)*scanline +(g_maxdisp + 1)*y+d]);
      }
      printf("\n");
   }
}


/********************************************************************* */
/* print_dis */
/* */

void Stereo::print_dis(int *dis,
               int scanline,
               int y0,
               int y1,
               int d0,
               int d1)
{
   int y, d;
   
   if (y0<0)  y0=0;
   if (y0>=width) y0=width-1;
   if (y1<y0) y1=y0;
   if (y1>=width) y1=width-1;
   if (d0<0)  d0=0;
   if (d0>g_maxdisp)  d0=g_maxdisp;
   if (d1<d0) d1=d0;
   if (d1>g_maxdisp)  d1=g_maxdisp;
   if (scanline<0) scanline=0;
   if (scanline>=height) scanline=height-1;

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
         printf("%3d ", dis[(width+g_slop)*scanline+(g_maxdisp + 1)*y+d]);
      }
      printf("\n");
   }
}

/********************************************************************* */
/* postprocess_column.c */
/* */
/* Postprocesses the disparity map using the column-wise method. */
/********************************************************************* */

void Stereo::setReliableThreshold(int th)
{
  if (th < 0)  {
    printf("Reliable threshold must be nonnegative.  Setting to zero.");
    th = 0;
  }
  th_reliable = th;
}

void Stereo::setAlpha(double a)
{
  if (a < 0)  {
    printf("Alpha must be nonnegative.  Setting to zero.");
    a = 0;
  }
  alpha = a;
}

void Stereo::setMaxAttractionThreshold(int th)
{
  if (th < 0)  {
    printf("Max-attraction threshold must be nonnegative.  Setting to zero.");
    th = 0;
  }
  th_max_attraction = th;
}

int Stereo::getReliableThreshold(void)
{
  return th_reliable;
}

double Stereo::getAlpha(void)
{
  return alpha;
}

int Stereo::getMaxAttractionThreshold(void)
{
  return th_max_attraction;
}

/********************************************************************* */
/* multiplay_unsigned char_mat_by_scalar */

void Stereo::char_mat_by_scalar(unsigned char *mat_in, unsigned char *mat_out, int scalar)
{
  unsigned char *pi = mat_in;
  unsigned char *po = mat_out;
  int val;
  int i;
  
  for (i=height*width ; i>0 ; i--) {
    val = *pi++ * scalar;
    val = max(val, 0);
    val = min(val, 255);
    *po++ = (unsigned char) val;
  }
}


void Stereo::ceil_uint_mat(unsigned int *mat_in, unsigned char *mat_out)
{
  unsigned int *pi = mat_in;
  unsigned char *po = mat_out;
  int val;
  int i;
  
  for (i=height*width ; i>0 ; i--) {
    val = *pi++;
    val = max(val, 0);
    val = min(val, 255);
    *po++ = (unsigned char) val;
  }
}

void Stereo::ceil_int_mat(int *mat_in, unsigned char *mat_out)
{
  int *pi = mat_in;
  unsigned char *po = mat_out;
  int val;
  int i;
  
  for (i=height*width ; i>0 ; i--) {
    val = *pi++;
    val = max(val, 0);
    val = min(val, 255);
    *po++ = (unsigned char) val;
  }
}

void Stereo::logical_or_mat(unsigned char *mat1, unsigned char *mat2, unsigned char *mato)
{
  unsigned char *pr1 = mat1;
  unsigned char *pr2 = mat2;
  unsigned char *pro = mato;
  int i;
  
  for (i=0 ; i<height*width ; i++) {
    *pro = *pr1 || *pr2;
    pro++;
    pr1++;
    pr2++;
  }
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

void Stereo::compute_igxy(unsigned char *imgL, unsigned char *igx, unsigned char *igy)
{
  int th = 5;                /* minimum variation w/i window */
  int w = 3;                 /* window width */
  int maxx, minn;
  int i, j, k;
  
  /* Initialize arrays */
  for (i = 0 ; i < height ; i++)  {
    for (j = 0 ; j < width ; j++)  {
      igx[(width)*i+j] = 0;
      igy[(width)*i+j] = 0;
    }
  }
  
  /* Compute intensity gradients in x-direction */
  for (i = 0 ; i < height ; i++)
    for (j = 0 ; j < width - w + 1 ; j++)  {
      maxx = 0;      minn = INF;
      for (k = j ; k < j + w ; k++)  {
        if (imgL[(width*depth)*i+k*depth] < minn)   minn = imgL[(width*depth)*i+k*depth];
        if (imgL[(width*depth)*i+k*depth] > maxx)   maxx = imgL[(width*depth)*i+k*depth];
      }
      if (maxx - minn >= th)
        for (k = j ; k < j + w ; k++)
          igx[(width)*i+k] = 1;
    }
  
  /* Compute intensity gradients in y-direction */
  for (j = 0 ; j < width ; j++)
    for (i = 0 ; i < height - w + 1 ; i++)  {
      maxx = 0;      minn = INF;
      for (k = i ; k < i + w ; k++)  {
        if (imgL[(width*depth)*k+j*depth] < minn)   minn = imgL[(width*depth)*k+j*depth];
        if (imgL[(width*depth)*k+j*depth] > maxx)   maxx = imgL[(width*depth)*k+j*depth];
      }
      if (maxx - minn >= th)
        for (k = i ; k < i + w ; k++)
          igy[(width)*k+j] = 1;
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

void Stereo::compute_igyd(unsigned char *igy, int *igyd)
{
  int i, j, curr_dist;
  
  for (j = 0 ; j < width ; j++)  {
    
    /* Expand downward */
    curr_dist = - 1 * INF;
    for (i = 0 ; i < height ; i++)  {
      if (igy[(width)*i+j])  curr_dist = 0;
      else  curr_dist--;
      igyd[(width)*i+j] = curr_dist;
    }
    
    /* Expand upward */
    curr_dist = INF;
    for (i = height - 1 ; i >= 0 ; i--)  {
      if (igy[(width)*i+j])  curr_dist = 0;
      else  curr_dist++;
      if (curr_dist < -1 * igyd[(width)*i+j]) igyd[(width)*i+j] = curr_dist;
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

void Stereo::compute_igxd(unsigned char *igx, int *igxd)
{
  int i, j, curr_dist;
  
  for (i = 0 ; i < height ; i++)  {
    
    /* Expand rightward */
    curr_dist = - 1 * INF;
    for (j = 0 ; j < width ; j++)  {
      if (igx[(width)*i+j])  curr_dist = 0;
      else  curr_dist--;
      igxd[(width)*i+j] = curr_dist;
    }
    
    /* Expand leftward */
    curr_dist = INF;
    for (j = width - 1 ; j >= 0 ; j--)  {
      if (igx[(width)*i+j])  curr_dist = 0;
      else  curr_dist++;
      if (curr_dist < -1 * igxd[(width)*i+j]) igxd[(width)*i+j] = curr_dist;
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

void Stereo::computeReliabilitiesY(unsigned char *disp_map, unsigned int *reliability_map)
{
  int i, j, k, curr_disp, curr_length;
  
  for (j = 0 ; j < width ; j++)  {
    curr_disp = -1;
    curr_length = 0;
    for (i = 0 ; i < height ; i++)  {
      if (disp_map[(width)*i+j] == curr_disp)  curr_length++;
      else  {
        for (k = i - curr_length ; k < i ; k++)
          reliability_map[(width)*k+j] = curr_length;
        curr_disp = disp_map[(width)*i+j];
        curr_length = 1;
      }
    }
    for (k = i - curr_length ; k < i ; k++)
      reliability_map[(width)*k+j] = curr_length;
  }
}


/********************************************************************* */
/* computeReliabilitiesX */
/*  */
/* Same as computeReliabilitiesY, but in the x direction. */
/********************************************************************* */

void Stereo::computeReliabilitiesX(unsigned char *disp_map, unsigned int *reliability_map)
{
  int i, j, k, curr_disp, curr_length;
  
  for (i = 0 ; i < height ; i++)  {
    curr_disp = -1;
    curr_length = 0;
    for (j = 0 ; j < width ; j++)  {
      if (disp_map[(width)*i+j] == curr_disp)  curr_length++;
      else  {
        for (k = j - curr_length ; k < j ; k++)
          reliability_map[(width)*i+k] = curr_length;
        curr_disp = disp_map[(width)*i+j];
        curr_length = 1;
      }
    }
    for (k = j - curr_length ; k < j ; k++)
      reliability_map[(width)*i+k] = curr_length;
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

void Stereo::propagateY(unsigned char *disp_map, unsigned char *igy, int th_moderately_reliable, int th_slightly_reliable, unsigned int *reliability_map, int *igyd, int max_attraction)
{
  int i, j, k, curr_disp;
  
  for (j = 0 ; j < width ; j++)  {
    
    if (j==col_interest) {
      int oo;
      printf("Reliabilities of column %d\n", j);
      for (oo=row_interest0 ; oo<row_interest1 ; oo++) {
        printf("   Row %3d:  %3d\n", oo, reliability_map[(width)*oo+j]);
      }
      printf("\n");
    }
    
    i = 0;
    while (i < height)  {
      
      /* Find top of new stable region */
      while (i < height && reliability_map[(width)*i+j] < (unsigned int)th_moderately_reliable)  i++;
      if (i >= height)  break;
      curr_disp = disp_map[(width)*i+j];
      if (j == col_interest)  
        printf("top is i = %d, curr_disp = %d\n", i, curr_disp);
      
#ifdef HANDLE_NEARLY_HORIZONTAL_BORDERS
      /* Unless ig just below, ... */
      if (!(i > 0 && (reliability_map[(width)*(i - 1)+j] >= th_slightly_reliable)
          && igyd[(width)*(i - 1)+j] > 0 && igyd[(width)*(i - 1)+j] <= max_attraction))
#endif
      /* expand region upward */
        for (k = i - 1 ;
             k >= 0
               && !igy[(width)*k+j]
               && (reliability_map[(width)*k+j] < (unsigned int)th_slightly_reliable 
                   || disp_map[(width)*k+j] == curr_disp
#ifndef ONLY_OVERWRITE_UNRELIABLE
                   || disp_map[(width)*k+j] >= curr_disp + 2
#endif
                   ) ;
             k-- )  {
          if (j == col_interest)  
            printf("prop up at [%d][%d] with disp = %d\n",  k, j, curr_disp);
          disp_map[(width)*k+j] = curr_disp;
          reliability_map[(width)*k+j] = th_moderately_reliable;
        }
    
      /* Find bottom of stable region */
      for (k = i + 1 ;
           k < height && disp_map[(width)*k+j] == curr_disp ;
           k++) ;
      i = k - 1;
      if (k >= height)  break;
    
      if (j == col_interest)  
        printf("bottom is i = %d, k = %d, curr_disp = %d\n", i, k, curr_disp);
    
#ifdef HANDLE_NEARLY_HORIZONTAL_BORDERS
      /* Unless ig just above, ... */
      if (i < height - 1 && (reliability_map[(width)*(i + 1)+j] >= th_slightly_reliable)
          && igyd[(width)*(i + 1)+j] < 0 && -1 * igyd[(width)*(i + 1)+j] <= max_attraction) {
      }
      else
#endif
      {
        /* expand region downward */
        if (j==col_interest) printf("** k=%3d, curr_disp=%2d\n", k, curr_disp);
        
        for ( ;
              k < height
                && !igy[(width)*k+j]
                && (reliability_map[(width)*k+j] < (unsigned int)th_slightly_reliable 
                    || disp_map[(width)*k+j] == curr_disp
#ifndef ONLY_OVERWRITE_UNRELIABLE
                    || disp_map[(width)*k+j] >= curr_disp + 2
#endif
                    ) ;
              k++ )  {
          disp_map[(width)*k+j] = curr_disp;
          reliability_map[(width)*k+j] = th_moderately_reliable;
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

void Stereo::propagateX(unsigned char *disp_map, unsigned char *igx, int th_moderately_reliable, int th_slightly_reliable, unsigned int *reliability_map, int *igxd, int max_attraction)
{
  int i, j, k, curr_disp;

  for (i = 0 ; i < height ; i++)  {

    if (i==col_interest) {
      int oo;
      printf("Reliabilities of row %d\n", i);
      for (oo=row_interest0 ; oo<row_interest1 ; oo++) {
        printf("   Column %3d:  %3d\n", oo, reliability_map[(width)*i+oo]);
      }
      printf("\n");
    }
    
    j = 0;
    while (j < width)  {

      /* Find left of new stable region */
      while (j < width && reliability_map[(width)*i+j] < (unsigned int)th_moderately_reliable)  j++;
      if (j >= width)  break;
      curr_disp = disp_map[(width)*i+j];
      if (i == col_interest)  
         printf("left is j = %d, curr_disp = %d\n", j, curr_disp);

#ifdef HANDLE_NEARLY_HORIZONTAL_BORDERS
      /* Unless ig just to the right, ... */
      if (!(j > 0 && (reliability_map[(width)*i+j - 1] >= th_slightly_reliable)
          && igxd[(width)*i+j - 1] > 0 && igxd[(width)*i+j - 1] <= max_attraction))
#endif
        /* expand region leftward */
        for (k = j - 1 ;
             k >= 0
             && !igx[(width)*i+k]
	       && (reliability_map[(width)*i+k] < (unsigned int)th_slightly_reliable 
                 || disp_map[(width)*i+k] == curr_disp
#ifndef ONLY_OVERWRITE_UNRELIABLE
                 || disp_map[(width)*i+k] >= curr_disp + 2
#endif
                 ) ;
             k-- )  {
            if (i == col_interest)  
               printf("prop left at [%d][%d] with disp = %d\n",  i, k, curr_disp);
            disp_map[(width)*i+k] = curr_disp;
            reliability_map[(width)*i+k] = th_moderately_reliable;
        }

      /* Find right of stable region */
      for (k = j + 1 ;
           k < width && disp_map[(width)*i+k] == curr_disp ;
           k++) ;
      j = k - 1;
      if (k >= width)  break;

      if (i == col_interest)  
         printf("right is j = %d, k = %d, curr_disp = %d\n", j, k, curr_disp);

#ifdef HANDLE_NEARLY_HORIZONTAL_BORDERS
      /* Unless ig just to the left, ... */
      if (j < width - 1 && (reliability_map[(width)*i+j + 1] >= th_slightly_reliable)
          && igxd[(width)*i+j + 1] < 0 && -1 * igxd[(width)*i+j + 1] <= max_attraction) {
      }
      else
#endif
      {
        /* expand region rightward */
        for ( ;
              k < width
                && !igx[(width)*i+k]
                && (reliability_map[(width)*i+k] < (unsigned int)th_slightly_reliable
                    || disp_map[(width)*i+k] == curr_disp
#ifndef ONLY_OVERWRITE_UNRELIABLE
                    || disp_map[(width)*i+k] >= curr_disp + 2
#endif
                    ) ;
              k++ )  {
          disp_map[(width)*i+k] = curr_disp;
          reliability_map[(width)*i+k] = th_moderately_reliable;
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

void Stereo::removeIsolatedPixelsX(unsigned char *array, int len)
{
  int i, j, k, curr_len;

  for (i = 0 ; i < height ; i++)  {
    curr_len = 0;
    for (j = 0 ; j < width ; j++)  {
      if (array[(width)*i+j])  curr_len++;
      else if (curr_len < len)  {
        for (k = j - curr_len ; k < j ; k++)
          array[(width)*i+k] = 0;
        curr_len = 0;
      }
      else  curr_len = 0;
    }  /* endfor j */
    if (curr_len < len)
      for (k = j - curr_len ; k < j ; k++)
        array[(width)*i+k] = 0;
  }  /* endfor i */
}


/********************************************************************* */
/* removeIsolatedPixelsY */
/*  */
/* Same as removeIsolatedPixelsX, except in the y direction. */
/********************************************************************* */

void Stereo::removeIsolatedPixelsY(unsigned char *array, int len)
{
  int i, j, k, curr_len;

  for (j = 0 ; j < width ; j++)  {
    curr_len = 0;
    for (i = 0 ; i < height ; i++)  {
      if (array[(width)*i+j])  curr_len++;
      else if (curr_len < len)  {
        for (k = i - curr_len ; k < i ; k++)
          array[(width)*k+j] = 0;
        curr_len = 0;
      }
      else  curr_len = 0;
    }  /* endfor i */
    if (curr_len < len)
      for (k = i - curr_len ; k < i ; k++)
        array[(width)*k+j] = 0;
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

void Stereo::coerceSurroundedPixelsY(unsigned char *array)
{
  int i, j;

  for (i = 1 ; i < height - 1 ; i++)
    for (j = 0 ; j < width ; j++)
      if (array[(width)*(i-1)+j] == array[(width)*(i+1)+j])
        array[(width)*i+j] = array[(width)*(i-1)+j];
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

void Stereo::modefilterY(unsigned char *array, int h)
{
  int i, j, k, maxx, mode;
  int hh = h / 2;          /* filter half-height */
  int disp;
  int inertia;

  if (h % 2 == 0)
    printf("modefilterY:  filter height must be odd\n");

  for (j = 0 ; j < width ; j++)
    for (i = 0 ; i < height ; i++)  {
      for (k = 0 ; k <= g_maxdisp ; k++)
        hist[k] = 0;
      for (k = max(0,i-hh) ; k <= min(height-1,i+hh) ; k++)  {
        disp = array[(width)*k+j];
        (hist[ disp ])++;   
      }

      disp = array[(width)*i+j];
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
        array[(width)*i+j] = mode;
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
        array[(width)*i+j] = mode;
      }
    }
}


/********************************************************************* */
/* modefilterX */
/*  */
/* Same as modefilterY, but in the x direction. */
/********************************************************************* */

void Stereo::modefilterX(unsigned char *array, int w)
{
  int i, j, k, maxx, mode;
  int hw = w / 2;          /* filter half-width */
  int disp;
  int inertia;

  if (w % 2 == 0)
    printf("modefilterX:  filter width must be odd\n");

  for (i = 0 ; i < height ; i++)
    for (j = 0 ; j < width ; j++)  {
      for (k = 0 ; k <= g_maxdisp ; k++)
        hist[k] = 0;
      for (k = max(0,j-hw) ; k <= min(width-1,j+hw) ; k++)  {
        disp = array[(width)*i+k];
        (hist[ disp ])++;
      }

      disp = array[(width)*i+j];
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
        array[(width)*i+j] = mode;
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
        array[(width)*i+j] = mode;
      }
    }
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

void Stereo::computeDepthDiscontinuities(unsigned char *disp_map, unsigned char *dd_map)
{
  int i, j;

  for (i = 1 ; i < height - 1 ; i++)
    for (j = 1 ; j < width - 1 ; j++)  {
      if (   disp_map[(width)*i+j] < disp_map[(width)*(i+1)+j] - 1
          || disp_map[(width)*i+j] < disp_map[(width)*(i-1)+j] - 1
          || disp_map[(width)*i+j] < disp_map[(width)*i+j+1] - 1
          || disp_map[(width)*i+j] < disp_map[(width)*i+j-1] - 1 )
        dd_map[(width)*i+j] = DISCONTINUITY;
      else dd_map[(width)*i+j] = NO_DISCONTINUITY;
    }

  for (i = 0 ; i < height ; i++)  {
    dd_map[(width)*i+0] = NO_DISCONTINUITY;
    dd_map[(width)*i+width-1] = NO_DISCONTINUITY;
  }
  for (j = 0 ; j < width ; j++)  {
    dd_map[(width)*0+j] = NO_DISCONTINUITY;
    dd_map[(width)*(height-1)+j] = NO_DISCONTINUITY;
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

void Stereo::postprocess(unsigned char *imgL, 
			 unsigned char *imgR,   /* unused in this routine */
			 unsigned char *dm_orig, 
			 unsigned char *disp_map, 
			 unsigned char *dd_map)
{
  th_slightly_reliable = (int) (th_reliable*(1-alpha) + 0.5);
  th_moderately_reliable = (int) (th_reliable*(1+alpha) + 0.5);

  if (DEBUG) printf("Parameters:  sr=%d, mr=%d", th_slightly_reliable, th_moderately_reliable);
#ifdef HANDLE_NEARLY_HORIZONTAL_BORDERS
  if (DEBUG) printf(", ma=%d\n", th_max_attraction);
#else
  if (DEBUG) printf("\n");
#endif

  if ((th_slightly_reliable > th_moderately_reliable))
    printf("postprocess:  Reliability thresholds do not obey monotonicity.");
  if (row_interest0 < 0 || row_interest0 >= height ||
      row_interest1 < 0 || row_interest1 >= height)
    row_interest1 = row_interest0 - 1;

  /* Copy original disparity map to new disparity map */
  memcpy((unsigned char *) disp_map, (unsigned char *) dm_orig, height*width);

  /* Remove "obvious errors" in the disparity map */
  coerceSurroundedPixelsY(disp_map);

  /* Compute intensity gradients */
  compute_igxy(imgL, igx, igy);

  /* Remove "isolated" intensity gradients in the y direction */
  removeIsolatedPixelsX(igy, 3);

  /* Propagate reliable regions in the y direction */
  compute_igyd(igy, igyd);
  computeReliabilitiesY(disp_map, reliability_map);
  propagateY(disp_map, igy, th_moderately_reliable, th_slightly_reliable,
             reliability_map, igyd, th_max_attraction);

  /* Remove "isolated" intensity gradients in the x direction */
  removeIsolatedPixelsY(igx, 3);

  /* Propagate reliable regions in the x direction */
  compute_igxd(igx, igxd);
  computeReliabilitiesX(disp_map, reliability_map);
  propagateX(disp_map, igx, th_moderately_reliable, th_slightly_reliable,
             reliability_map, igxd, th_max_attraction);

  /* Mode filter the disparity map */
  modefilterY(disp_map, 11);
  modefilterX(disp_map, 11);

  /* Find the depth discontinuities from the disparity map */
  computeDepthDiscontinuities(disp_map, dd_map);
}
