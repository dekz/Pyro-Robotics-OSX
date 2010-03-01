/*#########################################
 * Functions for controlling the Sony
 * Pan-Tilt-Zoom (PTZ; EVI-D30/D31) camera
 *  via its VISCA interface to PSOS
 *#########################################
 */


/**
 ** ptzsys.c
 **
 ** Copyright 1998 by Kurt Konolige
 **
 ** The author hereby grants to SRI permission to use this software.
 ** The author also grants to SRI permission to distribute this software
 ** to schools for non-commercial educational use only.
 **
 ** The author hereby grants to other individuals or organizations
 ** permission to use this software for non-commercial
 ** educational use only.  This software may not be distributed to others
 ** except by SRI, under the conditions above.
 **
 ** Other than these cases, no part of this software may be used or
 ** distributed without written permission of the author.
 **
 ** Neither the author nor SRI make any representations about the 
 ** suitability of this software for any purpose.  It is provided 
 ** "as is" without express or implied warranty.
 **
 ** Kurt Konolige
 ** Senior Computer Scientist
 ** SRI International
 ** 333 Ravenswood Avenue
 ** Menlo Park, CA 94025
 ** E-mail:  konolige@ai.sri.com
 **
 **/


#include "saphira.h"

#define sfCOMPTZCAM 42		/* packet number for sony camera commands */

static unsigned char initb[9]  = { 0x88, 0x01, 0x00, 0x01, 0xFF, 0x88,
				   0x30, 0x01, 0xff };

/* Zoom: 81 01 04 47 0z 0z 0z 0z ff, where zzzz is a 16-bit zoom value,
   with 0-1023 being valid values.  1023 is wide-angle ?? */
static unsigned char zoomb[9]  = { 0x81, 0x01, 0x04, 0x47, 0x00, 0x00,
				   0x00, 0x00, 0xff };

/* Pan/tilt: 81 01 06 02 vv ww 0p 0p 0p 0p 0t 0t 0t 0t ff, where
   vv is pan speed, ww is tilt speed (leave at 0x18, 0x14 for max),
   and pppp is pan angle (from -0x370 to +0x370) and tttt is tilt
   angle (from -0x12c to +0x12c */
static unsigned char ptb[15]   = { 0x81, 0x01, 0x06, 0x02, 0x18, 0x14,
				   0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
				   0x00, 0x00, 0xff };

/* globals for current positions */
EXPORT int sfPTZCamPanAngle = 0, sfPTZCamTiltAngle = 0;
#define DEG_TO_PAN (0x370 / 95.0)
#define MAX_PAN 95
#define DEG_TO_TILT (0x12c / 20)
#define MAX_TILT 20

/* help function */
void 
set_nibbles(int pos, unsigned char *buf)
{
  buf[0] = (pos & 0xf000) >> 12;
  buf[1] = (pos & 0x0f00) >> 8;
  buf[2] = (pos & 0x00f0) >> 4;
  buf[3] = (pos & 0x000f) >> 0;
}

EXPORT void
sfPTZCamInit(void)		/* initializes the camera */
{
  sfRobotComStrn(sfCOMPTZCAM, initb, 9);
  sfPTZCamPanAngle = sfPTZCamTiltAngle = 0;
  set_nibbles(0, &ptb[6]);
  set_nibbles(0, &ptb[10]);
  sfRobotComStrn(sfCOMPTZCAM, ptb, 15);
  set_nibbles(0, &zoomb[4]);
  sfRobotComStrn(sfCOMPTZCAM, zoomb, 9);  

}


EXPORT void			/* pan to an absolute position */
sfPTZCamPan(int deg)
{
  int pos;
  if (deg > MAX_PAN) deg = MAX_PAN;
  if (deg < -MAX_PAN) deg = -MAX_PAN;
  pos = (int)(((double)deg)*DEG_TO_PAN);
  set_nibbles(pos, &ptb[6]);
  sfRobotComStrn(sfCOMPTZCAM, ptb, 15);  
  sfPTZCamPanAngle = deg;
}

EXPORT void			/* tilt to an absolute position */
sfPTZCamTilt(int deg)
{
  int pos;
  if (deg > MAX_TILT) deg = MAX_TILT;
  if (deg < -MAX_TILT) deg = -MAX_TILT;
  pos = (int)(((double)deg)*DEG_TO_TILT);
  set_nibbles(pos, &ptb[10]);
  sfRobotComStrn(sfCOMPTZCAM, ptb, 15);  
  sfPTZCamTiltAngle = deg;
}

EXPORT void			/* pan and tilt to an absolute position */
sfPTZCamPanTilt(int pan, int tilt)
{
  int pos;
  if (tilt > MAX_TILT) tilt = MAX_TILT;
  if (tilt < -MAX_TILT) tilt = -MAX_TILT;
  if (pan > MAX_PAN) pan = MAX_PAN;
  if (pan < -MAX_PAN) pan = -MAX_PAN;
  pos = (int)(((double)pan)*DEG_TO_PAN);
  set_nibbles(pos, &ptb[6]);
  pos = (int)(((double)tilt)*DEG_TO_TILT);
  set_nibbles(pos, &ptb[10]);
  sfRobotComStrn(sfCOMPTZCAM, ptb, 15);  
  sfPTZCamPanAngle = pan;
  sfPTZCamTiltAngle = tilt;
}

EXPORT void			/* zoom in or out */
sfPTZCamZoom(int val)
{
  if (val < 0) val = 0;
  if (val > 1023) val = 1023;
  set_nibbles(val, &zoomb[4]);
  sfRobotComStrn(sfCOMPTZCAM, zoomb, 9);  
}

EXPORT void
sfLoadInit(void)		/* this should be evaluated on open */
{
  sfMessage("Loading PTZ system control functions");
  sfAddEvalFn("sfPTZCamInit", sfPTZCamInit, sfVOID, 0);
  sfAddEvalFn("sfPTZCamPan",  sfPTZCamPan,  sfVOID, 1, sfINT);
  sfAddEvalFn("sfPTZCamTilt", sfPTZCamTilt,  sfVOID, 1, sfINT);
  sfAddEvalFn("sfPTZCamPanTilt", sfPTZCamPanTilt,  sfVOID, 2, sfINT, sfINT);
  sfAddEvalFn("sfPTZCamZoom", sfPTZCamZoom, sfVOID, 1, sfINT);
  sfAddEvalVar("sfPTZCamPanAngle", sfINT, &sfPTZCamPanAngle);
  sfAddEvalVar("sfPTZCamTiltAngle", sfINT, &sfPTZCamTiltAngle);
}

