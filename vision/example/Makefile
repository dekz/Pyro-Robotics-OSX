CC=g++

ifeq ($(PYROBOT),)
$(warning You do not have a PYROBOT environment variable set.)
$(warning Try:    export PYROBOT=/usr/local/pyro)
$(error )
endif

include $(PYROBOT)/Makefile.cfg

OBJS = _myvision.so
INCLUDE = -I$(PYROBOT)/camera/device/
CPPFLAGS = -O3 -Wall -Wno-unused -D_POSIX_THREADS \
	-D_POSIX_THREAD_SAFE_FUNCTIONS \
	-D_REENTRANT -DPOSIX \
	-D__x86__ -D__linux__ \
	-D__OSVERSION__=2 -frepo -DUSINGTHREADS -DLINUX -D_GNU_SOURCE \
	$(PYTHON_INCLUDE) $(INCLUDE)
LIBS= -lstdc++ -ldl -lpthread 

_myvision.so: myvision.o myVisionLib.o $(PYROBOT)/camera/device/Device.o
	$(CC) $(CPPFLAGS) -framework Python -dynamiclib $^ -o $@ $(LIBS)

myVisionLib.o:: myVisionLib.cpp
	$(CC) $(CPPFLAGS) -o $@ -c $<

myVisionLib.cc: myVisionLib.i myVisionLib.h myVisionLib.cpp
	swig $(INCLUDE) -python -c++ -o $@ myVisionLib.i

myvision.o: myVisionLib.cc
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) $^ -o $@

clean:
	$(RM) *~ *.so *.o *.cc *.so *.pyc myvision.py

