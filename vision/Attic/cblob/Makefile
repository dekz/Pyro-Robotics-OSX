SO = .so
OBJS = blob.o hsbrgb.o

include ../../Makefile.cfg
include ../../Makefile.src

CFLAGS += -g 

INC = -I ../../camera/v4l/

all:: _blob$(SO) _hsbrgb$(SO)

%module.c : %.i %.h
	swig -python -o $@ $<

%module.o : %module.c 
	$(CC) -c $(INC) $(PYTHON_INCLUDE) -o $@ $<

_%$(SO) : %module.o %.o
	$(CC) -nodefaultlibs -nostdlib -shared -o $@ $< $(OBJS)

#blob$(SO): $(OBJS)
#	$(LD) -shared $(OBJS) $(INC) -o blob$(SO)

hsbrgb.o: hsbrgb.c hsbrgb.h
	$(CC) $(CFLAGS) $(INC) -c hsbrgb.c -o hsbrgb.o

blob.o: blob.c blob.h hsbrgb.h
	$(CC) $(CFLAGS) $(INC) -c blob.c -o blob.o

clean::
	$(RM) blob$(SO) *module.c _*$(SO) *.o *.pyc bmp.p?m blob.p?m python.pgm cap.ppm

v4lblobtest: blob.o hsbrgb.o v4lblobtest.c
	gcc -g -I../../camera/v4l/ -o v4lblobtest v4lblobtest.c blob.o hsbrgb.o ../../camera/v4l/v4lcap.o

crashtest: blob.o hsbrgb.o crashtest.c
	gcc -g -I../../camera/v4l/ -o crashtest crashtest.c blob.o hsbrgb.o ../../camera/v4l/v4lcap.o
