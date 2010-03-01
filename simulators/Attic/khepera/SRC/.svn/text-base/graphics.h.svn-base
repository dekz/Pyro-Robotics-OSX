/*****************************************************************************/
/* File:        graphics.h (Khepera Simulator)                               */
/* Author:      Olivier MICHEL <om@alto.unice.fr>                            */
/* Date:        Tue Feb 13 17:26:49 MET 1996                                 */
/* Description: graphics header file                                         */
/*                                                                           */
/* Copyright (c) 1995                                                        */
/* Olivier MICHEL                                                            */
/* MAGE team, i3S laboratory,                                                */
/* CNRS, University of Nice - Sophia Antipolis, FRANCE                       */
/*                                                                           */
/* Permission is hereby granted to copy this package for free distribution.  */
/* The author's name and this copyright notice must be included in any copy. */
/* Commercial use is forbidden.                                              */
/*****************************************************************************/

#ifndef GRAPHICS_H

#define GRAPHICS_H

#include <X11/Xatom.h>
#include <X11/Xos.h>
#include <X11/keysym.h>
#include <X11/cursorfont.h>
#include <X11/Xutil.h>
#include "colors.h"
#include "robot.h"

#define WINDOW_W                510
#define WINDOW_H                741
#define PLATE1_H								550
#define ROBOT_SCALE             (double)2.0
#define WORLD_SCALE             (double)0.5
#define WORLD_INV_SCALE         2   /* integer value equal to 1/SCALE */
#define WORLD_X									500
#define WORLD_Y									500
#define WORLD_OFFSET_X          5
#define WORLD_OFFSET_Y          44

#define FONT1                   "7x13bold" /* default font */ 
#define FONT2                   "7x13"     /* if FONT1 doesn't exist */

struct Button
{
  char          *Text;
  u_char        State,Value;
  short int     X,Y,Width,Height;
  struct Button *Next;
};

#define DrawBox(x,y,c)         DrawPlate(x,y,9,9,c,PLATE_UP)
#define DrawText(x,y,t)        XDrawString(display,window,gc,x,y,t,strlen(t))
#define Color(c)               XSetForeground(display,gc,color[c].pixel)
#define FillRectangle(x,y,w,h) XFillRectangle(display,window,gc,x,y,w,h)
#define DrawRectangle(x,y,w,h) XDrawRectangle(display,window,gc,x,y,w,h)
#define DrawLine(x1,y1,x2,y2)  XDrawLine(display,window,gc,x1,y1,x2,y2)
#define DrawPoint(x,y)         XDrawPoint(display,window,gc,x,y)
#define ClearValC(size,x,y)    FillRectangle((x)-(size)*4,(y)-10,(size)*8,12)
#define XCOORD(x)             ((short int)(WORLD_OFFSET_X+(x)/WORLD_INV_SCALE))
#define YCOORD(y)             ((short int)(WORLD_OFFSET_Y+(y)/WORLD_INV_SCALE))

#define FreeObject(x)          free(x)

extern struct Object *CreateObject(u_char type,short int x,short int y,
                                   double alpha);
extern void DrawUserInfo(struct Robot *robot,u_char info,u_char page);

#endif
