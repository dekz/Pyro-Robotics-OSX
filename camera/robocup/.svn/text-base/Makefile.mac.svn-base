CC = g++
OBJS = _robocup.so

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
LIBS= -lstdc++ -ldl -lpthread

../device/Device.o: ../device/Device.h ../device/Device.cpp
	cd ../device/; make

_robocup.so: robocup.o RobocupLib.o 
	$(CC) $(CPPFLAGS) -framework Python -dynamiclib robocup.o RobocupLib.o ../device/Device.o $(LIBDIRS) -o $@ $(LIBS)

RobocupLib.o:: RobocupLib.cpp RobocupLib.h ../device/Device.o
	$(CC) $(CPPFLAGS) -o $@ -c RobocupLib.cpp

RobocupLib.cc: RobocupLib.i RobocupLib.h ../device/Device.o
	swig -python -c++ $(INCLUDE) -o RobocupLib.cc RobocupLib.i

robocup.o: RobocupLib.cc 
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) RobocupLib.cc -o $@

clean::
	$(RM) *~ *.so *.o RobocupLib.cc robocup.py

