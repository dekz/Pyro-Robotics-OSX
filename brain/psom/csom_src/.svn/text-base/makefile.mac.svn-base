# makefile for building python swig interfaces from c files
# ---------------------------------------------------------
# this is designed to work in a directory structure where your c object
# files are stored in another directory, with an independent makefile
# containing rules for each object file and a 'clean' rule, and the 
# interface (.i) file in the directory with this makefile (consider 
# it your python/c interface project directory)
#
# TARGET is the resultant .so file for importing to python
# INTERFACE is the interface (.i) file
# MYOBJS is a list of c object files in your c project directory
# OBJDIR is the relative path to your c project directory to the
#   interface project directory

OBJS=_csom.so
INTERFACE=som_pak.i
MYOBJS:=som_devrobs.o lvq_pak.o som_rout.o datafile.o fileio.o version.o labels.o
OBJLIB=som_pak-dev

include ../../../Makefile.cfg
include ../../../Makefile.src

CC=gcc
SWIG=swig
#On linux ld must be gcc, so you get a shared library instead of a
#statically linked one. -- WKV 2003-07-28
#LD=ld
LD=$(CC)
CC_FLAGS=-c -g -I $(PYTHON_INCLUDE)
SWIG_FLAGS=-python
LD_FLAGS=-framework Python -dynamiclib

MYOBJS:=$(patsubst %.o, $(OBJLIB)/%.o, $(MYOBJS))

$(OBJS): $(INTERFACE:.i=_wrap.o) $(MYOBJS) 
	$(LD) $(LD_FLAGS) $^ -o $@

$(INTERFACE:.i=_wrap.o): $(INTERFACE:.i=_wrap.c) $(MYOBJS:.o=.h)
	$(CC) $(CC_FLAGS) $(INTERFACE:.i=_wrap.c) $(PYTHON_INCLUDE) -I$(OBJLIB)

$(INTERFACE:.i=_wrap.c): $(INTERFACE)
	$(SWIG) $(SWIG_FLAGS) $<

$(OBJLIB)/%.o: $(OBJLIB)/%.c $(OBJLIB)/%.h
	(cd $(OBJLIB) && make $(@F)) 

clean::
	$(RM) -f $(OBJS) *.o *.html *.doc $(INTERFACE:.i=_wrap.c) core test*.cod $(OBJLIB)/core csom.py
	(cd $(OBJLIB) && make clean)


# notes on some make details:
# ---------------------------
# := variable assignments work like a normal language;
# = is a recursive variable assignment
# :: allows multiple definitions
#
# $(patsubt a, b, c) returns a string with all instances of the pattern
#   'a' found in 'c' replaced by 'b'
# $(varname:a=b) returns a string with all instances of the string 'a'
#   replaced by 'b' in the variable varname)
# % is used in pattern matching in a fairly intuitive manner
#
# $@ is the target of a rule
# $(@F) is just the file part of the target of a rule (so that for a rule
#    dir/file.o, $(@F) is equivalent to file.o)
# 
