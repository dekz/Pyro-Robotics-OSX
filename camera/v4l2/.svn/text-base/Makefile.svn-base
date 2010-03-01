
OBJS = _v4l2.so

include ../../Makefile.cfg
include ../../Makefile.src

INCLUDE = -I../device/
CPPFLAGS = -Wall -Wno-unused -D_POSIX_THREADS \
	-D_POSIX_THREAD_SAFE_FUNCTIONS \
	-D_REENTRANT -DPOSIX \
	-D__x86__ -D__linux__ \
	-D__OSVERSION__=2 -frepo -DUSINGTHREADS -DLINUX -D_GNU_SOURCE \
	$(PYTHON_INCLUDE)

LIBDIRS= 
LIBS= -lstdc++ -ldl -lpthread -ljpeg

_v4l2.so: v4l2.o V4L2.o jpeg.o
	$(CC) $(CPPFLAGS) -shared v4l2.o jpeg.o V4L2.o ../device/Device.o $(LIBDIRS) -o $@ $(LIBS)

jpeg.o: jpeg.c jpeg.h
	$(CC) jpeg.c -c

V4L2.o:: V4L2.cpp ../device/Device.o
	$(CC) $(CPPFLAGS) $(INCLUDE) -o $@ -c V4L2.cpp

V4L2.cc: V4L2.i V4L2.h ../device/Device.o
	swig -python $(INCLUDE) -c++ -o $@ V4L2.i

v4l2.o: V4L2.cc ../device/Device.o
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) V4L2.cc -o $@

clean::
	$(RM) *~ *.so *.o v4l2.py V4L2.cc 

