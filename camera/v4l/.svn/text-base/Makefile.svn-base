
OBJS = _v4l.so

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
LIBS= -lstdc++ -ldl -lpthread

_v4l.so: v4l.o V4L.o
	$(CC) $(CPPFLAGS) -shared v4l.o V4L.o ../device/Device.o $(LIBDIRS) -o $@ $(LIBS)

V4L.o:: V4L.cpp ../device/Device.o
	$(CC) $(CPPFLAGS) $(INCLUDE) -o $@ -c V4L.cpp

V4L.cc: V4L.i V4L.h ../device/Device.o
	swig -python $(INCLUDE) -c++ -o $@ V4L.i

v4l.o: V4L.cc ../device/Device.o
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) V4L.cc -o $@

clean::
	$(RM) *~ *.so *.o v4l.py V4L.cc 

