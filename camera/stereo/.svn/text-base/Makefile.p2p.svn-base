MAIN = p2p
OBJS = error.o match_scanlines.o pnmio.o postprocess.o
OBJS_SGI = error.u match_scanlines.u pnmio.u postprocess.u
SRCS = $(OBJS:.o=.c) $(MAIN).c
COPT = -fullwarn
CC = gcc
CC_SGI = cc

all:  $(MAIN)

.c.o: 
	$(CC) -O3 -c $<

.c.u: 
	$(CC_SGI) -j $(COPT) $<

$(MAIN): $$@.c $(OBJS)
	$(CC) -O3 -o $@ $(OBJS) $@.c

$(MAIN)-SGI: $(MAIN).c $(OBJS_SGI)
	$(CC_SGI) -O3 $(COPT) -o $(MAIN) $(OBJS_SGI) $(MAIN).c

clean:
	\rm -f *.o *.a *.u
