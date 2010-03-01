/*
 * cluster.c -- cluster main program
 *
 * $Log$
 * Revision 1.2  2005/06/22 05:06:57  dblank
 * Optimized; fixed for gcc4; commented out a free to keep from segfaulting
 *
 * Revision 1.1  2002/07/03 01:08:51  dblank
 * Cluster 2.9 added to pyro/tools
 *
 * Revision 1.23  1993/02/03  07:43:07  stolcke
 * added code vector output for cluster
 *
 * Revision 1.22  1993/01/20  10:28:02  stolcke
 * faster O(n^2) clustering
 *
 * Revision 1.21  1993/01/16  01:44:34  stolcke
 * use triangular distance matrix (save 1/2 the memory)
 *
 * Revision 1.20  1993/01/16  00:27:07  stolcke
 * make dflag printing more efficient
 *
 * Revision 1.19  1993/01/16  00:03:30  stolcke
 * avoid unnecessary reallocation of patterns
 * skip non-root distance entries more efficiently
 *
 * Revision 1.18  1992/02/12  07:13:13  stolcke
 * -E option added
 *
 * Revision 1.17  91/07/15  12:56:00  stolcke
 * width option added 
 * 
 * Revision 1.16  91/07/14  01:10:54  stolcke
 * curses support added
 * graphing routines moved to separate file
 * 
 * Revision 1.15  91/07/10  21:26:54  stolcke
 * saber-cleaned and bad bug in allocation macro fixed
 * 
 * Revision 1.14  91/04/20  16:17:59  stolcke
 * second release (beta)
 * 
 * Revision 1.13  91/04/18  19:03:39  stolcke
 * some more error checks
 * 
 * Revision 1.12  91/04/18  18:28:21  stolcke
 * general cleanup and partial rewrite
 * 
 * Revision 1.11  91/04/18  13:29:29  stolcke
 * merged pca into cluster
 *
 * Revision 1.10  91/04/12  02:09:48  stolcke
 * name quoting added
 *
 * Revision 1.9  90/12/06  21:47:46  stolcke
 * fixed averaging with D/C values
 *
 * Revision 1.8  90/12/06  14:32:52  stolcke
 * support for don't care values added
 * fixed bug when total_distance = 0
 *
 * Revision 1.7  90/11/12  20:31:22  stolcke
 * two initialization fixed
 *
 * Revision 1.6  90/11/12  18:43:26  stolcke
 * workaround to avoid old Sun compiler bug
 *
 * Revision 1.5  90/11/12  16:40:34  stolcke
 * added metric selection and scaling
 *
 * Revision 1.4  90/11/11  18:14:27  stolcke
 * -n flag no longer needed
 *
 * Revision 1.3  90/11/11  02:30:14  stolcke
 * no more seek needed, can use in pipe now
 *
 * Revision 1.2  90/11/10  23:44:02  stolcke
 * added new features (see manpage)
 *
 */

#if !defined(lint) && !defined(SABER)
static char rcsid[] = "$Header$";
#endif				/* not lint */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include "alloc.h"
#include "error.h"
#include "cluster.h"

#define NONE (-2)

#define BUFSIZE 256

#ifndef SCALE
#define SCALE "_SCALE_"
#endif

#ifndef DONTCARE
#define DONTCARE "D/C"
#endif

static FLOAT   distance();
static FLOAT   root();

static char buffer[BUFSIZE];	/* temporary string read buffer */

#define PCA	"pca"
char   *program;		/* program name */

int     vflag = 0;		/* print explanatory messages */
static int pflag = 0;		/* do PCA instead of HCA */
static int dflag = 0;		/* print distances */
static int tflag = 0;		/* print tree in ASCII */
static int Tflag = 0;		/* display tree using curses */
static int gflag = 0;		/* print tree in graph(1) format */
static int bflag = 0;		/* print tree in graph(1) format, with breaks */
static int Bflag = 0;		/* print patterns as bit vectors */
static int sflag = 0;		/* suppress scaling  */
int	Eflag = 0;		/* print eigenvalues */

static int width = 0;		/* width of ASCII tree representation */

static int norm = 2;		/* which l-norm to use for distance metric */

static 
usage()
{
    if (!pflag)
	fprintf(stderr,
	   "usage: %s [-dtTgbBsv] [-w width] [-n norm] [vectorfile [namesfile]]\n", program);
    else
	fprintf(stderr,
		"usage: %s [-Esv] [-e eigenbase] [-c pcs] [vectorfile [namesfile]]\n", PCA);
    exit(2);
}

main(argc, argv)
    int     argc;
    char   *argv[];
{
    FILE   *fp;
    char   *efile = NULL;
    char   *comps = NULL;
    FLOAT **pattern = NULL;
    int     lpat, npat;
    char  **name = NULL;

    int     opt;
    extern char *optarg;
    extern int optind;

    /* who are we ? */
    if ((program = strrchr(argv[0], '/')) == NULL)
	program = argv[0];
    else
	program += 1;

    if (strcmp(program, PCA) == 0)
	pflag = 1;

    while ((opt = getopt(argc, argv, "pdtTgbBvsn:e:c:w:E")) != -1)
	switch (opt) {
	case 'p':
	    pflag = 1;
	    break;
	case 'd':
	    if (pflag)
		usage();
	    dflag = 1;
	    break;
	case 't':
	    if (pflag)
		usage();
	    tflag = 1;
	    break;
	case 'T':
	    if (pflag)
		usage();
	    Tflag = 1;
	    break;
	case 'g':
	    if (pflag)
		usage();
	    gflag = 1;
	    break;
	case 'b':
	    if (pflag)
		usage();
	    bflag = 1;
	    gflag = 1;
	    break;
	case 'B':
	    if (pflag)
		usage();
	    Bflag = 1;
	    break;
	case 'v':
	    vflag = 1;
	    break;
	case 'n':
	    if (pflag)
		usage();
	    if (sscanf(optarg, "%d", &norm) != 1 || norm < 0)
		usage();
	    break;
	case 'e':
	    if (!pflag)
		usage();
	    efile = optarg;
	    break;
	case 'c':
	    if (!pflag)
		usage();
	    comps = optarg;
	    break;
	case 's':
	    sflag = 1;
	    break;
	case 'w':
	    if (pflag)
		usage();
	    if (sscanf(optarg, "%d", &width) != 1 || width <= 0)
		usage();
	    break;
	case 'E':
	    if (!pflag)
		usage();
	    Eflag = 1;
	    break;
	case '?':
	    usage();
	    break;
	}

    if (!(pflag || dflag || tflag || Tflag || gflag || Bflag))
	dflag = tflag = vflag = 1;	/* default behavior */

    if (optind + 2 < argc)
	usage();

    if (!(optind < argc) || !strcmp(argv[optind], "-"))
	fp = stdin;
    else
	IfErr(fp = fopen(argv[optind], "r")) {
	    fprintf(stderr, "%s: cannot open file %s\n", argv[0], argv[optind]);
	    exit(1);
	}

    IfErr(read_pattern(fp, &pattern, &lpat, &npat, &name)) {
	fprintf(stderr, "%s: %s: cannot read pattern\n", program, ERR_MSG);
	exit(1);
    }
    if (vflag)
	fprintf(stderr, "read %d patterns:  size = %d\n", npat, lpat);

    if (optind + 1 < argc) {
	IfErr (name = new_array_of(npat, char *)) {;
	    fprintf(stderr, "%s: not enough core for name array\n", program);
	    exit(1);
	}

	if (!strcmp(argv[optind + 1], "-"))
	    fp = stdin;
	else
	    IfErr(fp = fopen(argv[optind + 1], "r")) {
		fprintf(stderr, "%s: cannot open file %s\n",
			program, argv[optind + 1]);
		exit(1);
	    }

	IfErr(read_names(fp, name, npat)) {
	    fprintf(stderr, "%s: %s: cannot read names\n", program, ERR_MSG);
	    exit(1);
	}
    }
    if (!pflag)
	cluster(pattern, name, lpat, npat);
    else
	pca(pattern, name, lpat, npat, efile, comps);

    exit(0);
}

/* skip blanks and next end of line */
skip_blanks(fp)
    FILE   *fp;
{
    char    c;

    while ((c = getc(fp)) == ' ' || c == '\t');
    if (c != '\n')
	ungetc(c, fp);
    return c;
}

read_names(fp, name, npat)
    FILE   *fp;
    char  **name;
    int     npat;
{
    register int i;

    for (i = 0; i < npat; i++) {
	char    c = skip_blanks(fp);

	if (c == '\"') {
	    getc(fp);
	    fgets(buffer, sizeof(buffer), fp);
	    buffer[strlen(buffer) - 1] = '\0';
	}
	else {
	    IfEOF(fscanf(fp, "%s", buffer))
		Erreturn("not enough names");
	    skip_blanks(fp);
	}

	IfErr(name[i] = new_string(buffer))
	    Erreturn("not enough core");
    }
    return MY_OK;
}

void
print_names(tree, name)
    BiTree *tree;
    char  **name;
{
    if (tree->leaf != LEAF) {
	if (name)
	    printf(" %s", name[tree->leaf]);
	else
	    printf(" %d", tree->leaf);
    }
    else {
	print_names(tree->r_tree, name);
	print_names(tree->l_tree, name);
    }
}

find_nnb(items, which, lpat, index, ndist)
    BiTree *items;	/* node array */
    int which;		/* index of node to find nearest neightbor for */
    int lpat;		/* pattern length */
    int *index;		/* returns: index of nnb (-1 if none) */
    FLOAT *ndist;	/* returns: distance to nnb */
{
    int i;
    FLOAT dist, min_dist;
    int min_index;

    if (items[which].root == FALSE) {
	*index = NONE;
	return;
    }

    min_index = NONE;
    min_dist = 0.0;
    /*
     * find minimum distance neighbor -- to avoid duplication
     * only pairs with 1st index < 2nd index are considered
     */
    for (i = 0; i < which; i++) {
	if (items[i].root == FALSE)
	    continue;
	
	dist = distance(items[which].pat, items[i].pat, lpat);
	if (min_index == NONE || dist < min_dist) {
	    min_index = i;
	    min_dist = dist;
	}
    }

    *index = min_index;
    if (min_index >= 0)
	*ndist = min_dist;
    return;
}

cluster(pattern, name, lpat, npat)
    FLOAT **pattern;
    char  **name;
    int     lpat, npat;
{
    register int i, k;
    BiTree *item = new_array_of(npat, BiTree);
    /*
     * for each data point or cluster center, we keep the index of the nearest
     * neighbor, as well as the distance to it.
     */
    int *nnb_index = new_array_of(npat, int);
    FLOAT *nnb_dist = new_array_of(npat, FLOAT);

    if (item == NULL || nnb_index == NULL || nnb_dist == NULL) {
	    fprintf(stderr, "%s: not enough core\n", program);
	    exit(1);
    }

    /*
     * initialize leaf nodes
     */
    for (i = 0; i < npat; i++) {
	item[i].pat = pattern[i];
	item[i].root = TRUE;
	item[i].size = 1;
	item[i].leaf = i;
	item[i].distance = 0.0;
	item[i].l_tree = item[i].r_tree = NULL;
    }

    /*
     * initialize nearest neighbors
     */
    for (i = 0; i < npat; i++)
	find_nnb(item, i, lpat, &nnb_index[i], &nnb_dist[i]);

    /*
     * cluster until done
     */
    for (;;) {
	BiTree  *newitem;
	FLOAT   dist, min_dist;
	int     pair1, pair2;
	
	/*
	 * find minimum distance pair
	 */
	pair1 = NONE;
	min_dist = 0.0;
	for (i = 0; i < npat; i++) {
	    if (item[i].root == FALSE)
		continue;
	    if (nnb_index[i] != NONE &&
		(pair1 == NONE || nnb_dist[i] < min_dist)) {
		pair1 = i;
		pair2 = nnb_index[i];
		min_dist = nnb_dist[i];
	    }
	}
	if (pair1 == NONE)
	    break;		/* analysis finished */

	min_dist = root(min_dist);

	if (dflag) {
	    printf("minimum distance = %f\t(", (float)min_dist);
	    print_names (&item[pair1], name);
	    printf(" )\t(");
	    print_names (&item[pair2], name);
	    printf(" )\n");
	}

	IfErr (newitem = new_tree(&item[pair1])) { /* copy */
	    fprintf(stderr, "%s: not enough core\n", program);
	    exit(1);
	}

	/*
	 * replace left child node with new tree node
	 * link right child node into parent
	 */
	item[pair1].l_tree = newitem;
	item[pair1].r_tree = &item[pair2];
	item[pair1].leaf = LEAF;	/* ith item cannot be a leaf it has
					 * subtrees */
	IfErr (item[pair1].pat = new_array_of(lpat, FLOAT)) {
	    fprintf(stderr, "%s: not enough core\n", program);
	    exit(1);
	}

	for (k = 0; k < lpat; k++)	/* pat of non-leaf is weighted
					 * average of pat's of its right
					 * & left subtrees */
#ifndef NO_DONTCARES
	    if (IS_DC(item[pair2].pat[k]))
		 item[pair1].pat[k] = newitem->pat[k];
	    else if (IS_DC(newitem->pat[k]))
		item[pair1].pat[k] = item[pair2].pat[k];
	    else
#endif
		item[pair1].pat[k] =
		    (newitem->pat[k] * newitem->size
		     + item[pair2].pat[k] * item[pair2].size)
		    / (newitem->size + item[pair2].size);

	item[pair1].size = newitem->size + item[pair2].size;
	item[pair1].distance = min_dist;

	newitem->root = FALSE;
	item[pair2].root = FALSE;	/* jth item is no longer a root.its a
					 * subtree */
	/*
	 * update nearest neighbors
	 */
	for (i = 0; i < npat; i++) {
	    if (nnb_index[i] == NONE) {
		continue;
	    } else if (nnb_index[i] == pair1 || nnb_index[i] == pair2) {
		/*
		 * worst case: the old nnb is the node that will disappear.
		 * recompute nnb from scratch
		 */
		find_nnb(item, i, lpat, &nnb_index[i], &nnb_dist[i]);
	    } else if (pair1 < i &&
		       (dist = distance(item[pair1].pat, item[i].pat, lpat))
			    < nnb_dist[i]) {
		/*
		 * distance to new node is smaller than previous nnb,
		 * so make it the new nnb.
		 */
		nnb_index[i] = pair1;
		nnb_dist[i] = dist;
	    }
	}
    }

    /*
     * search for root
     */
    for (i = 0; i < npat; i++)
	if (item[i].root == TRUE)
	    break;		/* there should be only one root */

    if (tflag) {
	if (vflag)
	    printf("Resulting Tree = \n");
	IfErr (print_tree(&item[i], name, npat, width)) {
	    fprintf(stderr, "%s: %s: error printing tree\n", program, ERR_MSG);
	    exit(1);
	}
    }

    if (gflag) {
	if (vflag)
	    printf("Tree Graph= \n");
	graph_tree(&item[i], name, npat, bflag);
    }

    if (Tflag) {
#ifdef HAVE_CURSES
	if (vflag)
	    printf("Displaying tree with curses...\n");
	curses_tree(&item[i], name, npat, width);
#else
	fprintf(stderr, "Sorry, no curses support available.\n");
#endif
    }

    if (Bflag) {
	print_bits(&item[i], name, npat);
    }
}

static FLOAT
distance(pat1, pat2, lpat)
    FLOAT  *pat1, *pat2;
    int     lpat;
{
    register int i;
    FLOAT   dist = 0.0;

    for (i = 0; i < lpat; i++) {
	FLOAT   diff = 0.0;

#ifndef NO_DONTCARES
	if (!IS_DC(pat1[i]) && !IS_DC(pat2[i]))
#endif
	    diff = pat1[i] - pat2[i];

	switch (norm) {
	    FLOAT   adiff;

	case 2:
	    dist += diff * diff;
	    break;
	case 1:
	    dist += fabs(diff);
	    break;
	case 0:
	    if ((adiff = fabs(diff)) > dist)
		dist = adiff;
	    break;
	default:
	    dist += pow(fabs(diff), (double) norm);
	    break;
	}
    }
    return dist;
}

static FLOAT
root(dist)
    FLOAT   dist;
{
    switch (norm) {
    case 2:
	return sqrt(dist);
    case 1:
    case 0:
	return dist;
    default:
	return pow(dist, 1 / (double) norm);
    }
}

BiTree *
new_tree(item)
    BiTree *item;
{
    BiTree *tree;

    IfErr (tree = new(BiTree))
	return NULL;

    tree->r_tree = item->r_tree;
    tree->l_tree = item->l_tree;
    tree->leaf = item->leaf;
    tree->root = item->root;
    tree->size = item->size;
    tree->distance = item->distance;
    tree->pat = item->pat;

    return tree;
}

#define Blksize 128

read_pattern(Pfile, patternP, lpatternP, npatternP, nameP)
    FILE   *Pfile;		/* ptrs to pattern file */
    FLOAT ***patternP;
    int    *lpatternP, *npatternP;
    char ***nameP;
{
    register int i;
    int     status;
    int     Asize = Blksize;	/* current array size */

    /***** these local variables are temporary storage and are ****
     ***** copied to the real variables if there is no error ******/
    int     lpattern, npattern;	/* size and # of patterns */
    FLOAT **pattern;
    FLOAT  *first_pattern;
    char  **name = NULL;
    char   *first_name = NULL;
    FLOAT  *scales = NULL;

    IfErr(lpattern = nstrings(Pfile, &first_pattern, &first_name))
	return MY_ERR;

    /* check for scaling info */
    if (first_name != NULL && strcmp(first_name, SCALE) == 0) {
	scales = first_pattern;
	free(first_name);

	/* read first vector again */
	IfErr(status = nstrings(Pfile, &first_pattern, &first_name))
	    return MY_ERR;
	if (status != lpattern)
	    Erreturn("scaling vector not matching data");
    }

    /* allocate space for input/target arrays */
    IfErr(pattern = new_2d_array_of(Asize, lpattern, FLOAT))
	Erreturn("cannot allocate memory for patterns");

    if (first_name != NULL)
	IfErr(name = new_array_of(Asize, char *))
	    Erreturn("cannot allocate memory for names");

    /**** this loop reads in one line from pattern file,**
     **** stores each pattern into pattern buffer    *****/

    for (npattern = 0;; npattern++) {

	if (npattern >= Asize) {/* need to allocate more space for arrays */
	    IfErr(pattern = change_2d_array_size(
		pattern, Asize, lpattern, Asize + Blksize, lpattern, FLOAT))
		Erreturn("cannot allocate memory for pattern ");

	    if (name != NULL)
		IfErr(name = change_array_size(name, Asize + Blksize, char *))
		    Erreturn("cannot allocate memory for pattern ");

	    Asize += Blksize;	/* array size is now Blksize bigger */
	}

	if (first_pattern != NULL) {	/* copy data from first line */
	    for (i = 0; i < lpattern; i++)
		pattern[npattern][i] = first_pattern[i];
	    free(first_pattern);
	    first_pattern = NULL;

	    if (first_name != NULL) {
		name[npattern] = first_name;
		first_name = NULL;
	    }
	}
	else {			/* read data from file */
	    for (i = 0; i < lpattern; i++) {
		IfEOF(status = fscanf(Pfile, "%s", buffer)) {
		    if (i == 0)
			break;
		    Erreturn1("cannot read pattern # %d", npattern);
		}
#ifndef NO_DONTCARES
		if (strcmp(buffer, DONTCARE) == 0)
		    pattern[npattern][i] = DC_VAL;
		else
#endif
		{
		    double f;
		    IfErr (status = sscanf(buffer, "%lf", &f))
			Erreturn1("cannot read pattern # %d", npattern);
		    pattern[npattern][i] = f;
		}
	    }
	    IfEOF(status) break;

	    if (name != NULL) {
		char    c = skip_blanks(Pfile);

		if (c == '\"') {
		    getc(Pfile);
		    fgets(buffer, sizeof(buffer), Pfile);
		    buffer[strlen(buffer) - 1] = '\0';
		}
		else {
		    IfEOF(status = fscanf(Pfile, "%s", buffer))
			Erreturn("not enough names");
		    skip_blanks(Pfile);
		}

		IfErr(name[npattern] = new_string(buffer))
		    Erreturn("not enough core");
	    }
	    IfEOF(status) break;
	}

	if (!sflag && scales != NULL)	/* scale data if requested */
	    for (i = 0; i < lpattern; i++)
		pattern[npattern][i] *= scales[i];

    }
    /* if there is any error, these pointers below aren't changed */

    /* free any space already allocated for patterns */
    if (*patternP != NULL)
	free_2d_array(*patternP, *npatternP);
    if (*nameP != NULL)
	free(*nameP);

    *npatternP = npattern;	/* # of patterns read in from file */
    *lpatternP = lpattern;	/* # of elements in pattern */
    *patternP = pattern;	/* input array */
    *nameP = name;		/* name array */

    return MY_OK;		/* patterns were read in without error */
}

nstrings(fp, patternP, nameP)	/* counts number of strings in the first line
				 * of file */
    FILE   *fp;
    FLOAT **patternP;
    char  **nameP;
{
    register int i;
    int     c;
    FLOAT  *pattern;
    char   *name = NULL;

    IfErr (pattern = new_array_of(1, FLOAT))
	Erreturn("not enough core");

    for (i = 0;; i++) {
	double f;

	if ((c = skip_blanks(fp)) == '\n')
	    break;

	/* read field (number of name) */
	if (c == '\"') {
	    getc(fp);		/* discard quote */
	    fgets(buffer, sizeof(buffer), fp);
	    buffer[strlen(buffer) - 1] = '\0';
	}
	else if (fscanf(fp, "%s", buffer) != 1)
	    break;

#ifndef NO_DONTCARES
	if (c != '\"' && strcmp(buffer, DONTCARE) == 0)
	    pattern[i] = DC_VAL;
	else
#endif
	if (c == '\"' || sscanf(buffer, "%lf", &f) != 1) {
	    IfErr (name = new_string(buffer))
		Erreturn("not enough core");

	    if (c != '\"')
		skip_blanks(fp);
	    break;
	}
	pattern[i] = f;

	IfErr(pattern = change_array_size(pattern, (i + 2), FLOAT))
	    Erreturn("not enough core");
    }

    if (i == 0)
	Erreturn("empty pattern");

    *patternP = pattern;
    *nameP = name;
    return i;
}
