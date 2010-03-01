/*
 * error.h -- error handling defines for cluster
 *
 * $Header$
 * $Log$
 * Revision 1.1  2002/07/03 01:08:51  dblank
 * Cluster 2.9 added to pyro/tools
 *
 * Revision 1.7  1993/03/25  05:19:03  stolcke
 * sgi port
 *
 * Revision 1.6  1993/03/01  19:58:17  stolcke
 * use Nan for D/C reps
 *
 * Revision 1.5  1991/07/14  01:10:50  stolcke
 * curses support added
 * graphing routines moved to separate file
 *
 * Revision 1.4  91/04/20  16:18:10  stolcke
 * second release (beta)
 * 
 * Revision 1.3  91/04/18  18:28:24  stolcke
 * general cleanup and partial rewrite
 * 
 * Revision 1.2  91/04/18  13:29:32  stolcke
 * merged pca into cluster
 *
 */

extern 	char    ERR_MSG[];
extern	int     ERR_FLAG;

#define MY_OK	1		/* avoid conflict with curses result code */
#define MY_ERR	0

/* error handling macros */
#define Erreturn(msg) { \
	(void)strcpy(ERR_MSG, msg); \
	return MY_ERR; \
    }

#define Erreturn1(msg, x) { \
	(void)sprintf(ERR_MSG, msg, x); \
	return MY_ERR; \
    }

#define Erreturn2(msg, x, y) { \
	(void)sprintf(ERR_MSG, msg, x, y); \
	return MY_ERR; \
    }

#define Erreturn3(msg, x, y, z) { \
	(void)sprintf(ERR_MSG, msg, x, y, z); \
	return MY_ERR; \
    }

#define IfErr(x) 	if ((x) == MY_ERR)
#define IfEOF(x)	if ((x) == EOF)

/*
 * macros handling D/C values
 */
#ifndef NO_DONTCARES
/*
 * we use IEEE NaN to represent don't care values -- ugly, but it works
 */
static long _nan = 0x7fffffff;
#define DC_VAL		((double)*(float *)(&_nan))
#define IS_DC(x)	isnan(x)

#ifdef sgi
#define isnan(x)	((x) == DC_VAL)
#endif

#endif /* !NO_DONTCARES */

