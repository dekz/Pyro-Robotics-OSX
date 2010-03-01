# simple makefile for maintaining a concurrent version of a built file
# (i'm using it to manage a .so file) in multiple places, where you
# want an up-to-date version in the directory with this makefile but
# there is also a copy in the directory LIB, along with a makefile there
# with a rule for building it, and a cleanall rule for, well, cleaining

LIB=csom_src
TARGET=_csom.so

# -----------------------


$(TARGET): $(LIB)/$(TARGET)
	mv $(LIB)/$(TARGET) .

$(LIB)/$(TARGET): 
	(cd $(LIB) && make $(TARGET))

clean::
	$(RM) $(TARGET) 
	(cd $(LIB) && make clean)
