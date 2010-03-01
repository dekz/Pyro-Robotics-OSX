/* som_devrobs.h
 * -------------
 * june 14, 2002
 * Daniel Sproul, sproul@sccs.swarthmore.edu
 * header for som_devrobs.c
 * ----------------------------------
 */

%module csom

%{
#include "som_devrobs.h"
#include "som_rout.h"
#include "datafile.h"
#include "labels.h" /* WKV 2003-07-28 */
%}


//%include cpointer.i
%include typemaps.i
%include carrays.i
%array_functions(float,floatarray)
%array_functions(short,shortarray)
%array_functions(int,intarray)
%array_functions(char, chararray)
%array_functions(char*,charstararray)
//%include cdata.i
//%cdata(char)
//%include cstring.i
//%cstring_output_allocate(char **s, free(*$1))
//%cstring_output_allocate_size(char **x, int *slen, free(*$1))

//passing in char ** to functions
%typemap(in) char ** label {
	int i, size;
	//Check if is a list
	if(!PyList_Check($input)) {
		PyErr_SetString(PyExc_TypeError, "Not a list");
		return NULL;	
	}
	
	size = PyList_Size($input);
	i = 0;
	$1 = (char **) malloc((size+1)*sizeof(char *));
	for(i=0; i<size; i++) {
		PyObject *o = PyList_GetItem($input, i);
		if(PyString_Check(o)) 
			$1[i] = PyString_AsString(o);
		else {
			PyErr_SetString(PyExc_TypeError, "List must contain strings");
			free($1);
			return NULL;
		}
	}
	$1[i] = NULL;
}

//cleanup argument data.  free up resources allocated when the wrapper function exits.

%typemap(freearg) char ** label {
	if($1) free($1);
}

//to return labels from c function
%typemap(out) char ** {
	int i;
	if(arg2 == 0) return PyList_New(0);
	$result = PyList_New(arg2);
	for(i=0; $1[i] != NULL; i++){
		PyObject *o = PyString_FromString($1[i]);
		PyList_SetItem($result, i, o);
	}	
}

#define CYCLIC    0   // for train_fromdataset()
#define RAND      1   // for train_fromdataset()
#define LINEAR    0   // for construct_teach_params()
#define INVERSE_T 1   // for construct_teach_params()
#define NO_TRAIN  0   // for input_one()
#define TRAIN     1   // for input_one()

#define REGULAR    0  // for get_reg_tcounter(), get_reg_mcounter()
#define CONSEC     1  // for get_consec_tcounter(), get_consec_mcounter()
#define MAX_CONSEC 2  // for get_maxconsec_tcounter(), get_maxconsec_mcounter()

#define TOPOL_HEXA 3
#define TOPOL_RECT 4
#define NEIGH_BUBBLE   1
#define NEIGH_GAUSSIAN 2




/* --------------- some data structures --------------------------- */

struct data_entry {
    float  *points;
    union {
      int  *label_array;
      int  label;
    } lab;
    short  num_labs;
    short  weight;
    struct data_entry *next;
    char   *mask;  
    struct fixpoint *fixed;
  };

struct entries {
  short dimension;      /* dimension of the entry */
  short topol;          /* topology type */
  short neigh;          /* neighbourhood */
  short xdim, ydim;     /* dimensions of the map */
  struct data_entry *current;  /* current entry */
  struct data_entry *entries;  /* pointer to entries */
  long num_loaded;      /* number of lines loaded in entries list */
  long num_entries;     /* number of entries in the data set if known */
  struct {
    unsigned int loadmode;
   	unsigned int totlen_known;
    unsigned int random_order; 
    unsigned int skip_empty; 
    unsigned int labels_needed; 
  } flags;
  int lap;               /* how many times have all samples been used */
  struct file_info *fi;  /* file info for file if needed */
  long buffer;           /* how many lines to read from file at one time */
};

struct teach_params {
  short topol;
  short neigh;
  short alpha_type;
  MAPDIST_FUNCTION *mapdist;  /* calculates distance between two units */
  DIST_FUNCTION *dist;        /* calculates distance between two vectors */
  NEIGH_ADAPT *neigh_adapt;   /* adapts weights */
  VECTOR_ADAPT *vector_adapt; /* adapt one vector */
  WINNER_FUNCTION *winner;    /* function to find winner */
  ALPHA_FUNC *alpha_func;
  ALPHA_FUNC *radius_func;  // used for devrobs hacks
  float radius;               /* initial radius (for SOM) */
  float alpha;                /* initial alpha value */
  long length;                /* length of training */
  long count;  // current training iteration, used by devrobs modifications
  double qerror;       // devrobs error tracking
  float error_factor;  // ditto
  int knn;                    /* nearest neighbours */
  struct entries *codes;
  struct entries *data;
  struct snapshot_info *snapshot;
  time_t start_time, end_time;
};

struct teach_params_counters {
  struct teach_params *teach;
  unsigned int ***tcounters; /* 3 training counters per som node */
  unsigned int ***mcounters; /* 3 mapping counters per som node */
  int counters_xdim;
  int counters_ydim;
};

/* ------------------- from datafile.h: ------------------------------ */
/* ------------------------------------------------------------------- */

extern struct entries *open_entries(char *name);
extern void close_entries(struct entries *entries);
extern struct data_entry *rewind_entries(struct entries *entries, eptr *p);
extern struct data_entry *next_entry(eptr *p);

/* ------------------- from som_rout.h: ------------------------------ */
/* ------------------------------------------------------------------- */

extern struct entries *lininit_codes(struct entries *data, int topol,
                                  int neigh, int xdim, int ydim);
extern struct entries *randinit_codes(struct entries *data, int topol, 
                                   int neigh, int xdim, int ydim);

/* ------------------- from som_devrobs.h: --------------------------- */
/* ------------------------------------------------------------------- */

extern int write_entries(struct entries *codes, char *out_code_file);
extern void set_globals(void);
extern eptr *get_eptr(void);
extern void free_eptr(eptr *);

/* --------------------- data set manipulation functions ----------------- */

extern struct entries *init_dataset(int dim);
extern void free_dataset(struct entries *);
extern int addto_dataset(struct entries *data, struct data_entry *entry);
extern struct data_entry *make_data_entry_weighted_masked(float *points, 
                                           short weight, short *mask, int dim,
					   char **label);
extern void free_data_entry(struct data_entry *entry);
extern struct data_entry *make_data_entry(float *points);

/* --------------------- label manipulation functions ----------------- */
extern int find_conv_to_ind(char *str);
extern char *find_conv_to_lab(int ind);
extern int number_of_labels();
extern void free_labels();

//extern int set_label_data_entry(struct data_entry *entry, char **label);
extern void add_label_data_entry(struct data_entry *entry, char **label);
extern void clear_labels_data_entry(struct data_entry *entry);

/* ------------------ training session initialization functions ---------- */

extern struct teach_params_counters *construct_teach_params(struct entries *codes,
                                            short alpha_mode, 
                                            short radius_mode);
extern void free_teach_params(struct teach_params_counters *);
extern int init_training_session(struct teach_params_counters *params,
        	                  float alpha_0, float radius_0, long length,
                	          long qerror_window);
extern int setup_snapshot(struct teach_params_counters *params,
                   	char *snapfile_prefix, long interval);

/* ------------------- counter manipulation functions ----------------- */
extern void setup_counters(struct teach_params_counters *params);
extern void free_counters(struct teach_params_counters *params);
extern void update_counters(unsigned int ***counters, int *curr_coords, 
				int *last_coords);
extern int get_reg_tcounter(struct teach_params_counters *params, int *coords);
extern int get_consec_tcounter(struct teach_params_counters *params, int *coords);
extern int get_maxconsec_tcounter(struct teach_params_counters *params, int *coords);

extern int get_reg_mcounter(struct teach_params_counters *params, int *coords);
extern int get_consec_mcounter(struct teach_params_counters *params, int *coords);
extern int get_maxconsec_mcounter(struct teach_params_counters *params, int *coords);

extern int get_counter(struct teach_params_counters *params, 
			int *coords, short mode, int counter_type);

/* ------------------ training/mapping functions ---------------------- */

extern int *input_one(struct teach_params_counters *params,
	          	struct data_entry *sample, short mode, 
			int *last_coords, int update_counter_flag);
extern int *map_one(struct teach_params_counters *params, 
			struct data_entry *sample, 
			int *last_coords, int update_counter_flag);
extern int *train_one(struct teach_params_counters *params, 
			struct data_entry *sample, 
			int *last_coords, int update_counter_flag);
/*
extern struct data_entry *train_fromdataset_old(struct teach_params_counters *params, 
						struct entries *data, short mode);
*/
extern struct data_entry *train_fromdataset(struct teach_params_counters *params, 
						struct entries *data, short mode);
extern struct data_entry *map_fromdataset(struct teach_params_counters *params, 
				   		struct entries *data);

/* ------------------- training timing functions ---------------------- */

extern void timing_start(struct teach_params_counters *params);
extern void timing_stop(struct teach_params_counters *params);
extern int get_training_time(struct teach_params_counters *params);

/* -------------- functions for getting info about SOM state ---------- */

extern float get_error(struct teach_params_counters *params);
extern float *get_activation_levels(struct teach_params_counters *params,
	                             int *coords, float radius, short mode);
extern float *get_levels_by_error(struct teach_params_counters *params,
                struct data_entry *sample, float tolerance);
extern struct data_entry *get_model_vector(struct entries *codes, int *coords);
extern void print_dataset(struct entries *data);

/* ------ testing ------ */

extern char *get_mask_data_entry(struct data_entry *entry, int dim);

extern char **get_label_data_entry(struct data_entry *entry, int num_labels);
//extern void foo(char **s);
