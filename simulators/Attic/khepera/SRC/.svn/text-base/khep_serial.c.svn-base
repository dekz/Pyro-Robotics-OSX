/*-----------------------------------------------------------------------------
Project name	:	khep_serial
Filename	:	khep_serial.c
Release		:	0.1 bis
Purpose		:	Basic Package for communications with Khepera through
                        the serial line
Creation date	:	17/11/93
Author		:	M. von Holzen, L. Tettoni
Releaser        :       J.-Y. Tigli, O. Michel
History         :       0.1	17/11/93	Creation
                        0.1 bis 14/03/94        Modification
                        0.1 ter 21/09/95        Modification
-----------------------------------------------------------------------------*/

#include "types.h"
#include "khep_serial.h"

/* Management of the serial line                                            */
/* These routines provide a set of simple primitives to read and write on   */
/* the serial line                                                          */

/* configure serial link fd      */
/* according to khepera protocol */
boolean serial_configure(int fd,int speed)
{
  struct termios term;
  static int32	 speedkey;

  if (tcgetattr(fd,&term)!=0)
  {
    perror("khepera::serial_configure(), getting attributes");
    return FALSE;
  }
  switch(speed)
  {
    case 9600:	speedkey=B9600; break;
    case 19200:	speedkey=B19200; break;
    case 38400:	speedkey=B38400; break;
    default:	return FALSE;
  }
  cfsetispeed(&term,speedkey);  /* Speed */
  cfsetospeed(&term,speedkey);
  clear(term.c_iflag,            /* Input modes */
        IGNBRK|BRKINT|IGNPAR|INPCK|ISTRIP|ICRNL|INLCR|IXON|IXOFF);
  set(term.c_iflag,0);
  clear(term.c_oflag, OPOST);    /* Output modes */
  set(term.c_oflag,0);
  clear(term.c_cflag,CSIZE|PARENB);     /* Control modes */
  set(term.c_cflag,CS8|CSTOPB);
                                               /* Line modes */
  clear(term.c_lflag,ISIG|ICANON|XCASE|ECHO|IEXTEN);
  set(term.c_lflag,0);   /* MIN and TIME */
  term.c_cc[VMIN]  = 0;
  term.c_cc[VTIME] = KHEP_DEFAULT_TIMEOUT;
  if (tcsetattr(fd,TCSANOW,&term)!=0)
  {
    perror("khepera: serial_configure(), setting attributes");
    return FALSE;
  }
  return TRUE;
}

extern int serial_open(char *portname) /* open serial link on portname */
{
  int fd;

  if ((fd = open(portname,O_RDWR|O_EXCL)) > 0)
   serial_configure(fd,KHEP_DEFAULT_BAUD);
  return(fd);
}

/* Read until and including \n */
/* Terminate char * with \0    */
extern int serial_readline(int  fd,char buffer[],int size)
{
  int  nrd,rsize;
  char c;

  rsize = 0;
  do
  {
    nrd = read(fd,&c,1);
    if (nrd < 0) break;
    buffer[rsize] = c;
    rsize += nrd;
  }
  while (nrd==1 && rsize < size && c != '\n');
  buffer[rsize] = '\0';

  if (nrd>=0) return(rsize);
  else
  {
    perror("khepera: serial_readline()");
    return(nrd);
  }
}

/* Try to empty input buffer  */
extern void serial_drain(int fd,boolean verbose)
{
  char answer[KHEP_MSG_SIZE];
  int  rsize;

  do
  {
    rsize = serial_readline(fd,answer,sizeof(answer));
    if (verbose) fprintf (stderr,"draining %d bytes",rsize);
  }
  while (rsize > 0); /* Read till nothing more to read */
}

/* Khepera package routines                                                 */
/* These routine make a specific use of the serial management functions to  */
/* provide a more complex tool to communicate with a Khepera                */

/* Send line send           */
/* and receive line receive */
/* without any check control*/
extern boolean khep_send_recv(int fd,char *send,char *receive,int recv_len)
{
  int rd;

  serial_write(fd,send,strlen(send));

  if ((rd = serial_readline(fd,receive,recv_len)) > 0 ) return(TRUE);
  else
  {
    if (rd < 0) perror("khepera_send_recv(): read error");
    else perror("khepera_send_recv(): khepera not responding");
    return(FALSE);
  }
}

/* Send line send and receive line       */
/* receive with check control :          */
/* The first character of the received   */
/* line is the lower first character of  */
/* the send line.                        */
/* Try to have the good answer           */
/* KHEP_NB_RETRY times                   */
extern boolean khep_talk(int fd,char *send,char *receive,int recv_len)
{
  int  rd,rsize,tries = 0;
  char respond = tolower(send[0]);

  do
  {
    serial_write(fd,send,strlen(send));
    rd = serial_readline(fd,receive,recv_len);
    if (rd < 0) /* File error */
    {
      perror("khep_talk(): read/write error");
      break;
    }
    else if (rd == 0) /* No response */
    tries++;
    else if (receive[0] != respond) /* Incorrect answer */
    {
      perror("khep_talk(): protocol error");
      serial_drain(fd,FALSE);
      tries++;
    }
    else /* Correct answer */
    {
      if ((rsize = strlen(receive)) >= 2) /* Strip terminating '\r\n' if any */
      {
        if (receive[rsize-1] == '\n') receive[rsize-1] = '\0';
        if (receive[rsize-2] == '\r') receive[rsize-2] = '\0';
      }
      return(TRUE);
    }
  }
  while (tries < KHEP_NB_RETRY);
  if (rd == 0) perror("khep_talk(): Khepera not responding");
  return(FALSE);
}


