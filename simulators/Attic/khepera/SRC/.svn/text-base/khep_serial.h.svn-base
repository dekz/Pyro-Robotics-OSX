/*-----------------------------------------------------------------------------
Project name	:	khep_serial
Filename	:	khep_serial.h
Release		:	0.1 bis
Purpose		:	Basic Package for communications with Khepera through
                        the serial line
Creation date	:	17/11/93
Author		:	M. von Holzen, L. Tettoni
Releaser        :       J.-Y. Tigli, O.Michel
History         :       0.1	17/11/93	Creation
                        0.1 bis 14/03/94        Modification
                        0.1 ter 21/09/95        Modification
-----------------------------------------------------------------------------*/

#ifndef __KHEP_SERIAL_H__
#define __KHEP_SERIAL_H__

#include "gen_types.h"
#include <stdio.h>
#include <unistd.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>
#include <termios.h>
#include <termio.h>

#define KHEP_MSG_SIZE		200
#define	KHEP_DEFAULT_BAUD	38400
#define	KHEP_DEFAULT_TIMEOUT	5			/* 1/10 seconds	*/
#define	KHEP_NB_RETRY		3

/*---------------------------------------------------------------------------*/
/* Management of the serial line                                             */
/*---------------------------------------------------------------------------*/
/* These routines provide a set of simple primitives to read and write on    */
/* the serial line                                                           */
/*---------------------------------------------------------------------------*/

#define clear(var,mask)         var &= (~(mask))
#define set(var,mask)           var |= (mask)
#define let(var,mask)
#define unused(var,mask)
#define	serial_close(fd)                close(fd)
#define	serial_read(fd,buffer,size)     read(fd,buffer,size)
#define	serial_write(fd,buffer,size)    write(fd,buffer,size)

#if  __GNUC__
extern int      serial_open(char portname[]);
extern boolean	serial_configure(int fd,int speed);
extern int      serial_readline(int fd,char buffer[],int size);
extern int      serial_readexactly(int fd,char buffer[],int size);
extern void     serial_drain(int fd,boolean verbose);
#endif

/*---------------------------------------------------------------------------*/
/* khepera package routines                                                  */
/*---------------------------------------------------------------------------*/
/* These routine make a specific use of the serial management functions to   */
/* provide a more complete tool to communicate with a Khepera                */
/*---------------------------------------------------------------------------*/

#if  __GNUC__
extern boolean	khep_send_recv(int fd,char *send,char *receive,int recv_len);
extern boolean	khep_talk(int fd,char *send,char *receive,int recv_len);
#endif

#endif

