/*
 * alloc.c -- Memory allocation utilities for cluster
 *
 * $Log$
 * Revision 1.1  2002/07/03 01:08:51  dblank
 * Cluster 2.9 added to pyro/tools
 *
 * Revision 1.8  1993/01/20  19:00:40  stolcke
 * triangular matrix stuff no longer needed
 *
 * Revision 1.7  1993/01/16  01:44:13  stolcke
 * added triangular matrix allocation
 *
 * Revision 1.6  1991/07/14  01:10:52  stolcke
 * curses support added
 * graphing routines moved to separate file
 *
 * Revision 1.5  91/07/10  21:26:26  stolcke
 * saber-cleaned and bad bug in allocation macro fixed
 * 
 * Revision 1.4  91/04/20  16:17:52  stolcke
 * second release (beta)
 * 
 * Revision 1.3  91/04/18  18:28:18  stolcke
 * general cleanup and partial rewrite
 * 
 * Revision 1.2  91/04/18  13:29:19  stolcke
 * merged pca into cluster
 *
 */

#if !defined(lint) && !defined(SABER)
static char rcsid[] = "$Header$";
#endif				/* not lint */

#include <stdio.h>
#include <string.h>
#include "alloc.h"
#include "error.h"

/* allocates space for a N1 * N2 * N3 array of specified element size.
	returns the pointer (char*) - type must be casted by the caller */

char ***
calloc_3d(N1, N2, N3, size)
    unsigned N1, N2, N3, size;
{
    register int i, j;
    char ***ptr = (char ***) calloc(N1, sizeof(char *));
    if (ptr == NULL)
	return NULL;

    for (i = 0; i < N1; i++) {
	if (NULL == (ptr[i] = (char **) calloc(N2, sizeof(char *))))
	    return NULL;
	for (j = 0; j < N2; j++)
	    if (NULL == (ptr[i][j] = calloc(N3, size)))
		return NULL;
    }
    return ptr;
}

/* change size of 2d array pointed by "array" from N1xN2 to M1xM2. */
/* contents are undisturbed up to the lesser of N1/M1 and N2/M2 */

char  **
realloc_2d(array, N1, N2, M1, M2, size)
    char  **array;
    unsigned N1, N2, M1, M2;
    unsigned size;		/* size of one element */
{
    char  **ptr;
    register int i, j;

    if (NULL == (ptr = (char **) calloc_2d(M1, M2, size)))
	return NULL;
    N2 *= size;
    M2 *= size;
    for (i = 0; i < N1 && i < M1; i++)
	for (j = 0; j < N2 && j < M2; j++)
	    ptr[i][j] = array[i][j];
    free_2d_array(array, N1);

    return ptr;
}

/* frees a 2d array.  N is range of 1st index */

free_2d_array(array, N)
    char  **array;
    int     N;
{
    register int i;
    for (i = 0; i < N; i++)
	free(array[i]);
    free((char *) array);
}

/* frees a 3d array.  N1/N2 are ranges of 1st/2nd index */

free_3d_array(array, N1, N2)
    char ***array;
    int     N1, N2;
{
    register int i;
    for (i = 0; i < N1; i++)
	free_2d_array(array[i], N2);
    free((char *) array);
}

/* allocates space for a N1 * N2 array of specified element size.
	returns the pointer (char*) - type must be casted by the caller */

char  **
calloc_2d(N1, N2, size)
    unsigned N1, N2, size;
{
    register int i;
    char  **ptr = (char **) calloc(N1, sizeof(char *));
    if (ptr == NULL) {
	return NULL;
    }
    for (i = 0; i < N1; i++)
	if (NULL == (ptr[i] = calloc(N2, size)))
	    return (NULL);
    return ptr;
}

char   *
new_string(string)
    char   *string;
{
    char   *buf;
    IfErr(buf = new_array_of(strlen(string) + 1, char))
	return MY_ERR;
    strcpy(buf, string);
    return buf;
}
