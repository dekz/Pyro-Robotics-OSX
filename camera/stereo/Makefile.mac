CC = g++
OBJS = _stereo.so
#OOBJS = error.o match_scanlines.o pnmio.o postprocess.o

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

_stereo.so: stereo.o StereoLib.o
	$(CC) $(CPPFLAGS) -dynamiclib stereo.o StereoLib.o ../device/Device.o -framework Python $(OOBJS) -o $@ $(LIBS)

StereoLib.o:: StereoLib.cpp StereoLib.h ../device/Device.o
	$(CC) $(CPPFLAGS) -o $@ -c StereoLib.cpp

StereoLib.cc: StereoLib.i StereoLib.h ../device/Device.o
	swig -python -c++ $(INCLUDE) -o StereoLib.cc StereoLib.i

stereo.o: StereoLib.cc
	$(CC) -c $(PYTHON_INCLUDE) $(INCLUDE) StereoLib.cc -o $@

clean::
	$(RM) *~ *.so *.o stereo.py StereoLib.cc p2p

#error.o: error.c error.h
#	$(CC) -O3 $(LIBS) -c $<
#match_scanlines.o: match_scanlines.c
#	$(CC) -O3 $(LIBS) -c $<
#pnmio.o: pnmio.c pnmio.h
#	$(CC) -O3 $(LIBS) -c $<
#postprocess.o: postprocess.c
#	$(CC) -O3 $(LIBS) -c $<

