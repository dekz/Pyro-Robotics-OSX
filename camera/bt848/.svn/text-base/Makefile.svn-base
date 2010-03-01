OBJS = _bt848.so

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

_bt848.so: bt848.o BT848.o
	$(CC) $(CPPFLAGS) -shared bt848.o BT848.o ../device/Device.o $(LIBDIRS) -o $@ $(LIBS)

BT848.o:: BT848.cpp ../device/Device.o
	$(CC) $(CPPFLAGS) $(INCLUDE) -o $@ -c BT848.cpp

BT848.cc: BT848.i BT848.h ../device/Device.o
	swig -python $(INCLUDE) -c++ -o $@ BT848.i

bt848.o: BT848.cc ../device/Device.o
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) BT848.cc -o $@

clean::
	$(RM) *~ BT848.cc bt848.py bt848.cc bt848grab *.so *.o

