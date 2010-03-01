/*
 * pca.c -- PCA attachment for cluster program
 *
 * $Log$
 * Revision 1.2  2005/06/22 05:06:57  dblank
 * Optimized; fixed for gcc4; commented out a free to keep from segfaulting
 *
 * Revision 1.1  2002/07/03 01:08:51  dblank
 * Cluster 2.9 added to pyro/tools
 *
 * Revision 1.8  1996/01/10 19:58:14  stolcke
 * fixed misplaced free() call
 *
 * Revision 1.7  1992/02/12 07:13:13  stolcke
 * -E option added
 *
 * Revision 1.6  1992/02/12  06:26:28  stolcke
 * eigenvector file format transposed
 *
 * Revision 1.5  1991/07/14  01:10:58  stolcke
 * curses support added
 * graphing routines moved to separate file
 *
 * Revision 1.4  91/07/10  21:26:56  stolcke
 * saber-cleaned and bad bug in allocation macro fixed
 * 
 * Revision 1.3  91/04/20  16:18:19  stolcke
 * second release (beta)
 * 
 * Revision 1.2  91/04/18  18:28:27  stolcke
 * general cleanup and partial rewrite
 * 
 * Revision 1.1  91/04/18  13:28:15  stolcke
 * Initial revision
 *
 */

#if !defined(lint) && !defined(SABER)
static char rcsid[] = "$Header$";
#endif				/* not lint */

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>
#include "alloc.h"
#include "error.h"

/*
 * vars defined in main program
 */
extern char *program;
extern int vflag;
extern int Eflag;

/*
 * computational subroutines for PCA
 */
static int
covariance(vecs, m, cov, n)
    FLOAT **vecs, **cov;
    int     m, n;
{
    FLOAT  *mean;		/* vector of means */
    int     i, j, k;

    IfErr (mean = new_array_of(n, FLOAT))
	Erreturn("not enough core");

    /* compute means */
    for (i = 0; i < n; i++) {
	FLOAT sum = 0.0;
	int   l = 0;

	for (k = 0; k < m; k++) {
#ifndef NO_DONTCARES
	    if ( !IS_DC(vecs[k][i]) )
#endif
	    {
		sum += vecs[k][i];
		l += 1;
	    }
	}

	mean[i] = sum / (l != 0 ? l : 1);

#ifndef NO_DONTCARES
	/* replace all D/C's my the mean on that dimension */
	for (k = 0; k < m; k++)
	    if ( IS_DC(vecs[k][i]) )
		vecs[k][i] = mean[i];
#endif
    }

    /* compute covariance */
    for (i = 0; i < n; i++)
	for (j = 0; j <= i; j++)
	    cov[i][j] = 0.0;

    for (k = 0; k < m; k++)
	for (i = 0; i < n; i++)
	    for (j = 0; j <= i; j++)
		cov[i][j] += (vecs[k][i] - mean[i]) *
		    (vecs[k][j] - mean[j]);

    for (i = 0; i < n; i++) {
	for (j = 0; j < i; j++) {
	    cov[i][j] /= m;
	    cov[j][i] = cov[i][j];
	}
	cov[i][i] /= m;
    }

    free(mean);
    return MY_OK;
}

static int
jacobi(a, n, d, v, nrot)
    FLOAT **a, d[], **v;
    int     n, *nrot;
{
    int     j, iq, ip, i;
    FLOAT   *b, *z;

    IfErr (b = new_array_of(n, FLOAT))
	Erreturn("not enough core");
    IfErr (z = new_array_of(n, FLOAT))
	Erreturn("not enough core");

    for (ip = 0; ip < n; ip++) {
	for (iq = 0; iq < n; iq++)
	    v[ip][iq] = 0.0;
	v[ip][ip] = 1.0;
    }

    for (ip = 0; ip < n; ip++) {
	b[ip] = d[ip] = a[ip][ip];
	z[ip] = 0.0;
    }

    *nrot = 0;
    for (i = 1; i <= 50; i++) {
	FLOAT	tresh;
	FLOAT	sm = 0.0;

	for (ip = 0; ip < n - 1; ip++) {
	    for (iq = ip + 1; iq < n; iq++)
		sm += fabs(a[ip][iq]);
	}

	if (sm == 0.0) {
	    free(z);
	    free(b);
	    return MY_OK;
	}

	if (i < 4)
	    tresh = 0.2 * sm / (n * n);
	else
	    tresh = 0.0;

	for (ip = 0; ip < n - 1; ip++) {
	    for (iq = ip + 1; iq < n; iq++) {
		FLOAT g = 100.0 * fabs(a[ip][iq]);

		if (i > 4 &&
		    fabs(d[ip]) + g == fabs(d[ip]) &&
		    fabs(d[iq]) + g == fabs(d[iq]))
		    a[ip][iq] = 0.0;

		else if (fabs(a[ip][iq]) > tresh) {
		    FLOAT tau, t, s, c;
		    FLOAT h = d[iq] - d[ip];

		    if (fabs(h) + g == fabs(h))
			t = (a[ip][iq]) / h;
		    else {
			FLOAT theta = 0.5 * h / (a[ip][iq]);
			t = 1.0 / (fabs(theta) + sqrt(1.0 + theta * theta));
			if (theta < 0.0)
			    t = -t;
		    }

		    c = 1.0 / sqrt(1 + t * t);
		    s = t * c;
		    tau = s / (1.0 + c);
		    h = t * a[ip][iq];
		    z[ip] -= h;
		    z[iq] += h;
		    d[ip] -= h;
		    d[iq] += h;
		    a[ip][iq] = 0.0;

#define rotate(a,i,j,k,l) \
			g = a[i][j]; \
			h = a[k][l]; \
			a[i][j] = g - s *(h + g*tau); \
			a[k][l] = h + s*(g - h*tau);

		    for (j = 0; j < ip; j++) {
			rotate(a, j, ip, j, iq)
		    }
		    for (j = ip + 1; j < iq; j++) {
			rotate(a, ip, j, j, iq)
		    }
		    for (j = iq + 1; j < n; j++) {
			rotate(a, ip, j, iq, j)
		    }
		    for (j = 0; j < n; j++) {
			rotate(v, j, ip, j, iq)
		    }

		    *nrot += 1;
		}
	    }
	}
	for (ip = 0; ip < n; ip++) {
	    b[ip] += z[ip];
	    d[ip] = b[ip];
	    z[ip] = 0.0;
	}
    }

    Erreturn("too many Jacobi iterations");
}

static void
eigsrt(d, v, n)
    FLOAT   d[], **v;
    int     n;
{
    int     k, j, i;

    for (i = 0; i < n - 1; i++) {
	FLOAT p = d[k = i];

	for (j = i + 1; j < n; j++)
	    if (d[j] >= p)
		p = d[k = j];

	if (k != i) {
	    d[k] = d[i];
	    d[i] = p;

	    for (j = 0; j < n; j++) {
		p = v[j][i];
		v[j][i] = v[j][k];
		v[j][k] = p;
	    }
	}
    }
}

static int
gaussjt(a, n, b, m)
    FLOAT **a, **b;
    int     n, m;
{
    int    *indxc, *indxr, *ipiv;
    int     i, j, k, l;

    IfErr (indxc = new_array_of(n, int))
	Erreturn("not enough core");
    IfErr (indxr = new_array_of(n, int))
	Erreturn("not enough core");
    IfErr (ipiv = new_array_of(n, int))
	Erreturn("not enough core");

    for (j = 0; j < n; j++)
	ipiv[j] = 0;

    for (i = 0; i < n; i++) {
	int	icol, irow, ll;
	FLOAT	pivinv;
	FLOAT	big = 0.0;

	for (j = 0; j < n; j++)
	    if (ipiv[j] != 1)
		for (k = 0; k < n; k++) {
		    if (ipiv[k] == 0) {
			if (fabs(a[j][k]) >= big) {
			    big = fabs(a[j][k]);
			    irow = j;
			    icol = k;
			}
		    }
		    else if (ipiv[k] > 1)
			Erreturn("singular matrix");
		}

	ipiv[icol] += 1;

#define swap(a,b) { \
		FLOAT temp = (a); \
		(a) = (b); \
		(b) = temp; \
	    }

	if (irow != icol) {
	    for (l = 0; l < n; l++)
		swap(a[irow][l], a[icol][l]);
	    for (l = 0; l < m; l++)
		swap(b[l][irow], b[l][icol]);
	}

	indxr[i] = irow;
	indxc[i] = icol;

	if (a[icol][icol] == 0.0)
	    Erreturn("singular matrix");

	pivinv = 1.0 / a[icol][icol];
	a[icol][icol] = 1.0;

	for (l = 0; l < n; l++)
	    a[icol][l] *= pivinv;

	for (l = 0; l < m; l++)
	    b[l][icol] *= pivinv;

	for (ll = 0; ll < n; ll++)
	    if (ll != icol) {
		FLOAT dum = a[ll][icol];
		a[ll][icol] = 0.0;

		for (l = 0; l < n; l++)
		    a[ll][l] -= a[icol][l] * dum;

		for (l = 0; l < m; l++)
		    b[l][ll] -= b[l][icol] * dum;
	    }
    }
    for (l = n - 1; l >= 0; l--) {
	if (indxr[l] != indxc[l])
	    for (k = 0; k < n; k++)
		swap(a[k][indxr[l]], a[k][indxc[l]]);
    }
    free(ipiv);
    free(indxr);
    free(indxc);
    return MY_OK;
}

/*
 * matrix I/O
 */
static int
write_matrix(fp, mat, n)
    FILE   *fp;
    FLOAT **mat;
    int     n;
{
    int     i, j;

    /* print column vectors line-by-line */
    for (j = 0; j < n; j++) {
	for (i = 0; i < n; i++) {
	    fprintf(fp, FLOAT_FORMAT, (double)mat[i][j]);
	    fprintf(fp, " ");
	}
	fprintf(fp, "\n");
    }

    return MY_OK;
}

static int
read_matrix(fp, mat, n)
    FILE   *fp;
    FLOAT **mat;
    int     n;
{
    int     i, j;


    /* read column vectors line-by-line */
    for (j = 0; j < n; j++) {
	for (i = 0; i < n; i++) {
	    double f;
	    if (fscanf(fp, "%lf", &f) != 1)
		return MY_ERR;
	    mat[i][j] = f;
	}
    }

    return MY_OK;
}

static int
write_pattern(mat, m, n, name, comps)
    FLOAT **mat;
    char  **name;
    int     m, n;
    char   *comps;
{
    int     i, j;
    int    *pcs;

    IfErr (pcs = new_array_of(n, int))
	Erreturn("not enough core");

    /* initialize list of pcs */
    for (j = 0; j < n; j++)
	pcs[j] = comps == NULL ? j : -1;

    /* parse list of pcs */
    for (j = 0; j < n && comps != NULL;) {
	if (sscanf(comps, "%d", &i) == 1 &&
	    i > 0 && i <= n)
	    pcs[j++] = i - 1;
	if ((comps = strchr(comps, ',')) != NULL)
	    comps++;
    }

    /* dump vectors */
    for (i = 0; i < m; i++) {
	for (j = 0; j < n && pcs[j] >= 0; j++) {
	    printf(FLOAT_FORMAT, (double)mat[i][pcs[j]]);
	    printf(" ");
	}
	if (name != NULL) {
	    if (strpbrk(name[i], " \t") != NULL)
		printf("\"");
	    printf("%s", name[i]);
	}
	printf("\n");
    }

    free(pcs);
    return MY_OK;
}

pca(pattern, name, lpat, npat, efile, comps)
    FLOAT **pattern;		/* array of pattern vectors */
    char  **name;		/* array of label strings (or NULL) */
    int     lpat, npat;
    char   *efile;		/* name of an eigenbase file (or NULL) */
    char   *comps;		/* list of PCs to print (or NULL) */
{
    FLOAT **covar;		/* covariance matrix */
    FLOAT  *eval;		/* eigenvalues thereof */
    FLOAT **evec;		/* eigenvectors thereof */
    int     nrot;		/* no of jacobi rots */

    FILE   *efp = NULL;

    if (Eflag || efile == NULL || (efp = fopen(efile, "r")) == NULL) {

	if (efile != NULL &&
	    (efp = fopen(efile, "w")) == NULL) {
	    fprintf(stderr, "%s: cannot create %s\n", program, efile);
	}
	IfErr (covar = new_2d_array_of(lpat, lpat, FLOAT)) {
	    fprintf(stderr, "%s: not enough core for covar matrix\n", program);
	    exit(1);
	}

	/* compute covariance matrix */
	if (vflag)
	    fprintf(stderr, "computing covariance ...\n");
	IfErr (covariance(pattern, npat, covar, lpat)) {
	    fprintf(stderr, "%s: %s: covariance failed\n", program, ERR_MSG);
	    exit(1);
	}

	/* compute eigenvectors and -values */
	IfErr (eval = new_array_of(lpat, FLOAT)) {
	    fprintf(stderr, "%s: not enough core\n", program);
	    exit(1);
	}
	IfErr (evec = new_2d_array_of(lpat, lpat, FLOAT)) {
	    fprintf(stderr, "%s: not enough core for eigenbasis\n", program);
	    exit(1);
	}

	if (vflag)
	    fprintf(stderr, "computing eigenbasis ...\n");

	IfErr (jacobi(covar, lpat, eval, evec, &nrot)) {
	    fprintf(stderr, "%s: %s: jacobi failed\n", program, ERR_MSG);
	    exit(1);
	}

	/* order eigenvectors */
	if (vflag)
	    fprintf(stderr, "sorting eigenbasis ...\n");
	eigsrt(eval, evec, lpat);

	if (efp != NULL) {
	    if (vflag)
		fprintf(stderr, "saving eigenbasis in %s\n", efile);
	    write_matrix(efp, evec, lpat);
	    fclose(efp);
	}
	free_2d_array(covar, lpat);
    }
    else {
	/* read eigenvectors from file */
	IfErr (evec = new_2d_array_of(lpat, lpat, FLOAT)) {
	    fprintf(stderr, "%s: not enough core for eigenbasis\n", program);
	    exit(1);
	}

	if (vflag)
	    fprintf(stderr, "reading eigenbasis from %s\n", efile);

	IfErr(read_matrix(efp, evec, lpat)) {
	    fprintf(stderr, "%s: bad eigenbasis format\n", program);
	    exit(1);
	}
    }

    /* convert pattern vectors to eigenbasis */
    if (vflag)
	fprintf(stderr, "converting to eigenbasis ...\n");
    IfErr (gaussjt(evec, lpat, pattern, npat)) {
	fprintf(stderr, "%s: %s: gaussjt failed\n", program, ERR_MSG);
	exit(1);
    }

    /* output converted patterns */
    if (Eflag) {
	IfErr (write_pattern(&eval, 1, lpat, NULL, comps)) {
	    fprintf(stderr, "%s: %s: cannot write eigenvalues\n",
			    program, ERR_MSG);
	    exit(1);
	}
    }
    else {
	IfErr (write_pattern(pattern, npat, lpat, name, comps)) {
	    fprintf(stderr, "%s: %s: cannot write patterns\n",
			    program, ERR_MSG);
	    exit(1);
	}
    }

    //free(eval);
    free_2d_array(evec, lpat);
}
