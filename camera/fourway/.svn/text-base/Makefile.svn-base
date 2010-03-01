OBJS = _fourway.so

include ../../Makefile.cfg
include ../../Makefile.src

INCLUDE = -I../device/
CPPFLAGS = -O3 -Wall -Wno-unused -D_POSIX_THREADS \
	-D_POSIX_THREAD_SAFE_FUNCTIONS \
	-D_REENTRANT -DPOSIX \
	-D__x86__ -D__linux__ \
	-D__OSVERSION__=2 -frepo -DUSINGTHREADS -DLINUX -D_GNU_SOURCE \
	$(PYTHON_INCLUDE) $(INCLUDE)

LIBS= -lstdc++ -ldl -lpthread

../device/Device.o: ../device/Device.h ../device/Device.cpp
	cd ../device/; make

_fourway.so: fourway.o FourwayLib.o
	$(CC) $(CPPFLAGS) -shared fourway.o FourwayLib.o ../device/Device.o -o $@ $(LIBS)

FourwayLib.o:: FourwayLib.cpp FourwayLib.h ../device/Device.o
	$(CC) $(CPPFLAGS) -o $@ -c FourwayLib.cpp

FourwayLib.cc: FourwayLib.i FourwayLib.h ../device/Device.o
	swig -python -c++ $(INCLUDE) -o FourwayLib.cc FourwayLib.i

fourway.o: FourwayLib.cc
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) FourwayLib.cc -o $@

clean::
	$(RM) *~ *.so *.o fourway.py FourwayLib.cc

