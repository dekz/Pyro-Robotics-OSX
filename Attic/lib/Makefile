# March 1998
#
# Makefile for PTZ Camera object
#

OBJS = libptzsys.so

include ../Makefile.cfg
include ../Makefile.src

#############################################################

SRCD = ./
OBJD = ./
INCD = $(SAPHIRA)/handler/include/
LIBD = $(SAPHIRA)/handler/obj/
BIND = ./
COLBERT = $(SAPHIRA)/colbert/
OAALIB = $(SAPHIRA)/oaa/agents/lib/
SHARED = -shared

# find out which OS we have 
#include $(SAPHIRA)/handler/include/os.h

CFLAGS =  -g -DLINUX
INCLUDE = -I$(INCD) -I$(X11_DIR)/include

#############################################################

#
# PTZ camera loadable object file
#

libptzsys.so: ptzsys.o
	$(LD) $(SHARED) ptzsys.o -o libptzsys.so

ptzsys.o: ptzsys.c $(INCD)saphira.h
	$(CC) $(CFLAGS) -c ptzsys.c $(INCLUDE) -o ptzsys.o

