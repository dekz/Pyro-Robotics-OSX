/*
 * Copyright (C) 1997-2002, R3vis Corporation.
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
 * USA, or visit http://www.gnu.org/copyleft/lgpl.html.
 *
 * Original Contributor:
 *   Wes Bethel, R3vis Corporation, Marin County, California
 * Additional Contributor(s):
 *
 * The OpenRM project is located at http://openrm.sourceforge.net/.
 */

#define RM_MAX(a,b)       ((a) > (b) ? (a) : (b))
#define RM_MIN(a,b)       ((a) < (b) ? (a) : (b))

/*
 * ----------------------------------------------------
 void rmHSVtoRGB (float hue,
	          float saturation,
		  float value,
		  float *redReturn,
		  float *greenReturn,
		  float *blueReturn)

 float hue, saturation, value - floating point values in the range
    [0..1] (input).

 float *redReturn, *greenReturn, *blueReturn - handles to floats. will
    contain floats in the range [0..1] (return). 


 Convert a three-component pixel from HSV space to RGB space. Input
 hue is in the range 0..1, with 0 corresponding to 0 degrees on the
 HSV circle, and 1.0 corresponding to 360 degrees on the HSV
 circle. Saturation is in the range 0..1, where 0 is fully desaturated
 and 1 is fully saturated.  Value, or brightness, is in the range
 0..1. A brightness value of 0 is black (not very bright), and a value
 of 1.0 is full brightness.

 The results of the conversion are placed into caller-supplied memory.
 The return RGB values are also in the range 0..1, with 0 representing
 "full off" and 1 representing "full on."

 * ----------------------------------------------------
 */
void
rmHSVtoRGB (float h,
	    float s,
	    float v,
	    float *r,
	    float *g,
	    float *b)
{
    int   i;
    float f, p, q, t;
    float tr = 0.0, tg = 0.0, tb = 0.0; /* inits satisfies gcc warning */
    float ht;
 
    /* (h,s,v) in [0..1] --> (r,g,b) will be in [0..1] - Foley & VanDam */
    ht = h;

    if (v == 0.0)
    {
	tr=0.0;
	tg=0.0;
	tb=0.0;
    }
    else
    {
	if (s == 0.0)
	{
	    tr = v;
	    tg = v;
	    tb = v;
	}
	else
	{
	    ht = ht * 6.0;
	    if (ht >= 6.0)
		ht = 0.0;
      
	    i = ht;
	    f = ht - i;
	    p = v * (1.0 - s);
	    q = v * (1.0 - s*f);
	    t = v * (1.0 - (s * (1.0 - f)));
      
 	    if (i == 0) 
	    {
		tr = v;
		tg = t;
		tb = p;
	    }
	    else if (i == 1)
	    {
		tr = q;
		tg = v;
		tb = p;
	    }
	    else if (i == 2)
	    {
		tr = p;
		tg = v;
		tb = t;
	    }
	    else if (i == 3)
	    {
		tr = p;
		tg = q;
		tb = v;
	    }
	    else if (i == 4)
	    {
		tr = t;
		tg = p;
		tb = v;
	    }
	    else if (i == 5)
	    {
		tr = v;
		tg = p;
		tb = q;
	    }
	}
    }
    *r = tr;
    *g = tg;
    *b = tb;
}


/*
 * ----------------------------------------------------
 void rmRGBtoHSV (float red,
	          float green,
		  float blue,
		  float *hueReturn,
		  float *saturationReturn,
		  float *valueReturn)

 float red, green, blue - floating point values in the range 0..1 that
    represent a 3-component RGB pixel.

 float *hueReturn, *saturationReturn, *valueReturn - handles to floats
    that will contain the HSV representation of the input RGB pixel
    upon return. The return values are in the range 0..1 (result).


 Converts an RGB 3-tuple into HSV space.

 Output hue is in the range 0..1, with 0 corresponding to 0 degrees on
 the HSV circle, and 1.0 corresponding to 360 degrees on the HSV
 circle. Saturation is in the range 0..1, where 0 is fully desaturated
 and 1 is fully saturated.  Value, or brightness, is in the range
 0..1. A brightness value of 0 is black (not very bright), and a value
 of 1.0 is full brightness.

 * ----------------------------------------------------
 */
void
rmRGBtoHSV (float rr,
	    float gg,
	    float bb,
	    float *hh,		/* return: 0 <= h <= 1 */
	    float *ss,		/* return: 0 <= s <= 1 */
	    float *vv)		/* return: 0 <= v <= 1 */
{
   double min, max, v, s, h, rc, gc, bc, r, g, b;

    /* (h,s,v) in [0..1] --> (r,g,b) will be in [0..1] - Foley & VanDam */
    r = rr;
    g = gg;
    b = bb;
    
    max = RM_MAX(r, g);
    max = RM_MAX(max, b);

    min = RM_MIN(r, g);
    min = RM_MIN(min, b);

    v = max;

    if (max != 0.0)
	s = (max - min) / max;
    else
	s = 0.0;

    if (s == 0)
      /* h = UNDEFINED_HUE pick something */
      h = 0.0;
    else
    {
	rc = (max - r) / (max - min);
	gc = (max - g) / (max - min);
	bc = (max - b) / (max - min);
	if (r == max)
	    h = bc - gc;
	else 
	   if (g == max)
	      h = 2 + rc - bc;
	else 
	   if (b == max)
	      h = 4 + gc - rc;
	h = h * 60;
	if (h < 0.0)
	    h = h + 360.0;
    }
    *hh = h / 360.0;
    *ss = s;
    *vv = v;
}
