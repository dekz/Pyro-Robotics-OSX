OBJS = _geometry.so

include ../../Makefile.cfg
include ../../Makefile.src

INCLUDE = 
CPPFLAGS = -O3 -Wall -Wno-unused -D_POSIX_THREADS \
	-D_POSIX_THREAD_SAFE_FUNCTIONS \
	-D_REENTRANT -DPOSIX \
	-D__x86__ -D__linux__ \
	-D__OSVERSION__=2 -frepo -DUSINGTHREADS -DLINUX -D_GNU_SOURCE \
	$(PYTHON_INCLUDE) $(INCLUDE)

LIBS= -lstdc++ -ldl -lpthread

_geometry.so: geometry.o GeometryLib.o
	$(CC) $(CPPFLAGS) -shared $^ $(LIBDIRS) -o $@ $(LIBS)

GeometryLib.o:: GeometryLib.cpp
	$(CC) $(CPPFLAGS) -o $@ -c $<

GeometryLib.cc: GeometryLib.i GeometryLib.h GeometryLib.cpp
	swig $(INCLUDE) -python -c++ -o $@ GeometryLib.i

geometry.o: GeometryLib.cc
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) $^ -o $@

clean::
	$(RM) *~ *.so *.o *.cc *.so *.pyc geometry.py

