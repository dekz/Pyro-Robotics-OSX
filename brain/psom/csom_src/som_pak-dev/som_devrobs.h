/* som_devrobs.h
 * -------------
 * june 14, 2002
 * Daniel Sproul, sproul@sccs.swarthmore.edu
 * header for som_devrobs.c
 * ----------------------------------
 */



#ifndef SOM_DEVROBS_H
#define SOM_DEVROBS_H

#include "Python.h"
#include "lvq_pak.h"

#define CYCLIC    0   // for train_fromdataset()
#define RAND      1   // for train_fromdataset()
#define LINEAR    0   // for construct_teach_params()
#define INVERSE_T 1   // for construct_teach_params()
#define NO_TRAIN  0   // for input_one()
#define TRAIN     1   // for input_one()

#define REGULAR    0  // for get_reg_tcounter(), get_reg_mcounter()
#define CONSEC     1  // for get_consec_tcounter(), get_consec_mcounter()
#define MAX_CONSEC 2  // for get_maxconsec_tcounter(), get_maxconsec_mcounter()

/* other relevant definitions:
 * lvq_pak.h:
 *   #define TOPOL_HEXA
 *   #define TOPOL_RECT
 *   #define NEIGH_BUBBLE
 *   #define NEIGH_GAUSSIAN
 */

/* other relevant functions:
 * datafile.h:
 *   struct entries *open_entries(char *name);
 *   void close_entries(struct entries *entries);
 *   int save_entries(struct entries *codes, char *out_code_file);
 *   int save_entries_wcomments(struct entries *codes,
 *                              char *out_code_file, char *comments);
 * somrout.h:
 *   struct entries *lininit_codes(struct entries *data, int topol, 
 *                                 int neigh, int xdim, int ydim);
 *   struct entries *randinit_codes(struct entries *data, int topol, 
 *                                  int neigh, int xdim, int ydim);
 */

/*
 * Structure to hold the teach_params alongside counters for mapping
 * and training.
 */
struct teach_params_counters {
  struct teach_params *teach;
  unsigned int ***tcounters; /* 3 training counters per som node */
  unsigned int ***mcounters; /* 3 mapping counters per som node */
  int counters_xdim;         /* WKV 2003-07-28 */
  int counters_ydim;         /* WKV 2003-07-28 */
};


int write_entries(struct entries *codes, char *out_code_file);
void set_globals(void);
eptr *get_eptr(void);
void free_eptr(eptr *); /* WKV 2003-07-23 */

/* --------------------- data set manipulation functions ----------------- */

struct entries *init_dataset(int dim);
void free_dataset(struct entries *);
int addto_dataset(struct entries *data, struct data_entry *entry);
struct data_entry *make_data_entry_weighted_masked(float *points, 
						   short weight, short *mask, 
						   int dim, char **label);
void free_data_entry(struct data_entry *);
struct data_entry *make_data_entry(float *points);

/* --------------------- label manipulation functions ----------------- */
//int set_label_data_entry(struct data_entry *entry, char **label);
void add_label_data_entry(struct data_entry *entry, char **label);
void clear_labels_data_entry(struct data_entry *entry);

/* ------------------ training session initialization functions ---------- */

struct teach_params_counters *construct_teach_params(struct entries *codes,
					    short alpha_mode, 
					    short radius_mode);
void free_teach_params(struct teach_params_counters *);
int init_training_session(struct teach_params_counters *params,
			  float alpha_0, float radius_0, long length,
			  long qerror_window);
int setup_snapshot(struct teach_params_counters *params,
		   char *snapfile_prefix, long interval);

/* ------------------- counter manipulation functions ----------------- */
void setup_counters(struct teach_params_counters *params);
void free_counters(struct teach_params_counters *params);
void update_counters(unsigned int ***counters, int *curr_coords, 
		     int *last_coords);

int get_reg_tcounter(struct teach_params_counters *params, int *coords);
int get_consec_tcounter(struct teach_params_counters *params, int *coords);
int get_maxconsec_tcounter(struct teach_params_counters *params, int *coords);

int get_reg_mcounter(struct teach_params_counters *params, int *coords);
int get_consec_mcounter(struct teach_params_counters *params, int *coords);
int get_maxconsec_mcounter(struct teach_params_counters *params, int *coords);

int get_counter(struct teach_params_counters *params, 
		int *coords, short mode, int counter_type);

/* ------------------ training/mapping functions ---------------------- */

int *input_one(struct teach_params_counters *params,
	       struct data_entry *sample, short mode, 
	       int *last_coords, int update_counter_flag);
int *map_one(struct teach_params_counters *params, 
	     struct data_entry *sample, 
	     int *last_coords, int update_counter_flag);
int *train_one(struct teach_params_counters *params, 
	       struct data_entry *sample, 
	       int *last_coords, int update_counter_flag);

struct data_entry *train_fromdataset(struct teach_params_counters *params, 
				     struct entries *data, short mode);
struct data_entry *map_fromdataset(struct teach_params_counters *params, 
				   struct entries *data);

/* ------------------- training timing functions ---------------------- */

void timing_start(struct teach_params_counters *params);
void timing_stop(struct teach_params_counters *params);
int get_training_time(struct teach_params_counters *params);



/* -------------- functions for getting info about SOM state ---------- */

float get_error(struct teach_params_counters *params);
float *get_activation_levels(struct teach_params_counters *params,
			     int *coords, float radius, short mode);
float *get_levels_by_error(struct teach_params_counters *params,
			   struct data_entry *sample, float tolerance);
struct data_entry *get_model_vector(struct entries *codes, int *coords);
void print_dataset(struct entries *data);


char *get_mask_data_entry(struct data_entry *entry, int dim);
char **get_label_data_entry(struct data_entry *entry, int num_labels);

#endif /* SOM_DEVROBS_H */
