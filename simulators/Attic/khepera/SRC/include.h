/*****************************************************************************/
/* File:        include.h (Khepera Simulator)                                */
/* Author:      Olivier MICHEL <om@alto.unice.fr>                            */
/* Date:        Wed Feb 14 10:05:32 MET 1996                                 */
/* Description: include file (to be included by user.c)                      */
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

#ifndef INCLUDE_H
#define INCLUDE_H
#include "header.h"
#include "context.h"
#include "colors.h"
#include "robot.h"

#define X_O            603
#define Y_O            185
#define INFO_WIDTH     502
#define INFO_HEIGHT    337
#define Color(c)               XSetForeground(display,gc,color[c].pixel)
#define DrawPoint(x,y)         XDrawPoint(display,window,gc,x+X_O,y+Y_O)
#define DrawLine(x1,y1,x2,y2)  XDrawLine(display,window,gc,x1+X_O,y1+Y_O,x2+X_O,y2+Y_O)
#define DrawRectangle(x,y,w,h) XDrawRectangle(display,window,gc,x+X_O,y+Y_O,w,h)
#define FillRectangle(x,y,w,h) XFillRectangle(display,window,gc,x+X_O,y+Y_O,w,h)
#define FillArc(x,y,w,h,a,b)   XFillArc(display,window,gc,x+X_O,y+Y_O,w,h,a,b)
#define DrawArc(x,y,w,h,a,b)   XDrawArc(display,window,gc,x+X_O,y+Y_O,w,h,a,b)
#define DrawText(x,y,t)        XDrawString(display,window,gc,x+X_O,y+Y_O,t,strlen(t))
#define UndrawText(x,y,t);     {Color(GREY_69); XFillRectangle(display,window,gc,x+X_O-1,y+Y_O-10,2+strlen(t)*8,14);}
#define WriteComment(t)        DisplayComment(context,t)
#define EraseComment()         UndisplayComment(context)
#define FastRunRobot(r)        RobotRunFast(context)
#define RunRobot(r)            RobotRun(context)
#define StopCommand()          UnpressButton(context,context->Buttons)
#define ShowUserInfo(i,p)      ShowInfoUser(context,i,p)
#define GetUserInfo()          (context->Info)
#define GetUserInfoPage()      ((context->Info==0) ? context->InfoAbout + 1 : context->InfoUser[context->Info-1] + 1)
#define DrawRobot(robot)       DrawLittleRobot(robot,robot)
#define RIGHT                  0
#define LEFT                   1

extern struct Context  *context;
extern Display         *display;
extern Window          window;
extern GC              gc;
extern XColor          color[NUMBER_OF_COLORS];

extern void            DisplayComment(struct Context *c,char *text);
extern void            UndisplayComment(struct Context *c);
extern void            RobotRunFast(struct Context *c);
extern boolean         RobotRun(struct Context *c);
extern boolean         UnpressButton(struct Context *c,struct Button *b);
extern void            ShowInfoUser(struct Context *c,u_char info,u_char page);
extern void            DrawLittleRobot(struct Robot *r1,struct Robot *r2);

#endif
