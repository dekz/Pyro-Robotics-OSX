/* test_devrobs.c
 * --------------
 * a few tests for the routines in som_devrobs.c */



#include <stdio.h>
#include <float.h>
#include <stdlib.h>
#include <math.h>
#include "lvq_pak.h"
#include "som_rout.h"
#include "datafile.h"
#include "labels.h" /* WKV 2003-07-28 */

#include "som_devrobs.h"



int main() {
  //struct teach_params *params;
  struct teach_params_counters *params; /* WKV 2003-07-28 */
  struct entries *codes, *data;
  struct data_entry *input, *output, *sample;
  float points[5] = {13.57, 12.61, -1.38, -1.99, 399.77};
  float points1[5] = {19.58, 13.08, -1.17, -0.84, 400.03};
  float points2[5] = {29.36, 38.69, -1.10, -0.87, 405.21};
  float points3[5] = {19.82, 27.08, -2.35, -3.70, 404.86};
  short mask[5] = {0, 0, 1, 0, 1};
  char *in_data_file = "ex.dat", *in_code_file = "ex.cod";
  char *out_code_verify1 = "test1_verify.cod";
  char *out_code_file1 = "test1.cod";
  char *out_code_file2 = "test2.cod";
  //int *coords, i, j, error;
  int *coords, *last_coords, i, j, error; /* WKV 2003-07-28 */
  float *levels;
  float alpha = 0.02, radius = 4.0;
  long rlen = 5000, ewin = 100;
  int dim = 5;
  char sysdo[200];
  eptr p;
  float radius2, *erange;

  // sets global parameters.  i think this is necessary...
  set_globals();
	
  printf("testing package som_devrobs.c:\n\n");

 test1:
  printf(" test 1: training from data file and code file:\n");
  // open data and code files
  data = open_entries(in_data_file);
  if(data == NULL) {
    printf("  data file %s could not be opened, abandoning test 1\n",
	   in_data_file);
    goto test2;
  }
  codes = open_entries(in_code_file);
  if(codes == NULL) {
    printf("  code file %s could not be opened, abandoning test 1\n",
	   in_code_file);
    goto test2;
  }
  params = construct_teach_params(codes, LINEAR, LINEAR);
  if(params == NULL) {
    printf("  could not create teach_params, abandoning test 1\n");
    goto test2;
  }
  init_training_session(params, alpha, radius, rlen, ewin);
  timing_start(params);
  train_fromdataset(params, data, CYCLIC);
  timing_stop(params);
  printf("  training session completed in %d seconds\n", 
  	 get_training_time(params));
  printf("  resulting quantization error: %f\n", get_error(params));
  error = save_entries(codes, out_code_file1);
  if(error) printf("  could not create file %s\n", out_code_file2);
  else printf("  resulting code file saved to %s\n", out_code_file2);

  free_teach_params(params); /* WKV 2003-07-28 */
  close_entries(codes);
  close_entries(data);
  
  printf("  running som-pak code for verification:\n");
  sprintf(sysdo, 
	  "./vsom -din %s -cin %s -cout %s -rlen %d -alpha %f -radius %f\n",
	 in_data_file, in_code_file, out_code_verify1, rlen, alpha, radius);
  system(sysdo);
  printf("  compare %s and %s to verify accuracy of test 1\n",
	 out_code_file1, out_code_verify1);

  printf("  test 1 completed\n\n");



 test2:
  printf(" test 2: training from data file, codes initialized from data:\n");
  // open data file
  data = open_entries(in_data_file);
  if(data == NULL) {
    printf("  data file %s could not be opened, abandoning test 2\n",
	   in_data_file);
    goto test3;
  }
  codes = randinit_codes(data, TOPOL_HEXA, NEIGH_BUBBLE, 12, 8);
  params = construct_teach_params(codes, LINEAR, LINEAR);
  if(params == NULL) {
    printf("  could not create teach_params, abandoning test 2\n");
    goto test3;
  }
  init_training_session(params, 0.02, 4.0, 5000, 25);
  timing_start(params);
  train_fromdataset(params, data, CYCLIC);
  timing_stop(params);
  printf("  training session completed in %d seconds\n", 
  	 get_training_time(params));
  printf("  resulting quantization error: %f\n", get_error(params));
  error = save_entries(codes, out_code_file2);
  if(error) printf("  could not create file %s\n", out_code_file2);
  else printf("  resulting code file saved to %s\n", out_code_file2);

  close_entries(codes);
  close_entries(data);
  free_teach_params(params); /* WKV 2003-07-28 */
  printf("  test 2 completed\n\n");


 test3:
  printf(" test 3: load codes from file, create data set dynamically,\n");
  printf("         train the SOM a few times, look at activation levels:\n");
  codes = open_entries(in_code_file);
  if(codes == NULL) {
    printf("  code file %s could not be opened, abandoning test 3\n",
	   in_code_file);
    goto end;
  }
  params = construct_teach_params(codes, LINEAR, LINEAR);
  if(params == NULL) {
    printf("  could not create teach_params, abandoning test 3\n");
    goto end;
  }
	init_training_session(params, 0.02, 4.0, 5000, 25);
  data = init_dataset(dim);
  input = make_data_entry(points);
  addto_dataset(data, input);
  input = make_data_entry(points1); 
  addto_dataset(data, input);
  input = make_data_entry_weighted_masked(points2, 2.0, mask, 5,0); 
  addto_dataset(data, input);
  input = make_data_entry(points3); 
  addto_dataset(data, input);
  printf("  data set:\n");
  print_dataset(data);

  input = rewind_entries(data, &p);
  last_coords = malloc(2*sizeof(int));  /* WKV 2003-07-28 */
  last_coords[0] = last_coords[1] = -1; /* WKV 2003-07-28 */

  while(input != NULL) {
    //coords = train_one(params, input);
    coords = train_one(params, input, last_coords, 1); /* WKV 2003-07-28 */
    free(last_coords);                                 /* WKV 2003-07-28 */
    last_coords = coords;                              /* WKV 2003-07-28 */
    
    printf("  input ");
    for(i=0;i<dim;i++) printf("%f ", input->points[i]);
    printf("\n    maps to model (%d,%d): ", coords[0], coords[1]);
    output = get_model_vector(codes, coords);
    for(i=0;i<dim;i++) printf("%f ", output->points[i]);
    printf("\n");
    sample = input;
    input = next_entry(&p);
  }

  radius2 = 2.0;
  erange = (float *) malloc(2*sizeof(float));
  erange[0] = 5.0;
  erange[1] = 20.0;

  printf("  last mapping, to model (%d,%d):\n",coords[0],coords[1]);
  printf("    produces the bubble (radius %.3f) SRN activations:\n",radius2);
  levels = get_activation_levels(params, coords, radius2, NEIGH_BUBBLE);
  for(i=0;i<codes->ydim;i++) {
    printf("    ");
    if(i%2==1) printf("   ");
    for(j=0;j<codes->xdim;j++)
      printf("%.3f ", levels[j+i*codes->xdim]);
    printf("\n");
  }
  free(levels); /* WKV 2003-07-28 */

  printf("    produces the gaussian (radius %.3f) SRN activations:\n",radius2);
  levels = get_activation_levels(params, coords, radius2, NEIGH_GAUSSIAN);
  for(i=0;i<codes->ydim;i++) {
    printf("    ");
    if(i%2==1) printf("   ");
    for(j=0;j<codes->xdim;j++)
      printf("%.3f ", levels[j+i*codes->xdim]);
    printf("\n");
  }
  free(levels); /* WKV 2003-07-28 */
  /* FIX:
  printf("    produces the fixed-window error-based SRN activations:\n");
  levels = get_levels_by_error(params, sample, erange[0]);
  for(i=0;i<codes->ydim;i++) {
    printf("    ");
    if(i%2==1) printf("   ");
    for(j=0;j<codes->xdim;j++)
      printf("%.3f ", levels[j+i*codes->xdim]);
    printf("\n");
  }
  printf("    produces the dynamic-window error-based SRN activations:\n");
  levels = get_levels_by_error(params, sample, 0.0);
  for(i=0;i<codes->ydim;i++) {
    printf("    ");
    if(i%2==1) printf("   ");
    for(j=0;j<codes->xdim;j++)
      printf("%.3f ", levels[j+i*codes->xdim]);
    printf("\n");
  }
  */
  close_entries(codes);
  //close_entries(data);
  // cannot close data because points# and mask are constant size arrays

  /* WKV 2003-07-28 */
  free_dataset(data);
  free(coords);
  free(erange);
  free_teach_params(params);

  printf("  test 3 completed\n\n");


 end:
  free_labels();
  printf("testing completed\n");
}
