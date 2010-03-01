OBJS = _playercam.so

include ../../Makefile.cfg
include ../../Makefile.src

INCLUDE = -I../device/ -I/usr/local/include $(PLAYER_INCLUDE)
CPPFLAGS = -Wall -Wno-unused -D_POSIX_THREADS \
	-D_POSIX_THREAD_SAFE_FUNCTIONS \
	-D_REENTRANT -DPOSIX \
	-D__x86__ -D__linux__ \
	-D__OSVERSION__=2 -frepo -DUSINGTHREADS -DLINUX -D_GNU_SOURCE \
	$(PYTHON_INCLUDE) $(INCLUDE)

LIBS= -lstdc++ -ldl -L/usr/local/lib -L/usr/lib -lpthread -lplayerc -ljpeg  

../device/Device.o: ../device/Device.h ../device/Device.cpp
	cd ../device/; make

_playercam.so: playercam.o PlayerCamLib.o
	$(CC) $(CPPFLAGS) -shared playercam.o PlayerCamLib.o ../device/Device.o $(LIBS) -o $@ 

PlayerCamLib.o: PlayerCamLib.cpp PlayerCamLib.h ../device/Device.o
	$(CC) $(CPPFLAGS) -o $@ -c PlayerCamLib.cpp

PlayerCamLib.cc: PlayerCamLib.i PlayerCamLib.h ../device/Device.o
	swig -python -c++ $(INCLUDE) -o PlayerCamLib.cc PlayerCamLib.i

playercam.o: PlayerCamLib.cc 
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) PlayerCamLib.cc -o $@

clean::
	$(RM) *~ *.so *.o PlayerCamLib.cc playercam.py

