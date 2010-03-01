/*****************************************************************************/
/* File:        world.h (Khepera Simulator)                                  */
/* Author:      Olivier MICHEL <om@alto.unice.fr>                            */
/* Date:        Thu Sep 21 14:39:05 1995                                     */
/* Description: world header file                                            */
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

#ifndef WORLD_H

#define FreeObject(x) free(x)
#define WORLD_H                  1000  /* The playground is 1000x1000 mm */
#define WORLD_W                  1000

#define N_OBJECTS                3 /* number of types of objects */

/*
 *               Object types
 */

#define BRICK                    0
#define BRICKWidth               20
#define BRICKHeight              50
#define LAMP                     1
#define LAMP_ON                  1
#define LAMP_OFF                 3
#define LAMPWidth                34
#define LAMPHeight               34
#define CORK                     2
#define CORKWidth                16
#define CORKHeight               16
#define ROBOT                    255

struct Object
{
  u_char        Type;
  short int     X,Y;
  double        Alpha;
  struct Object *Next;
};

struct World
{
  char          Name[16];
  struct Object *Objects;
  u_char        ObjectType;                       /* Construction Kit Object */
  short int     ObjectAlpha[N_OBJECTS];           /*    Angles of Objects    */
  char          ObjectName[N_OBJECTS][16];        /*     Names of Objects    */
  u_long        BackgroundPixel;
  u_long        Image[16][500];
  XImage        *BehindObject;
  short int     BehindX,BehindY;
};

extern long int            Rnd(int x);

#endif
