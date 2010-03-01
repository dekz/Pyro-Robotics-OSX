/********************************************************************* */
/* pnmio.h */
/********************************************************************* */

#ifndef _PNMIO_H_
#define _PNMIO_H_

#include "base.h"
#include <stdio.h>

/********** */
/* used for reading from/writing to files */
unsigned char* pgmReadFile(
     char *fname,
     int *ncols, 
     int *nrows);
void pgmReadHeaderFile(
     char *fname,
     int *magic,
     int *ncols, int *nrows,
     int *maxval);
unsigned char* ppmReadFile(
     char *fname,
     int *ncols, int *nrows);
void ppmReadHeaderFile(
     char *fname,
     int *magic,
     int *ncols, int *nrows,
     int *maxval);
void pgmWriteFile(
     char *fname,
     unsigned char *img,
     int ncols,
     int nrows);
void ppmWriteFile(
     char *fname,
     unsigned char *img,
     int ncols,
     int nrows);
void ppmWriteFileRGB(
     char *fname,
     unsigned char *redimg,
     unsigned char *greenimg,
     unsigned char *blueimg,
     int ncols,
     int nrows);

/********** */
/* used for communicating with stdin and stdout */
unsigned char* pgmRead(
     FILE *fp,
     int *ncols, int *nrows);
void pgmWrite(
     FILE *fp,
     unsigned char *img,
     int ncols,
     int nrows);
unsigned char* ppmRead(
     FILE *fp,
     int *ncols, int *nrows);
void ppmWrite(
     FILE *fp,
     uchar *img,
     int ncols,
     int nrows);
void ppmWriteRGB(
     FILE *fp,
     unsigned char *redimg,
     unsigned char *greenimg,
     unsigned char *blueimg,
     int ncols,
     int nrows);

/********** */
/* lower level functions */
void pnmReadHeader(
     FILE *fp,
     int *magic,
     int *ncols, int *nrows,
     int *maxval);

#endif
