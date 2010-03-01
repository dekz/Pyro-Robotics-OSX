#ifndef CONTEXT_H
#define CONTEXT_H

#define TEXT_BUF_SIZE           64

struct UserInfo
{
  char Info;
  char Pages[4];
  char Title[4][256];
};

struct Context
{
  struct World      *World;
  struct Robot      *Robot;
  struct Button     *Buttons;
  struct UserInfo   *UserInfo;
  char              Comment[TEXT_BUF_SIZE];
  char              TextInput[TEXT_BUF_SIZE];
  char              Info,InfoAbout,InfoUser[4];
  boolean           KheperaAvailable,MonoDisplay,Pipe;
};

#endif
