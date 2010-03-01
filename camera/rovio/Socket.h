#ifndef __SOCKET_H__
#define __SOCKET_H__

#include <sys/types.h> 
#include <netinet/in.h> 
#include <netdb.h>
#include <sys/socket.h> 

class Socket {
 public:
  Socket(char *hostname, int port, int tcp);
  char *read(int cnt);
  char *readUntil(char stop);
  int write(char *message);
  char *host;
 private:
  int sock;
  struct sockaddr_in server_addr;
  struct hostent *host_id;
};

class FakeSocket {
 public:
  FakeSocket(char *buf);
  char *read(int cnt);
  char *readUntil(char stop);
 private:
  char *buffer;
  int current;
};

#endif
