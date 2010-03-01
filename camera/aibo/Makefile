CC = g++
OBJS = _aibo.so

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

_aibo.so: aibo.o AiboLib.o Socket.o jpeg.o RWLock.o
	$(CC) $(CPPFLAGS) -framework Python -dynamiclib aibo.o AiboLib.o Socket.o jpeg.o RWLock.o ../device/Device.o $(LIBDIRS) -o $@ $(LIBS)

RWLock.o: RWLock.cpp RWLock.h
	$(CC) RWLock.cpp -c

jpeg.o: jpeg.c jpeg.h
	$(CC) jpeg.c -c

AiboLib.o: AiboLib.cpp AiboLib.h ../device/Device.o
	$(CC) $(CPPFLAGS) -o $@ -c AiboLib.cpp

AiboLib.cc: AiboLib.i AiboLib.h ../device/Device.o
	swig -python -c++ $(INCLUDE) -o AiboLib.cc AiboLib.i

aibo.o: AiboLib.cc 
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) AiboLib.cc -o $@

Socket.o: Socket.cpp Socket.h
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) Socket.cpp -o $@

clean::
	$(RM) *~ *.so *.o AiboLib.cc aibo.py

