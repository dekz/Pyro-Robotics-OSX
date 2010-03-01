/*****************************************************************************/
/* File:        world.c (Khepera Simulator)                                  */
/* Author:      Olivier MICHEL <om@alto.unice.fr>                            */
/* Date:        Thu Sep 21 14:39:05 1995                                     */
/* Description: world management                                             */
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
#include "world.h"
#include "sim.h"

void AddObject(struct World  *world,struct Object *object)
{
  struct Object **obj;

  /* LAMPS are added first, other objects are added last */

  if (object->Type == LAMP)
  {
    object->Next = world->Objects;
    world->Objects = object;
  }
  else
  {
    obj = &(world->Objects);
    while(*obj) obj = &((*obj)->Next);
    *obj = object;
  }
}

struct Object *CreateObject(u_char type,short int x,short int y,double alpha)
{
  struct Object *object;

  object              = (struct Object *)malloc(sizeof(struct Object));
  object->Type        = type;
  object->X           = x;
  object->Y           = y;
  object->Alpha       = alpha;
  object->Next        = NULL;
  return(object);
}

void FreeObjects(struct Object *object)
{
  if (object)
  { 
    FreeObjects(object->Next);
    FreeObject(object);
  }
}

void CreateEmptyWorld(struct Context *context)
{
  short int i,j,s;
  struct World *world;
  FILE *file;
  char text[256];

  world = context->World;
  FreeObjects(world->Objects);
  strcpy(world->Name,"new");
  world->Objects = (struct Object *)NULL;
  world->ObjectType = BRICK;
  world->BehindObject = NULL;
  world->BehindX = 0;
  world->BehindY = 0;
  for(i=0;i<N_OBJECTS;i++) world->ObjectAlpha[i]=0;
  strcpy(world->ObjectName[BRICK],"brick");
  strcpy(world->ObjectName[CORK],"cork");
  strcpy(world->ObjectName[LAMP],"lamp");
}

void CreateDefaultWorld(struct Context *context)
{
  short int i,j;
  struct World *world;

  CreateEmptyWorld(context);
  world = context->World;
  strcpy(world->Name,"default");
  for(i=25;i<WORLD_W;i+=50)
  {
    AddObject(world,CreateObject(BRICK,i,14,0.0));
    AddObject(world,CreateObject(BRICK,i,987,0.0));
  }
  for(j=50;j<WORLD_H;j+=50)
  {
    AddObject(world,CreateObject(BRICK,10,j,M_PI/2));
    AddObject(world,CreateObject(BRICK,989,j,M_PI/2));
  }
  for(i=0;i<16;i++) for(j=0;j<13;j++) world->Image[i][j] = (u_long)0xffffffff;
  for(j=13;j<488;j++)
  {
    world->Image[0][j] = (u_long)0x00007ff;
    for(i=1;i<15;i++) world->Image[i][j] = (u_long)0x00000000;
    world->Image[15][j] = (u_long)0x00ffe00;
  }
  for(i=0;i<16;i++) for(j=488;j<500;j++) world->Image[i][j]=(u_long)0xffffffff;
}

void CreateChaoWorld(struct Context *context)
{
  short int i,j;
  struct World *world;

  CreateDefaultWorld(context);
  world = context->World;
  strcpy(world->Name,"chao");
  for(i=0;i<90;i++)
  {
    AddObject(world,
     CreateObject(BRICK,Rnd(950)+25,Rnd(950)+25,(double)Rnd(1000)*M_PI/1000));
  }
}

void FreeWorld(struct Context *context)
{
  short int i,j;
  struct World *world;

  world = context->World;
  FreeObjects(world->Objects);
  free(world);
}

void RemoveObject(struct World  *world,struct Object *object)
{
  struct Object **search;

  if (object)
  {
    search = &(world->Objects);
    while(*search)
    {
      if (*search == object)
      {
        *search = object->Next;
        FreeObject(object);
      }
      else search = &((*search)->Next);
    }
  }
}

struct Object *FindObject(struct World *world,short int x,short int y)
{
  struct Object *search,*found;

  search = world->Objects;
  found  = NULL;
  while (search)
  {
    if ((search->X - x < 7)&&(search->X - x > -7)&&
        (search->Y - y < 7)&&(search->Y - y > -7))
    {
      found  = search;
      search = NULL;
    }
    else search = search->Next;
  }
  return(found);
}

void WriteWorldToFile(struct World *world,FILE *file)
{
  u_char obj;
  short int i,j;
  struct Object *object;

  if (world->Objects) obj = 1; else obj = 0;
  fprintf(file,"%d,%d\n",obj,world->ObjectType);
  for(i=0;i<N_OBJECTS;i++)
   fprintf(file,"%s\n%d\n",world->ObjectName[i],world->ObjectAlpha[i]);
  for(i=0;i<16;i++)for(j=0;j<500;j++) fprintf(file,"%lx,",world->Image[i][j]);
  object = world->Objects;
  while(object)
  {
    if (object->Next) obj = 1; else obj = 0;
    fprintf(file,"%d,%d,%d,%d,%d\n",object->Type,object->X,object->Y,
                                     (int)(object->Alpha*180/M_PI),obj);
    object = object->Next;
  }
}

void ReadWorldFromFile(struct World *world,FILE *file)
{
  short int i,j,obj,type;
  struct Object **object;

  fscanf(file,"%hd,%hd\n",&obj,&type);
  world->ObjectType = (u_char)type;
  if (obj) world->Objects = (struct Object *)1; else world->Objects = NULL;
  for(i=0;i<N_OBJECTS;i++)
   fscanf(file,"%s\n%hd\n",world->ObjectName[i],&(world->ObjectAlpha[i]));
  for(i=0;i<16;i++) for(j=0;j<500;j++)
   fscanf(file,"%lx,",&(world->Image[i][j]));
  world->BehindX = 0;
  world->BehindY = 0;
  world->BehindObject = NULL;
  object = &(world->Objects);
  while(*object)
  {
    *object = (struct Object *)malloc(sizeof(struct Object));
    fscanf(file,"%hd,%hd,%hd,%lf,%hd\n",&type,&((*object)->X),
                                   &((*object)->Y),&((*object)->Alpha),&obj);
    (*object)->Type = (u_char)type;
    (*object)->Alpha *= M_PI/180.0;
    if (obj) (*object)->Next = (struct Object *)1;
    else (*object)->Next = NULL;
    object = &((*object)->Next);
  }
}

void ChooseRandomPosition(struct World *world,double *x,double *y,
                          double *alpha)
{
  u_char    success;
  short int ix,iy;

  do
  {
    ix = (Rnd(900) + 50)/2;
    iy = (Rnd(900) + 50)/2;
    if ((world->Image[ix/32][iy]         & (1 << (ix%32)))||
        (world->Image[(ix+15)/32][iy]    & (1 << ((ix+15)%32)))||
        (world->Image[(ix-15)/32][iy]    & (1 << ((ix-15)%32)))||
        (world->Image[ix/32][iy+15]      & (1 << (ix%32)))||
        (world->Image[ix/32][iy-15]      & (1 << (ix%32)))||
        (world->Image[(ix+11)/32][iy+11] & (1 << ((ix+11)%32)))||
        (world->Image[(ix+11)/32][iy-11] & (1 << ((ix+11)%32)))||
        (world->Image[(ix-11)/32][iy+11] & (1 << ((ix-11)%32)))||
        (world->Image[(ix-11)/32][iy-11] & (1 << ((ix-11)%32))))
         success = FALSE; else success = TRUE;
  }
  while(success == FALSE);
  *x = (double)ix*2;
  *y = (double)iy*2;
  *alpha = (2.0*M_PI*Rnd(1000))/999.0;
}
