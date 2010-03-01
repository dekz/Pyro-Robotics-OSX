/*
  XRCL: The Extensible Robot Control Language
  (c) 2000, Douglas S. Blank
  University of Arkansas, Roboticists Research Group
  http://ai.uark.edu/xrcl/
  
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
  02111-1307, USA.

  As a special exception, you have permission to link this program
  with the Qt library and distribute executables, as long as you
  follow the requirements of the GNU GPL in regard to all of the
  software in the executable aside from Qt.
*/

#include "Camera.h"
//#include "xrcl.h"
#include <stdio.h>

Camera::Camera(const char* dname, int w, int h ) 
{
  rows = h;
  cols = w;
  int n = strlen(dname);
  devicename = new char[n+1];
  strcpy(devicename, dname);
  for (int i = 0; i < 2000; i++)
    ChunkList[i] = i;
  intensity = new unsigned char *[cols];
  for (int i = 0; i < cols; i++) {
    intensity[i] = new unsigned char[rows];
  }
  for (int i = 0; i < xcMAXIMAGEHIST; i++) {
    history[i] = new unsigned char [h * w * 3];
    for (int n = 0; n < h * w; n++) {
      history[i][n*3 + 0] = 0;
      history[i][n*3 + 1] = 0;
      history[i][n*3 + 2] = 0;
    }
  }
}

Camera::~Camera() {
  Cleanup();
}

void Camera::saveFile(char *filename)
{
  FILE * imageFile;
  imageFile=fopen(filename,"w");
  fwrite(buf, 1, buf_length,imageFile);
  fclose(imageFile);
}

unsigned char * Camera::Image ( void )
{
  GetData();
  return (buf);
}

unsigned char * Camera::RawImage ( void )
{
  GetData();
  return (rawbuf);
}

void Camera::swap_rgb24(char *mem, int n) {
  char  c;
  char *p = mem;
  int   i = n;
  
  while (--i) {
    c = p[0]; p[0] = p[2]; p[2] = c;
    p += 3;
  }
}

void Camera::Update() {
  GetData();
}

void Camera::ApplyMask() {
  for (int x = 0; x < cols; x++) {
    for (int y = 0; y < rows; y++) {
      if (!mask[x][y]) {
	// Black out:
	setPixel(x, y, 0, 0, 0);
      }
    }
  }
}

/*
Blob *Camera::ApplyFilter(Filter *filter, bool mark_it) {
  if (!filter) return NULL;
  for (int x = 0; x < cols; x++) {
    for (int y = 0; y < rows; y++) {
      if (filter->combine == 0) 
	mask[x][y] = false;
      tmpmask[x][y] = false; // always
    } 
  } 
  while (filter) {
    fprintf(stderr, "Filter->type = %d\n", filter->Type);
    if (filter->Type == xcCOLORFILTER) {
      for (int x = 0; x < cols; x++) {
	for (int y = 0; y < rows; y++) {
	  if (Red(x,y) != 0) {
	    double my_g_over_r = ((double) Green(x,y)) / 
	      ((double) Red(x,y));
	    double my_b_over_r = ((double) Blue(x,y)) / 
	      ((double) Red(x,y));
	    double diff_gr = fabs(filter->g_over_r - my_g_over_r);
	    double diff_br = fabs(filter->b_over_r - my_b_over_r);
	    if (diff_gr < filter->delta && diff_br < filter->delta) {
	      // if it is within range, mark it:
	      tmpmask[x][y] = true;
	    }
	  }
	}
      }
    } else if (filter->Type == xcMOTIONFILTER) {
      for (int x=0;x<cols;x++){
	for (int y=0;y<rows;y++){
	  if (abs(((Red(x, y)+Green(x, y)+Blue(x, y)) / 3) - 
		  intensity[x][y]) > 25) {	
	    tmpmask[x][y] = true;
	    intensity[x][y] = (Red(x, y)+Green(x, y)+Blue(x, y)) / 3;
	  }
	}
      }
    } else if (filter->Type == xcVERTICALLINEFILTER) {
    } else if (filter->Type == xcEDGEFILTER) {
    } else if (filter->Type == xcCONVOLUTION) {
      for (int x = 0; x < cols; x++) {
	for (int y = 0; y < rows; y++) {
	  if (x == 0 || x == cols ||
	      y == 0 || y == rows) {
	    tmpmask[x][y] = !filter->val;
	    exit(1);
	  }
	  int matches = 0;
	  for (int delta_x = -1; delta_x <= 1; delta_x++) {
	    for (int delta_y = -1; delta_y <= 1; delta_y++) {
	      if ((filter->matrix[delta_x + 1][delta_y + 1] == 1 &&
		   mask[x + delta_x][y + delta_y]) ||
		  (filter->matrix[delta_x + 1][delta_y + 1] == 0 &&
		   !mask[x + delta_x][y + delta_y]) ||
		  (filter->matrix[delta_x + 1][delta_y + 1] == 2)) {
		matches++;
	      }
	    }
	  }
	  if (matches == 9) {
	    tmpmask[x][y] = filter->val;
	  } else {
	    tmpmask[x][y] = !filter->val;
	  }
	}
      }
    }
    for (int x = 0; x < cols; x++) {
      for (int y = 0; y < rows; y++) {
	if (filter->combine == 0 || filter->combine == xcUNION) 
	  mask[x][y] = tmpmask[x][y];
	else { // intersection
	  if (mask[x][y] && tmpmask[x][y]) 
	    mask[x][y] = true;
	}
      }
    }
    filter = filter->pNext;
  }

  // blobify
  int count=1;  
  for (int y=0;y<rows;y++){
    for (int x=0;x<cols;x++){
      if (mask[x][y]) {
	if (x == 0 || y == 0) {
	  tmpmask[x][y] = count++;
	} else if (mask[x-1][y] && mask[x][y-1]){
	  if (tmpmask[x-1][y] == tmpmask[x][y-1]){
	    tmpmask[x][y] = tmpmask[x][y-1];
	  } else {
	    int temp = xrcl::min(ChunkList[tmpmask[x-1][y]], 
				 ChunkList[tmpmask[x][y-1]]);
            int temp2 = xrcl::max(ChunkList[tmpmask[x-1][y]],
				  ChunkList[tmpmask[x][y-1]]);
	    tmpmask[x][y] = temp;
	    for (int counter=0; counter<8000; counter++) {
	      if (ChunkList[counter]==temp2) 
		ChunkList[counter]=temp;
	    } 
	  }
	} else if (!mask[x-1][y] && !mask[x][y-1]) {
	  tmpmask[x][y] = count++;
	} else if (mask[x-1][y]) {
	  tmpmask[x][y] = tmpmask[x-1][y];
	} else if (mask[x][y-1]) {
	  tmpmask[x][y] = tmpmask[x][y-1];
	} else {
	  fprintf(stderr, "Error: can't happen!\n");
	}
      }
    }
  }	
  
  #define MAXBLOBREGIONS 2000
 
  int Count[MAXBLOBREGIONS]={0};
  int ave_x[MAXBLOBREGIONS]={0};
  int ave_y[MAXBLOBREGIONS]={0};
  int min_x[MAXBLOBREGIONS]={100000};
  int min_y[MAXBLOBREGIONS]={100000};
  int max_x[MAXBLOBREGIONS]={0};
  int max_y[MAXBLOBREGIONS]={0};
  
  for (int y=0;y<rows;y++){
    for (int x=0;x<cols;x++){
      tmpmask[x][y] = ChunkList[tmpmask[x][y]];
      Count[tmpmask[x][y]]++;
      ave_x[tmpmask[x][y]] += x;
      ave_y[tmpmask[x][y]] += y;
      //min_x[tmpmask[x][y]] = xrcl::min(x, min_x[tmpmask[x][y]]);
      //min_y[tmpmask[x][y]] = xrcl::min(y, min_y[tmpmask[x][y]]);
      //max_x[tmpmask[x][y]] = xrcl::max(x, max_x[tmpmask[x][y]]);
      //max_y[tmpmask[x][y]] = xrcl::max(y, max_y[tmpmask[x][y]]);
    }
  }

  int operableregions=0;

  for (int i=1;i<MAXBLOBREGIONS;i++){
    if (Count[i]!=0){
      operableregions++;
      ave_x[i] /= Count[i];
      ave_y[i] /= Count[i];
    }
    else{
      ave_x[i]=0;  
      ave_y[1]=0;
    }
  }
if (operableregions > 15)
  operableregions = 15;

#define MAXREGIONS 15 
  int Best_regions[MAXREGIONS];
  int Best_areas[MAXREGIONS];

  int howmanyblobs=0;
  int maxcount;
  int region;
  for (int i=0;i<MAXREGIONS;i++){
    maxcount=0;
    for (int j=1;j<MAXBLOBREGIONS;j++){
      if (Count[j]>maxcount){
	maxcount=Count[j];
	region=j;
      }
    }
    if (howmanyblobs > MAXREGIONS) break;
    if (maxcount!=0) {
      Best_regions[howmanyblobs]=region;
      Count[region]=0;
      Best_areas[howmanyblobs]=maxcount;
      howmanyblobs++;
    }
  }

  Blob *blob_head = NULL;
  Blob *blob_ptr = NULL;
  for (int i=0;i<howmanyblobs;i++){
    if (Best_areas[i] > 0) {
      if (blob_ptr == NULL) {	
	blob_ptr = new Blob();	
	blob_head = blob_ptr;
      } else {
	blob_ptr->next = new Blob();
	blob_ptr = blob_ptr->next;
      }
      blob_ptr->count = Best_areas[i] ;
      blob_ptr->x_avg = (int)ave_x[Best_regions[i]];
      blob_ptr->y_avg = (int)ave_y[Best_regions[i]];
      blob_ptr->y_min = min_y[Best_regions[i]];
      blob_ptr->x_min = min_x[Best_regions[i]];
      blob_ptr->y_max = max_y[Best_regions[i]];
      blob_ptr->x_max = max_x[Best_regions[i]];

      //crosshair(blob_ptr->x_avg,blob_ptr->y_avg);
      //upperleftcorner(blob_ptr->x_min,blob_ptr->y_min);
      //upperrightcorner(blob_ptr->x_max,blob_ptr->y_min);
      //lowerleftcorner(blob_ptr->x_max,blob_ptr->y_min);
      //lowerrightcorner(blob_ptr->x_max,blob_ptr->y_max);
    }
  }
  saveFile("applyfilter.ppm");

  int total = 0;
  int total_x = 0;
  int total_y = 0;
  for (int x = 0; x < cols; x++) {
    for (int y = 0; y < rows; y++) {
      if (mask[x][y]) {
	total++;
	total_x += x;
	total_y += y;
      }	
    }
  }
  Blob *blob = NULL;	
  if (total) {
    blob =  new Blob();	
    blob->count = total;
    blob->x_avg = total_x / total;
    blob->y_avg = total_y / total;
  }
  return blob;
}
*/
void Camera::Sort(int little, int big) {
  if (ChunkList[little] == big) {
    // stop
  } else if (ChunkList[little] == 0) {
    ChunkList[little] = big;
    // stop
  } else if (ChunkList[little] < big) {
    Sort(ChunkList[little], big);
  } else if (ChunkList[little] > big) {
    Sort(little, ChunkList[little]);
  }
}

void Camera::Convolve(short int im[3][3], bool val) {
  for (int x = 0; x < cols; x++) {
    for (int y = 0; y < rows; y++) {
      if (x == 0 || x == cols ||
	  y == 0 || y == rows) {
	tmpmask[x][y] = !val;
	exit(1);
      }
      int matches = 0;
      for (int delta_x = -1; delta_x <= 1; delta_x++) {
	for (int delta_y = -1; delta_y <= 1; delta_y++) {
	  if ((im[delta_x + 1][delta_y + 1] == 1 &&
	       mask[x + delta_x][y + delta_y]) ||
	      (im[delta_x + 1][delta_y + 1] == 0 &&
	       !mask[x + delta_x][y + delta_y]) ||
	      (im[delta_x + 1][delta_y + 1] == 2)) {
	    matches++;
	  }
	}
      }
      if (matches == 9) {
	tmpmask[x][y] = val;
      } else {
	tmpmask[x][y] = !val;
      }
    }
  }
  for (int x = 0; x < cols; x++) {
    for (int y = 0; y < rows; y++) {
      mask[x][y] = tmpmask[x][y];
    }
  }
}

void Camera::Convolve(short int im1[3][3],
		     short int im2[3][3], 
		     bool val) {
  for (int x = 0; x < cols; x++) {
    for (int y = 0; y < rows; y++) {
      if (x == 0 || x == cols ||
	  y == 0 || y == rows) {
	tmpmask[x][y] = !val;
	exit(1);
      }
      int matches = 0;
      for (int delta_x = -1; delta_x <= 1; delta_x++) {
	for (int delta_y = -1; delta_y <= 1; delta_y++) {
	  if ((im1[delta_x + 1][delta_y + 1] == 1 &&
	       mask[x + delta_x][y + delta_y]) ||
	      (im1[delta_x + 1][delta_y + 1] == 0 &&
	       !mask[x + delta_x][y + delta_y]) ||
	      (im1[delta_x + 1][delta_y + 1] == 2)) {
	    matches++;
	  }
	}
      }
      if (matches == 9) {
	tmpmask[x][y] = val;
      } else {
	matches = 0;
	for (int delta_x = -1; delta_x <= 1; delta_x++) {
	  for (int delta_y = -1; delta_y <= 1; delta_y++) {
	    if ((im2[delta_x + 1][delta_y + 1] == 1 &&
		 mask[x + delta_x][y + delta_y]) ||
		(im2[delta_x + 1][delta_y + 1] == 0 &&
		 !mask[x + delta_x][y + delta_y]) ||
		(im2[delta_x + 1][delta_y + 1] == 2)) {
	      matches++;
	    }
	  }
	}
	if (matches == 9) 
	  tmpmask[x][y] = val;
	else 
	  tmpmask[x][y] = !val;
      }
    }
  }
  for (int x = 0; x < cols; x++) {
    for (int y = 0; y < rows; y++) {
      mask[x][y] = tmpmask[x][y];
    }
  }
}

int Camera::pos(int x, int y) {
  return (y * cols) * bpp + (x * bpp);
}

void Camera::setPixel(int x, int y, int r, int g, int b) {
  rawbuf[pos(x,y) + 0] = r;
  rawbuf[pos(x,y) + 1] = g;
  rawbuf[pos(x,y) + 2] = b;
}

int Camera::Red(int x, int y) { // 0 255
  return rawbuf[pos(x,y) + 0]; // red = 0, grn = 1, blu = 2
}

int Camera::Green(int x, int y) { // 0 255
  return rawbuf[pos(x,y) + 1]; // red = 0, grn = 1, blu = 2
}

int Camera::Blue(int x, int y) { // 0 255
  return rawbuf[pos(x,y) + 2]; // red = 0, grn = 1, blu = 2
}


void Camera::crosshair(int x,int y){
  setPixel(x,y,0,255,0);
  setPixel(x+1,y,0,255,0);
  setPixel(x+2,y,0,255,0);
  setPixel(x-1,y,0,255,0);
  setPixel(x-2,y,0,255,0);
  setPixel(x,y+1,0,255,0);
  setPixel(x,y+2,0,255,0);
  setPixel(x,y-1,0,255,0);
  setPixel(x,y-2,0,255,0);
}

void Camera::upperleftcorner(int x,int y){
  setPixel(x,y,0,255,0);
  setPixel(x+1,y,0,255,0);
  setPixel(x+2,y,0,255,0);
  setPixel(x,y+1,0,255,0);
  setPixel(x,y+2,0,255,0);
}

void Camera::upperrightcorner(int x,int y){
  setPixel(x,y,0,255,0);
  setPixel(x-1,y,0,255,0);
  setPixel(x-2,y,0,255,0);
  setPixel(x,y+1,0,255,0);
  setPixel(x,y+2,0,255,0);
}

void Camera::lowerleftcorner(int x,int y){
  setPixel(x,y,0,255,0);
  setPixel(x-1,y,0,255,0);
  setPixel(x-2,y,0,255,0);
  setPixel(x,y+1,0,255,0);
  setPixel(x,y+2,0,255,0);
}

void Camera::lowerrightcorner(int x,int y){
  setPixel(x,y,0,255,0);
  setPixel(x-1,y,0,255,0);
  setPixel(x-2,y,0,255,0);
  setPixel(x,y-1,0,255,0);
  setPixel(x,y-2,0,255,0);
}
