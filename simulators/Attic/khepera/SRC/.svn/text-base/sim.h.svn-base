/*****************************************************************************/
/* File:        sim.h (Khepera Simulator)                                    */
/* Author:      Olivier MICHEL <om@alto.unice.fr>                            */
/* Date:        Thu Sep 21 14:39:05 1995                                     */
/* Description: sim header file                                              */
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

#ifndef SIM_H

#define SIM_H 

#include "context.h"
#include <sys/types.h>

/* shared memory parameters */
#define SHM_BUF_SIZE	64
#define SHM_KEY_IN		(key_t) 4000
#define SHM_KEY_OUT		(key_t) 4001
#define SHM_PERM			0600

#define INFO_ABOUT              0
#define INFO_USER0              1
#define INFO_USER1              2
#define INFO_USER2              3
#define INFO_USER3              4
#define RAD(x)                  ((double)(x)*M_PI/180)

/*
 *                             Buttons
 */

#define QUIT                      0

#define NEW_WORLD                 1
#define LOAD_WORLD                2
#define SAVE_WORLD                3
#define SET_ROBOT                 4
#define REDRAW_WORLD              5
#define SET_ANGLE                6
#define REMOVE_OBJECT             7
#define ADD_OBJECT                8
#define TURN_OBJECT               9
#define OBJECT_PLUS              10
#define OBJECT_MINUS             11

#define NEW_ROBOT                12
#define LOAD_ROBOT               13
#define SAVE_ROBOT               14
#define STEP_ROBOT               15
#define RUN_ROBOT                16
#define RESET_ROBOT              17
#define COMMAND                  18
#define TEST                     19
#define INFO_NEXT                20
#define PAGE_PLUS                21
#define PAGE_MINUS               22

#define KHEPERA_BUTTON           23
#define SENSORS_BUTTON           24
#define MOTORS_BUTTON            25

#define RUN_ROBOT_NO_GUI         26


#define FILE_NAME_TEXT "enter a file name:                                             "
#define COMMAND_TEXT   "enter the command:                                             "
#define ANGLE_TEXT     "enter robot angle:                                             "

extern void              CreateEmptyWorld(struct Context *c);
extern void              ReadWorldFromFile(struct World *w,FILE *f);
extern void              CreateDefaultRobot(struct Context *c);
extern void              InitSensors(struct Context *c);
extern struct Button     *CreateButton(u_char command,char *name,int x, int y);
extern struct UserInfo   *SetUserInfo();
extern void              OpenGraphics(struct Context *c);
extern void              FreeRobot(struct Context *c);
extern void              FreeWorld(struct Context *c);
extern void              FreeButtons(struct Context *c);
extern void              CloseGraphics();
extern void              UserInit(struct Robot *robot);
extern void              UserClose(struct Robot *r);
extern struct Button     *PressButton(struct Context *c);
extern boolean UnpressButton(struct Context *context,
			     struct Button *cancelbutton, 
			     struct Robot *robot);
extern char              *ReadText(struct Context *c,char *text,
                                   struct Button *b);
extern XPoint            *ClickInWorld(struct Context *c,struct Button *b);
extern struct Object     *CreateObject(u_char type,short int x,short int y,
                                       double alpha);
extern struct Object     *FindObject(struct World *w,short int x,
                                     short int y);
extern struct Object     *AddObjectInWorld(struct Context *c,struct Button *b);
extern void              InitKheperaSerial(char *text);
extern void              DisplayComment(struct Context *c,char *text);
extern void              CreateDefaultWorld(struct Context *c);
extern void              DrawWorld(struct Context *c);
extern void              WaitCursor();
extern void              PointerCursor();
extern void              CancelCursor();
extern void              DrawRobotIRSensors(struct Robot *r);
extern void              WriteWorldToFile(struct World *w,FILE *f);
extern void              UndisplayComment(struct Context *c);
extern void              DrawObstacles(struct Context *c);
extern void              ScanWorld(struct Context *c);
extern void              RemoveObject(struct World *w,struct Object *o);
extern void              AddObject(struct World *w,struct Object *o);
extern void              DrawObject(struct Object *o);
extern void              DrawConsObject(struct World *w);
extern void              NewRobot(struct Robot *r);
extern void              DrawRobotEffectors(struct Robot *r);
extern void              ReadRobotFromFile(struct Robot *r,FILE *f);
extern void              DrawRobot(struct Context *c);
extern void              InitKheperaSensors(struct Context *c);
extern void              DrawLittleRobot(struct Robot *sr,struct Robot *r);
extern void              WriteRobotToFile(struct Robot *r,FILE *f);
extern void              RunRobotStart(struct Robot *r);
extern boolean           RunKhepera(struct Context *c);
extern void              SolveKheperaEffectors(struct Context *c);
extern boolean           RobotRun(struct Context *c);
extern void              RunRobotStop(struct Robot *r);
extern void              InitRobot(struct Context *c);
extern void              UserCommand(struct Robot *r,char *text);
extern void              DrawInfo(struct Context *c);
extern void              CloseKheperaSerial(struct Context *c);
extern void              OpenKheperaSerial(struct Context *c);
extern void              DrawRobotToggleButtons(struct Robot *r);
extern void              DrawButton(struct Button *b);
extern boolean           PipedRobotRun(struct Context *c,int i,int o);
extern void					 MessageRobotDeal(struct Context *c, char *q, char *a);
extern boolean					 MessageRobotRun(struct Context *c, boolean graphics);

#endif
