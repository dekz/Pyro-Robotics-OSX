OBJS = _rovio.so

include ../../Makefile.cfg
include ../../Makefile.src

INCLUDE = -I../device/
CPPFLAGS = -Wall -Wno-unused -D_POSIX_THREADS \
	-D_POSIX_THREAD_SAFE_FUNCTIONS \
	-D_REENTRANT -DPOSIX \
	-D__x86__ -D__linux__ \
	-D__OSVERSION__=2 -frepo -DUSINGTHREADS -DLINUX -D_GNU_SOURCE \
	$(PYTHON_INCLUDE) $(INCLUDE)

LIBDIRS= 
LIBS= -lstdc++ -ldl -lpthread -ljpeg

../device/Device.o: ../device/Device.h ../device/Device.cpp
	cd ../device/; make

_rovio.so: rovio.o RovioLib.o Socket.o jpeg.o RWLock.o
	$(CC) $(CPPFLAGS) -shared rovio.o RovioLib.o Socket.o jpeg.o RWLock.o ../device/Device.o $(LIBDIRS) -o $@ $(LIBS)

RWLock.o: RWLock.cpp RWLock.h
	$(CC) RWLock.cpp -c

jpeg.o: jpeg.c jpeg.h
	$(CC) jpeg.c -c

RovioLib.o: RovioLib.cpp RovioLib.h ../device/Device.o
	$(CC) $(CPPFLAGS) -o $@ -c RovioLib.cpp

RovioLib.cc: RovioLib.i RovioLib.h ../device/Device.o
	swig -python -c++ $(INCLUDE) -o RovioLib.cc RovioLib.i

rovio.o: RovioLib.cc 
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) RovioLib.cc -o $@

Socket.o: Socket.cpp Socket.h
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) Socket.cpp -o $@

clean::
	$(RM) *~ *.so *.o RovioLib.cc rovio.py

