/********************************************************************* */
/* pnmio.c */
/* */
/* Various routines to manipulate PNM files. */
/********************************************************************* */

/* Standard includes */
#include <stdio.h>		/* FILE  */
#include <stdlib.h>		/* malloc(), atoi() */

/* Our includes */
#include "base.h"
#include "error.h"

#define LENGTH 80

static int verbose = 1;


/********************************************************************* */

static void _getNextString(
	FILE *fp,
	char *line)
{
	int i;

	line[0] = '\0';

	while (line[0] == '\0')  {
		fscanf(fp, "%s", line);
/* printf("String before removing comment: %s\n", line); */
		i = -1;
		do  {
			i++;
			if (line[i] == '#')  {
				line[i] = '\0';
				while (fgetc(fp) != '\n') ;
			}
		}  while (line[i] != '\0');
/* printf("                         After: %s\n", line); */
	}
/* printf("Final string: %s\n", line); */
}


/********************************************************************* */
/* pnmReadHeader */

void pnmReadHeader(
	FILE *fp, 
	int *magic, 
	int *ncols, int *nrows, 
	int *maxval)
{
	char line[LENGTH];
	
	/* Read magic number */
	_getNextString(fp, line);
	if (line[0] != 'P')
		error("(pnmReadHeader) Magic number does not begin with 'P', "
			"but with a '%c'", line[0]);
	sscanf(line, "P%d", magic);
	
	/* Read size, skipping comments */
	_getNextString(fp, line);
	*ncols = atoi(line);
	_getNextString(fp, line);
	*nrows = atoi(line);
	if (*ncols < 0 || *nrows < 0 || *ncols > 10000 || *nrows > 10000)
  		error("(pnmReadHeader) The dimensions %d x %d are unacceptable",
			*ncols, *nrows);
	
	/* Read maxval, skipping comments */
	_getNextString(fp, line);
	*maxval = atoi(line);
	fread(line, 1, 1, fp); /* Read newline which follows maxval */
	
	if (*maxval != 255)
  		warning("(pnmReadHeader) Maxval is not 255, but %d", *maxval);
}


/********************************************************************* */
/* pgmReadHeader */

void pgmReadHeader(
	FILE *fp, 
	int *magic, 
	int *ncols, int *nrows, 
	int *maxval)
{
	pnmReadHeader(fp, magic, ncols, nrows, maxval);
	if (*magic != 5)
		error("(pgmReadHeader) Magic number is not 'P5', but 'P%d'", *magic);
}


/********************************************************************* */
/* ppmReadHeader */

void ppmReadHeader(
	FILE *fp, 
	int *magic, 
	int *ncols, int *nrows, 
	int *maxval)
{
	pnmReadHeader(fp, magic, ncols, nrows, maxval);
	if (*magic != 6)
		error("(ppmReadHeader) Magic number is not 'P6', but 'P%d'", *magic);
}


/********************************************************************* */
/* pgmReadHeaderFile */

void pgmReadHeaderFile(
	char *fname, 
	int *magic, 
	int *ncols, int *nrows, 
	int *maxval)
{
	FILE *fp;

	/* Open file */
	if ( (fp = fopen(fname, "rb")) == NULL)
		error("(pgmReadHeaderFile) Can't open file named '%s' for reading\n", fname);

	/* Read header */
	pgmReadHeader(fp, magic, ncols, nrows, maxval);

	/* Close file */
	fclose(fp);
}


/********************************************************************* */
/* ppmReadHeaderFile */

void ppmReadHeaderFile(
	char *fname, 
	int *magic, 
	int *ncols, int *nrows, 
	int *maxval)
{
	FILE *fp;

	/* Open file */
	if ( (fp = fopen(fname, "rb")) == NULL)
		error("(ppmReadHeaderFile) Can't open file named '%s' for reading\n", fname);

	/* Read header */
	ppmReadHeader(fp, magic, ncols, nrows, maxval);

	/* Close file */
	fclose(fp);
}


/********************************************************************* */
/* pgmRead */
/* */

unsigned char* pgmRead(
	FILE *fp,
	int *ncols, int *nrows)
{
	unsigned char *ptr;
	int magic, maxval;
	//int i;

	/* Read header */
	pgmReadHeader(fp, &magic, ncols, nrows, &maxval);

	/* Allocate memory, and set pointer */

	ptr = malloc(*ncols * *nrows * sizeof(char));
	if (ptr == NULL)  
		error("(pgmRead) Memory not allocated");

    /* Read binary image data */
	fread(ptr, *ncols * *nrows, 1, fp);
/*
	{
		unsigned char *tmpptr = ptr;
		for (i = 0 ; i < *nrows ; i++)  {
			fread(tmpptr, *ncols, 1, fp);
			tmpptr += *ncols;
		}
	}
*/

	return ptr;
}


/********************************************************************* */
/* pgmReadFile */
/* */

unsigned char* pgmReadFile(
	char *fname,
	int *ncols, int *nrows)
{
	unsigned char *ptr;
	FILE *fp;

	/* Open file */
	if ( (fp = fopen(fname, "rb")) == NULL)
		error("(pgmReadFile) Can't open file named '%s' for reading\n", fname);

	/* Read file */
	ptr = pgmRead(fp, ncols, nrows);

	/* Close file */
	fclose(fp);

	return ptr;
}


/********************************************************************* */
/* ppmRead */
/* */

unsigned char* ppmRead(
	FILE *fp,
	int *ncols, int *nrows)
{
	unsigned char *ptr;
	int magic, maxval;
	//int i;

	/* Read header */
	ppmReadHeader(fp, &magic, ncols, nrows, &maxval);

	/* Allocate memory, and set pointers */
	ptr = malloc(*ncols * *nrows * 3 * sizeof(char));
	if (ptr == NULL)  
		error("(ppmRead) Memory not allocated");

	/* Read binary image data */
	fread(ptr, *ncols * *nrows * 3, 1, fp);

	return ptr;
}


/********************************************************************* */
/* ppmReadFile */
/* */
/* NOTE:  If img is NULL, memory is allocated. */

unsigned char* ppmReadFile(
	char *fname,
	int *ncols, int *nrows)
{
	unsigned char *ptr;
	FILE *fp;

	/* Open file */
	if ( (fp = fopen(fname, "rb")) == NULL)
		error("(ppmReadFile) Can't open file named '%s' for reading\n", fname);

	/* Read file */
	ptr = ppmRead(fp, ncols, nrows);

	/* Close file */
	fclose(fp);

	return ptr;
}


/********************************************************************* */
/* pgmWrite */

void pgmWrite(
	FILE *fp,
	unsigned char *img, 
	int ncols, 
	int nrows)
{
     int i;

	/* Write header */
     fprintf(fp, "P5\n");
     fprintf(fp, "%d %d\n", ncols, nrows);
     fprintf(fp, "255\n");

	/* Write binary data */
     for (i = 0 ; i < nrows ; i++)  {
          fwrite(img, ncols, 1, fp);
          img += ncols;
     }
}


/********************************************************************* */
/* pgmWriteFile */

void pgmWriteFile(
	char *fname, 
	unsigned char *img, 
	int ncols, 
	int nrows)
{
     FILE *fp;

	/* Open file */
	if ( (fp = fopen(fname, "wb")) == NULL)
		error("(pgmWriteFile) Can't open file named '%s' for writing\n", fname);

	/* Write to file */
	pgmWrite(fp, img, ncols, nrows);

	/* Close file */
     fclose(fp);
}


/********************************************************************* */
/* ppmWrite */

void ppmWrite(
	FILE *fp,
	uchar *img,
	int ncols, 
	int nrows)
{
	/* Write header */
     fprintf(fp, "P6\n");
     fprintf(fp, "%d %d\n", ncols, nrows);
     fprintf(fp, "255\n");

	/* Write binary data */
     fwrite(img, ncols * nrows * 3, 1, fp); 
     
}


/********************************************************************* */
/* ppmWriteFile */

void ppmWriteFile(
	char *fname, 
	unsigned char *img,
	int ncols, 
	int nrows)
{
     FILE *fp;

	/* Open file */
	if ( (fp = fopen(fname, "wb")) == NULL)
		error("(ppmWriteFile) Can't open file named '%s' for writing\n", fname);

	/* Write to file */
	ppmWrite(fp, img, ncols, nrows);

	/* Close file */
     fclose(fp);
}


/********************************************************************* */
/* ppmWriteRGB */

void ppmWriteRGB(
	FILE *fp,
	unsigned char *redimg,
	unsigned char *greenimg,
	unsigned char *blueimg,
	int ncols, 
	int nrows)
{
     int i, j;

	/* Write header */
     fprintf(fp, "P6\n");
     fprintf(fp, "%d %d\n", ncols, nrows);
     fprintf(fp, "255\n");

	/* Write binary data */
     for (j = 0 ; j < nrows ; j++)  {
     	for (i = 0 ; i < ncols ; i++)  {
          	fwrite(redimg, 1, 1, fp); 
			fwrite(greenimg, 1, 1, fp);
          	fwrite(blueimg, 1, 1, fp);
          	redimg++;  greenimg++;  blueimg++;
		}
     }
}


/********************************************************************* */
/* ppmWriteFileRGB */

void ppmWriteFileRGB(
	char *fname, 
	unsigned char *redimg,
	unsigned char *greenimg,
	unsigned char *blueimg,
	int ncols, 
	int nrows)
{
     FILE *fp;

	/* Open file */
	if ( (fp = fopen(fname, "wb")) == NULL)
		error("(ppmWriteFileRGB) Can't open file named '%s' for writing\n", fname);

	/* Write to file */
	ppmWriteRGB(fp, redimg, greenimg, blueimg, ncols, nrows);

	/* Close file */
     fclose(fp);
}


