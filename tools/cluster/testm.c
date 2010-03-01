/*
 * Test some tricks we play with special IEEE floating point values
 */

#include <stdio.h>
#include <math.h>

#include "alloc.h"
#include "error.h"

#ifdef ultrix
#define isinf(x) (!finite(x))
#endif

main()
{
	FLOAT val;
	
	val = HUGE;
	printf("val = %lf (0x%08x), isinf = %d, == HUGE = %d\n",
		val, *(long *)&val, isinf(val), (val == HUGE));

	if (IS_DC(val)) {
		fprintf(stderr, "IS_DC gives wrong result on infinity\n");
		exit (1);
	}

	val = DC_VAL;
	printf("val = %lf (0x%08x), IS_DC = %d, == DC_VAL = %d\n",
		val, *(long *)&val, IS_DC(val), (val == DC_VAL));

	if (!IS_DC(val)) {
		fprintf(stderr, "IS_DC gives wrong result on DC_VAL\n");
		exit (1);
	}

	val = 1.0;
	printf("val = %lf (0x%08x), IS_DC = %d, == DC_VAL = %d\n",
		val, *(long *)&val, IS_DC(val), (val == DC_VAL));

	if (IS_DC(val)) {
		fprintf(stderr, "IS_DC gives wrong result on regular number\n");
		exit (1);
	}

	exit (0);
}
