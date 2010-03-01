# daniel sproul, june 24, 2002
# modified june 17, 2002 (yeelin tan)

# psom is a python interface to csom.so, which is itself in turn a low-level
# python interface to the som-pak c library.

# this file implements the following classes:
#		psom
#		vector
#		dataset
#		point
#		activations

from os import getenv
import time, types
from posixpath import exists
import _csom as csom
from pyrobot import pyrobotdir

csom.set_globals()  # neither worry about nor change this
                    # doug, trust me, this sets global parameters that
                    # are invariant from som to som

class PsomError(AttributeError):
    """
    Used to indicate that an attribute reference or assignment failed
    for a psom object.
    """

class VectorError(AttributeError):
    """
    Used to indicate that an attribute reference or assignment failed
    for a vector object.
    """

class DatasetError(AttributeError):
    """
    Used to indicate that an attribute reference or assignment failed
    for a dataset object.
    """

class PointError(AttributeError):
    """
    Used to indicated that an attribute reference or assignment failed
    for a point object.
    """

class FileNotFound(IOError):
    """
    Used to indicate that an attribute does not name an existing file.
    """

# Hacks added to replace the ptrset, ptrvalue, ptrcreate functions
# from pointer.i which has been deprecated with SWIG 1.3.  cpointer.i
# is the new SWIG pointer library now.  Need to find a better way to
# determine C types.  The reason Doug checks the last 3 or 5 elements
# in myarr for type is because SWIG encodes pointers to primitive C
# types such as int *, double ***, and char ** in a representation
# that contains the actual value of the pointer and a type tag.  For
# example, the SWIG representation of the above pointers may look like
# the following: _10081012_p_int, _1008e124_ppp_double, f8ac_pp_char.
# These representations are of type str in python.

def _ptrset(myarr, item, i):
    """
    Given an array, an item, and an index, this function inserts the item
    into the array at position indexed by i.
    NOTE: Users should not ever use this function.
    """
    #print "FIXME:", repr(myarr), item, i
    if 'float' in repr(myarr):
        csom.floatarray_setitem(myarr, i, item)
    elif 'short' in repr(myarr):
        csom.shortarray_setitem(myarr, i, item)
    elif 'int' in repr(myarr):
        csom.intarray_setitem(myarr, i, item)
    elif 'char' in rep(myarr):
        csom.charstararray_setitem(myarr, i, item) # array of character pointers
    else:
        raise TypeError, myarr		
    
def _ptrvalue(myarr, i):
    """
    Given an array and an index, this function returns the value stored
    at index position i.
    NOTE: Users should not ever use this function.
    """
    if 'float' in repr(myarr):
        return csom.floatarray_getitem(myarr, i)
    elif 'short' in repr(myarr):
        return csom.shortarray_getitem(myarr, i)
    elif 'int' in repr(myarr):
        return csom.intarray_getitem(myarr, i)
    elif 'char' in repr(myarr):
        return csom.charstararray_getitem(myarr, i) # array of character pointers
    else:
        raise TypeError, myarr
    
def _ptrcreate(type, init, nitems):
    """
    Given a type and the number of elements, this function creates
    an array of the specified type and number of elements.
    The init param is unused.
    NOTE: Users should not ever use this function.
    """
    if type == "short":
        return csom.new_shortarray(nitems)
    elif type == "float":
        return csom.new_floatarray(nitems)
    elif type == "int":
        return csom.new_intarray(nitems)
    elif type == "char":
        return csom.new_charstararray(nitems) # array of character pointers
    else:
        raise TypeError, type

csom.ptrcreate = _ptrcreate
csom.ptrset = _ptrset
csom.ptrvalue = _ptrvalue

def list_to_arr(mylist,type):
    """
    Function to convert a python list into a c array/pointer.
    NOTE: Users should not ever use this function.
    
    PARAMS
    mylist: python list
    type  : type of list elements
    """
    nitems = len(mylist)
    myarr = csom.ptrcreate(type,0,nitems)
    i = 0
    for item in mylist:
        csom.ptrset(myarr,item,i)
        i += 1
    return myarr

def arr_to_list(myarr,nitems):
    """
    Function to convert a c array/pointer into a python list.
    NOTE: Users should not ever use this function.
    
    PARAMS
    myarr: c array/pointer
    type : type of array elements
    """
    """
    WKV 2003-07-28
    
    mylist = []
    for i in range(nitems):
        mylist.append(csom.ptrvalue(myarr,i))
    """
    mylist = [0] * nitems
    for i in xrange(nitems):
        mylist[i] = csom.ptrvalue(myarr, i)
    return mylist



#################################################################################
# class: psom                                                                   #
#################################################################################
class psom:
    def __init__(self, xdim='unset', ydim='unset', topol='hexa',
                 neigh='gaussian', alpha_mode='linear', radius_mode='linear',
                 rmin=0.0, rmax=1.0, dim='unset', data='unset', file='unset'):
        """
        psom: __init__()
        ----------------
        psom constructor
        In general, construct a psom, initialize it, then train/map to it,
        periodically doing something with the information it produces.
        
        PARAMS:
        xdim, ydim : x and y dimensions of the map
        topol      : topology of the map ('hexa' or 'rect'. 'hexa' by default.)
        neigh      : neighborhood type ('gaussian' or 'bubble'. 'gaussian' by default.)
        alpha_mode : function governing the decrease in learning rate
                     ('linear' or 'inverse_t'. 'linear' by default.)
        radius_mode: function governing the decrease in the radius of learning effect.
                     ('linear' or 'inverse_t'.  'linear' by default.)
        rmin,rmax  : min and max values for random init of SOM model vectors
                     (0.0 and 1.0 by default)
        dim        : length of SOM model vectors
        data       : dataset containing sample data vectors for SOM initialization
        file       : .cod file containing model vectors to be loaded into SOM
        
        USAGE:
        1. to read a som's model vectors from a .cod file (same file format as used
        in som_pak):
        >>> mysom = psom(file=filename)
        2. to create a som with model vectors evenly distributed in the space of a
        pre-existing data set:
        >>> mysom = psom(xdim,ydim,data=mydataset)
        3. to randomly initialize
        >>> mysom = psom(xdim,ydim,dim=d)
        - the values of the model vectors would be generated using the default 
        rmin and rmax values which are 0.0 and 1.0 respectively .
        or
        >>> mysom = psom(xdim,ydim,dim=d,rmin=range_min,rmax=range_max)
        - the values of the model vectors would be generated using user specified rmin
        and rmax values.
        """
            
        if(alpha_mode=='inverse_t'):
            alpha_mode = csom.INVERSE_T
        else:
            alpha_mode = csom.LINEAR
        if(radius_mode=='inverse_t'):
            radius_mode = csom.INVERSE_T
        else:
            radius_mode = csom.LINEAR
        if(file!='unset'):
            if exists(file): # som created from .cod file, so no need to specify dims
                codes = csom.open_entries(file)
                self.params = csom.construct_teach_params(codes, alpha_mode, radius_mode)
            else:
                raise FileNotFound, "File '%s' was not found" % file
        else:
            if(xdim=='unset' or ydim=='unset'):
                raise PsomError, "x and y dimensions for the map must be specified"
            if(topol=='rect'):
                topol=csom.TOPOL_RECT
            else:
                topol=csom.TOPOL_HEXA
            if(neigh=='bubble'):
                neigh=csom.NEIGH_BUBBLE
            else:
                neigh=csom.NEIGH_GAUSSIAN
            if(data=='unset'): # dataset unspecified; random init of model vectors
                if(dim=='unset'):
                    raise PsomError, "Vector dimension must be specified for random init"
                data = dataset(dim=dim) # create a dataset with user specified vector dimension
                import random
                gen = random.Random()
                for count in range(10 * xdim * ydim):
                    mylist = []
                    for i in range(dim):
                        # random() returns a floating point number between 0 and 1
                        mylist.append(gen.random() * (rmax - rmin) + rmin)
                    data.addvec(vector(mylist))
            codes = csom.lininit_codes(data.data,topol,neigh,xdim,ydim)
            self.params = csom.construct_teach_params(codes,alpha_mode,radius_mode)

        self.xdim = csom.entries_xdim_get(codes)
        self.ydim = csom.entries_ydim_get(codes)
        self.dim = csom.entries_dimension_get(codes) # dim of model vectors
        if(csom.teach_params_topol_get(csom.teach_params_counters_teach_get \
                                       (self.params)) == csom.TOPOL_RECT):
            self.topol = 'rect'
        else:
            self.topol = 'hexa'
        self.last = 'unset' # flag indicating SOM has not been trained; get_activations() will not work
        self.last_trained = 'unset'
        self.last_mapped = 'unset'
        
        self.logging = 0
        self.log_mode = 'both'
        self.log_type = 'file'
        self.log_dir = getenv("PWD") + "/"
        self.log_fprefix = "psom"
        self.log_count = 0
        self.log_file = 'unopened'
        self.log_padding = 4
        self.log_format = "%C: [%i] maps to %p at time %d-%t\n"

    def __del__(self):
        """
        psom: __del__()
        ---------------
        Added by WKV 2003-07-28
        """
        if self.params:
            if csom:
                codes = csom.teach_params_codes_get(csom.teach_params_counters_teach_get(self.params))
                csom.close_entries(codes)
                csom.free_teach_params(self.params)
            self.params = None
                                                    
                
    def init_training(self,alpha_0,radius_0,runlen,errorwindow=1):
        """
        psom: init_training()
        ---------------------
        Sets the initial learning rate, radius of learning effect and the number of
        training patterns.
        
        runlen is the number of training samples you expect to use in the current
        training session.  This number affects the rate at which alpha and radius
        decay.  By default, the decay of these is linear, such that after running
        runlen samples, alpha is zero and radius is 1.0.  It is kind of important to
        set unlen appropriately.  Instead of using the default linear decay function,
        both radius and alpha can be set to decay with an inverse time function
        (i.e alpha_mode='inverse_t'...), which can sometimes be less drastic because
        then the learning rate never actually ends up at zero, even if you exceed the
        expected runlen number of training samples.  you can also reinitialize a
        training session whenever you like (currently alpha_mode and radius_mode are
        set in stone when the psom is created, however)
        
        errorwindow is sort of an ad-hoc way of making the error value returned
        by get_error() time dependent on the last 'errorwindow' number of
        training samples.  The default is 1, which should just return the error
        associated with the most recent training sample.
        
        PARAMS
        alpha_0    : initial learning rate.  Range: 0 <= alpha_0 <= 1.0
        radius_0   : initial radius of learning effect.
                     Range: 0 <= radius_0 <= xdim or ydim (whichever is bigger)
        runlen     : number of training patterns.  Range: runlen >= 1
        errorwindow: number of previous training samples to consider when calculating
        SOM error.  Range: errorwindow >= 1 (1 by default).  See get_error().
        
        USAGE
        1. To initialize a som with a learning rate of 0.02, radius of learning effect
        of 3, and number of training patterns of 1000:
        >>> mysom.init_training(0.02,3,1000)
        
        2. Once the som is initialized, train it using one of the following:
        >>> mysom.train_from_dataset
        or
        >>> mysom.train(vector1)
        See train() and train_from_dataset().
        
        3. map() acts a lot like train() but will not actually adjust any map model
        vectors (equivalent to training with zero alpha).  See map().
        
        4. To time a training session, see timing_start().
        
        Note: error checking that was previously done in init_training_session() in
        som_devrobs.c has been moved here.
        """
        # check alpha (learning rate)
        if(alpha_0 < 0.0 or alpha_0 > 1.0):
            raise PsomError, \
                  "Invalid learning rate: %s. Alpha must be between 0 and 1.0 \
                  (inclusive)" % alpha_0
        # check radius of learning effect
        if(radius_0 < 1.0):
            raise PsomError, \
                  "Invalid radius: %s. Radius of learning effect must be at least 1" \
                  % radius_0
        # make sure radius of learning effect is not greater than map dimension
        if(radius_0 > self.xdim and radius_0 > self.ydim):
            raise PsomError, \
                  "Invalid radius: %s. SOM dimension is only %sx%s" \
                  % (radius_0, self.xdim, self.ydim)
        # runlen must be greater than or equal to 1
        if(runlen < 1):
            raise PsomError, \
                  "Invalid run length: %s. Run length must be at least 1" % runlen
        
        # error window must be greater than or equal to 1
        if(errorwindow < 1):
            raise PsomError, \
                  "Invalid size of error window: %s.  Window size must be at least 1" \
                  % errorwindow

        self.runlen = runlen
        csom.init_training_session(self.params,alpha_0,radius_0,runlen,errorwindow)

    def timing_start(self):
        """
        psom: timing_start()
        --------------------
        Start timing.
        
        USAGE:
        >>> mysom.timing_start()
        >>> mysom.train_from_dataset(mydataset)
        >>> mysom.timing_stop()
        >>> ttime = mysom.get_training_time()
        >>> print ttime
        """
        csom.timing_start(self.params)
            
    def timing_stop(self):
        """
        psom: timing_stop()
        -------------------
        Stop timing.
        
        USAGE:
        >>> mysom.timing_start()
        >>> mysom.train_from_dataset(mydataset)
        >>> mysom.timing_stop()
        >>> ttime = mysom.get_training_time()
        >>> print ttime
        """
        csom.timing_stop(self.params)
        
    def get_training_time(self):
        """
        psom: timing_stop()
        -------------------
        Returns training time if training session was timed.
        
        USAGE:
        >>> mysom.timing_start()
        >>> mysom.train_from_dataset(mydataset)
        >>> mysom.timing_stop()
        >>> ttime = mysom.get_training_time()
        >>> print ttime
        """
        return csom.get_training_time(self.params)

    # psom: som logging utility 
    def logging_set(self, mode='unset', type='unset', dir='unset', prefix='unset',
                    padding='unset', format='unset'):
        """
        psom: logging_set()
        -------------------
        This function is used to initialize logging settings.
        
        PARAMS
        mode  : specifies what kind of data vectors are logged -- those that
        are trained ('train'), those that are mapped ('map'), or 'both'.
        type  : type can be 'dir' or 'file'; 'dir' will create a separate file for
        each log entry and 'file' will create a single file, putting each entry
        on a separate line.
        dir   : directory for the target file(s)
        prefix: file prefix for the target file(s)
        format: specifies a format string:
        %i: input vector (entries separated by spaces)
        %m: model vector (entries separated by spaces)
        %p: coordinates of model vector as '(x,y)'
        %x: x coordinate of model vector
        %y: y coordinate of model vector
        %c: the current log count
        %C: a padded version of the current log count
        %d: the current date as 'MM/DD/YY'
        %D: date as 'Mon DD, YYYY'
        %e: date as 'MM/DD'
        %E: date as 'Mon DD'
        %t: the current 24-hour time as 'HH:MM:SS'
        %T: 12-hour time as 'HH:MM:SS:AM/PM'
        %u: 24-hour time as 'HH:MM'
        %U: 12-hour time as 'HH:MM:AM/PM'
        \n: newline
        \t: tab
        %%: a literal '%' sign
        """
        if(mode != 'unset'):
            if(mode != 'map' and mode != 'train' and mode != 'both'):
                raise PsomError, \
                      "Unrecognized logging mode: %s" % mode
            self.log_mode = mode
        if(type != 'unset'):
            if(type != 'file' and type != 'dir'):
                raise PsomError, \
                      "Unrecognized logging type: %s" % type
            self.log_type = type
        if(dir != 'unset'):
            if(dir[-1] != "/"):
                dir += "/"
            if(dir[0:2] == "~/"):
                dir = getenv("HOME") + dir[1:]
            if(dir[0] != "/"):
                dir = getenv("PWD") + "/" + dir
            self.log_dir = dir
        if(prefix != 'unset'):
            self.log_fprefix = prefix
        if(padding != 'unset'):
            self.log_padding = padding
        if(format != 'unset'):
            self.log_format = format

    def logging_on(self):
        """
        psom: logging_on()
        ------------------
        Turn logging on.
        """
        self.logging = 1
        if(self.log_type == 'file'):
            fname = self.log_dir + self.log_fprefix + ".log"
            self.log_file = open(fname, "a")
            
    def logging_off(self):
        """
        psom: logging_off()
        -------------------
        Turn logging off.
        """
        self.logging = 0
        if(self.log_type == 'file'):
            self.log_file.close()
            
    def logging_reset(self):
        """
        psom: logging_reset()
        ---------------------
        Reset the log count.
            """
        self.log_count = 0
        
    def logging_clear(self):
        """
        psom: logging_clear()
        ---------------------
        Remove log files
        """
        from os import system	
        if(self.log_type == 'dir'):
            fname = self.log_dir + self.log_fprefix + "[0-9]*.log"
            system("rm " + fname)
        else:
            if(self.logging):
                self.log_file.close()
            fname = self.log_dir + self.log_fprefix + ".log"
            system("rm " + fname)
            if(self.logging):
                self.log_file = open(fname, "a")

    def log(self, model_vec):
        """
        psom: log()
        -----------
        PARAMS
        model_vec:  model vector to be logged
        """
        import re
        tag = "____%____%____"  # this should be something no one will ever use
        padcnt = str(self.log_count)
        while(len(padcnt) < self.log_padding):
            padcnt = "0" + padcnt
        s = self.log_format
        s = re.sub("%%", tag, s)
        s = re.sub("%i", str(self.last), s)
        s = re.sub("%m", str(self.get_model_vector(self.last.point)), s)
        s = re.sub("%p", str(self.last.point), s)
        s = re.sub("%x", str(self.last.point.x), s)
        s = re.sub("%y", str(self.last.point.y), s)
        s = re.sub("%c", str(self.log_count), s)
        s = re.sub("%C", padcnt, s)
        s = re.sub("%t", time.strftime("%X"), s)
        s = re.sub("%T", time.strftime("%I:%M:%S:%p"), s)
        s = re.sub("%u", time.strftime("%H:%M"), s)
        s = re.sub("%U", time.strftime("%I:%M:%p"), s)
        s = re.sub("%d", time.strftime("%x"), s)
        s = re.sub("%D", time.strftime("%h %d, %Y"), s)
        s = re.sub("%e", time.strftime("%m/%d"), s)
        s = re.sub("%E", time.strftime("%h %d"), s)
        s = re.sub(tag, "%", s)
        if(self.log_type == 'dir'):
            fname = self.log_dir + self.log_fprefix + padcnt +".log"
            self.log_file = open(fname, "w")
        self.log_file.write(s)
        if(self.log_type == 'dir'):
            self.log_file.close()
        self.log_count += 1

    def map(self,vector):
        """
        psom: map()
        -----------
        Given a psom vector, this function maps the vector to the SOM.  The model
        vector of the winning node is returned.  Model vectors of neighboring nodes
        remain unchanged, i.e no learning occurs.
        
        PARAMS
        vector: vector object to be mapped
        
        USAGE
        >>> mylist = [0,1,0,2]
        >>> mysom.map(psom.vector(mylist))
        """
        # make sure dimensions of mapping vector and SOM model vector match
        if(vector.dim != self.dim):
            raise PsomError, \
                  "Mismatched dimensions of mapping vector (size %s) \
                  and model vector (size %s)" % (vector.dim, self.dim)
        
        if self.last_mapped == 'unset': # first run
            coords = csom.map_one(self.params, vector.entry,
                                  point(-1,-1).asIntPtr(),
                                  1) # 1=update counters
        else:
            coords = csom.map_one(self.params, vector.entry,
                                  self.last_mapped.asIntPtr(), 1)
        
        pt = point(csom.ptrvalue(coords,0), csom.ptrvalue(coords,1))
        csom.delete_intarray(coords) # WKV 2003-07-28
        self.last = vector
        self.last.point = pt
        self.last_mapped = pt
        
        model = self.get_model_vector(pt)
        if(self.logging and self.log_mode != 'train'):
            self.log(model)
        return model

    def train(self,vector):
        """
        psom: train()
        -------------
        Given a psom vector, this function maps the vector to the SOM.  The model
        vector of the winning node is returned.  Model vectors of neighboring nodes
        are changed so that their values are closer to that of the winnning node.
        
        PARAMS
        vector: vector to be mapped
        
        USAGE
        >>> mylist = [0,1,0,2]
        >>> mysom.train(psom.vector(mylist))
        """
        # make sure dimensions of training vector and SOM model vector match
        if(vector.dim != self.dim):
            raise PsomError, \
                  "Mismatched dimensions of training vector (size %s) \
                  and model vector (size %s)" % (vector.dim, self.dim)
        
        if self.last_trained == 'unset': # first run
            coords = csom.train_one(self.params, vector.entry,
                                    point(-1,-1).asIntPtr(),
                                    1) # 1=update counters
        else:
            coords = csom.train_one(self.params, vector.entry,
                                    self.last_trained.asIntPtr(), 1)

        pt = point(csom.ptrvalue(coords,0), csom.ptrvalue(coords,1))
        csom.delete_intarray(coords)
        self.last = vector
        self.last.point = pt
        self.last_trained = pt
        
        model = self.get_model_vector(pt)
        if(self.logging and self.log_mode != 'map'):
            self.log(model)
        
        return model
	
    def train_from_dataset(self,dataset,mode='cyclic'):
        """
        psom: train_from_dataset()
        --------------------------
        Trains SOM from vectors in a dataset.  There are two training modes: cyclic
        and rand (for random).  The dimension of the vectors in the dataset must match
        the dimension of the SOM model vectors.
        
        PARAMS
        dataset: dataset of training vectors
        mode   : mode of training from dataset ('cyclic' or 'rand'. 'cyclic' by default,
        i.e. vectors are mapped in order, and training is repeated iteratively 
        depending on the number of training patterns specifiied at initialization.)
        As for 'rand', vectors are chosen at random from the dataset. 
        
        USAGE
        >>> mydataset = psom.dataset(file=filename)
        >>> mysom.train_from_dataset(mydataset)
        """
    def train_from_dataset(self, dataset, mode='cyclic'):
        # make sure dimension of dataset vectors and SOM model vectors match
        if(dataset.dim != self.dim):
            raise PsomError, \
                  "Mismatched dimensions of training vector (size %s) \
                  and model vector (size %s)" % (dataset.dim, self.dim)
        if(mode == 'rand'):
            mode = csom.RAND
        else:
            mode = csom.CYCLIC
        
        entry = csom.train_fromdataset(self.params,dataset.data,mode)
        #self.last = vector(entry=entry,dim=self.dim)

        self.last = vector(entry=entry,dim=self.dim,
                           label=csom.get_label_data_entry(entry,
                           csom.data_entry_num_labs_get(entry)))

        coords = csom.map_one(self.params, self.last.entry,
                              point(-1,-1).asIntPtr(),
                              0) # 0=don't update counters
        pt = point(csom.ptrvalue(coords,0), csom.ptrvalue(coords,1))
        csom.delete_intarray(coords) # WKV 2003-07-28
        self.last.point = pt
        self.last_trained = pt
        return self.get_model_vector(pt)
    
    def map_from_dataset(self,dataset):
        """
        psom: map_from_dataset()
        ------------------------
        Maps vectors from a dataset in order to the SOM.  The dimension of the vectors
        in the dataset must match the dimension of the SOM model vectors.
        
        PARAMS
        dataset: dataset of vectors to be mapped
        
        USAGE
        >>> mydataset = psom.dataset(file=filename)
        >>> mysom.map_from_dataset(mydataset)
        """
        # make sure dimension of dataset vectors and SOM model vectors match
        if(dataset.dim != self.dim):
            raise PsomError, \
                  "Mismatched dimensions of training vector (size %s) \
                  and model vector (size %s)" % (dataset.dim, self.dim)
        entry = csom.map_fromdataset(self.params, dataset.data)

        #self.last = vector(entry=entry,dim=self.dim)

        self.last = vector(entry=entry, dim=self.dim,
                           label=csom.get_label_data_entry(entry, \
                           csom.data_entry_num_labs_get(entry)))

        coords = csom.map_one(self.params, self.last.entry,
                              point(-1,-1).asIntPtr(),
                              0) # 0=don't update counters
        pt = point(csom.ptrvalue(coords,0),csom.ptrvalue(coords,1))
        csom.delete_intarray(coords) # WKV 2003-07-28
        self.last.point = pt
        self.last_mapped = pt
        return self.get_model_vector(pt)

    def get_model_vector(self, point):
        """
        psom: get_model_vector()
        ------------------------
        Returns model vector of SOM node at the specified point.
        
        PARAMS
        point:  point object.  see point constructor.
        
        USAGE
        >>> mysom.get_model_vector(psom.point(2, 3))
        - this returns the model vector at node (2,3) of the SOM
        """
        codes = csom.teach_params_codes_get(csom.teach_params_counters_teach_get(self.params))
        entry = csom.get_model_vector(codes, point.asIntPtr())
        label = csom.get_label_data_entry(entry, csom.data_entry_num_labs_get(entry))
        dim = csom.entries_dimension_get(codes)
        return vector(entry=entry, dim=dim, point=point, label=label)

    def get_activations(self,mode='bubble',radius=1.0):
        """
        psom: get_activations()
        -----------------------
        Returns the som activation levels after the som has been mapped to.  Calling
        this function prior to som mapping will result in error.  For pretty
        print, call display_activations() on the return value of this function.
        
        After calling map(), train(), or train_from_dataset(), calling this function
        returns a list corresponding to the appropriate activation levels.  This can
        be done based on simple 'bubble' or 'gaussian' neighborhoods, or (as suggested
        by Doug) by assigning activation weight according to error in mapping to each
        corresponding model vector ('error').
            
        If the 'error' mode is used, the radius is taken as a tolerance parameter,
        and should vary between 0.0 to 1.0.  0.0 will look a lot more like bubble
        activation, while 1.0 will have pretty much every node activated to at least
        some degree.
        
        In summary,
        mode: bubble     radius range: >= 1.0
        mode: gaussian   radius range: >= 1.0
        mode: error      radius range: between 0 and 1.0 (inclusive)
        
        PARAMS
        mode  : 'bubble' (by default), 'gaussian', 'error'
        radius: radius of effect
            
        USAGE
        >>> myactiv = mysom.get_activations('bubble', 2.0)
        >>> myactiv = mysom.get_activations('bubble',2.0)
        >>> myactiv = mysom.get_activations('gaussian',3.0)
        >>> myactiv = mysom.get_activations('error')
        >>> myactiv = mysom.get_activations('error',0.25)
        
        Note: error values are always >= 0.0
        """
        if(self.last == 'unset'):
            raise PsomError, \
                  "Cannot get activation levels. SOM has not yet been mapped to."
        if(mode == 'gaussian' or mode == 'bubble'):
            if(mode == 'gaussian'): mode = csom.NEIGH_GAUSSIAN
            else: mode = csom.NEIGH_BUBBLE
            float_levels = csom.get_activation_levels(self.params,
                                                      self.last.point.asIntPtr(),
                                                      radius, mode)
        elif(mode == 'error'):
            float_levels = csom.get_levels_by_error(self.params,
                                                    self.last.entry,radius)
        else:
            raise PsomError, "mode %s has not yet implemented" % mode
        levels = arr_to_list(float_levels,self.xdim*self.ydim)
        csom.delete_floatarray(float_levels) # WKV 2003-07-28
        return levels

    def get_xy(self, mylist, x, y):
        """
        psom: get_xy()
        --------------
        This function allows x,y addressing of a list representation of a
        matrix.  
        
        PARAMS
        mylist: list representation of a matrix (e.g. activation levels of
        som nodes returned by get_activations())
        x     : x coordinate of matrix element
        y     : y coordinate of matrix element
        
        USAGE
        To obtain the activation level of som node at coordinate (2,3):
        >>> mysom.get_xy(get_activations(),2,3)
        """
        return mylist[x + y * self.xdim]

    def save_to_file(self, file):
        """
        psom: save_to_file()
        --------------------
        Given a filename, this function saves the SOM model vectors to a
        specified file.
        Use this function to save the model vectors after a training session.
        
        PARAMS
        file: name of file.  recommended extension: .cod
        
        USAGE
        >>> mysom.save_to_file(filename.cod)
        """
        codes = csom.teach_params_codes_get(csom.teach_params_counters_teach_get(self.params))
        csom.write_entries(codes,file)
        
    def display(self):
        """
        psom: display()
        ---------------
        Displays all model vectors in the given som.
        
        USAGE
        >>> mysom.display()
        """
        codes = csom.teach_params_codes_get(csom.teach_params_counters_teach_get(self.params))
        csom.print_dataset(codes)
        
    def display_activations(self,levels='unset'):
        """
        psom: display_activations()
        ---------------------------
        Displays som activations in pretty print.  If the levels parameter is unspecified,
        then, by default, this function displays the activation levels returned by calling
        get_activations() with gaussian mode and a radius of 1.0.  Otherwise, the user
        can specify the activation levels to be displayed by calling get_activations()
        with desired mode and radius.
            
        PARAMS
        levels: list of activation levels.  
        
        USAGE
        1. To use default display (gaussian mode and radius = 1.0):
        >>> mysom.display_activations()
        
        2. To display the activation levels returned by get_activations() with gaussian
        mode and radius of 3:
        >>> mysom.display_activations(get_activations(mode='gaussian', radius=3))
        """
        if(levels == 'unset'):
            levels = self.get_activations('gaussian')
        for j in range(0,self.ydim):
            if(j % 2 == 1 and self.topol=='hexa'):
                print "  ",
            for i in range(0,self.xdim):
                index = i + j * self.xdim
                print "%.2f" % (levels[index]),
            print ""

    def get_reg_counter(self, pt, mode):
        """
        psom: get_reg_counter()
        -----------------------
        Given a point and a mode ('train' or 'map'), this function returns
        the corresponding (regular) counter associated with that point.

        PARAMS
        pt  : point object
        mode: 'train' or 'map'

        USAGE:
        1.  To get training (regular) counter associated with point (0,2)
        >>> mysom.get_counter(point(0,2), 'train')
        2.  To get mapping (regular) counter associated with point (5,5)
        >>> mysom.get_counter(point(5,5), 'map')
        """
        if not isinstance(pt, point):
            raise TypeError, "Expecting a point object, given %s intead" % type(pt)
        if mode == 'train':
            return csom.get_reg_tcounter(self.params, pt.asIntPtr())
        elif mode == 'map':
            return csom.get_reg_mcounter(self.params, pt.asIntPtr())
        else:
            raise PsomError, "Unknown mode: %s" % mode

    def get_consec_counter(self, pt, mode):
        """
        psom: get_consec_counter()
        --------------------------
        Given a point and a mode ('train' or 'map'), this function returns
        the corresponding consecutive counter associated with that point.

        PARAMS
        pt  : point object
        mode: 'train' or 'map'

        USAGE:
        1.  To get consecutive training counter associated with point (0,2)
        >>> mysom.get_consec_counter(point(0,2), 'train')
        2.  To get consecutive mapping counter associated with point (5,5)
        >>> mysom.get_consec_counter(point(5,5), 'map')
        """
        if not isinstance(pt, point):
            raise TypeError, "Expecting a point object, given %s intead" % type(pt)
        if mode == 'train':
            return csom.get_consec_tcounter(self.params, pt.asIntPtr())
        elif mode == 'map':
            return csom.get_consec_mcounter(self.params, pt.asIntPtr())
        else:
            raise PsomError, "Unknown mode: %s" % mode
        
    def get_maxconsec_counter(self, pt, mode):
        """
        psom: get_consec_counter()
        --------------------------
        Given a point and a mode ('train' or 'map'), this function returns
        the corresponding maximum consecutive counter associated with that point.
        
        PARAMS
        pt  : point object
        mode: 'train' or 'map'
        
        USAGE:
        1.  To get maximum consecutive training counter associated with point (0,2)
        >>> mysom.get_max_consec_counter(point(0,2), 'train')
        2.  To get maximum consecutive mapping counter associated with point (5,5)
        >>> mysom.get_max_consec_counter(point(5,5), 'map')
        """
        if not isinstance(pt, point):
            raise TypeError, "Expecting a point object, given %s intead" % type(pt)
        if mode == 'train':
            return csom.get_maxconsec_tcounter(self.params, pt.asIntPtr())
        elif mode == 'map':
            return csom.get_maxconsec_mcounter(self.params, pt.asIntPtr())
        else:
            raise PsomError, "Unknown mode: %s" % mode
    
    def get_highest_counter(self, counter_type='unset', mode='unset'):
        """
        Given a mode ('train' or 'map') and a counter type ('regular' -- default,
        'consec', 'max_consec'), this function looks for the specified counter with
        the highest value, and returns a reference to the corresponding point object
        and the counter in a two-element list. Return format: [pt, counter value]

        USAGE:
        1. To get point and highest (regular) train counter:
        >>> mysom.get_highest_counter(mode='train')
        2. To get point and highest consecutive train counter:
        >>> mysom.get_highest_counter('consec', 'map')
        3. To get point and highest max consecutive map counter:
        >>> mysom.get_highest_counter('max_consec', 'train')
        """
        """
        if mode == 'train':
            dict = self.train_counter_dict
        elif mode == 'map':
            dict = self.map_counter_dict
        else:
            raise PsomError, "Unknown mode: %s" % mode
        
        if counter_type == 'consec': ct_type = 1
        elif counter_type == 'max_consec': ct_type = 2
        else: ct_type = 0
            
        max_val = 0
        max_ls = []
        for i in range(self.xdim):
            for j in range(self.ydim):
                pt = point(i,j)
                curr_val = dict[pt.__str__()][ct_type]                
                if curr_val >= max_val:
                    if curr_val > max_val:
                        max_val = curr_val
                        max_ls = []
                    max_ls.append([pt, curr_val])
        return max_ls
        """
        """
        max = 0
        for i in range(self.xdim):
            for j in range(self.ydim):
                pt = point(i,j)
                counter = self._get_highest_counter_helper(counter_type, pt, mode)
                if counter > max:
                    max = counter
        return max
                

    def _get_highest_counter_helper(self, counter_type, pt, mode):
        if counter_type == 'consec':
            self.get_consec_counter(pt, mode)
        elif counter_type == 'maxconsec':
            self.get_maxconsec_counter(pt, mode)
        else:
            self.get_reg_counter(pt, mode)
    """
#################################################################################
# class: vector                                                                 #
#################################################################################
class vector:
    """
    Used both for data and model vectors.
    get_elts() can be used to access the actual values of the entries
    in the vector.  The point data member should remain 'unset' for data
    vectors, but for model vectors represents its coordinates in the SOM
    """
    def __init__(self, elts='unset', weight=1, mask='NULL', entry='unset',
                 dim='unset', point='unset', label=[]):
	"""
	vector: __init__()
	------------------
	vector constructor
        
	PARAMS
	elts  : list of elements to be converted into a c float array
	weight: training weight of the vector (1 by default).  greater weights have
        greater training impact on the map.  weight must be >= 0.
	mask  : list of 1's and 0's.  length of mask list should be the same as that of
	        elts list.  a 1 indicates that the corresponding value in elts list would
		be ignored in computing the winning model vector.  if all values in the
		elts list are to be considered in the computation of the winning model
		vector, then the mask should be NULL or set to [0,0,...,0].
	entry : reserved for internal use.  after initialization, this param stores
	        the SWIG representation of the array pointer.
	dim   : reserved for internal use.  after initialization, this param stores
	        the size of the c array.
	point : this param should remain 'unset' for data vectors, but for model vectors
                this represents its coordinates in the som.
        label : list of integers or strings to be associated with a vector.
                e.g. ['X'], [1, 45], ['ab', 'C3'], etc.
        
        Note: Typically, all a user need worry about is the elts parameter.

	USAGE
	1. The vector constuctor is typically used in the following way:
        >>> mysom.train(vector([7,2.5,0.2]))
	2. To use masking:
        >>> mysom.train(vector([7,2.5,0.2],mask=[1,0,0])
        -- the first element of the vector (i.e. 7) will be ignored when computing the
        winning model vector.
        3. To map a vector with a label:
        >>> mysom.map(vector([7,2.5,0.2],label=['X',2,'ab','C4']))
        """
        if(elts != 'unset'):
            # make sure weight of training vector >= 0.
            # Note: This check used to be performed in som_devrobs.c
            if(weight < 0.0):
                raise VectorError, \
                      "Invalid weight for training vector: %s. \
                      Weight must be >= 0" % weight
            points = list_to_arr(elts, "float")
            dim = len(elts)

            # mask
            c_mask = 'NULL' # Warning: c_mask must be initialized to NULL, otherwise call to
                            # make_data_entry_weighted_masked() below will fail if mask is NULL.
            if(mask != 'NULL'):
                # make sure len(mask) matches vector dimension
                if (len(mask) != dim):
                    raise VectorError, \
                          "Mismatched dimensions of vector (len %s) and mask (len %s)" \
                          % (dim,len(mask))
                # make sure mask is a binary list
                for item in mask:
                    if(item != 0 and item != 1):
                        raise VectorError, \
                              "Invalid mask: %s.  Mask must be a binary list" % mask
                c_mask = list_to_arr(mask, "short") # convert mask list into a c array of shorts
            else:
                c_mask = list_to_arr([], "short")

            # label
            #c_str_label = 'NULL' # Warning: c_str_label must be initialized to NULL first.
            str_label = []
            if(len(label) != 0):
                # convert every elt in label (python list) to a string,
                # storing it in str_label, a new python list of strings.
                #str_label = []
                for item in label:
                    print str(item)
                    str_label.append(str(item))
                    
                # Null-terminate the list of strings. this is needed to determine
                # the array size in make_data_entry_weighted_masked() in som_devrobs.c
                #str_label.append(str(0)) 
                    
                # Convert list of strings into a c array of character pointers.
                # Note: each elt in c_str_label is a char pointer.  So, c_str_label is the
                # equivalent of C's char **.
                #c_str_label = list_to_arr(str_label, "char") 
                
            # create a data entry struct (see som_devrobs.c for more info)
            entry = csom.make_data_entry_weighted_masked(points, weight,
                                                         c_mask, dim,
                                                         str_label)
        # data members of vector object (separated from code for clarity)
        self.dim   = dim
        self.entry = entry
        self.point = point
        self.mask  = mask

    def get_elts(self):
        """
        vector: get_elts()
        ------------------
        Returns the original list representation of the elements in the vector.
        """
        points = csom.data_entry_points_get(self.entry)
        return arr_to_list(points, self.dim)

    def __getitem__(self, key):
        """
        vector: __getitem__()
        ---------------------
        Returns the vector element at index position given by key.
        """
        mylist = self.get_elts()
        if isinstance(key, types.SliceType):
            #WKV 2003-07-28
            
            if key.stop > len(self):
                stop = len(self)
            else:
                stop = key.stop
            return mylist[key.start:stop]

            #return mylist[key.start:key.stop] # WKV 2003-07-28
        else:
            return mylist[key]
    
    def __len__(self):
        """
        vector: __len__()
        -----------------
        Returns the length of the vector.
        """
        return len(self.get_elts())
    
    def get_weight(self):
        """
        vector: get_weight()
        --------------------
        Returns the training weight of the vector.  See vector constructor for
        more info.
        """
        return csom.data_entry_weight_get(self.entry)	
    
    def get_mask(self):
        """
        vector: get_mask()
        ------------------
        Returns the mask of the vector.  Mask is returned as a python list.
        """
        return self.mask

    # DEPRECATED
    """
    def set_label(self,label=[]):
        vector: set_label()
        -------------------
        Associates a vector with the given label.  Removes all labels previously
        associated with the vector.
        #c_str_label = 'NULL' # Warning: c_str_label must be initialized to NULL first.
        #if(label == 'NULL'):
        if(len(label) == 0):
            raise VectorError, "No label provided"
            
        # convert every elt in label (python list) to a string,
        # storing it in str_label, a new python list of strings.
        str_label = []
        for item in label:
            str_label.append(str(item))
			
        # Null-terminate the list of strings. this is needed to determine
        # the array size in make_data_entry_weighted_masked() in som_devrobs.c
        str_label.append(str(0)) 
        
        # Convert list of strings into a c array of character pointers.
        # Note: each elt in c_str_label is a char pointer.  So, c_str_label is the
        # equivalent of C's char **.
        #c_str_label = list_to_arr(str_label, "char")
		
        #csom.set_label_data_entry(self.entry, c_str_label)
        print str_label
        csom.set_label_data_entry(self.entry, str_label)
        self.label = str_label
    """
        
    #def add_label(self,label='NULL'):
    def add_label(self,label=[]):
        """
        vector: add_label()
        -------------------
        Associates a vector with the given label.  All labels previously
        associated with the vector remain unchanged.
        """
        #c_str_label = 'NULL' # Warning: c_str_label must be initialized to NULL first.
        #if(label == 'NULL'):
        if(len(label) == 0):
            raise VectorError, "No label provided"
        
        # convert every elt in label (python list) to a string,
        # storing it in str_label, a new python list of strings.
        str_label = []
        for item in label:
            str_label.append(str(item))

        # Null-terminate the list of strings. this is needed to determine
        # the array size in make_data_entry_weighted_masked() in som_devrobs.c
        #str_label.append(str(0)) 
        
        # Convert list of strings into a c array of character pointers.
        # Note: each elt in c_str_label is a char pointer.  So, c_str_label is the
        # equivalent of C's char **.
        #c_str_label = list_to_arr(str_label, "char")
        
        #csom.add_label_data_entry(self.entry, c_str_label)
        csom.add_label_data_entry(self.entry, str_label)

    def clear_label(self):
        """
        vector: clear_label()
        ---------------------
        Removes all labels associated with the vector.
        For some reason, this is giving me a segfault.
        """
        csom.clear_labels_data_entry(self.entry)
        
    def get_label(self):
        """
        vector: get_label()
        -------------------
        Returns the label list associated with the vector or 'NULL'
        if no labels are associated with this vector.
        """
        return csom.get_label_data_entry(self.entry, self.get_numlabels())

    def get_label_asString(self):
        """
        vector: get_label_asString()
        ----------------------------
        Returns the list of labels associated with the vector
        in a string representation.  Used in vis.py for labeling
        of SOM nodes in gui.
        """
        label_ls = self.get_label()
        label_str = ""
        if len(label_ls) != 0:
            for item in label_ls:
                label_str += item
        return label_str
        
    def get_numlabels(self):
        """
        Returns the number of labels associated with the vector.
        """
        return csom.data_entry_num_labs_get(self.entry)
    
    def __str__(self):
        """
        vector: __str__()
        -----------------
        Returns a string representation of all elements in the vector.  This function
        is typically called by print().  Only the elements in the vector are returned,
        i.e. weight, mask, and label are not.
        """
        
        mylist = self.get_elts()
        """
        # WKV 2003-07-28
        
        s = ""
        for elt in mylist:
            s += "%.3f" % (elt) + " "
        s = s[:-1]
        return s
        """        
        mylist = ["%.3f" % x for x in mylist]
        return " ".join(mylist)

    def display(self):
        """
        vector: display()
        -----------------
        Displays the vector as a list of values.  Datamembers (e.g. weight, mask, and
        label) associated with the vector are displayed as well.
        Format: [<vector elts>]  weight:<wt>  mask:[<mask elts>]  label:[<label elts>]
        """
        mylist = self.get_elts()
        weight = self.get_weight()
        mask   = self.get_mask()
        label  = self.get_label()
        
        print "[",
        for elt in mylist:
            print "%.3f" % (elt),
        print "] weight: %s" % weight,

        if(mask != 'NULL'):
            print " mask: [",
            for elt in mask:
                print "%s" % elt,
            print "]",
        if(label != []):
            print " label: [",
            for elt in label:
                print "\'%s\'" % elt,
            print "]"


#################################################################################
# class: dataset                                                                #
#################################################################################
class dataset:
    """
    A python front-end to the c library's wacky linked-list data set implementation.
    Can read and write to .dat files (same file format as specified in the som_pak
    documentation).  Keeps a pointer to the current position in the list, so you can
    call next() until the end of the list is reached, at which point you need to call
    rewind().  There is also a get() method, but this will interfere with the previous
    pointer (so if you call get(6) and then next(), next() will return the 7th vector
    in the list).  addvec() adds a vector to the list, and also causes wacky pointer
    behavior.  Note that it is a bad idea to try to traverse the list and add things
    to it at the same time.
    """
    
    def __init__(self, init_vector='NULL', dim='unset', file='unset'):
        """
	dataset: __init__()
	-------------------
	dataset constructor
        
	PARAMS
	init_vector: initial vector used to create dataset
	dim        : dimension of vectors in dataset
	file       : file from which the dataset is to be created
	
	USAGE
	1.  To read in a dataset from a file:
        >>> mydataset = dataset(file=filename)
        2.  To build a dataset by hand, first initialize it, either by dimension or
        with an initial vector:
        >>> mydataset = dataset(dim=4)
        or 
        >>> mydataset = dataset(initial_vector)
        Then, add vectors to it.
        >>> mydataset.addvec(vector1)
        >>> mydataset.addvec(vector2)
        """
        self.p = csom.get_eptr()
        if(file != 'unset'):
            if exists(file):
                self.data = csom.open_entries(file)
                self.dim = csom.entries_dimension_get(self.data)
            else:
                raise FileNotFound, "File '%s' was not found" % file
        else:
            """
            WKV 2003-07-28
            
            if(init_vector != 'NULL'):
                dim = init_vector.dim	
            self.data = csom.init_dataset(dim)
            if(init_vector != 'NULL'):
                self.addvec(init_vector)
            self.dim = dim
            """
            # Code works the same, but it's probably clearer this way.  YT
            if(init_vector != 'NULL'):
                dim = init_vector.dim
                self.data = csom.init_dataset(dim)
                self.addvec(init_vector)
            else:
                self.data = csom.init_dataset(dim)
            self.dim = dim
            
    # this was giving me problems with python2.2's garbage collection
    # no idea why, but if you are creating a whole lot of datasets
    # with this commented out you might end up with a memory leak
    #def __del__(self):
    #   csom.close_entries(self.data)

    # Fixed other memory corruptions, uncommented and didn't find problems.
    # -- WKV 2003-07-23
    # close_entries() may not mix with init_dataset (the entries structures
    # are slightly different), however it appears to work.  If things start
    # acting likve memory corruption you could try commenting out the
    # close_entries() call.  WKV 2003-07-28
    def __del__(self):
        csom.close_entries(self.data)
        csom.free_eptr(self.p)

    def addvec(self, vec):
        """
        dataset: addvec()
        -----------------
        Adds a vector to the dataset.
        """
        csom.addto_dataset(self.data, vec.entry)

    def rewind(self):
        """
	dataset: rewind()
	-----------------
        Rewinds the dataset.
	"""
        entry = csom.rewind_entries(self.data, self.p)
        return vector(entry=entry,dim=self.dim)

    def next(self):
        """
	dataset: next()
	---------------
        Get the next entry in the dataset and return it as a vector.
	"""
        entry = csom.next_entry(self.p)
        return vector(entry=entry,dim=self.dim)

    def get(self, index):
        """
	dataset: get()
	--------------
        Get the data entry at position given by index, and return
        it as a vector.
	"""
        if(index >= self.n_vectors()):
            raise IndexError, "Dataset index out of bounds"
        vec = self.rewind()
        i = 0
        while(i < index):
            vec = self.next()
            i = i+1
        return vec

    def load_from_file(self,file):
        """
	dataset: load_from_file()
	-------------------------
        Given a filename, this function reloads the dataset from the file.
	"""
        csom.close_entries(self.data)
        self.data = csom.open_entries(file)
        self.dim = csom.entries_dimension_get(self.data)

    def save_to_file(self,file):
        """
	dataset: save_to_file()
	-----------------------
        Given a filename, this function saves the dataset to the file.
	"""
        csom.write_entries(self.data, file)  # WKV 2003-07-28

    def n_vectors(self):
        """
	dataset: n_vectors()
	--------------------
        Returns the number of entries in the dataset.
	"""
        return csom.entries_num_entries_get(self.data)

    def display(self):
        """
	dataset: display()
	------------------
        Displays the entire dataset.
	"""
        csom.print_dataset(self.data)			



#################################################################################
# class: point                                                                  #
#################################################################################
class point:
    """
    simple x,y coordinate holder
    mypoint.x is equivalent to mypoint[0], mypoint.y to mypoint[1]
    mypoint.asList() will give you an actual list
    """

    def __init__(self, x=0, y=0):
        """
	point: __init()
	---------------
	point constructor
	
	PARAMS
	x: x coordinate of point
	y: y coordinate of point
	"""
        self.x = x
        self.y = y
        self.__array = None # WKV 2003-07-28

    def __getitem__(self,key):
        """
        point: __getitem__()
        --------------------
        This function returns either the x or y value of a point depending on
        the specified key.
        
        PARAMS: key (0 returns the x value, 1 returns the y value)
        """
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        raise PointError, "Invalid address to 'point' class data member"
    
    def __len__(self):
        """
        point: __len__()
        ----------------
        Returns the length of a point.
        """
        return 2
        
    def asList(self):
        """
        point: asList()
        ---------------
        Returns a two-element python list set to the values in the point object
        """
        """
        YT 2003-07-30
        
        mylist = []
        mylist.append(self.x)
        mylist.append(self.y)
        return mylist
        """
        return [self.x, self.y]

    def isEqual(self, pt):
        if self.x == pt.x and self.y == pt.y:
            return 1
        return 0
    
    def asIntPtr(self):
        """
        point: asIntPtr()
        -----------------
        Returns a c array of two integers set to the values in the point
        object.
        
        NOTE: This function is intended for internal use only.  Don't use it!
        """
        """
        WKV 2003-07-28
        
        ptr = csom.ptrcreate("int",0,2)
        csom.ptrset(ptr,self.x,0)
        csom.ptrset(ptr,self.y,1)
        return ptr
        """
        if not self.__array:
            self.__array = csom.ptrcreate("int", 0, 2)
            #csom.ptrset(self.__array, self.x, 0)
            #csom.ptrset(self.__array, self.y, 1)
        csom.ptrset(self.__array, self.x, 0) # YT 2003-07-29
        csom.ptrset(self.__array, self.y, 1) # YT 2003-07-29
        return self.__array

    def __str__(self):
        """
        point: __str__()
        ----------------
        Returns a string representation of the point object.  By default, print()
        calls this function.
        """
        return "(%d,%d)" % (self.x,self.y)

    def display(self):
        """
        point: display()
        ----------------
        Displays point object as a string.
        """
        print self.__str__()


#################################################################################
# main function for testing purposes                                            #
#################################################################################
if(__name__ == '__main__'):
    """
    Main function for testing purposes
    these tests closely follow the tests implemented for csom.so
    (test_csom.py) and for som_pak-dev (test_devrobs.c)
    
    To test, run this file as a program, i.e. python __init__.py
    """

    # test 1:
    # SOM's model vectors are read in from ex.cod.  SOM is then trained
    # using a dataset created from ex.dat.  After training, model vectors
    # are saved to test1.cod.
    # The training/map counters are saved to test1.<train/map>_counter.
    print "test 1: som from file, data from file, train from dataset"
    print "---------------------------------------------------------"
    if 1:
        mysom = psom(file=pyrobotdir() + '/brain/psom/ex.cod')
        mydataset = dataset(file=pyrobotdir() + '/brain/psom/ex.dat')
        mysom.init_training(0.02,4.0,5000)
        mysom.timing_start()
        # test train_from_dataset
        mysom.train_from_dataset(mydataset)
        #mysom.train_from_dataset(mydataset)
        mysom.timing_stop()
        ttime = mysom.get_training_time()
        mysom.save_to_file("test1.cod")
        print "training session completed in", ttime, "seconds"
        print "output written to file \"test1.cod\""
        print "for verification, compare to test_csom.py output \"test1.cod\""
        print "  and to test_devrobs output \"test1_verify.cod\""
        print "test 1 successfully completed"

        # test train counters
        test1t_fd = open("test1.train_counter", "w")
        test1t_fd.write("*** Train Counter ***\n")
        for i in range(mysom.xdim):
            for j in range(mysom.ydim):
                pt = point(i,j)
                tcounter = mysom.get_reg_counter(pt, 'train')
                test1t_fd.write("point: %s\tcounter: %s\n" % \
                                (pt.__str__(), tcounter))
        test1t_fd.write("*** End Train Counter ***\n")

        test1t_fd.write("*** Consec Train Counter ***\n")
        for i in range(mysom.xdim):
            for j in range(mysom.ydim):
                pt = point(i,j)
                consec_tcounter = mysom.get_consec_counter(pt, 'train')
                test1t_fd.write("point: %s\tconsec_counter: %s\n" % \
                                (pt.__str__(), consec_tcounter))
        test1t_fd.write("*** End Consec Train Counter\n")

        test1t_fd.write("*** Max Consec Train Counter ***\n")
        for i in range(mysom.xdim):
            for j in range(mysom.ydim):
                pt = point(i,j)
                maxconsec_tcounter = mysom.get_maxconsec_counter(pt, 'train')
                test1t_fd.write("point: %s\tmax_consec_counter: %s\n" % \
                                (pt.__str__(), maxconsec_tcounter))
        test1t_fd.write("*** End Max Consec Train Counter ***\n")
        test1t_fd.close()
        print "==> Test 1: Train counters written to: %s\n" % \
              'test1.train_counter'

        # test map_from_dataset
        print "Testing map from dataset"
        mysom1a = psom(file=pyrobotdir() + '/brain/psom/ex.cod')
        mysom1a.timing_start()
        mysom1a.map_from_dataset(mydataset)
        #mysom1a.map_from_dataset(mydataset)
        mysom1a.timing_stop()
        ttime = mysom1a.get_training_time()
        print "Mapping took", ttime, "seconds"

        # test map counters
        test1m_fd = open("test1.map_counter", "w")
        test1m_fd.write("*** Map Counter ***\n")
        for i in range(mysom1a.xdim):
            for j in range(mysom1a.ydim):
                pt = point(i,j)
                mcounter = mysom1a.get_reg_counter(pt, 'map')
                test1m_fd.write("point: %s\tcounter: %s\n" % \
                                (pt.__str__(), mcounter))
        test1m_fd.write("*** End Map Counter ***\n")

        test1m_fd.write("*** Consec Map Counter ***\n")
        for i in range(mysom1a.xdim):
            for j in range(mysom1a.ydim):
                pt = point(i,j)
                consec_mcounter = mysom1a.get_consec_counter(pt, 'map')
                test1m_fd.write("point: %s\tconsec_counter: %s\n" % \
                                (pt.__str__(), consec_mcounter))
        test1m_fd.write("*** End Consec Map Counter ***\n")

        test1m_fd.write("*** Max Consec Map Counter ***\n")
        for i in range(mysom1a.xdim):
            for j in range(mysom1a.ydim):
                pt = point(i,j)
                maxconsec_mcounter = mysom1a.get_maxconsec_counter(pt, 'map')
                test1m_fd.write("point: %s\tmax_consec_counter: %s\n" % \
                                (pt.__str__(), maxconsec_mcounter))
        test1m_fd.write("*** End Max Consec Counter ***\n")
        test1m_fd.close()
        print "==> Test 1: Map counters written to: %s\n" % 'test1.map_counter'


        # test 2:
        # SOM is randomly initialized using dataset created from ex.dat.  SOM is
        # then trained using the same dataset.  After training, model vectors
        # are saved to test2.cod.
        print "test 2: dataset from file, som randinit from data, train from dataset"
        print "---------------------------------------------------------------------"
        mysom2 = psom(12,8,data=mydataset)
        mysom2.init_training(0.02,4.0,5000)
        mysom2.timing_start()
        mysom2.train_from_dataset(mydataset)
        mysom2.timing_stop()
        ttime = mysom2.get_training_time()
        mysom2.save_to_file("test2.cod")
        print "training session completed in", ttime, "seconds"
        print "last vector produces the following gaussian SRN activations:"
        myact = mysom2.get_activations('gaussian',2.0)
        mysom2.display_activations(myact)
        print "last vector produces the following error-based SRN activations:"
        myact = mysom2.get_activations('error')
        mysom2.display_activations(myact)
        print "output written to file \"test2.cod\""
        print "test 2 successfully completed\n"

        # test 3:
        # SOM is randomly initialized to values between 0 and 10.  The initial model
        # vectors (before training) are saved to test3a.cod.  SOM is then trained
        # using the dataset created from ex.dat, and the model vectors (after training)
        # are saved to test3b.cod.
        print "test 3: dataset from file, som pure randinit, train from dataset"
        print "----------------------------------------------------------------"
        mysom3 = psom(12,8,dim=5,rmin=0.0,rmax=10.0)
        mysom3.save_to_file("test3a.cod")
        print "initial som written to file \"test3a.cod\""
        mysom3.init_training(0.02,4.0,5000)
        mysom3.timing_start()
        mysom3.train_from_dataset(mydataset)
        mysom3.timing_stop()
        ttime = mysom3.get_training_time()
        mysom3.save_to_file("test3b.cod")
        print "training session completed in", ttime, "seconds"
        print "last vector produces the following gaussian SRN activations:"
        myact = mysom3.get_activations('gaussian',2.0)
        mysom3.display_activations(myact)
        print "last vector produces the following error-based SRN activations:"
        myact = mysom3.get_activations('error')
        mysom3.display_activations(myact)
        print "output written to file \"test3b.cod\""
        print "test 3 successfully completed\n"

        # test 4:
        # SOM's model vectors are read in from ex.cod.  SOM is then trained on
        # 4 manually created training vectors.  SOM's model vectors are saved to
        # test4.cod after training.
        print "test 4: data/training dynamic, view SRN levels"
        print "----------------------------------------------"
        mysom4 = psom(file=pyrobotdir() + '/brain/psom/ex.cod')
        mysom4.init_training(0.02,8,6)
        vecs = []
        vecs.append(vector([13.57, 12.61, -1.38, -1.99, 399.77]))
        vecs.append(vector([19.58, 13.08, -1.17, -0.84, 400.03]))
        vecs.append(vector([29.36, 38.69, -1.10, -0.87, 405.21],
                           weight=3, mask=[1,0,0,1,0],
                           label=['X', 13, 'ab', 'C4']))
        vecs.append(vector([19.82, 27.08, -2.35, -3.70, 404.86]))
        vecs.append(vector([19.82, 27.08, -2.35, -3.70, 404.86]))
        vecs.append(vector([19.58, 13.08, -1.17, -0.84, 400.03]))

        mydataset = dataset(vecs[0])

        print "Adding vectors to dataset, displaying mask and labels"
        for i in range(1,5):
            vecs[i].display()
            mydataset.addvec(vecs[i])
            print "\n-->Prev label: %s" % vecs[i].get_label_asString()
            vecs[i].add_label([i])
            print "-->New Label : %s" % vecs[i].get_label_asString()
            if(i==3):
                vecs[i].clear_label()
                print "Label at vecs[%s] cleared" % i
            print "\n"
        print "Displaying dataset..."
        mydataset.display()
        print "\n"

        mysom4.logging_set(type="file", prefix="psomtest", mode="train")
        mysom4.logging_clear()
        mysom4.logging_on()

        # Make sure model vectors were updated during training
        # Compare this output with the ones printed under
        # "AFTER TRAINING"
        """
        print "****** BEFORE TRAINING *******"
        print "Model vector at point:"
        print "(0,4): ", mysom4.get_model_vector(point(0,4))
        print "(0,6): ", mysom4.get_model_vector(point(0,6))
        print "(7,4): ", mysom4.get_model_vector(point(7,4))
        print "(3,4): ", mysom4.get_model_vector(point(3,4))
        print "(3,4): ", mysom4.get_model_vector(point(3,4))
        print "(0,6): ", mysom4.get_model_vector(point(0,6))
        print "******************************"
        """
        # Training
        i=0
        for v in vecs:
            print "\nTraining vector #%s" % i
            i += 1
            m = mysom4.train(v)
            print "input vector",
            v.display()
            print "maps to model vector",
            m.display()
            print "at point",
            m.point.display()
        mysom4.logging_off()

        # Make sure model vectors were updated during training
        # Compare this output with the ones printed under
        # "BEFORE TRAINING"
        """
        print "\n****** AFTER TRAINING *******"
        print "Model vector at point:"
        print "(0,4): ", mysom4.get_model_vector(point(0,4))
        print "(0,6): ", mysom4.get_model_vector(point(0,6))
        print "(7,4): ", mysom4.get_model_vector(point(7,4))
        print "(3,4): ", mysom4.get_model_vector(point(3,4))
        print "(3,4): ", mysom4.get_model_vector(point(3,4))
        print "(0,6): ", mysom4.get_model_vector(point(0,6))
        print "******************************\n"
        """
        print "\nlast mapping produces the following bubble srn activations:"
        myact = mysom4.get_activations()
        mysom4.display_activations(myact)
        print "last mapping produces the following gaussian srn activations:"
        myact = mysom4.get_activations('gaussian',2.0)
        mysom4.display_activations(myact)
        print "error-based srn activations, tolerance 1.0:"
        myact = mysom4.get_activations('error')
        mysom4.display_activations(myact)
        print "error-based srn activations, tolerance 0.5:"
        myact = mysom4.get_activations('error', 0.5)
        mysom4.display_activations(myact)

        mysom4.save_to_file("test4.cod")
        print "output written to \"test4.cod\""
        print "log written to \"psomtest.log\""

        test4t_fd = open("test4.train_counter", "w")    
        test4t_fd.write("*** Train Counter ***\n")
        for i in range(mysom4.xdim):
            for j in range(mysom4.ydim):
                pt = point(i,j)
                tcounter = mysom4.get_reg_counter(pt, 'train')
                test4t_fd.write("point: %s\tcounter: %s\n" % \
                             (pt.__str__(), tcounter))
        test4t_fd.write("*** End Train Counter ***\n")

        test4t_fd.write("*** Consec Train Counter ***\n")
        for i in range(mysom4.xdim):
            for j in range(mysom4.ydim):
                pt = point(i,j)
                consec_tcounter = mysom4.get_consec_counter(pt, 'train')
                test4t_fd.write("point: %s\tconsec_counter: %s\n" % \
                             (pt.__str__(), consec_tcounter)) 
        test4t_fd.write("*** End Consec Train Counter ***\n")

        test4t_fd.write("*** Max Consec Train Counter ***\n")
        for i in range(mysom4.xdim):
            for j in range(mysom4.ydim):
                pt = point(i,j)
                maxconsec_tcounter = mysom4.get_maxconsec_counter(pt, 'train')
                test4t_fd.write("point: %s\tmax_consec_counter: %s\n" % \
                                (pt.__str__(), maxconsec_tcounter))
        test4t_fd.write("*** End Max Consec Train Counter ***\n")
        test4t_fd.close()
        print "==> Test 4: Train counters written to: %s\n" % \
              'test4.train_counter'

        # Make sure model vectors were not updated during mapping
        # Compare with "AFTER MAPPING"
        """
        print "\n******* BEFORE MAPPING ********"
        print "Model vector at point:"
        print "(0,4): ", mysom4.get_model_vector(point(0,4))
        print "(0,6): ", mysom4.get_model_vector(point(0,6))
        print "(7,4): ", mysom4.get_model_vector(point(7,4))
        print "(3,4): ", mysom4.get_model_vector(point(3,4))
        print "(3,4): ", mysom4.get_model_vector(point(3,4))
        print "(0,6): ", mysom4.get_model_vector(point(0,6))
        print "*******************************"
        """
        # Mapping

        i=0
        for v in vecs:
            print "\nMapping vector #%s" % i
            i += 1
            m = mysom4.map(v)
            print "input vector",
            v.display()
            print "maps to model vector",
            m.display()
            print "at point",
            m.point.display()

        """
        print "\n******* AFTER MAPPING ********"
        print "Model vector at point:"
        print "(0,4): ", mysom4.get_model_vector(point(0,4))
        print "(0,6): ", mysom4.get_model_vector(point(0,6))
        print "(7,4): ", mysom4.get_model_vector(point(7,4))
        print "(3,4): ", mysom4.get_model_vector(point(3,4))
        print "(3,4): ", mysom4.get_model_vector(point(3,4))
        print "(0,6): ", mysom4.get_model_vector(point(0,6))
        print "********************************\n"
        """
        test4m_fd = open("test4.map_counter", "w")    
        test4m_fd.write("*** Map Counter ***\n")
        for i in range(mysom4.xdim):
            for j in range(mysom4.ydim):
                pt = point(i,j)
                mcounter = mysom4.get_reg_counter(pt, 'map')
                test4m_fd.write("point: %s\tcounter: %s\n" % \
                             (pt.__str__(), mcounter))
        test4m_fd.write("*** End Map Counter ***\n")

        test4m_fd.write("*** Consec Map Counter ***\n")
        for i in range(mysom4.xdim):
            for j in range(mysom4.ydim):
                pt = point(i,j)
                consec_mcounter = mysom4.get_consec_counter(pt, 'map')
                test4m_fd.write("point: %s\tconsec_counter: %s\n" % \
                             (pt.__str__(), consec_mcounter)) 
        test4m_fd.write("*** End Consec Map Counter ***\n")

        test4m_fd.write("*** Max Consec Map Counter ***\n")
        for i in range(mysom4.xdim):
            for j in range(mysom4.ydim):
                pt = point(i,j)
                maxconsec_mcounter = mysom4.get_maxconsec_counter(pt, 'map')
                test4m_fd.write("point: %s\tmax_consec_counter: %s\n" % \
                                (pt.__str__(), maxconsec_mcounter))
        test4m_fd.write("*** End Max Consec Map Counter ***\n")
        test4m_fd.close()
        print "==> Test 4: Map counters written to: %s\n" % 'test4.map_counter'
