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

#ifndef __CAMERA_H
#define __CAMERA_H

//#include "Blob.h"
//#include "Filter.h"
#include "Constants.h"
#include <string.h>
#include <stdlib.h>

class Camera 
{
 public:
  unsigned char *buf;    // image data (rgb PPM format, with header)
  unsigned char *rawbuf; // image data (rgb PPM format, no header)
  unsigned char *area;
  unsigned char *history[xcMAXIMAGEHIST];
  unsigned char **intensity;
  int ChunkList[2000];

  int rows,
    cols,
    size;

  Camera ( const char* dname, int w, int h );
  virtual ~Camera();
  virtual void Cleanup() {};

  // Camera defines these:
  void Update();
  unsigned char * Image ();
  unsigned char * RawImage ();
  void saveFile(char *filename);
  int width() { return cols;}
  int height() { return rows;}
  void swap_rgb24(char *mem, int n); 

  int Camera::pos(int x, int y);
  void Camera::setPixel(int x, int y, int r, int g, int b);
  int Camera::Red(int x, int y);
  int Camera::Green(int x, int y);
  int Camera::Blue(int x, int y);

  //Blob *ApplyFilter(Filter *filter, bool mark_it = 0);
  void ApplyMask();
  void Convolve(short int im[3][3], bool val);
  void Convolve(short int im1[3][3], short int im2[3][3], bool val);
  void Sort(int little, int big);
  void Camera::crosshair(int x,int y);
  void Camera::upperleftcorner(int x,int y);
  void Camera::upperrightcorner(int x,int y);
  void Camera::lowerleftcorner(int x,int y);
  void Camera::lowerrightcorner(int x,int y);


 protected:
  char *devicename;
  int fp;
  unsigned char *ptr;
  virtual void GetData (void) {};
  virtual void init(void) {};
  int buf_length;

 public:
  short int mask[ICOLS][IROWS];
  short int tmpmask[ICOLS][IROWS];

  int bpp;
};

#endif // __CAMERA_H



