#include "Socket.h"

#include <unistd.h>
#include <string.h>
#include <strings.h>
#include <stdio.h>
#define MAXBUFSIZE 10000

FakeSocket::FakeSocket(char *buf) {
  printf("here we are!\n");
  buffer = buf; // memory allocated in Socket
  current = 0;
}

char *FakeSocket::read(int cnt) {
  static char retval[MAXBUFSIZE];
  strncpy(retval, &buffer[current], cnt);
  retval[cnt + 1] = '\0';
  current += cnt;
  return retval;
}

char *FakeSocket::readUntil(char stop) {
  static char retval[MAXBUFSIZE];
  int numbytes = 0;
  char ch[5];
  int pos = 0;
  while (buffer[current] != stop && pos < 50) { // no text is > 50
    retval[pos++] = buffer[current++];
  }
  retval[pos] = 0; // end of string
  printf("readUntil: read %d chars\n", pos);
  return retval;
}

Socket::Socket(char *hostname, int port, int tcp) {
  char buf[MAXBUFSIZE];
  char buf2[MAXBUFSIZE];
  bzero(buf2, MAXBUFSIZE);
  host = hostname;
  host_id = gethostbyname(host);
  // open socket
  server_addr.sin_family = AF_INET;      /* host byte order */
  server_addr.sin_port = htons(port);    /* short, network byte order */
  server_addr.sin_addr = *((struct in_addr *)host_id->h_addr);
  bzero(&(server_addr.sin_zero), 8);     /* zero the rest of the struct */
  if (tcp) { // TCP
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
      printf("Error: tcp socket could not be opened\n");
    } else {
      if (connect(sock, (struct sockaddr *)&server_addr,
		  sizeof(struct sockaddr)) == -1) {
	printf("Error: tcp socket could not connect\n");    
      }
    }
  } else { // UDP
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
      printf("Error: udp socket could not be opened\n");
    } else {
      if (connect(sock, (struct sockaddr *)&server_addr,
		  sizeof(struct sockaddr)) == -1) {
	printf("Error: udp socket could not connect\n");    
      }
      strcpy(buf, "connection request");
      printf("buffer: '%s'\n", buf);
      int retval = send(sock, buf, strlen(buf), 0);
      printf("The send returned: %d\n", retval);
      sleep(1);
      // set timeout to 500 ms (0.5 sec)
      retval = recv(sock, buf2, MAXBUFSIZE, 0); //receive incoming message
      printf("The recv returned: %d\n", retval);
      printf("buffer: '%s'\n", buf2);
      // set timeout to 0 so that it is blocking
    }
  }
}

char *Socket::read(int cnt) {
  static char buf[MAXBUFSIZE];
  //struct timeval timeVal;
  //fd_set readSet;
  //FD_ZERO(&readSet);
  //FD_SET(sock, &readSet);
  //timeVal.tv_sec = 0;
  //timeVal.tv_usec = 500;
  char ch[5];
  bzero(buf, MAXBUFSIZE);
  int numbytes;
  for (int i = 0; i < cnt; i++) {
    /*
    if (select(sock+1, &readSet, NULL, NULL, &timeVal)) {
      numbytes = recv(sock, ch, 1, 0);
      if (numbytes < 0) {
	printf("closing socket\n");
        close(sock);
        //exit(1);
      }
    */
    numbytes = recv(sock, ch, 1, 0);
    if (numbytes == 1) {
      //printf("read: %d ", (int)ch[0]);
      buf[i] = ch[0];
    } else {
      i--;
    }
    //    } else {
    // timeout
    //break;
    //}
  }
  //printf("\nread %d bytes: ", cnt);
  return buf;
}

int Socket::write(char *message) {
  return send(sock, message, strlen(message), 0);
}

char *Socket::readUntil(char stop) {
  static char retval[MAXBUFSIZE];
  int numbytes = 0;
  char ch[5];
  int pos = 0;
  numbytes = recv(sock, &ch, 1, 0);
  while (ch[0] != stop && numbytes == 1 && pos < 50) { // no text is > 50
    retval[pos++] = ch[0];
    numbytes = recv(sock, &ch, 1, 0);
  }
  retval[pos] = 0; // end of string
  //printf("readUntil: read %d chars\n", pos);
  return retval;
}


