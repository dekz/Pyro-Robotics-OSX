/*****************************************************************************/
/* File:        graphics.c (Khepera Simulator)                               */
/* Author:      Olivier MICHEL <om@alto.unice.fr>                            */
/* Date:        Thu Sep 21 14:39:05 1995                                     */
/* Description: X11 graphical interface                                      */
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

#include "header.h"
#include "graphics.h"
#include "robot.h"
#include "sim.h"
#include "world.h"

short int ROBOT_BASE_X = 95;
short int ROBOT_BASE_Y = 93+PLATE1_H;

Display       *display;
Window        window;
GC            gc;
XColor        color[NUMBER_OF_COLORS];
Font          font;
Cursor        pointer_cursor,wait_cursor,cancel_cursor;

void WaitCursor()
{
  XDefineCursor(display,window,wait_cursor);
  XSync(display,FALSE);
}

void PointerCursor()
{
  XDefineCursor(display,window,pointer_cursor);
  XSync(display,FALSE);
}

void CancelCursor()
{
  XDefineCursor(display,window,cancel_cursor);
  XSync(display,FALSE);
}

void DrawPlate(int x,int y,int w,int h,u_char c,u_char state)
{
  h--; w--;
  Color(c);
  FillRectangle(x+1,y+1,w-1,h-1);
  if (state == PLATE_DOWN) Color(BLACK);
  else Color(WHITE);
  DrawLine(x,y,x,y+h-1);
  DrawLine(x,y,x+w-1,y);
  if (state == PLATE_DOWN) Color(WHITE);
  else Color(BLACK);
  DrawLine(x+1,y+h,x+w,y+h);
  DrawLine(x+w,y+1,x+w,y+h);
}

void DrawObject(struct Object *object)
{
  short int x,y,w,h;
  double    alpha,dw,dh;
  XPoint    polygon[5];

  switch(object->Type)
  {
    case LAMP_OFF: Color(BLACK);
                   x = XCOORD(object->X);
                   y = YCOORD(object->Y);
                   FillRectangle(x-1,y-1,3,3);
                   Color(GREY_69);
                   DrawLine(x+4,y,x+8,y);
                   DrawLine(x-4,y,x-8,y);
                   DrawLine(x,y+4,x,y+8);
                   DrawLine(x,y-4,x,y-8);
                   DrawLine(x+4,y+4,x+6,y+6);
                   DrawLine(x-4,y-4,x-6,y-6);
                   DrawLine(x+4,y-4,x+6,y-6);
                   DrawLine(x-4,y+4,x-6,y+6);
                   break;
    case LAMP_ON:  Color(YELLOW);
                   x = XCOORD(object->X);
                   y = YCOORD(object->Y);
                   FillRectangle(x-1,y-1,3,3);
                   DrawLine(x+4,y,x+8,y);
                   DrawLine(x-4,y,x-8,y);
                   DrawLine(x,y+4,x,y+8);
                   DrawLine(x,y-4,x,y-8);
                   DrawLine(x+4,y+4,x+6,y+6);
                   DrawLine(x-4,y-4,x-6,y-6);
                   DrawLine(x+4,y-4,x+6,y-6);
                   DrawLine(x-4,y+4,x-6,y+6);
                   break;
    case BRICK: x     = XCOORD(object->X);
                y     = YCOORD(object->Y);
                dw    = (double)BRICKWidth/(WORLD_INV_SCALE*2);
                dh    = (double)BRICKHeight/(WORLD_INV_SCALE*2);
                alpha = object->Alpha;
                polygon[0].x = x + (int)floor(0.5+dh*cos(alpha))
                                 - (int)floor(0.5+dw*sin(alpha));
                polygon[0].y = y + (int)floor(0.5+dw*cos(alpha))
                                 + (int)floor(0.5+dh*sin(alpha));
                polygon[1].x = x - (int)floor(0.5+dh*cos(alpha))
                                 - (int)floor(0.5+dw*sin(alpha));
                polygon[1].y = y + (int)floor(0.5+dw*cos(alpha))
                                 - (int)floor(0.5+dh*sin(alpha));
                polygon[2].x = x - (int)floor(0.5+dh*cos(alpha))
                                 + (int)floor(0.5+dw*sin(alpha));
                polygon[2].y = y - (int)floor(0.5+dw*cos(alpha))
                                 - (int)floor(0.5+dh*sin(alpha));
                polygon[3].x = x + (int)floor(0.5+dh*cos(alpha))
                                 + (int)floor(0.5+dw*sin(alpha));
                polygon[3].y = y - (int)floor(0.5+dw*cos(alpha))
                                 + (int)floor(0.5+dh*sin(alpha));
                polygon[4].x = polygon[0].x;
                polygon[4].y = polygon[0].y;
                Color(RED);
                XFillPolygon(display,window,gc,polygon,4,Convex,
                             CoordModeOrigin);
                Color(WHITE);
                XDrawLines(display,window,gc,polygon,5,CoordModeOrigin);
                break;
    case CORK:  x     = XCOORD(object->X);
                y     = YCOORD(object->Y);
                w     = CORKWidth/WORLD_INV_SCALE;
                h     = CORKHeight/WORLD_INV_SCALE;
                x    -= w/2;
                y    -= h/2;
                Color(GOLD);
                XFillArc(display,window,gc,x,y,w,h,0,360*64);
                Color(MAROON);
                XDrawArc(display,window,gc,x,y,w,h,0,360*64);
                break;
  }
}

void DrawIntValue(long int  value,short int x,short int y)
{
  char t[16];

  if (value==-1) sprintf(t,"?"); else sprintf(t,"%d",value);
  DrawText(x,y,t);
}

void DrawPercent(double value,short int x,short int y)
{
  char t[16];

  if (value==-1.0) sprintf(t,"?"); else sprintf(t,"%lg%%",value*100);
  DrawText(x,y,t);
}

void DrawRealValue(double value,short int x,short int y)
{
  char t[16];

  if (value==-1.0) sprintf(t,"?"); else sprintf(t,"%lg",value);
  DrawText(x,y,t);
}

void DrawIntValC(int value,int x,int y)
{
  char t[16];

  if (value==-1) sprintf(t,"?"); else sprintf(t,"%d",value);
  DrawText(x-4*strlen(t),y,t);
}

void DrawRealValC(double value,short int x,short int y)
{
  char t[16];

  if (value==-1.0) sprintf(t,"?"); else sprintf(t,"%lg",value);
  DrawText(x-4*strlen(t),y,t);
}

void UpdateBehind(struct Object *object,struct World *world)
{
  if (world->BehindObject)
  {
    XPutImage(display,window,gc,world->BehindObject,0,0,
              world->BehindX,world->BehindY,40,40);
    XDestroyImage(world->BehindObject);
  }
  world->BehindX = object->X - 20;
  world->BehindY = object->Y - 20;
  world->BehindObject = XGetImage(display,window,
                                  world->BehindX,world->BehindY,
                                  40,40,255,ZPixmap);
}

void DrawConsObject(struct World *world)
{
  struct Object *object;

  Color(GREY_69);
  FillRectangle(WINDOW_W-2*WORLD_OFFSET_X-30,3,36,36);
  object = CreateObject(world->ObjectType,965,-49,
                   M_PI*(double)world->ObjectAlpha[world->ObjectType]/180.0);
  DrawObject(object);
  FreeObject(object);
}

void DrawLittleRobot(struct Robot *old_r,struct Robot *new_r)
{
  short int     x,y,i;
  double        dx,dy,cosa,sina;
/*  static XImage *back_image = NULL; */


  x = XCOORD(old_r->X) - 15;
  y = YCOORD(old_r->Y) - 15;
  Color(GREY_69);
  XFillArc(display,window,gc,x,y,30,30,0,360*64);
/*
  if (back_image)
  {
    XPutImage(display,window,gc,back_image,0,0,x,y,30,30);
    XDestroyImage(back_image);
  }
  x = XCOORD(new_r->X) - 15;
  y = YCOORD(new_r->Y) - 15;
  back_image = XGetImage(display,window,x,y,30,30,255,ZPixmap);
  x += 15;
  y += 15;
*/
  x = XCOORD(new_r->X);
  y = YCOORD(new_r->Y);
  cosa = cos(new_r->Alpha);
  sina = sin(new_r->Alpha);
  Color(LIGHT_GREY);
  XFillArc(display,window,gc,x-14,y-14,28,28,0,360*64);
  Color(WHITE);
  XDrawArc(display,window,gc,x-14,y-14,28,28,40*64,220*64);
  Color(BLACK);
  XDrawArc(display,window,gc,x-14,y-14,28,28,0,40*64);
  XDrawArc(display,window,gc,x-14,y-14,28,28,0,-140*64);
  dx = cosa*12.0;
  dy = sina*12.0;
  Color(DIM_GREY);            /* wheels */
  DrawLine(x+(short int)(dy-dx/3.2),y+(short int)(dx+dy/3.2),
           x+(short int)(dy+dx/3.2),y+(short int)(dx-dy/3.2));
  DrawLine(x-(short int)(dy+dx/3.2),y-(short int)(dx-dy/3.2),
           x-(short int)(dy-dx/3.2),y-(short int)(dx+dy/3.2));
  dx = cosa*11.1;
  dy = sina*11.1;
  DrawLine(x+(short int)(dy-dx/3.2),y+(short int)(dx+dy/3.2),
           x+(short int)(dy+dx/3.2),y+(short int)(dx-dy/3.2));
  DrawLine(x-(short int)(dy+dx/3.2),y-(short int)(dx-dy/3.2),
           x-(short int)(dy-dx/3.2),y-(short int)(dx+dy/3.2));
  Color(LIME_GREEN);       /* green point */
  FillRectangle(x+(short int)(cosa*10-sina),y-(short int)(sina*10+cosa),
                3,3);

/*         ***********************************************
 *        * Drawing of the IR sensors on the little robot *
 *         ***********************************************
 *
 * Color(BLUE);
 * for(i=0;i<8;i++)
 * {
 *   dx = new_r->IRSensor[i].X/WORLD_INV_SCALE;
 *   dy = new_r->IRSensor[i].Y/WORLD_INV_SCALE;
 *   DrawPoint(x+(short int)(dx*cosa-dy*sina),y+(short int)(dy*cosa-dx*sina));
 * }
 *
 *
 */
  XSync(display,FALSE);
}

void DrawComment(char *text)
{
  Color(GREY);
  FillRectangle(2,PLATE1_H+2,WINDOW_W-4,16);
  Color(BLUE);
  DrawText(WINDOW_W/2 - strlen(text)*7/2,PLATE1_H+16,text);
}

void DisplayComment(struct Context *context,char *text)
{
  strcpy(context->Comment,text);
  DrawComment(context->Comment);
  XSync(display,FALSE);
}

void UndisplayComment(struct Context *context)
{
  strcpy(context->Comment,"");
	DrawComment("Khepera Simulator");
  XSync(display,FALSE);
}

void DrawTextInput(char *text)
{
  Color(GREY);
  FillRectangle(WINDOW_W/3,PLATE1_H+2,318,16);
  Color(BLUE);
  DrawText(WINDOW_W/3,PLATE1_H+16,text);
}

void DrawWorldSquare(struct World *world)
{
  struct Object *object;

  DrawPlate(WORLD_OFFSET_X-2,WORLD_OFFSET_Y-2,WORLD_X+4,WORLD_Y+4,
			GREY_69,PLATE_DOWN);
  object = world->Objects;
  while (object)
  {
    DrawObject(object);
    object = object->Next;
  }
}

void DrawWorld(struct Context *context)
{
  char         text[TEXT_BUF_SIZE];
  struct World *world;
  struct Robot *robot;

  world = context->World;
  robot = context->Robot;
  strcpy(text,world->Name);
  //strcat(text,"...");
  Color(GREY);
  FillRectangle(2,2,WINDOW_W/4-4,16);
  Color(BLACK);
  DrawText(5,14,text);
  DrawWorldSquare(world);
  DrawPlate(WINDOW_W-2*WORLD_OFFSET_X-31,2,38,38,
			GREY_69,PLATE_DOWN);
  DrawConsObject(world);
  DrawLittleRobot(robot,robot);
}

void DrawObstacles(struct Context *context)
{
  struct World *world;
  short int    i,j;

  world = context->World;
  Color(BLUE);
  for(i=0;i<500;i++) for(j=0;j<500;j++)
   if (world->Image[i/32][j] & (1 << (i%32)))
    DrawPoint(i + WORLD_OFFSET_X,j + WORLD_OFFSET_Y);
}

void ScanWorld(struct Context *context)
{
  long int     i,j;
  struct World *world;
  XImage       *image;

  world = context->World;
  DrawWorldSquare(world);
  DisplayComment(context,"scanning world");
  image = XGetImage(display,window,WORLD_OFFSET_X,WORLD_OFFSET_Y,
                    500,500,255,XYPixmap);
  DisplayComment(context,"");
  for(i=0;i<16;i++) for(j=0;j<500;j++) world->Image[i][j] = (u_long)0;
  
  DisplayComment(context,"scanning point by point");
  Color(WHITE);
  for(i=0;i<500;i++) for(j=0;j<500;j++)
  {
    if (XGetPixel(image,i,j) != world->BackgroundPixel)
    {
      world->Image[i/32][j] |= (1 << (i%32));
      DrawPoint(i+WORLD_OFFSET_X,j+WORLD_OFFSET_Y);
    }
  }
  if (image) XDestroyImage(image);
  DrawWorld(context);
  DisplayComment(context,"world scanning complete");
}

void DrawButton(struct Button *but)
{
  short int x,y;
  u_char    c;

  if (but->State == PLATE_UP) {x = but->X + 3; y = but->Y + 12; c = GREY;}
            else              {x = but->X + 4; y = but->Y + 13; c = GREY_69;}
  DrawPlate(but->X,but->Y,but->Width,but->Height,c,but->State);
  Color(BLACK);
  DrawText(x,y,but->Text);
  XSync(display,FALSE);
}

void DrawRobotIRSensors(struct Robot *robot)
{
  short int i;
  double    alpha,xc,yc;
  XPoint    polygon[4];

  for(i=0;i<8;i++)
  {
    xc    = (double)ROBOT_BASE_X - robot->IRSensor[i].Y * ROBOT_SCALE;
    yc    = (double)ROBOT_BASE_Y - robot->IRSensor[i].X * ROBOT_SCALE;
    alpha = robot->IRSensor[i].Alpha + M_PI/2.0;
    polygon[0].x = (short int)(xc - (cos(alpha) - 2.0*sin(alpha))*ROBOT_SCALE);
    polygon[0].y = (short int)(yc + (2.0*cos(alpha) + sin(alpha))*ROBOT_SCALE);
    polygon[1].x = (short int)(xc - (-cos(alpha) -2.0*sin(alpha))*ROBOT_SCALE);
    polygon[1].y = (short int)(yc + (2.0*cos(alpha) - sin(alpha))*ROBOT_SCALE);
    polygon[2].x = (short int)(xc - (-cos(alpha) +2.0*sin(alpha))*ROBOT_SCALE);
    polygon[2].y = (short int)(yc + (-2.0*cos(alpha) -sin(alpha))*ROBOT_SCALE);
    polygon[3].x = (short int)(xc - (cos(alpha) + 2.0*sin(alpha))*ROBOT_SCALE);
    polygon[3].y = (short int)(yc + (-2.0*cos(alpha) +sin(alpha))*ROBOT_SCALE);
    Color(BLUE + robot->IRSensor[i].DistanceValue/114);
    XFillPolygon(display,window,gc,polygon,4,Convex,CoordModeOrigin);
    polygon[0].x=(short int)(xc-(2.0*cos(alpha)-2.0*sin(alpha))*ROBOT_SCALE);
    polygon[0].y=(short int)(yc+(2.0*cos(alpha)+2.0*sin(alpha))*ROBOT_SCALE);
    polygon[1].x=(short int)(xc-(2.0*cos(alpha)+2.0*sin(alpha))*ROBOT_SCALE);
    polygon[1].y=(short int)(yc-(2.0*cos(alpha)-2.0*sin(alpha))*ROBOT_SCALE);
    polygon[2].x=(short int)(xc-(4.0*cos(alpha)-0.0*sin(alpha))*ROBOT_SCALE);
    polygon[2].y=(short int)(yc-(0.0*cos(alpha)-4.0*sin(alpha))*ROBOT_SCALE);
    Color(RED - robot->IRSensor[i].LightValue/59);
    XFillPolygon(display,window,gc,polygon,3,Convex,CoordModeOrigin);
  }
  Color(GREY_69);
  ClearValC(4,ROBOT_BASE_X-18,ROBOT_BASE_Y-58);
  ClearValC(4,ROBOT_BASE_X+18,ROBOT_BASE_Y-58);
  ClearValC(4,ROBOT_BASE_X-51,ROBOT_BASE_Y-44);
  ClearValC(4,ROBOT_BASE_X+51,ROBOT_BASE_Y-44);
  ClearValC(4,ROBOT_BASE_X+70,ROBOT_BASE_Y-15);
  ClearValC(4,ROBOT_BASE_X-70,ROBOT_BASE_Y-15);
  ClearValC(4,ROBOT_BASE_X-20,ROBOT_BASE_Y+66);
  ClearValC(4,ROBOT_BASE_X+20,ROBOT_BASE_Y+66);
  if (robot->State & DISTANCE_SENSOR_FLAG)
  {
    Color(BLACK);
    DrawIntValC(robot->IRSensor[2].DistanceValue,
                ROBOT_BASE_X-18,ROBOT_BASE_Y-58);
    DrawIntValC(robot->IRSensor[3].DistanceValue,
                ROBOT_BASE_X+18,ROBOT_BASE_Y-58);
    DrawIntValC(robot->IRSensor[1].DistanceValue,
                ROBOT_BASE_X-51,ROBOT_BASE_Y-44);
    DrawIntValC(robot->IRSensor[4].DistanceValue,
                ROBOT_BASE_X+51,ROBOT_BASE_Y-44);
    DrawIntValC(robot->IRSensor[5].DistanceValue,
                ROBOT_BASE_X+70,ROBOT_BASE_Y-15);
    DrawIntValC(robot->IRSensor[0].DistanceValue,
                ROBOT_BASE_X-70,ROBOT_BASE_Y-15);
    DrawIntValC(robot->IRSensor[7].DistanceValue,
                ROBOT_BASE_X-20,ROBOT_BASE_Y+66);
    DrawIntValC(robot->IRSensor[6].DistanceValue,
                ROBOT_BASE_X+20,ROBOT_BASE_Y+66);
  }
  else if (robot->State & LIGHT_SENSOR_FLAG)
  {
    Color(BLUE);
    DrawIntValC(robot->IRSensor[2].LightValue,
                ROBOT_BASE_X-18,ROBOT_BASE_Y-58);
    DrawIntValC(robot->IRSensor[3].LightValue,
                ROBOT_BASE_X+18,ROBOT_BASE_Y-58);
    DrawIntValC(robot->IRSensor[1].LightValue,
                ROBOT_BASE_X-51,ROBOT_BASE_Y-44);
    DrawIntValC(robot->IRSensor[4].LightValue,
                ROBOT_BASE_X+51,ROBOT_BASE_Y-44);
    DrawIntValC(robot->IRSensor[5].LightValue,
                ROBOT_BASE_X+70,ROBOT_BASE_Y-15);
    DrawIntValC(robot->IRSensor[0].LightValue,
                ROBOT_BASE_X-70,ROBOT_BASE_Y-15);
    DrawIntValC(robot->IRSensor[7].LightValue,
                ROBOT_BASE_X-20,ROBOT_BASE_Y+66);
    DrawIntValC(robot->IRSensor[6].LightValue,
                ROBOT_BASE_X+20,ROBOT_BASE_Y+66);
  }
}

void DrawRobotPlate()
{
  Color(LIGHT_GREY);
  XFillArc(display,window,gc,
           ROBOT_BASE_X-(short int)(ROBOT_SCALE*ROBOT_DIAMETER/2),
           ROBOT_BASE_Y-(short int)(ROBOT_SCALE*ROBOT_DIAMETER/2),
           (short int)(ROBOT_SCALE*ROBOT_DIAMETER),
           (short int)(ROBOT_SCALE*ROBOT_DIAMETER),0,360*64);
  Color(WHITE);
  XDrawArc(display,window,gc,
           ROBOT_BASE_X-(short int)(ROBOT_SCALE*ROBOT_DIAMETER/2),
           ROBOT_BASE_Y-(short int)(ROBOT_SCALE*ROBOT_DIAMETER/2),
           (short int)(ROBOT_SCALE*ROBOT_DIAMETER),
           (short int)(ROBOT_SCALE*ROBOT_DIAMETER),40*64,220*64);
  Color(BLACK);
  XDrawArc(display,window,gc,
           ROBOT_BASE_X-(short int)(ROBOT_SCALE*ROBOT_DIAMETER/2),
           ROBOT_BASE_Y-(short int)(ROBOT_SCALE*ROBOT_DIAMETER/2),
           (short int)(ROBOT_SCALE*ROBOT_DIAMETER),
           (short int)(ROBOT_SCALE*ROBOT_DIAMETER),0,40*64);
  XDrawArc(display,window,gc,
           ROBOT_BASE_X-(short int)(ROBOT_SCALE*ROBOT_DIAMETER/2),
           ROBOT_BASE_Y-(short int)(ROBOT_SCALE*ROBOT_DIAMETER/2),
           (short int)(ROBOT_SCALE*ROBOT_DIAMETER),
           (short int)(ROBOT_SCALE*ROBOT_DIAMETER),0,-140*64);
}

void DrawMotorActivity(short int x,short int activity)
{
  Color(GREY);
  FillRectangle(x-3,ROBOT_BASE_Y-10,7,21);
  if (activity)
  {
    Color(RED);
    DrawLine(x,ROBOT_BASE_Y - activity,
             x,ROBOT_BASE_Y + activity);
    if (activity>0)
    {
      DrawLine(x,ROBOT_BASE_Y - activity,x+3, ROBOT_BASE_Y+4 - activity);
      DrawLine(x,ROBOT_BASE_Y - activity,x-3, ROBOT_BASE_Y+4 - activity);
    }
    else
    {
      DrawLine(x,ROBOT_BASE_Y - activity,x+3,ROBOT_BASE_Y-4 - activity);
      DrawLine(x,ROBOT_BASE_Y - activity,x-3,ROBOT_BASE_Y-4 - activity);
    }
  }
}

void DrawRobotEffectors(struct Robot *robot)
{
  char t[16];

  DrawMotorActivity((short int)(ROBOT_BASE_X+ROBOT_DIAMETER*ROBOT_SCALE/3.6),
                    robot->Motor[0].Value);
  DrawMotorActivity((short int)(ROBOT_BASE_X-ROBOT_DIAMETER*ROBOT_SCALE/3.6),
                    robot->Motor[1].Value);
  Color(LIGHT_GREY);
  ClearValC(3,ROBOT_BASE_X+30,ROBOT_BASE_Y+24);
  ClearValC(3,ROBOT_BASE_X-30,ROBOT_BASE_Y+24);
  if (robot->State & MOTOR_VALUES_FLAG)
  {
    Color(BLACK);
    sprintf(t,"%d",robot->Motor[0].Value);
    DrawText(ROBOT_BASE_X+30-4*strlen(t),ROBOT_BASE_Y+24,t);
    sprintf(t,"%d",robot->Motor[1].Value);
    DrawText(ROBOT_BASE_X-30-4*strlen(t),ROBOT_BASE_Y+24,t);
  }
}

void DrawRobotBase(struct Robot *robot)
{
  XPoint    polygon[7];

  DrawRobotPlate();
  DrawLine(ROBOT_BASE_X-(short int)(ROBOT_SCALE*(ROBOT_WHEEL_BASE/2-15)),
           ROBOT_BASE_Y,
           ROBOT_BASE_X-(short int)(ROBOT_SCALE*ROBOT_WHEEL_BASE/2),
           ROBOT_BASE_Y);
  DrawLine(ROBOT_BASE_X+(short int)(ROBOT_SCALE*(ROBOT_WHEEL_BASE/2-15)),
           ROBOT_BASE_Y,
           ROBOT_BASE_X+(short int)(ROBOT_SCALE*ROBOT_WHEEL_BASE/2),
           ROBOT_BASE_Y);
  Color(DIM_GREY);
  FillRectangle(ROBOT_BASE_X-((short int)(ROBOT_SCALE*(ROBOT_WHEEL_BASE/2+1))),
                ROBOT_BASE_Y-(short int)(ROBOT_SCALE*WHEEL_DIAMETER/2),
                (short int)(ROBOT_SCALE*2),
                (short int)(ROBOT_SCALE*WHEEL_DIAMETER));
  FillRectangle(ROBOT_BASE_X+((short int)(ROBOT_SCALE*(ROBOT_WHEEL_BASE/2-1))),
                ROBOT_BASE_Y-(short int)(ROBOT_SCALE*WHEEL_DIAMETER/2),
                (short int)(ROBOT_SCALE*2),
                (short int)(ROBOT_SCALE*WHEEL_DIAMETER));

  DrawPlate(ROBOT_BASE_X-(short int)(ROBOT_SCALE*ROBOT_WHEEL_BASE*7/16),
            ROBOT_BASE_Y-(short int)(ROBOT_SCALE*ROBOT_WHEEL_BASE/8),
            (short int)(ROBOT_SCALE*ROBOT_WHEEL_BASE/4),
            (short int)(ROBOT_SCALE*ROBOT_WHEEL_BASE/4),GREY,PLATE_UP);
  DrawPlate(ROBOT_BASE_X+(short int)(ROBOT_SCALE*ROBOT_WHEEL_BASE*3/16),
            ROBOT_BASE_Y-(short int)(ROBOT_SCALE*ROBOT_WHEEL_BASE/8),
            (short int)(ROBOT_SCALE*ROBOT_WHEEL_BASE/4),
            (short int)(ROBOT_SCALE*ROBOT_WHEEL_BASE/4),GREY,PLATE_UP);
  Color(LIME_GREEN);
  XFillArc(display,window,gc,
           ROBOT_BASE_X-(short int)(0.047*ROBOT_DIAMETER*ROBOT_SCALE),
           ROBOT_BASE_Y-(short int)(0.41*ROBOT_DIAMETER*ROBOT_SCALE),
           (short int)(0.095*ROBOT_DIAMETER*ROBOT_SCALE),
           (short int)(0.095*ROBOT_DIAMETER*ROBOT_SCALE),
           0,360*64);
  DrawRobotIRSensors(robot);
  DrawRobotEffectors(robot);
}

/* This is for future expansion... */
/*
void UndrawRobotGripper(x,y)
short int x,y;
{
  Color(GREY);
  FillRectangle(x-(short int)(ROBOT_SCALE*35),y-(short int)(ROBOT_SCALE*60),
                (short int)(ROBOT_SCALE*70),(short int)(ROBOT_SCALE*90));
}

void DrawRobotGripper(robot,x,y)
struct Robot *robot;
short int x,y;
{
  XPoint polygon[19];
  double coef,space;

  coef  = (double)cos((double)robot->Gripper.Position*M_PI/180.0);
  space = (double)robot->Gripper.ObjectSize/20.0;
  DrawRobotPlate(x,y);
  DrawPlate(x-(short int)(ROBOT_SCALE*ROBOT_DIAMETER/2),
            y+(short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2-16)),
            (short int)(ROBOT_SCALE*ROBOT_DIAMETER),
            (short int)(ROBOT_SCALE*12),LIGHT_GREY,PLATE_UP);
  polygon[0].x = x + (short int)(ROBOT_SCALE*(1 + ROBOT_DIAMETER/2));
  polygon[0].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 - 10 + 6*coef));
  polygon[1].x = x + (short int)(ROBOT_SCALE*(7 + ROBOT_DIAMETER/2));
  polygon[1].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 - 10 + 6*coef));
  polygon[2].x = x + (short int)(ROBOT_SCALE*(7 + ROBOT_DIAMETER/2));
  polygon[2].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -10 -53*coef));
  polygon[3].x = x + (short int)(ROBOT_SCALE*(space+2));
  polygon[3].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -10 -53*coef));
  polygon[4].x = x + (short int)(ROBOT_SCALE*(space+2));
  polygon[4].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -10 -73*coef));
  polygon[5].x = x + (short int)(ROBOT_SCALE*space);
  polygon[5].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -10 -73*coef));
  polygon[6].x = x + (short int)(ROBOT_SCALE*space);
  polygon[6].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -10 -53*coef));
  polygon[7].x = x - (short int)(ROBOT_SCALE*space);
  polygon[7].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -10 -53*coef));
  polygon[8].x = x - (short int)(ROBOT_SCALE*space);
  polygon[8].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -10 -73*coef));
  polygon[9].x = x - (short int)(ROBOT_SCALE*(space+2));
  polygon[9].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -10 -73*coef));
  polygon[10].x = x - (short int)(ROBOT_SCALE*(space+2));
  polygon[10].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -10 -53*coef));
  polygon[11].x = x - (short int)(ROBOT_SCALE*(7 + ROBOT_DIAMETER/2));
  polygon[11].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -10 -53*coef));
  polygon[12].x = x - (short int)(ROBOT_SCALE*(7 + ROBOT_DIAMETER/2));
  polygon[12].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 - 10 +6*coef));
  polygon[13].x = x - (short int)(ROBOT_SCALE*(1 + ROBOT_DIAMETER/2));
  polygon[13].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 - 10 +6*coef));
  polygon[14].x = x - (short int)(ROBOT_SCALE*(1 + ROBOT_DIAMETER/2));
  polygon[14].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -10 -39*coef));
  polygon[15].x = x - (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 - 7));
  polygon[15].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -10 -47*coef));
  polygon[16].x = x + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 - 7));
  polygon[16].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -10 -47*coef));
  polygon[17].x = x + (short int)(ROBOT_SCALE*(1 + ROBOT_DIAMETER/2));
  polygon[17].y = y + (short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -10 -39*coef));
  polygon[18].x = polygon[0].x;
  polygon[18].y = polygon[0].y;

  Color(LIGHT_GREY);
  XFillPolygon(display,window,gc,polygon,18,Nonconvex,CoordModeOrigin);
  Color(BLACK);
  XDrawLines(display,window,gc,polygon,19,CoordModeOrigin);
  DrawBox(x-(short int)(ROBOT_SCALE*ROBOT_DIAMETER/2.1),
             y+(short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 - 15)),BLUE);
  DrawBox(x-(short int)(ROBOT_SCALE*ROBOT_DIAMETER/2.1),
             y+(short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 - 10)),BLUE);
  DrawSensor(x-(short int)(ROBOT_SCALE*ROBOT_DIAMETER/3),
             y+(short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -9)),BLUE);
  DrawBox(x-4,
             y+(short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 - 15)),BLUE);
  DrawBox(x-4,
             y+(short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 - 10)),BLUE);
  DrawSensor(x-(short int)(ROBOT_SCALE*ROBOT_DIAMETER/6),
             y+(short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -9)),BLUE);
  DrawSensor(x+(short int)(ROBOT_SCALE*ROBOT_DIAMETER/5.5),
             y+(short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -9)),BLUE);
  DrawSensor(x+(short int)(ROBOT_SCALE*ROBOT_DIAMETER/2.6),
             y+(short int)(ROBOT_SCALE*(ROBOT_DIAMETER/2 -9)),BLUE);
}

void DrawRobotVision(robot,x,y)
struct Robot *robot;
short int x,y;
{
  DrawRobotPlate(x,y);
  Color(BLACK);
  XSetBackground(display,gc,color[LIGHT_GREY].pixel);
  DrawText(x-52,y+4,"VISION MODULE");
  XSetBackground(display,gc,color[GREY].pixel);
}
*/

void DrawRobotToggleButtons(struct Robot *robot)
{
  Color(GREY_69);
  FillRectangle(299,PLATE1_H+44,180,41);
  Color(BLACK);
  //if (robot->State & REAL_ROBOT_FLAG)
  // DrawText(WINDOW_W/2+236,54,"real Khepera");
  //else DrawText(WINDOW_W/2+236,54,"simulated Khepera");
  if (robot->State & DISTANCE_SENSOR_FLAG)
   DrawText(300,PLATE1_H+64,"distance sensor values");
  else if (robot->State & LIGHT_SENSOR_FLAG)
   DrawText(300,PLATE1_H+64,"light sensor values");
  else DrawText(300,PLATE1_H+64,"sensor activities");
  if (robot->State & MOTOR_VALUES_FLAG)
   DrawText(300,PLATE1_H+84,"motor values");
  else DrawText(300,PLATE1_H+84,"motor activities");
}

void DrawRobotLegend(struct Robot *robot)
{
  int i;

  Color(BLACK);
  DrawText(310,PLATE1_H+130,"Activity");
  DrawText(220,PLATE1_H+146,"Low");
  DrawText(430,PLATE1_H+146,"High");
  for(i=0;i<9;i++)
   DrawPlate(250+i*20,PLATE1_H+136,10,10,BLUE+i,PLATE_UP);
}

void DrawRobot(struct Context *context)
{
  char      title[22];
  short int i;
  struct Robot *robot;
  struct Button *but;

  robot = context->Robot;
  Color(GREY);
//  FillRectangle(2,PLATE1_H+2,WINDOW_W-4,16);
  Color(BLACK);
  strcpy(title,robot->Name);
  strcat(title,".robot");
  //DrawText(WINDOW_W/4-4*strlen(title),PLATE1_H+14,title);
  DrawPlate(5,PLATE1_H+22,WINDOW_W-10,142,GREY_69,PLATE_DOWN);
  DrawRobotBase(robot);
  DrawRobotLegend(robot);
  DrawRobotToggleButtons(robot);
  but = context->Buttons;
  while(but)
  {
    if (but->Text[0]=='>') DrawButton(but);
    but = but->Next;
  }
}

void DrawInfoAbout(struct Context *context)
{
  switch(context->InfoAbout)
  {
    case 0: Color(BLUE);
            DrawRectangle(783,198,141,16);
            Color(YELLOW);
            DrawText(WINDOW_W*3/4-4*17,210,"Khepera Simluator");
            Color(BLACK);
            DrawText(630,270,
                  "This program is a simulator for Khepera robot featuring:");
            DrawText(630,290,"- A simulated Khepera robot");
            DrawText(630,305,"- A world editor");
            DrawText(630,320,"- A graphical user interface");
            DrawText(630,335,"- C programming facilities");
            DrawText(630,365,
            "This software is provided for the Official Khepera Contest");
            DrawText(630,380,
            "at  Evolution   Artificielle  conference   (Nimes,  1997).");
            DrawText(630,395,
            "It is public domain,  for research  and teaching purposes.");
            DrawText(630,410,
            "Commercial use  is  forbidden.  You can download it  from:");
            DrawText(630,425,"http://alto.unice.fr/~om/khep-contest.html");
            DrawText(630,460,
            "Author: Olivier MICHEL, MAGE team, i3s laboratory,");
            DrawText(630,475,
            "CNRS, University of Nice - Sophia Antipolis, FRANCE");
            DrawText(630,490,
            "om@alto.unice.fr, http://alto.unice.fr/~om/homepage.html");
            break;
    case 1: Color(BLUE);
            DrawRectangle(767,198,173,16);
            Color(YELLOW);
            DrawText(855-4*21,210,"Khepera: presentation");
            Color(BLACK);
            DrawText(680,250,
            "Khepera  is a  real  miniature  mobile  robot");
            DrawText(680,270,
            "developed  at the  LAMI (EPFL,  Lausanne)  by");
            DrawText(680,290,
            "Edo Franzi, Andre Guignard, Francesco Mondada");
            DrawText(680,310,
            "(K-Team).  It has eight  infra-red  proximity");
            DrawText(680,330,
            "and  light   sensors   allowing  it   to  see");
            DrawText(680,350,
            "obstacles and  light sources.  Two motors are");
            DrawText(680,370,
            "controlling the wheels. The robot has its own");
            DrawText(680,390,
            "batteries, processor and memory so that it is");
            DrawText(680,410,
            "really   autonomous .    Expansion    modules");
            DrawText(680,430,
            "(gripper, vision) can be  added to the robot.");
            DrawText(680,470,
            "More can be found on the Internet web at URL:");
            DrawText(736,490,
            "http://lamiwww.epfl.ch/Khepera/");
            break;
    case 2: Color(BLUE);
            DrawRectangle(779,198,149,16);
            Color(YELLOW);
            DrawText(855-4*18,210,"Khepera: simulator");
            Color(BLACK);
            DrawText(680,270,
            "The  simulator  includes  all the features of");
            DrawText(680,290,
            "the basic module  of Khepera  (IR sensors and");
            DrawText(680,310,
            "motors). For each IR sensor, the color of the");
            DrawText(680,330,
            "rectangle  indicates the excitation  relative");
            DrawText(680,350,
            "to the distance measure  and the color of the");
            DrawText(680,370,
            "triangle indicates the ambiant light measure.");
            DrawText(680,390,
            "Motors activity  is displayed  by  red arrows");
            DrawText(680,410,
            "appearing on each motor.");
            DrawText(680,430,
            "The simulator is provided for Khepera Contest");
            DrawText(680,470,
            "More can be found on the Internet web at URL:");
            DrawText(692,490,
            "http://alto.unice.fr/~om/khep-contest.html");
            break;
  }
}

void DrawPageNumber(int x,int y)
{
  char text[16];
  sprintf(text,"%d/%d",x,y);
  Color(BLACK);
  DrawText(1104-strlen(text)*8,520,text);
}

void DrawInfo(struct Context *context)
{
  DrawPlate(WINDOW_W/2+32,184,504,340,GREY_69,PLATE_DOWN);
  if (context->Comment[0]) DrawComment(context->Comment);
   else UndisplayComment(context);
  switch(context->Info)
  {
    case INFO_ABOUT:     DrawPageNumber(context->InfoAbout + 1,3);
                         DrawInfoAbout(context);
                         break;
    case INFO_USER0:     DrawPageNumber(context->InfoUser[0] + 1,
                                        context->UserInfo->Pages[0]);
                         DrawUserInfo(context->Robot,1,context->InfoUser[0]+1);
                         break;
    case INFO_USER1:     DrawPageNumber(context->InfoUser[1] + 1,
                                        context->UserInfo->Pages[1]);
                         DrawUserInfo(context->Robot,2,context->InfoUser[1]+1);
                         break;
    case INFO_USER2:     DrawPageNumber(context->InfoUser[2] + 1,
                                        context->UserInfo->Pages[2]);
                         DrawUserInfo(context->Robot,3,context->InfoUser[2]+1);
                         break;
    case INFO_USER3:     DrawPageNumber(context->InfoUser[3] + 1,
                                        context->UserInfo->Pages[3]);
                         DrawUserInfo(context->Robot,4,context->InfoUser[3]+1);
                         break;
  }
}

void DrawWindow(struct Context *context)
{
  struct Button *but;
  struct Robot  *robot;

  XSync(display,TRUE);
  robot = context->Robot;
  DrawPlate(0,0,WINDOW_W,PLATE1_H,GREY,PLATE_UP);
  DrawWorld(context);
  DrawLittleRobot(robot,robot);
  DrawPlate(0,PLATE1_H,WINDOW_W,WINDOW_H-PLATE1_H,GREY,PLATE_UP);
 DrawRobot(context);
 // DrawInfo(context);
  but = context->Buttons;;
  while(but)
  {
    DrawButton(but);
    but = but->Next;
  }
  XSync(display,FALSE);
}

void RefreshWindow(struct Context *context)
{
  XEvent report;
  u_char redraw = FALSE;

  while (XPending(display))
  {
    XNextEvent(display,&report);
    if (report.type == Expose) redraw = TRUE;
  }
  if (redraw == TRUE) DrawWindow(context);
}

void ShowInfoUser(struct Context *context,u_char info,u_char page)
{
  if ((context->UserInfo->Info >= info) && (info >= 1))
  if ((context->UserInfo->Pages[info-1] >= page) && (page >= 1))
  {
    context->Info = info;
    context->InfoUser[info - 1] = page - 1;
  }
  UndisplayComment(context);
  DrawInfo(context);
}

struct Object *AddObjectInWorld(struct Context *context,
                                struct Button *cancelbutton)
{
  XEvent               report;
  static struct Object obj;
  static short int     mouse_x = 0,mouse_y = 0;
  static u_char        okay = FALSE;
  u_char               redraw,end,cancel,pointer_move;
  char                 text[16];
  struct World         *world;

  world = context->World;
  obj.Type  = world->ObjectType;
  obj.Alpha = (M_PI*(double)(world->ObjectAlpha[world->ObjectType]))/180.0;
  obj.Next  = NULL;
  end = FALSE;
  cancel = FALSE;
  CancelCursor();
  while(end == FALSE)
  {
    redraw = FALSE;
    pointer_move = FALSE;
    while (XPending(display))
    {
      XNextEvent(display,&report);
      switch(report.type)
      {
        case Expose:
         redraw = TRUE;
         break;
        case ButtonPress:
         if (okay == TRUE) end = TRUE;
         break;
        case ButtonRelease:
         if (report.xbutton.button == Button1)
         {
           if ((mouse_x >= cancelbutton->X)&&
               (mouse_x <  cancelbutton->X + cancelbutton->Width)&&
               (mouse_y >= cancelbutton->Y)&&
               (mouse_y <  cancelbutton->Y + cancelbutton->Height))
           {
             cancel = TRUE;
             okay   = FALSE;
             end    = TRUE;
           }
         }
         break;
        case MotionNotify:
         pointer_move = TRUE;
         break;
      }
    }
    if (redraw) DrawWindow(context);
    if (pointer_move)
    {
      mouse_x = report.xbutton.x;
      mouse_y = report.xbutton.y;
      if ((mouse_x >= WORLD_OFFSET_X)&&
          (mouse_x < 500 + WORLD_OFFSET_X)&&
          (mouse_y >= WORLD_OFFSET_Y)&&
          (mouse_y < 500 + WORLD_OFFSET_Y))
      {
        obj.X = mouse_x;
        obj.Y = mouse_y;
        UpdateBehind(&obj,world);
        obj.X -= WORLD_OFFSET_X;
        obj.Y -= WORLD_OFFSET_Y;
        obj.X *=WORLD_INV_SCALE;
        obj.Y *=WORLD_INV_SCALE;
        DrawObject(&obj);
        sprintf(text,"(%d,%d)",obj.X,obj.Y);
        DisplayComment(context,text);
        okay = TRUE;
      }
      else
      {
        DisplayComment(context,"click in the world !");
        okay = FALSE;
      }
    }
  }
  if (world->BehindObject)
  {
    XPutImage(display,window,gc,world->BehindObject,0,0,
              world->BehindX,world->BehindY,40,40);
    XDestroyImage(world->BehindObject);
    world->BehindObject = NULL;
  }
  PointerCursor();
  if (cancel) return(NULL); else return(&obj);
}



XPoint *ClickInWorld(struct Context *context,struct Button *cancelbutton)
{
  XEvent               report;
  static XPoint        ret;
  static short int     mouse_x = 0,mouse_y = 0;
  static u_char        okay = FALSE;
  u_char               redraw,end,pointer_motion;
  char                 text[16];

  end = FALSE;
  CancelCursor();
  while(end == FALSE)
  {
    redraw = FALSE;
    pointer_motion = FALSE;
    while (XPending(display))
    {
      XNextEvent(display,&report);
      switch(report.type)
      {
        case Expose:
         redraw = TRUE;
         break;
       case ButtonPress:
         break;
        case ButtonRelease:
         if (report.xbutton.button == Button1)
         {
           if ((mouse_x >= cancelbutton->X)&&
               (mouse_x <  cancelbutton->X + cancelbutton->Width)&&
               (mouse_y >= cancelbutton->Y)&&
               (mouse_y <  cancelbutton->Y + cancelbutton->Height))
           {
             ret.x = -1;
             okay = FALSE;
             end  = TRUE;
           }
           else if (okay == TRUE) end = TRUE;
         }
         break;
        case MotionNotify:
         pointer_motion = TRUE;
         break;
      }
    }
    if (redraw) DrawWindow(context);
    if (pointer_motion)
    {
      mouse_x = report.xbutton.x;
      mouse_y = report.xbutton.y;
      if ((mouse_x>=WORLD_OFFSET_X)&&
          (mouse_x< 500 + WORLD_OFFSET_X)&&
          (mouse_y>=WORLD_OFFSET_Y)&&
          (mouse_y< 500 + WORLD_OFFSET_Y))
      {
        ret.x = mouse_x - WORLD_OFFSET_X;
        ret.y = mouse_y - WORLD_OFFSET_Y;
        ret.x *=WORLD_INV_SCALE;
        ret.y *=WORLD_INV_SCALE;
        sprintf(text,"(%d,%d)",ret.x,ret.y);
        DisplayComment(context,text);
        okay = TRUE;
      }
      else
      {
        DisplayComment(context,"click in the world !");
        okay = FALSE;
      }
    }
  }
  PointerCursor();
  return(&ret);
}

XPoint *WaitForClic(struct Context *context,struct Button *cancelbutton)
{
  XEvent               report;
  static XPoint        ret;
  int                  mouse_x,mouse_y;
  u_char               redraw;

  CancelCursor();
  ret.x = -2;
  while(ret.x == -2)
  {
    redraw = FALSE;
    while (XPending(display))
    {
      XNextEvent(display,&report);
      switch(report.type)
      {
        case Expose:
         redraw = TRUE;
         break;
        case ButtonPress:
         if (report.xbutton.button == Button1)
         {
           ret.x = report.xbutton.x;
           ret.y = report.xbutton.y;
         }
         break;
        case ButtonRelease:
         if (report.xbutton.button == Button1)
         {
           mouse_x = report.xbutton.x;
           mouse_y = report.xbutton.y;
           if ((mouse_x >= cancelbutton->X)&&
               (mouse_x <  cancelbutton->X + cancelbutton->Width)&&
               (mouse_y >= cancelbutton->Y)&&
               (mouse_y <  cancelbutton->Y + cancelbutton->Height)) ret.x = -1;
         }
         break;
      }
    }
    if (redraw == TRUE) DrawWindow(context);
  }
  PointerCursor();
  return(&ret);
}

struct Button *PressButton(struct Context *context)
{
  XEvent               report;
  int                  mouse_x,mouse_y;
  struct Button        *but,*ret=NULL;
  static struct Button *pressed_but=NULL;
  static struct Button button;
  u_char               redraw = FALSE;

  while (ret==NULL)
  {
    XNextEvent(display,&report);
    //printf("report.type: %d\n", report.type);
    switch(report.type)
    {
      case Expose:
       redraw = TRUE;
       break;
      case ButtonPress:
       if (report.xbutton.button == Button1)
       {
         mouse_x = report.xbutton.x;
         mouse_y = report.xbutton.y;
         but = context->Buttons;
         while(but)
         {
           if ((mouse_x >= but->X)&&(mouse_x < but->X + but->Width)&&
               (mouse_y >= but->Y)&&(mouse_y < but->Y + but->Height))
           {
             but->State = PLATE_DOWN;
             DrawButton(but);
             pressed_but = but;
           }
           but = but->Next;
         }
       }
       break;
      case ButtonRelease:
       if ((report.xbutton.button == Button1)&&(pressed_but))
       {
         mouse_x = report.xbutton.x;
         mouse_y = report.xbutton.y;
         but = pressed_but;
         pressed_but = NULL;
         if (but->State == PLATE_DOWN)
          if ((mouse_x >= but->X)&&(mouse_x < but->X + but->Width)&&
              (mouse_y >= but->Y)&&(mouse_y < but->Y + but->Height)) ret = but;
          else
          {
            but->State = PLATE_UP;
            DrawButton(but);
          }
       }
       break;
      case MotionNotify:
       if (pressed_but)
       {
         mouse_x = report.xmotion.x;
         mouse_y = report.xmotion.y;
         but = pressed_but;
         if (but->State == PLATE_DOWN)
         {
           if (!((mouse_x >= but->X)&&(mouse_x < but->X + but->Width)&&
                 (mouse_y >= but->Y)&&(mouse_y < but->Y + but->Height)))
           {
             but->State = PLATE_UP;
             DrawButton(but);
           }
         }
         else
         {
           if ((mouse_x >= but->X)&&(mouse_x < but->X + but->Width)&&
                (mouse_y >= but->Y)&&(mouse_y < but->Y + but->Height))
           {
             but->State = PLATE_DOWN;
             DrawButton(but);
           }
         }
       }
       break;
    }
    if (redraw == TRUE)
    {
      DrawWindow(context);
      redraw = FALSE;
    }
  }
  return(ret);
}

boolean UnpressButton(struct Context *context,struct Button *cancelbutton, 
		      struct Robot *robot)
{
  XEvent               report;
  int                  mouse_x,mouse_y;
  u_char               ret,redraw=FALSE;

  ret = FALSE;
  while (XPending(display))
  {
    XNextEvent(display,&report);
    //printf("unpress report.type: %d\n", report.type);
    switch(report.type)
    {
    case Expose:
      redraw = TRUE;
      break;
    case ButtonRelease:
      if (report.xbutton.button == Button1) {
	mouse_x = report.xbutton.x;
	mouse_y = report.xbutton.y;
	if ((mouse_x >= cancelbutton->X)&&
	    (mouse_x <  cancelbutton->X + cancelbutton->Width)&&
	    (mouse_y >= cancelbutton->Y)&&
	    (mouse_y <  cancelbutton->Y + cancelbutton->Height)) ret = TRUE;
      }
      break;
    case ButtonPress:
      //case ButtonRelease:
      mouse_x = report.xbutton.x;
      mouse_y = report.xbutton.y;
      if ((mouse_x>=WORLD_OFFSET_X)&&
          (mouse_x< 500 + WORLD_OFFSET_X)&&
          (mouse_y>=WORLD_OFFSET_Y)&&
          (mouse_y< 500 + WORLD_OFFSET_Y))
	{
	  robot->X = mouse_x - WORLD_OFFSET_X;
	  robot->Y = mouse_y - WORLD_OFFSET_Y;
	  robot->X *= WORLD_INV_SCALE;
	  robot->Y *= WORLD_INV_SCALE;
	  DrawWorld(context);
	  if (!(robot->State & REAL_ROBOT_FLAG)) InitSensors(context);
	  DrawRobotIRSensors(robot);
	}
    } 
  }
  if (redraw == TRUE) DrawWindow(context);
  return(ret);
}

char *ReadText(struct Context *context,char *text,
               struct Button *cancelbutton)
{
  XEvent               report;
  KeySym               keysym;
  XComposeStatus       compose;
  char                 buffer[TEXT_BUF_SIZE],*ret;
  static char          answer[TEXT_BUF_SIZE];
  int                  mouse_x,mouse_y,i;
  u_char               redraw;

  for(i=0;i<16;i++) buffer[i]='\0';
  CancelCursor();
  ret = NULL;
  strcpy(context->TextInput,"_");
  DisplayComment(context,text);
  DrawTextInput(context->TextInput);
  while(ret == NULL)
  {
    redraw = FALSE;
    while (XPending(display))
    {
      XNextEvent(display,&report);
      switch(report.type)
      {
        case Expose:
         redraw = TRUE;
         break;
        case ButtonRelease:
         if (report.xbutton.button == Button1)
         {
           mouse_x = report.xbutton.x;
           mouse_y = report.xbutton.y;
           if ((mouse_x >= cancelbutton->X)&&
               (mouse_x <  cancelbutton->X + cancelbutton->Width)&&
               (mouse_y >= cancelbutton->Y)&&
               (mouse_y <  cancelbutton->Y + cancelbutton->Height))
           {
             answer[0]='\0';
             context->TextInput[0]='\0';
             DrawTextInput(context->TextInput);
             ret = answer;
           }
         }
         break;
        case KeyPress:
         context->TextInput[strlen(context->TextInput)-1]='\0';
         XLookupString((XKeyEvent *)&report,buffer,TEXT_BUF_SIZE,
                       &keysym,&compose);
         if ((keysym==XK_Return)||(keysym==XK_KP_Enter)||(keysym==XK_Linefeed))
         {
           strcpy(answer,context->TextInput);
           context->TextInput[0]='\0';
           DrawTextInput(context->TextInput);
           ret = answer;
         }
         else
         {
            if (((keysym>=XK_KP_Space)&&(keysym<=XK_KP_9))||
                ((keysym>=XK_space)&&(keysym<=XK_asciitilde)))
            if ((strlen(context->TextInput)+strlen(buffer))>=39)
             XBell(display,0);
            else
            {
              context->TextInput[strlen(context->TextInput)+1] = '\0';
              context->TextInput[strlen(context->TextInput)]=buffer[0];
            }
           else if ((keysym >= XK_Shift_L) && (keysym <= XK_Hyper_R));
           else if ((keysym == XK_BackSpace) || (keysym == XK_Delete))
            if (strlen(context->TextInput)>0)
             context->TextInput[strlen(context->TextInput)-1]=0;
            else XBell(display,0);
           strcat(context->TextInput,"_");
           DrawTextInput(context->TextInput);
         }
         break;
       }
    }
    if (redraw == TRUE)
    {
      DrawWindow(context);
      DrawTextInput(context->TextInput);
    }
  }
  PointerCursor();
  return(ret);
}

struct Button *GetButton(struct Context *context,int number)
{
  struct Button *but;
  int           i;

  but = context->Buttons;
  for(i=0;i<number;i++) but=but->Next;
  return(but);
}

void FreeButtons(struct Context *context)
{
  struct Button *but,*next;

  but = context->Buttons;
  while(but)
  {
    next = but->Next;
    free(but->Text);
    free(but);
    but = next;
  }
}

struct Button *CreateButton(u_char value,char *text,int x,int y)
{
  struct Button *but;

  but         = (struct Button *)malloc(sizeof(struct Button));
  but->Value  = value;
  but->X      = x;    // - 4 - strlen(text)*4;
  but->Y      = y;
  but->Text   = (char *)malloc(TEXT_BUF_SIZE);
  but->Width  = strlen(text)*7 + 6;
  but->Height = 16;
  but->State  = FALSE;
  but->Next   = NULL;
  strcpy(but->Text,text);
  return(but);
}

void OpenGraphics(struct Context *context)
{
  u_char   i;
  Colormap map;
  char     *disp = NULL;
  XColor   exact;
  int c;

  if (!(display = XOpenDisplay(disp)))
  {
    perror("Cannot open display\n");
    exit(-1);
  }

  map = XDefaultColormap(display,DefaultScreen(display));
  
  if (context->MonoDisplay)
  {
    XAllocNamedColor(display,map,"black",&color[BLACK],&exact);
    XAllocNamedColor(display,map,"black",&color[DIM_GREY],&exact);
    XAllocNamedColor(display,map,"white",&color[GREY_69],&exact);
    context->World->BackgroundPixel = exact.pixel;
    XAllocNamedColor(display,map,"white",&color[GREY],&exact);
    XAllocNamedColor(display,map,"white",&color[LIGHT_GREY],&exact);
    XAllocNamedColor(display,map,"black",&color[WHITE],&exact);
    XAllocNamedColor(display,map,"black",&color[RED],&exact);
    XAllocNamedColor(display,map,"black",&color[GREEN],&exact);
    XAllocNamedColor(display,map,"black",&color[BLUE],&exact);
    XAllocNamedColor(display,map,"black",&color[CYAN],&exact);
    XAllocNamedColor(display,map,"black",&color[MAGENTA],&exact);
    XAllocNamedColor(display,map,"black",&color[YELLOW],&exact);
    XAllocNamedColor(display,map,"black",&color[LIME_GREEN],&exact);  
    XAllocNamedColor(display,map,"black",&color[BLUE_CYAN],&exact);
    XAllocNamedColor(display,map,"black",&color[CYAN_GREEN],&exact);
    XAllocNamedColor(display,map,"black",&color[GREEN_YELLOW],&exact);
    XAllocNamedColor(display,map,"black",&color[YELLOW_RED],&exact);
    XAllocNamedColor(display,map,"black",&color[BROWN],&exact);
    XAllocNamedColor(display,map,"black",&color[MAROON],&exact);
    XAllocNamedColor(display,map,"black",&color[GOLD],&exact);
    XAllocNamedColor(display,map,"black",&color[AQUAMARINE],&exact);
    XAllocNamedColor(display,map,"black",&color[FIREBRICK],&exact);
    XAllocNamedColor(display,map,"black",&color[GOLDENROD],&exact);
    XAllocNamedColor(display,map,"black",&color[BLUE_VIOLET],&exact);
    XAllocNamedColor(display,map,"black",&color[CADET_BLUE],&exact);
    XAllocNamedColor(display,map,"black",&color[CORAL],&exact);
    XAllocNamedColor(display,map,"black",&color[CORNFLOWER_BLUE],
                     &exact);
    XAllocNamedColor(display,map,"black",&color[DARK_GREEN],&exact);
    XAllocNamedColor(display,map,"black",&color[DARK_OLIVE_GREEN],
                     &exact);
    XAllocNamedColor(display,map,"black",&color[PEACH_PUFF],&exact);
    XAllocNamedColor(display,map,"black",&color[PAPAYA_WHIP],&exact);
    XAllocNamedColor(display,map,"black",&color[BISQUE],&exact);
    XAllocNamedColor(display,map,"black",&color[AZURE],&exact);
    XAllocNamedColor(display,map,"black",&color[LAVENDER],&exact);
    XAllocNamedColor(display,map,"black",&color[MISTY_ROSE],&exact);
    XAllocNamedColor(display,map,"black",&color[MEDIUM_BLUE],&exact);
    XAllocNamedColor(display,map,"black",&color[NAVY_BLUE],&exact);
    XAllocNamedColor(display,map,"black",&color[PALE_TURQUOISE],&exact);
    XAllocNamedColor(display,map,"black",&color[SEA_GREEN],&exact);
  }
  else
  {
    XAllocNamedColor(display,map,"black",&color[BLACK],&exact);
    XAllocNamedColor(display,map,"grey41",&color[DIM_GREY],&exact);
    XAllocNamedColor(display,map,"grey69",&color[GREY_69],&exact);
    context->World->BackgroundPixel = exact.pixel;
    XAllocNamedColor(display,map,"grey75",&color[GREY],&exact);
    XAllocNamedColor(display,map,"grey82",&color[LIGHT_GREY],&exact);
    XAllocNamedColor(display,map,"white",&color[WHITE],&exact);
    XAllocNamedColor(display,map,"red",&color[RED],&exact);
    XAllocNamedColor(display,map,"green",&color[GREEN],&exact);
    XAllocNamedColor(display,map,"blue",&color[BLUE],&exact);
    XAllocNamedColor(display,map,"cyan",&color[CYAN],&exact);
    XAllocNamedColor(display,map,"magenta",&color[MAGENTA],&exact);
    XAllocNamedColor(display,map,"yellow",&color[YELLOW],&exact);
    XAllocNamedColor(display,map,"lime green",&color[LIME_GREEN],&exact);  
    XAllocNamedColor(display,map,"#00b0f0",&color[BLUE_CYAN],&exact);
    XAllocNamedColor(display,map,"#00f0b0",&color[CYAN_GREEN],&exact);
    XAllocNamedColor(display,map,"#b0f000",&color[GREEN_YELLOW],&exact);
    XAllocNamedColor(display,map,"#f0b000",&color[YELLOW_RED],&exact);
    XAllocNamedColor(display,map,"brown",&color[BROWN],&exact);
    XAllocNamedColor(display,map,"maroon",&color[MAROON],&exact);
    XAllocNamedColor(display,map,"gold",&color[GOLD],&exact);
    XAllocNamedColor(display,map,"aquamarine",&color[AQUAMARINE],&exact);
    XAllocNamedColor(display,map,"firebrick",&color[FIREBRICK],&exact);
    XAllocNamedColor(display,map,"goldenrod",&color[GOLDENROD],&exact);
    XAllocNamedColor(display,map,"blue violet",&color[BLUE_VIOLET],&exact);
    XAllocNamedColor(display,map,"cadet blue",&color[CADET_BLUE],&exact);
    XAllocNamedColor(display,map,"coral",&color[CORAL],&exact);
    XAllocNamedColor(display,map,"cornflower blue",&color[CORNFLOWER_BLUE],
                     &exact);
    XAllocNamedColor(display,map,"dark green",&color[DARK_GREEN],&exact);
    XAllocNamedColor(display,map,"dark olive green",&color[DARK_OLIVE_GREEN],
                     &exact);
    XAllocNamedColor(display,map,"peach puff",&color[PEACH_PUFF],&exact);
    XAllocNamedColor(display,map,"papaya whip",&color[PAPAYA_WHIP],&exact);
    XAllocNamedColor(display,map,"bisque",&color[BISQUE],&exact);
    XAllocNamedColor(display,map,"azure",&color[AZURE],&exact);
    XAllocNamedColor(display,map,"lavender",&color[LAVENDER],&exact);
    XAllocNamedColor(display,map,"misty rose",&color[MISTY_ROSE],&exact);
    XAllocNamedColor(display,map,"medium blue",&color[MEDIUM_BLUE],&exact);
    XAllocNamedColor(display,map,"navy blue",&color[NAVY_BLUE],&exact);
    XAllocNamedColor(display,map,"pale turquoise",&color[PALE_TURQUOISE],
                     &exact);
    XAllocNamedColor(display,map,"sea green",&color[SEA_GREEN],&exact);
  }
  XListFonts(display,FONT1,1,&c);
  if (c) font=XLoadFont(display,FONT1);
  else   font=XLoadFont(display,FONT2);
  window = XCreateSimpleWindow(display,
                               RootWindow(display,DefaultScreen(display)),
                               0,0,WINDOW_W,WINDOW_H,0,
                               WhitePixel(display,DefaultScreen(display)),
                               BlackPixel(display,DefaultScreen(display)));
  XChangeProperty(display,window,XA_WM_NAME,XA_STRING,8,PropModeReplace,
                  (unsigned char *)
                 "Khepera Simulator version 2.0 by Olivier MICHEL",47);
  XChangeProperty(display,window,XA_WM_ICON_NAME,XA_STRING,8,PropModeReplace,
                  (unsigned char *)"Khepera Simulator",17);
  XSelectInput(display,window,ExposureMask|KeyPressMask|ButtonPressMask|
                              ButtonReleaseMask|PointerMotionMask);
  pointer_cursor = XCreateFontCursor(display,XC_left_ptr);
  wait_cursor    = XCreateFontCursor(display,XC_watch);
  cancel_cursor  = XCreateFontCursor(display,XC_right_ptr);
  XDefineCursor(display,window,pointer_cursor);
  XMapWindow(display,window);
  gc = XCreateGC(display,window,0,NULL);
  XSetBackground(display,gc,color[GREY].pixel);
  XSetFont(display,gc,font);
}

void CloseGraphics()
{
  XCloseDisplay(display);
}
