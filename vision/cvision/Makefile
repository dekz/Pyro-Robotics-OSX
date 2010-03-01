CC = g++

OBJS = _vision.so

include ../../Makefile.cfg
include ../../Makefile.src

INCLUDE = -I../../camera/device/
CPPFLAGS = -O3 -Wall -Wno-unused -D_POSIX_THREADS \
	-D_POSIX_THREAD_SAFE_FUNCTIONS \
	-D_REENTRANT -DPOSIX \
	-D__x86__ -D__linux__ \
	-D__OSVERSION__=2 -frepo -DUSINGTHREADS -DLINUX -D_GNU_SOURCE \
	$(PYTHON_INCLUDE) $(INCLUDE)

LIBS= -lstdc++ -ldl -lpthread

_vision.so: vision.o VisionLib.o ../../camera/device/Device.o
	$(CC) $(CPPFLAGS) -dynamiclib $^ $(LIBDIRS) -framework Python -o $@ $(LIBS)

VisionLib.o:: VisionLib.cpp
	$(CC) $(CPPFLAGS) -o $@ -c $<

VisionLib.cc: VisionLib.i VisionLib.h VisionLib.cpp
	swig $(INCLUDE) -python -c++ -o $@ VisionLib.i

vision.o: VisionLib.cc
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) $^ -o $@

clean::
	$(RM) *~ *.so *.o *.cc *.so *.pyc vision.py

