/* som_devrobs.c
 * -------------
 * june 12, 2002
 * Daniel Sproul, sproul@sccs.swarthmore.edu
 * modifications to som_pak-3.1 to create desired functions for use
 * in Developmental Robotics project.  to be wrapped in python with swig
 * and incorporated in Pyro
 * ----------------------------------
 */

#include <stdio.h>
#include <float.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

#include "lvq_pak.h"
#include "som_rout.h"
#include "datafile.h"
#include "som_devrobs.h"

/* write_entries()
 * ---------------
 * just a silly wrapper for the save_entries() macro because swig does
 * not support macros 
 */
int write_entries(struct entries *codes, char *out_code_file) {
  return save_entries(codes, out_code_file); }

/* set_globals()
 * -------------
 * set global som_pak parameters 
 */
void set_globals(void) {
  use_fixed(0);
  use_weights(1);
  label_not_needed(1);
  init_random((int) time(NULL));
}

/* get_eptr()
 * ----------
 * create an eptr 
 */
eptr *get_eptr(void) {
  eptr *p;
  //p = (eptr *) malloc(sizeof(eptr)); /* WKV 2003-07-28 */
  p = (eptr *) calloc(1, sizeof(eptr));
  return p;
}

/* free_eptr()
 * -----------
 * WKV 2003-07-23 
 */
void free_eptr(eptr *p) { 
  free(p);
}

/* --------------------- data set manipulation functions ----------------- */

/* init_dataset()
 * --------------
 * allocates space for an entries struct and makes some initializations,
 * intended for use in constructing data sets (as opposed to sets of model
 * vectors), ergo the name.  'dim' specfies the dimension of the vectors.
 * Often used in conjunction with addto_dataset() and train_fromdataset(). */

struct entries *init_dataset(int dim) {
  struct entries *data;
  
  if(dim <= 0) {
    fprintf(stderr, "init_dataset(): invalid dimension: %d\n", dim);
    return NULL;
  }

  data = alloc_entries();

  if(data != NULL) {
    data->dimension = dim;
    data->current = NULL;
    data->entries = NULL;
  } 
  else {
    fprintf(stderr, "init_dataset(): alloc_entries() returned NULL\n");
  }

  return data;
}

/* free_dataset()
 * --------------
 * Free memory allocated by init_dataset.
 * WKV 2003-07-28
 */
void free_dataset (struct entries *data) {
  struct data_entry *current, *next;
  
  if(data == NULL) return;
  current = data->entries;
  while(current) {
    next = current->next;
    free_data_entry(current);
    current = next;
    data->num_entries--;
  }
  if(data->num_entries > 0) {
    fprintf(stderr, "free_dataset: All entries freed however count %d is non-zero\n", data->num_entries);
  }
  free(data);
}


/* addto_dataset()
 * ---------------
 * Adds a data_entry struct to a pre-existing (already called init_dataset())
 * set of data.  Often used in conjunction with make_data_entry_*(). 
 * Returns 1 if an error occurs, 0 otherwise.  
 */
int addto_dataset(struct entries *data, struct data_entry *entry) {
  eptr p;
  struct data_entry *next;

  if(data == NULL) {
    fprintf(stderr, "addto_dataset(): NULL data set\n");
    return 1;
  }
  if(entry == NULL) {
    fprintf(stderr, "addto_dataset(): NULL data entry\n");
    return 1;
  }

  entry->next = data->entries;
  data->entries = entry;
  data->num_entries++;
  return 0;
}


/* make_data_entry_weighted_masked()
 * ---------------------------------
 * Create a data_entry struct.  
 * 'points' is a float array specifying the actual data vector
 * 'weight' specifies the training weight of the vector (typically 1.0, 
 *   greater weights have a greater training impact on the map, values 0.0 
 *   and greater are acceptable)
 * 'mask' is a character array of 1's and 0's, and should be the same
 *   length as 'points'.  A 1 indicates that the corresponding point in
 *   'points' should be ignored in computing the winning model vector.
 *   Typically 'mask' is {0, 0, ...}, or equivalently NULL.
 *
 * Modifications:
 * it is primarily left up to the user to make certain that 'points',
 * 'mask', and the associated SOM are all of the same vector dimension 
 * -- this is no longer true.  dim checks have been added to __init__.py 
 *    added June 9, 2003.
 * 
 * 'label' is an array of char pointers. 
 * -- added June 16, 2003. 
 */

struct data_entry *make_data_entry_weighted_masked(float *points, short weight,
						   short *mask, int dim,
						   char **label) {
  struct data_entry *entry;
  char *charmask = NULL;
  int i;
  
  // this check has been moved to __init__.py. YT
  /*
  if(weight < 0.0) {
    fprintf(stderr, "make_data_entry_weighted_masked(): invalid weight: ");
    fprintf(stderr, "%f\n", weight);
    return NULL;
  }
  */

  entry = (struct data_entry *)malloc(sizeof(struct data_entry));

  entry->points   = points;
  entry->num_labs = 0;
  entry->weight   = weight;
  entry->next     = NULL;
  entry->fixed    = NULL;
  entry->lab.label = 0; /* WKV 2003-07-28 */
  
  /* mask */
  if(mask) {
    charmask = (char *) malloc(dim);
    for(i=0;i<dim;i++)
      charmask[i] = (char) mask[i];
  }
  entry->mask = charmask;
  
  /* label */
  /* if the label array is not null, add it to the entry */
  if(label) {
    for(i=0; label[i] != NULL; i++)
      add_entry_label(entry, find_conv_to_ind(label[i]));
  }

  return entry;
}
  
/* free_data_entry()
 * -----------------
 * Free a data_entry struct.
 * WKV 2003-07-28
 */
void free_data_entry (struct data_entry *entry) {
  if(entry == NULL) return;
  if(entry->mask != NULL) {
    free(entry->mask);
    entry->mask = NULL;
  }
  clear_entry_labels(entry);
  free(entry);
}

/* make_data_entry()
 * -----------------
 * No labels required.  pass in 0. 
 */
struct data_entry *make_data_entry(float *points) {
  return make_data_entry_weighted_masked(points, 1, NULL, 0, 0);
}



/* set_label_data_entry()
 * ----------------------
 * DEPRECATED 
 * use clear_label() and add_label() instead.  YT
 *
 * Returns 0 if label setting is successful, 1 otherwise.
 * The difference between add_label and set_label is that 
 * set_label removes all labels previously associated with
 * the entry before setting the new label.
 * --added June 17, 2003 (YT)
 */
/*
int set_label_data_entry(struct data_entry *entry, char **label) {
  int i;
  
  if(label) {
    for(i=0; label[i][0] != '0'; i++) { //label array is null-terminated with '0'.
      //printf("Added: %c\n", label[i][0]);
      set_entry_label(entry, find_conv_to_ind(label[i]));
    }
    return 0;
  }
  return 1;
}
*/

/* add_label_data_entry()
 * ----------------------
 * Returns 0 if adding a label is successful, 1 otherwise. 
 * add_label simply adds a label to the entry; any previous
 * associations remain the same. 
 * --added June 17, 2003 (YT)
 */
void add_label_data_entry(struct data_entry *entry, char **label) {
  int i;
  if(label) {
    for(i=0; label[i] != NULL; i++)
      add_entry_label(entry, find_conv_to_ind(label[i]));
  }
}

/* clear_labels_data_entry()
 * -------------------------
 * Clears all labels associated with a data entry 
 * --added June 17, 2003 (YT)
 */
void clear_labels_data_entry(struct data_entry *entry) {
  clear_entry_labels(entry);
}


/* ------------------ training session initialization functions ---------- */

/* construct_teach_params()
 * ------------------------
 * Creates a teach_params struct (think of this as a SOM struct with
 * associated teaching parameters, where params->codes contains the
 * information about the actual model vectors).  'codes' should
 * be initialized as a set of model vectors, from a call to lininit(),
 * randinit(), or open_entries().  'codes' will then contain info
 * about topology, map dimension, vector dimension, and neighborhood
 * type.  'alpha_mode' and 'radius_mode' specify the alpha and radius
 * decay functions.  
 */
struct teach_params_counters *construct_teach_params(struct entries *codes,
						     short alpha_mode,
						     short radius_mode) {
  struct teach_params_counters *params;
  if(codes == NULL) {
    fprintf(stderr, "construct_teach_params(): NULL codes struct\n");
    return NULL;
  }

  params = (struct teach_params_counters*)malloc(sizeof(struct teach_params_counters));
  params->teach = (struct teach_params*)malloc(sizeof(struct teach_params));
  set_teach_params(params->teach, codes, NULL, 0);
  set_som_params(params->teach);
  setup_counters(params);

  params->teach->snapshot = NULL;
  params->teach->data = NULL;
  params->teach->count = -1;  //used to signal uninitialized training session
  
  switch(alpha_mode) {
  case LINEAR:    params->teach->alpha_func = linear_alpha;    break;
  case INVERSE_T: params->teach->alpha_func = inverse_t_alpha; break;
  default: fprintf(stderr, "construct_teach_params(): ");
    fprintf(stderr, "unrecognized alpha mode: %d, ", alpha_mode);
    fprintf(stderr, "using LINEAR\n");
    params->teach->alpha_func = linear_alpha;
  }
  switch(radius_mode) {
  case LINEAR:    params->teach->radius_func = linear_alpha;    break;
  case INVERSE_T: params->teach->radius_func = inverse_t_alpha; break;
  default: fprintf(stderr, "construct_teach_params(): ");
    fprintf(stderr, "unrecognized radius mode: %d, ", radius_mode);
    fprintf(stderr, "using LINEAR\n");
    params->teach->radius_func = linear_alpha;
  }

  return params;
}

/* free_teach_params()
 * -------------------
 * Free memory allocated by construct_teach_params().
 * WKV 2003-07-28
 */
void free_teach_params(struct teach_params_counters *params) {
  if(params == NULL) return;
  free_counters(params);
  if(params->teach) {
    free(params->teach);
    params->teach = NULL;
  }
  free(params);
}

/* init_training_session()
 * -----------------------
 * Initialize a training session with initial alpha and radius, intended
 * length of training session (number of iterations), and an error
 * calculation parameter.  This last is a bit ad-hoc, but roughly
 * speaking get_error() will depend on the last 'qerror_window'
 * vectors mapped, with the most recent having the greatest effect. 
 * Returns 1 if a fatal error occurs, 0 otherwise.  */

int init_training_session(struct teach_params_counters *params,
			  float alpha_0, float radius_0, long length,
			  long qerror_window) {
  if(params == NULL) {
    fprintf(stderr, "init_training_session(): NULL teach_params_counters\n");
    return 1;
  }
  if(params->teach == NULL) {
    fprintf(stderr, "init_training_session(): NULL params->teach_params\n");
    return 1;
  }

  /* these error checks are now done in the python code: __init__.py. YT */
  /* 
  if(alpha_0 < 0.0) {
    fprintf(stderr, "init_training_session(): invalid alpha_0: %f, ",
	    alpha_0);
    fprintf(stderr, "using 0.0\n");
    alpha_0 = 0.0;
  }
  if(alpha_0 > 1.0) {
    fprintf(stderr, "init_training_session(): invalid alpha_0: %f, ",
	    alpha_0);
    fprintf(stderr, "using 1.0\n");
    alpha_0 = 1.0;
  }
  if(radius_0 < 1.0) {
    fprintf(stderr, "init_training_session(): invalid radius_0: %f, ",
	    radius_0);
    fprintf(stderr, "using 1.0\n");
    radius_0 = 1.0;
  }
  if(length < 1) {
    fprintf(stderr, "init_training_session(): invalid length: %f, ",
	    length);
    fprintf(stderr, "using 1\n");
    length = 1;
  }
  if(qerror_window < 1) {
    fprintf(stderr, "init_training_session(): invalid qerror_window: %f, ",
	    qerror_window);
    fprintf(stderr, "using 1\n");
    qerror_window = 1;
  }
  */
  params->teach->alpha  = alpha_0;
  params->teach->radius = radius_0;
  params->teach->length = length;
  params->teach->count  = 0;
  params->teach->qerror = 0.0;
  params->teach->error_factor = 1.0 / ((float) qerror_window);
  return 0;
}

/* setup_snapshot()
 * ----------------
 * Sets up file snapshots of code vectors; these files will be saved
 * every 'interval' number of iterations.
 * If 'snapfile_prefix' is "snap.cod" and interval is 100
 * then the resulting files will be "snap.cod.100", "snap.cod.200", etc.
 * Returns 1 if an error occurs, 0 otherwise.  
 */
int setup_snapshot(struct teach_params_counters *params,
		   char *snapfile_prefix, long interval) {
  struct snapshot_info *snap;
  
  if(params == NULL) {
    fprintf(stderr, "setup_snapshot(): NULL teach_params_counters\n");
    return 1;
  }
  if(params->teach == NULL) {
    fprintf(stderr, "setup_snapshot(): NULL params->teach_params\n");
    return 1;
  }
  if(interval < 1) {
    fprintf(stderr, "setup_snapshot(): invalid interval: %d\n", interval);
    return 1;
  }
  snap = (struct snapshot_info *) malloc(sizeof(struct snapshot_info));
  snap->filename = snapfile_prefix;
  snap->interval = interval;
  snap->type = SNAPSHOT_SAVEFILE;
  params->teach->snapshot = snap;

  return 0;
}

/* ------------------- counter manipulation functions ----------------- */

/* Sets up the two 3-dimensional arrays in the teach_param_counters struct.
 * The two arrays store training and mapping counters for each SOM node. 
 * 3 training counters and 3 mapping counters are associated with each 
 * x,y coordinates.  The arrays are initialized to the number of nodes
 * in the som and are zeroed out.
 *
 */
void setup_counters(struct teach_params_counters *params) {
  int xdim, ydim, i, j, k;
  xdim = params->teach->codes->xdim;
  ydim = params->teach->codes->ydim;

  params->tcounters = (unsigned int ***) malloc(sizeof(unsigned int **)*xdim);
  params->mcounters = (unsigned int ***) malloc(sizeof(unsigned int **)*xdim);
  params->counters_xdim = xdim; /* WKV 2003-07-28 */
  params->counters_ydim = ydim; /* WKV 2003-07-28 */

  for(i=0; i<xdim; i++) {
    params->tcounters[i] = (unsigned int **)malloc(sizeof(unsigned int *)*ydim);
    params->mcounters[i] = (unsigned int **)malloc(sizeof(unsigned int *)*ydim);

    for (j=0; j<ydim; j++) {
      /* 3 training counters and 3 mapping counters per node */
      params->tcounters[i][j] = (unsigned int *)malloc(sizeof(unsigned int)*3); 
      params->mcounters[i][j] = (unsigned int *)malloc(sizeof(unsigned int)*3); 

      for (k=0; k<3; k++) {
	params->tcounters[i][j][k] = 0;
      	params->mcounters[i][j][k] = 0;
      }
    }
  }
}

/* free_counters()
 * --------------
 * WKV 2003-07-28
 */
void free_counters(struct teach_params_counters *params) {
  int i, j;

  if(params == NULL) return;
  if(params->tcounters) {
    for(i=0; i<params->counters_xdim; i++) {
      for(j=0; j<params->counters_ydim; j++) {
	free(params->tcounters[i][j]);
	free(params->mcounters[i][j]);
      }
      free(params->tcounters[i]);
      free(params->mcounters[i]);
    }
    free(params->tcounters);
    free(params->mcounters);
    params->tcounters = NULL;
    params->mcounters = NULL;
  }
}

/* update_counters()
 * -----------------
 * Given the winning coordinates and the previous winning coordinates, 
 * increment the counters.
 * counters[0]: regular counter    
 * counters[1]: consecutive counter
 * counters[2]: maximum consecutive counter                                   
 * The (regular) counter and the consecutive counter are always incremented.  
 * The maximum consecutive counter stores the highest consecutive train/map
 * counter associated with a SOM node.
 *
 * Note: For test runs (i.e. counters are not incremented, use (-1,-1) 
 *       as last_coords.
 */
void update_counters(unsigned int ***counters, int *curr_coords, 
		     int *last_coords) {
  int curr_x, curr_y;
  curr_x = curr_coords[0]; 
  curr_y = curr_coords[1];
  /*
  printf("Incrementing counter %d->%d for point:(%d,%d)\n", 
	 counters[curr_x][curr_y][0], counters[curr_x][curr_y][0] + 1,
	 curr_x, curr_y);
  */
  counters[curr_x][curr_y][0]++;
  /*
  printf("Incrementing consec counter %d->%d for point:(%d,%d)\n", 
	 counters[curr_x][curr_y][1], counters[curr_x][curr_y][1] + 1,
	 curr_x, curr_y);
  */
  counters[curr_x][curr_y][1]++;
  
  if(counters[curr_x][curr_y][1] > counters[curr_x][curr_y][2]) {
    /*
    printf("Setting max consec counter %d->%d for point:(%d,%d)\n", 
	   counters[curr_x][curr_y][2], counters[curr_x][curr_y][1],
	   curr_x, curr_y);
    */
    counters[curr_x][curr_y][2] = counters[curr_x][curr_y][1];
  }
  
  /* If this is not the first mapping, and the last mapped coordinate
   * is not the same as the current winning coordinate, reset the
   * consecutive counter for the last coordinate.
   * Note: last_coords is == NULL if this is the first run i.e.
   * the SOM has never been trained/mapped before.
   */
  if(!(last_coords[0] == -1     && last_coords[1] == -1) &&
     !(last_coords[0] == curr_x && last_coords[1] == curr_y)) {
    /*
      printf("Reseting consec counter %d->%d for last point:(%d,%d)\n", 
      counters[last_coords[0]][last_coords[1]][1], 0, 
      last_coords[0], last_coords[1]);
    */
    counters[last_coords[0]][last_coords[1]][1] = 0;
  }
  return;
}

/* get_reg_tcounter()
 * ------------------
 * Returns the regular train counter associated with the 
 * given coordinates.
 */
int get_reg_tcounter(struct teach_params_counters *params, 
		     int *coords) {
  return get_counter(params, coords, TRAIN, REGULAR);
}
/* get_consec_tcounter()
 * ---------------------
 * Returns the consecutive train counter associated with the 
 * given coordinates.
 */
int get_consec_tcounter(struct teach_params_counters *params, 
			int *coords) {
  return get_counter(params, coords, TRAIN, CONSEC);
}
/* get_maxconsec_tcounter()
 * ------------------------
 * Returns the max consecutive train counter associated with the 
 * given coordinates.
 */
int get_maxconsec_tcounter(struct teach_params_counters *params, 
			   int *coords) {
  return get_counter(params, coords, TRAIN, MAX_CONSEC);
}
/* get_reg_mcounter()
 * ------------------
 * Returns the regular map counter associated with the 
 * given coordinates.
 */
int get_reg_mcounter(struct teach_params_counters *params, 
		     int *coords) {
  return get_counter(params, coords, NO_TRAIN, REGULAR);
}
/* get_consec_mcounter()
 * ---------------------
 * Returns the consecutive map counter associated with the 
 * given coordinates.
 */
int get_consec_mcounter(struct teach_params_counters *params, 
			int *coords) {
  return get_counter(params, coords, NO_TRAIN, CONSEC);
}
/* get_maxconsec_mcounter()
 * ------------------------
 * Returns the max consecutive map counter associated with the 
 * given coordinates.
 */
int get_maxconsec_mcounter(struct teach_params_counters *params, 
			   int *coords) {
  return get_counter(params, coords, NO_TRAIN, MAX_CONSEC);
}

/* get_counter()
 * -------------
 * Given a teach_params_counters struct, a coordinate, a mode (TRAIN
 * for training mode, NO_TRAIN for mapping mode), and the counter type 
 * ([0]:REGULAR, [1]:CONSEC, [2]:MAX_CONSEC), this function returns
 * the corresponding counter associated with that coordinate. 
 * By default, it returns the regular counter associated with that 
 * coordinate.
 */
int get_counter(struct teach_params_counters *params, 
		int *coords, short mode, int counter_type) {
  unsigned int ***counters;

  if(params == NULL) {
    fprintf(stderr, "get_counter(): NULL teach_params_counters\n");
    return 1;
  }
  if(params->teach == NULL) {
    fprintf(stderr, "get_counter(): NULL params->teach_params\n");
    return 1;
  }
  if(coords[0] >= params->teach->codes->xdim ||
     coords[1] >= params->teach->codes->ydim) {
    fprintf(stderr, "get_regular_counter(): Invalid coordinates (%d,%d)\n",
	    params->teach->codes->xdim, params->teach->codes->ydim);
  }

  if(mode == TRAIN) 
    counters = params->tcounters;
  else 
    counters = params->mcounters;

  switch(counter_type) {
  case CONSEC:
    return counters[coords[0]][coords[1]][1];
  case MAX_CONSEC:
    return counters[coords[0]][coords[1]][2];
  default:
    return counters[coords[0]][coords[1]][0];
  }
}


/* ------------------ training/mapping functions ---------------------- */

/* input_one()
 * -----------
 * Takes teach_params_counters and a data_entry and applies the mapping 
 * algorithm to the data vector, returning a pointer to integer coordinates 
 * of the winning model vector, or NULL if an error occurs.
 * If mode is NO_TRAIN, then that is all that happens.
 * If mode is TRAIN, then the map is trained in accordance with alpha,
 *  radius, and whatnot, and the count is increased.
 * If appropriate, snapshots are also taken from here. 
 */
int *map_one(struct teach_params_counters *params, 
	     struct data_entry *sample, 
	     int *last_coords, int update_counter_flag) {
  return input_one(params, sample, NO_TRAIN, 
		   last_coords, update_counter_flag); 
}
int *train_one(struct teach_params_counters *params, 
	       struct data_entry *sample, 
	       int *last_coords, int update_counter_flag) {
  return input_one(params, sample, TRAIN, 
		   last_coords, update_counter_flag); 
}

int *input_one(struct teach_params_counters *params,
	       struct data_entry *sample, short mode, 
	       int *last_coords, int update_counter_flag) {
  NEIGH_ADAPT *adapt           = params->teach->neigh_adapt;
  WINNER_FUNCTION *find_winner = params->teach->winner;
  ALPHA_FUNC *get_alpha        = params->teach->alpha_func;
  ALPHA_FUNC *get_radius       = params->teach->radius_func;
  struct snapshot_info *snap   = params->teach->snapshot;
  struct winner_info win_info;
  struct entries *codes        = params->teach->codes;
  float alpha, radius;
  int *coords;

  if(params == NULL) {
    fprintf(stderr, "input_one(): NULL teach_params_counters\n");
    fflush(stdout);
    return NULL;
  }
  if(params->teach == NULL) {
    fprintf(stderr, "input_one(): NULL params->teach_params\n");
    fflush(stdout);
    return NULL;
  }
  if(sample == NULL) {
    fprintf(stderr, "input_one(): NULL sample data_entry\n");
    fflush(stdout);
    return NULL;    
  }
  if(mode != NO_TRAIN && mode != TRAIN) {
    fprintf(stderr, "input_one(): unrecognized mode: %d, using TRAIN\n", mode);
    fflush(stdout);
    mode = TRAIN;
  }
  if(mode == TRAIN && params->teach->count == -1) {
    fprintf(stderr, "input_one(): uninitialized training session\n");
    fflush(stdout);
    return NULL;
  }
  
  /* Find the best match, use fixed point if allowed */
  coords = (int *) malloc(2*sizeof(int));
  if ((sample->fixed != NULL) && (use_fixed(-1))) {
    coords[0] = sample->fixed->xfix;
    coords[1] = sample->fixed->yfix;
  } 
  else {
    if (find_winner(codes, sample, &win_info, 1) == 0) {
      fprintf(stderr, "input_one(): no winner found in call to find_winner()");
      fprintf(stderr, ", skipping teaching\n");
      free(coords);
      coords = NULL;
      goto skip_teach;
    }
    coords[0] = win_info.index % codes->xdim;
    coords[1] = win_info.index / codes->xdim;
    params->teach->qerror = (1.0-params->teach->error_factor) * params->teach->qerror 
      + params->teach->error_factor * sqrt((double) win_info.diff);
  }
  
  /* Adapt the units */
  if(mode == TRAIN) {
    radius = get_radius(params->teach->count, params->teach->length, 
			params->teach->radius-1) + 1;
    alpha  = get_alpha(params->teach->count, params->teach->length, 
		       params->teach->alpha);
    if ((sample->weight > 0) && (use_weights(-1)))
      alpha = 1.0 - (float) pow((double) (1.0 - alpha), 
				(double) sample->weight);
    if (alpha < 0.0) alpha = 0.0;
    if (radius < 1.0) radius = 1.0;
    adapt(params->teach, sample, coords[0], coords[1], radius, alpha);
    params->teach->count++;
  }

  skip_teach:
  /* save snapshot when needed */
  if ((snap) && ((params->teach->count % snap->interval) == 0) && 
      (params->teach->count > 0))
    save_snapshot(params->teach, params->teach->count);

  /* update training/mapping counters depending on mode */
  if(update_counter_flag) {
    if(mode == TRAIN) {
      update_counters(params->tcounters, coords, last_coords);
    }
    else {
      update_counters(params->mcounters, coords, last_coords);
    }
  }
  return coords;
}


/* train_fromdataset()
 * -------------------
 * Runs an entire training session from teach_params and a data set
 * contained in 'data'.  'data' will either be gotten from a call to
 * open_entries() or by calling init_dataset() and then making
 * subsequent calls to addto_dataset().
 * The training session will still need to be initialized with calls
 * to construct_teach_params() and init_training_session(), and
 * setup_snapshot() if desired.  Calls to timing_start() and timing_stop()
 * will need to be made if desired.
 * Training mode can either be CYCLIC or RANDOM, impacts the order in
 * which data vectors are fed to the SOM.
 * Returns NULL if a fatal error occurs, otherwise returns a pointer to
 * the last data_entry used in the data set (used in the python interface
 * to determine SRN activations after training from a data set).
 */
struct data_entry *train_fromdataset(struct teach_params_counters *params, 
				     struct entries *data, short mode) {
  struct data_entry *entry, *last;
  eptr p;
  int j = 0, *coords, *last_coords;
  
  if(params == NULL) {
    fprintf(stderr, "train_fromdataset(): NULL teach_param_counters\n");
    return NULL;
  }
  if(params->teach == NULL) {
    fprintf(stderr, "train_fromdataset(): NULL params->teach_params\n");
    return NULL;
  }
  if(params->teach->codes == NULL) {
    fprintf(stderr, "train_fromdataset(): NULL params->teach_params->codes\n");
    return NULL;
  }
  if(data == NULL) {
    fprintf(stderr, "train_fromdataset(): NULL data set\n");
    return NULL;    
  }
  if(data->dimension != params->teach->codes->dimension) {
    fprintf(stderr, "train_fromdataset(): mismatched data set and model ");
    fprintf(stderr, "vector dimensions: %d, %d\n", data->dimension,
	    params->teach->codes->dimension);
    return NULL;
  }

  data->flags.random_order = mode;
  if(mode == RAND) init_random((int) time(NULL));
  
  /* last_coords == (-1,-1) tells update_counters() that this
   * is the first run, so no need to check consecutive counter
   */
  last_coords = (int *) malloc(2*sizeof(int));
  last_coords[0] = last_coords[1] = -1;
  //entry = rewind_entries(data, &p);
  /* if a user has been so ignorant as to issue two
     training requests, his program gets killed with a segfault in the
     get_label routine.  The problem is once again garbage being returned
     to the python level (the last entry was uninitialized).
     WKV 2003-07-31 */
  last = entry = rewind_entries(data, &p); 

  while(params->teach->count < params->teach->length) {
    if(entry == NULL) entry = rewind_entries(data, &p);
    if((coords = train_one(params, entry, last_coords, 1)) == NULL) {
      fprintf(stderr, "train_fromdataset(): train_one() returned NULL\n");
      return NULL;
    }
    free(last_coords); /* WKV 2003-07-28 */
    last_coords = coords;
    last = entry;
    entry = next_entry(&p);
  }
  free(last_coords); /* YT 2003-07-31 */
  return last;
}

/* map_fromdataset()
 * -----------------
 * Given a dataset, this function maps the vectors in the dataset
 * to the trained SOM.  
 * Returns NULL if a fatal error occurs, otherwise returns a pointer to
 * the last data_entry used in the data set (used in the python interface
 * to determine SRN activations after training from a data set).
 */
struct data_entry *map_fromdataset(struct teach_params_counters *params, 
				   struct entries *data) {
  struct data_entry *entry, *last;
  eptr p;
  int *coords, *last_coords;

  if(params == NULL) {
    fprintf(stderr, "map_fromdataset(): NULL teach_params_counters\n");
    return NULL;
  }
  if(params->teach == NULL) {
    fprintf(stderr, "map_fromdataset(): NULL params->teach_params\n");
    return NULL;
  }
  if(params->teach->codes == NULL) {
    fprintf(stderr, "map_fromdataset(): NULL params->teach_params->codes\n");
    return NULL;
  }
  if(data == NULL) {
    fprintf(stderr, "map_fromdataset(): NULL dataset\n");
    return NULL;    
  }
  if(data->dimension != params->teach->codes->dimension) {
    fprintf(stderr, "map_fromdataset(): mismatched dataset and model ");
    fprintf(stderr, "vector dimensions: %d, %d\n", data->dimension,
	    params->teach->codes->dimension);
    return NULL;
  }
  
  /* last_coords == (-1,-1) tells update_counters() that this
   * is the first run, so no need to check consecutive counter
   */
  last_coords = (int *)malloc(2*sizeof(int));
  last_coords[0] = last_coords[1] = -1;
  //entry = rewind_entries(data, &p); 
  last = entry = rewind_entries(data, &p); /* same reason as above 
					      YT 2003-07-31 */

  while(entry != NULL){
    if((coords = map_one(params, entry, last_coords, 1)) == NULL) {
      fprintf(stderr, "map_fromdataset(): map_one() returned NULL\n");
      return NULL;
    }
    free(last_coords); /* WKV 2003-07-31 */
    last_coords = coords;
    last = entry;
    entry = next_entry(&p);
  }
  free(last_coords); /* WKV 2003-07-31 */
  return last;
}


/* ------------------- training timing functions ---------------------- */

/* all of these functions are really self explanatory */

void timing_start(struct teach_params_counters *params) {
  time(&params->teach->start_time);
}

void timing_stop(struct teach_params_counters *params) {
  time(&params->teach->end_time);
}

int get_training_time(struct teach_params_counters *params) {
  return params->teach->end_time - params->teach->start_time;
}

/* -------------- functions for getting info about SOM state ---------- */

/* get_error()
 * -----------
 * just returns a data element.  nothing too fancy.  
 * see init_training_session() and input_one() for info about how error
 * is actually calculated.  
 */
float get_error(struct teach_params_counters *params) {
  return params->teach->qerror;
}



/* get_activation_levels()
 * -----------------------
 * Given the x,y coordinates 'coords' for the SOM contained in 'teach', 
 * returns SRN-appropriate activation levels based on 'radius',
 * ranging from 1.0 at the specified coordinate and decaying based on
 * 'radius' and either gaussian or bubble function, as specified by 'mode'.  
 * Returns NULL if an error occurs.  */

float *get_activation_levels(struct teach_params_counters *params,
			     int *coords, float radius, short mode) {
  MAPDIST_FUNCTION *distf = params->teach->mapdist;
  float *levels, delta;
  int i, x, y, xdim, ydim;

  if(params == NULL) {
    fprintf(stderr, "get_activation_levels(): NULL teach_params_counters\n");
    return NULL;
  }
  if(params->teach == NULL) {
    fprintf(stderr, "get_activation_levels(): NULL params->teach_params\n");
    return NULL;
  }
  if(params->teach->codes == NULL) {
    fprintf(stderr, "get_activation_levels(): NULL params->teach_params->codes\n");
    return NULL;
  }
  if(coords == NULL) {
    fprintf(stderr, "get_activation_levels(): NULL coordinates\n");
    return NULL;
  }
  if(mode != NEIGH_GAUSSIAN && mode != NEIGH_BUBBLE) {
    fprintf(stderr, "get_activation_levels(): unrecognized mode %d, using %d\n",
	    mode,NEIGH_GAUSSIAN);
    mode = NEIGH_GAUSSIAN;
  }
  if(radius < 1.0) {
    fprintf(stderr, "get_activation_levels(): invalid radius: %f, ", radius);
    fprintf(stderr, "using 1.0\n");
    radius = 1.0;
  }
  
  xdim = params->teach->codes->xdim;
  ydim = params->teach->codes->ydim;
  
  if(coords[0] < 0 || coords[0] > xdim || coords[1] < 0 || coords[1] > ydim) {
    fprintf(stderr, "get_activation_levels(): invalid x,y coordinates: ");
    fprintf(stderr, "%d,%d, map dimensions: %d,%d\n", coords[0], coords[1],
	    xdim, ydim);
    return NULL;
  }
  
  levels = (float *) malloc(xdim*ydim*sizeof(float));
  if(mode == NEIGH_GAUSSIAN) {
    for(y=0; y<ydim; y++) {
      for(x=0; x<xdim; x++) {
	i = x + y * xdim;
	delta = 2.0*distf(coords[0], coords[1], x, y)/radius;
	levels[i] = 1.0 / (exp(delta*delta));
      }
    }
  } else {
    for(y=0; y<ydim; y++) {
      for(x=0; x<xdim; x++) {
	i = x + y * xdim;
	if(distf(coords[0],coords[1],x,y) <= radius-1.0) levels[i] = 1.0;
	else levels[i] = 0.0;
      }
    }
  }	
  
  return levels;
}


/* get_levels_by_error()
 * ---------------------
 * returns SRN appropriate activation levels based on error calculations
 * for each model vector 
 */
float *get_levels_by_error(struct teach_params_counters *params,
			   struct data_entry *sample, float tolerance) {
  DIST_FUNCTION *distf = params->teach->dist;
  float *levels, delta, emin, emax;
  int i, x, y, xdim, ydim, dim=params->teach->codes->dimension, *coords;
  struct data_entry *model;

  if(params == NULL) {
    fprintf(stderr, "get_levels_by_error(): NULL teach_params_counters\n");
    return NULL;
  }
  if(params->teach == NULL) {
    fprintf(stderr, "get_levels_by_error(): NULL params->teach_params\n");
    return NULL;
  }
  if(params->teach->codes == NULL) {
    fprintf(stderr, "get_levels_by_error(): NULL params->teach_params->codes\n");
    return NULL;
  }
  if(tolerance < 0.0 || tolerance > 1.0) {
    fprintf(stderr, "get_levels_by_error(): Invalid tolerance %d, using 1.0\n",
	    tolerance);
    tolerance = 1.0;
  }

  xdim = params->teach->codes->xdim;
  ydim = params->teach->codes->ydim;

  levels = (float *) malloc(xdim*ydim*sizeof(float));
  coords = (int *) malloc(2*sizeof(int));
  //emin = 100000.0; // should be largest possible float but i'm lazy
  emin = 3.40282347e+38F; /* WKV 2003-07-28 */
  emax = 0.0;

  for(y=0; y<ydim; y++) {
    for(x=0; x<xdim; x++) {
      i = x + y * xdim;
      coords[0] = x;
      coords[1] = y;
      model = get_model_vector(params->teach->codes,coords);
      levels[i] = distf(sample,model,dim);
      if(levels[i] < emin) emin = levels[i];
      if(levels[i] > emax) emax = levels[i];
    }
  }
  emax -= (emax-emin)*(1.0-tolerance);
  
  free(coords); /* WKV 2003-07-28 */

  for(y=0; y<ydim; y++) {
    for(x=0; x<xdim; x++) {
      i = x + y * xdim;
      levels[i] = 1.0 - (levels[i]-emin)/emax;
      if(levels[i] < 0.0) levels[i] = 0.0;
      if(levels[i] > 1.0) levels[i] = 1.0;
      levels[i] *= levels[i] * levels[i];
    }
  }
  
  return levels;
}


	
/* get_model_vector()
 * ------------------
 * returns a pointer to the data_entry struct associated with the model
 * vector at the specified x,y coordinates of 'coords' contained in the
 * SOM of codes (usually gotten by teach_params->codes).  returns NULL
 * if an error occurs.   */

struct data_entry *get_model_vector(struct entries *codes, int *coords) {
  eptr p;
  struct data_entry *model;
  int i, index;

  if(codes == NULL) {
    fprintf(stderr, "get_model_vector(): NULL codes\n");
    return NULL;
  }
  if(coords == NULL) {
    fprintf(stderr, "get_model_vector(): NULL coordinates\n");
    return NULL;
  }
  if(coords[0] < 0 || coords[0] > codes->xdim 
     || coords[1] < 0 || coords[1] > codes->ydim) {
    fprintf(stderr, "get_model_vector(): invalid x,y coordinates: ");
    fprintf(stderr, "%d,%d, map dimensions: %d,%d\n", coords[0], coords[1],
	    codes->xdim, codes->ydim);
    return NULL;
  }
  index = coords[0] + coords[1] * codes->xdim;

  model = rewind_entries(codes, &p);
  for(i=0;i<index;i++)
    model = next_entry(&p);

  return model;
}



/* print_dataset()
 * ---------------
 * prints the data set associated with 'data' to stdout.  Can be used for both
 * model vectors (codes) and data vectors.  
 *
 * prints label associated with model vectors. 
 * (see labels.c for info on labels) -- Added June 11, 2003 (Yee Lin Tan) */

void print_dataset(struct entries *data) {
  int i;
  int label; 
  eptr p;
  struct data_entry *entry;

  entry = rewind_entries(data, &p);
  while(entry!=NULL) {
    /* display points in vector */
    for(i=0;i<data->dimension;i++)
      printf("%.3f ", entry->points[i]);
    
    /* display weight of vector */
    printf(" wt: %d ", entry->weight);

    /* display mask associated with vector if there is one */
    if(entry->mask) {
      printf(" mask: ");
      for(i=0;i<data->dimension;i++)
        printf("%d ", entry->mask[i]);
    }

    /* display label(s) if there are any */
    if(entry->num_labs) {
      printf(" label: ");
      for(i=0;;i++) {
	label = get_entry_labels(entry, i);
	if(label != LABEL_EMPTY) 
	  /* last label in label array is always LABEL_EMPTY */
	  printf("%s ", find_conv_to_lab(label));
	else 
	  break;
      }
    }
    printf("\n");
    entry = next_entry(&p); /* go on to the next vector */
  }
  printf("%d total entries\n", data->num_entries);
}


/* Returns the mask array (char *) associated with the 
 * given data entry 
 * --added June 20, 2003 (YT)
 */
char *get_mask_data_entry(struct data_entry *entry, int dim) {
  return entry->mask;
}


/* Returns the label array associated with the given
 * data entry as a array of strings.
 * --added June 20, 2003 (YT)
 * Malloc'ed an extra spot for the NULL pointer at the end of char **.
 * --added July 22, 2003 (WKV)
 */
char **get_label_data_entry(struct data_entry *entry, int num_labels) {
  int i, label;
  char **labels = NULL, *str_label = NULL;

  if(entry->num_labs) {
    //labels = malloc(entry->num_labs*sizeof(char*));
    labels = malloc((entry->num_labs+1)*sizeof(char*));
    for(i=0;;i++) {
      label = get_entry_labels(entry, i);
      if(label != LABEL_EMPTY) {
	/* last label in label array is always LABEL_EMPTY */
	str_label = find_conv_to_lab(label);
	labels[i] = str_label;
      }
      else {
	labels[i] = NULL;
	break;
      }
    }
  }
  return labels;
}


/* -------------------------- end of file ----------------------------- */
