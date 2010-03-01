/*
 * graph.c -- graphing support for cluster
 *
 * $Log$
 * Revision 1.2  2005/06/22 05:06:57  dblank
 * Optimized; fixed for gcc4; commented out a free to keep from segfaulting
 *
 * Revision 1.1  2002/07/03 01:08:51  dblank
 * Cluster 2.9 added to pyro/tools
 *
 * Revision 1.4  93/02/19  09:31:32  stolcke
 * fixed NULL-misuse
 * 
 * Revision 1.3  93/02/03  07:43:07  stolcke
 * added code vector output for cluster
 * 
 * Revision 1.2  1991/07/15  12:56:13  stolcke
 * width option added
 *
 * Revision 1.1  91/07/14  01:09:17  stolcke
 * Initial revision
 * 
 *
 */

#if !defined(lint) && !defined(SABER)
static char rcsid[] = "$Header$";
#endif				/* not lint */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#ifdef HAVE_CURSES
#include <curses.h>
#endif

#include "alloc.h"
#include "error.h"
#include "cluster.h"

extern char *program;

max_lname(name, npat)
    char  **name;
    int     npat;
{
    register int i;
    int     max = 0, lname;

    if (name == NULL)
	return 3;

    for (i = 0; i < npat; i++)
	if ((lname = strlen(name[i])) > max)
	    max = lname;

    return max;
}

static FLOAT Y;

/*
 * number tree leaves with consecutive y coordinates
 */
FLOAT
y_tree(tree, right_to_left)
    BiTree *tree;
    int     right_to_left;
{
    if (tree->leaf == LEAF) {
	FLOAT   y_r, y_l;

	if (right_to_left) {
	    y_r = y_tree(tree->r_tree, right_to_left);
	    y_l = y_tree(tree->l_tree, right_to_left);
	}
	else {
	    y_l = y_tree(tree->l_tree, right_to_left);
	    y_r = y_tree(tree->r_tree, right_to_left);
	}
	return tree->y = (y_r + y_l) / 2;
    }
    else {
	FLOAT   y = Y;

	Y += 1.0;
	return tree->y = y;
    }
}

/*
 * compute distance from root to deepest leaf
 */
FLOAT
total_distance(tree)
    BiTree *tree;
{
    FLOAT   dist_r, dist_l, total_distance();
    if (tree->leaf == LEAF)
	return ((dist_r = total_distance(tree->r_tree)) >
		 (dist_l = total_distance(tree->l_tree))) ?
		tree->distance + dist_r : tree->distance + dist_l;
    else
	return tree->distance;
}

tree_depth(tree)
    BiTree *tree;
{
    int     depth_r, depth_l;
    if (tree->leaf == LEAF)
	return ((depth_r = tree_depth(tree->r_tree)) >
	 (depth_l = tree_depth(tree->l_tree))) ? depth_r + 1 : depth_l + 1;
    else
	return 1;
}

#define X0 0.01
#define XMAX 80

/* 
 * translate tree into graph(1) commands
 */
graph_tree(tree, name, npat, bflag)
    BiTree *tree;
    char  **name;
    int     npat;
    int bflag;
{
    FLOAT   x0;

    x0 = X0 * total_distance(tree);
    Y = 0.5;
    (void) y_tree(tree, 0);
    graph_tree_walk(tree, name, -x0, x0, bflag);
}

graph_tree_walk(tree, name, x, distance, bflag)
    BiTree *tree;
    char  **name;
    FLOAT   x, distance;
    int bflag;
{
    FLOAT   y = tree->y, x_next = x + distance;
    if (tree->leaf != LEAF) {
	printf(FLOAT2_FORMAT, (double)x, (double)y);
	printf("\n");
	printf(FLOAT2_FORMAT, (double)x_next, (double)y);
	if (name == NULL)
	    printf(" \" %d\"\n", tree->leaf);
	else
	    printf(" \" %s\"\n", name[tree->leaf]);

	if (!bflag) {
	    printf(FLOAT2_FORMAT, (double)x, (double)y);
	    printf("\n");
	    printf(FLOAT2_FORMAT, (double)x, (double)y);
	}
	printf("\n");
    }
    else {
	printf(FLOAT2_FORMAT, (double)x, (double)y);
	printf("\n");
	printf(FLOAT2_FORMAT, (double)x_next, (double)y);
	printf("\n");

	graph_tree_walk(tree->l_tree, name, x_next, tree->distance, bflag);

	if (!bflag) {
	    printf(FLOAT2_FORMAT, (double)x_next, (double)y);
	    printf("\n");
	}
	printf(FLOAT2_FORMAT, (double)x_next, (double)y);
	printf("\n");

	graph_tree_walk(tree->r_tree, name, x_next, tree->distance, bflag);

	if (!bflag) {
	    printf(FLOAT2_FORMAT, (double)x_next, (double)y);
	    printf("\n");
	    printf(FLOAT2_FORMAT, (double)x, (double)y);
	    printf("\n");
	}
    }
}

/*
 * print tree in ASCII
 */
print_tree(tree, name, npat, width)
    BiTree *tree;
    char  **name;
    int     npat;
    int width;
{
    register int i, j;
    char  **space;
    int     lname = max_lname(name, npat);	/* maximum name length */
    FLOAT   tdist = total_distance(tree);
    FLOAT   xscale;

    if ( width <= 0 )
	width = XMAX;

    if (tdist > 0.0)
	xscale = (width - tree_depth(tree) * 2 - lname - 3) / tdist;
    else
	xscale = 0;

    Y = 0.0;
    (void) y_tree(tree, 1);
    IfErr (space = new_2d_array_of(tree->size, width, char))
	Erreturn("not enough core");

    for (i = 0; i < tree->size; i++)
	for (j = 0; j < width; j++)
	    space[i][j] = ' ';

    draw_tree_in_space(tree, name, space, 0, xscale, 0.0);
    print_space(space, width, tree->size);
    free_2d_array(space, tree->size);

    return MY_OK;
}

print_space(space, depth, size)
    char  **space;
    int     depth, size;
{
    register int i;
    for (i = 0; i < size; i++) {
	space[i][depth - 1] = '\0';
	puts(space[i]);
    }
}

draw_tree_in_space(tree, name, space, x, xscale, distance)
    BiTree *tree;
    char  **name;
    char  **space;
    int     x;
    FLOAT   xscale, distance;
{
    int     y_l, y_r, y = (int) tree->y;
    char    char_x;
    int     x_next;
    if (tree->leaf != LEAF) {
	for (x_next = x + (int)(distance * xscale); x <= x_next; x++)
	    space[y][x] = '-';
	if (name == NULL)
	    sprintf(&space[y][x], "> %d", tree->leaf);
	else
	    sprintf(&space[y][x], "> %s", name[tree->leaf]);
    }
    else {
	y_l = (int) tree->l_tree->y;
	y_r = (int) tree->r_tree->y;
	if ((y_l - y_r) < 2) {
	    if (x > 0)
		space[y][x - 1] = ' ';
	    char_x = '_';
	}
	else
	    char_x = '-';
	for (x_next = x + (int)(distance * xscale); x <= x_next; x++)
	    space[y][x] = char_x;

	draw_tree_in_space(tree->l_tree, name, space, x + 1, xscale, tree->distance);
	for (y = y_r; y <= y_l; y++)
	    space[y][x] = '|';
	draw_tree_in_space(tree->r_tree, name, space, x + 1, xscale, tree->distance);
    }
}

#ifdef HAVE_CURSES

#define WIN_X(x)	((x) + 1)
#define WIN_Y(y)	((y) + 1)
#define BORDER_WID	1

/*
 * print tree in curses(3) window
 */
curses_tree(tree, name, npat, width)
    BiTree *tree;
    char  **name;
    int     npat;
    int	width;
{
    WINDOW *win;
    int     lname = max_lname(name, npat);	/* maximum name length */
    FLOAT   tdist = total_distance(tree);
    FLOAT   xscale;

    int	    pminrow = 0, pmincol = 0;
    int	    o_pminrow = -1, o_pmincol = -1;
    int	    pmaxrow = 0, pmaxcol = 0;
    int     exit = FALSE;

    (void) initscr();

    if ( width > 0 ) 
	pmaxcol = width;
    else
	pmaxcol = COLS;

    if (tdist > 0.0)
	xscale = (pmaxcol - 2*BORDER_WID -
		  tree_depth(tree) * 2 - lname - 3) / tdist;
    else
	xscale = 0;

    Y = 0.0;
    (void) y_tree(tree, 1);

    pmaxrow = tree->size + 2*BORDER_WID;
    win = newpad(pmaxrow, pmaxcol);

    box(win, (chtype)0, (chtype)0);
    draw_tree_in_window(tree, name, win, 0, xscale, 0.0);

    noecho(); cbreak(); nonl();
    curs_set(0);		
    leaveok(win, TRUE);		/* cursor not neaded */
    idlok(win, TRUE);		/* use insert, delete line caps */
    keypad(win, TRUE);		/* accept keypad input */

    do {
	/* update screen if necessary */
	if ( o_pminrow != pminrow || o_pmincol != pmincol ) {
	        prefresh(win, pminrow, pmincol, 0, 0, LINES-1, COLS-1);
		clearok(win, FALSE);
		o_pminrow = pminrow;
		o_pmincol = pmincol;
	}

	/* handle key command */
	switch (wgetch(win)) {
	case 'H':
	case KEY_HOME:
	case KEY_BEG:
		pminrow = 0;
		pmincol = 0;
		break;
	case 'k':
	case KEY_UP:
		pminrow--;
		break;
	case '\n':
	case '\r':
	case 'j':
	case KEY_DOWN:
		pminrow++;
		break;
	case 'h':
	case '\b':
	case KEY_LEFT:
	case KEY_BACKSPACE:
		pmincol--;
		break;
	case 'l':
	case KEY_RIGHT:
		pmincol++;
		break;
	case '\t':
		pmincol += 8;
		break;
	case KEY_BTAB:
		pmincol -= 8;
		break;
	case 'p':
	case KEY_PPAGE:
		pminrow -= LINES;
		break;
	case ' ':
	case 'n':
	case KEY_NPAGE:
		pminrow += LINES;
		break;
	case 'R':
	case KEY_REFRESH:
		o_pminrow = -1;
		o_pmincol = -1;
		clearok(win, TRUE);
		break;
	case 'q':
	case 'Q':
		exit = TRUE;
		break;
	default:
		beep();
	}

	/* make sure we don't scroll off the screen */
	if ( pminrow < 0 )
		pminrow = 0;
	if ( pmincol < 0 )
		pmincol = 0;
	if ( pminrow > pmaxrow - LINES )
		pminrow = pmaxrow - LINES;
	if ( pmincol > pmaxcol - COLS )
		pmincol = pmaxcol - COLS;

    } while ( !exit );
    
    endwin();
    return MY_OK;
}

draw_tree_in_window(tree, name, win, x, xscale, distance)
    BiTree *tree;
    char  **name;
    WINDOW *win;
    int     x;
    FLOAT   xscale, distance;
{
    int     y_l, y_r, y = (int) tree->y;
    int     x_next;
    if (tree->leaf != LEAF) {
	for (x_next = x + (int)(distance * xscale); x <= x_next; x++)
	    mvwaddch(win, WIN_Y(y), WIN_X(x), ACS_HLINE);

	mvwaddch(win, WIN_Y(y), WIN_X(x), ACS_RARROW);

	wmove(win, WIN_Y(y), WIN_X(x+2));

	wattrset(win, A_STANDOUT);
	if (name == NULL) {
	    char buffer[20];
	    sprintf(buffer, "%d" , tree->leaf);
	    waddstr(win, buffer);
	}
	else
	    waddstr(win, name[tree->leaf]);
	wattrset(win, A_NORMAL);
    }
    else {
	int yi;

	y_l = (int) tree->l_tree->y;
	y_r = (int) tree->r_tree->y;

	for (x_next = x + (int)(distance * xscale); x <= x_next; x++)
	    mvwaddch(win, WIN_Y(y), WIN_X(x), ACS_HLINE);

	draw_tree_in_window(tree->l_tree, name, win, x + 1, xscale, tree->distance);

	if ( y_r == y )
	    mvwaddch(win, WIN_Y(y_r), WIN_X(x), ACS_TTEE);
	else
	    mvwaddch(win, WIN_Y(y_r), WIN_X(x), ACS_ULCORNER);

	for (yi = y_r+1; yi < y; yi++)
	    mvwaddch(win, WIN_Y(yi), WIN_X(x), ACS_VLINE);
	if (y != y_l && y != y_r)
	    mvwaddch(win, WIN_Y(y), WIN_X(x), ACS_RTEE);
	for (yi = y+1; yi < y_l; yi++)
	    mvwaddch(win, WIN_Y(yi), WIN_X(x), ACS_VLINE);

	if ( y_l == y )
	    mvwaddch(win, WIN_Y(y_l), WIN_X(x), ACS_BTEE);
	else
	    mvwaddch(win, WIN_Y(y_l), WIN_X(x), ACS_LLCORNER);

	draw_tree_in_window(tree->r_tree, name, win, x + 1, xscale, tree->distance);
    }
}

#endif /* HAVE_CURSES */

/* 
 * print patterns as bit vectors
 */
print_bits(tree, name, npat)
    BiTree *tree;
    char  **name;
    int     npat;
{
    int depth = tree_depth(tree);
    char *bits = malloc (2 * depth + 1);

    if (!bits) {
	fprintf(stderr, "%s: not enough core for bit vector\n", program);
	exit(1);
    }

    print_bits_walk(tree, name, depth - 1, bits, 0);
}

print_bits_walk(tree, name, maxdepth, bits, depth)
    BiTree *tree;
    char  **name;
    int   maxdepth;
    char  *bits;
    int   depth;
{
    if (tree->leaf != LEAF) {
	bits[2 * depth]  = '\0';
	fputs(bits, stdout);

	for (; depth < maxdepth; depth++)
	    fputs ("x ", stdout);

	if (name != NULL) {
	    if (strpbrk(name[tree->leaf], " \t") != NULL)
		putchar('\"');
	    printf("%s\n", name[tree->leaf]);
	}
	else
	    printf("%d\n", tree->leaf);
    }
    else {
	bits[2 * depth + 1] = ' ';
	bits[2 * depth] = '0';
	print_bits_walk(tree->r_tree, name, maxdepth, bits, depth + 1);
	bits[2 * depth] = '1';
	print_bits_walk(tree->l_tree, name, maxdepth, bits, depth + 1);
    }
}

