/* Converts a SCoP from OpenScop to C using ClooG */

#include <stdlib.h>
#include <osl/osl.h>
#include <cloog/cloog.h>


/* Use the CLooG library to output a SCoP from OpenScop to C */
void print_scop_to_c(FILE* output, osl_scop_p scop) {
  CloogState* state;
  CloogOptions* options;
  CloogInput* input;
  struct clast_stmt* clast;

  state = cloog_state_malloc();
  options = cloog_options_malloc(state);
  options->openscop = 1;
  cloog_options_copy_from_osl_scop(scop, options);
  input = cloog_input_from_osl_scop(options->state, scop);
  clast = cloog_clast_create_from_input(input, options);
  clast_pprint(output, clast, 0, options);

  cloog_clast_free(clast);
  options->scop = NULL; // don't free the scop
  cloog_options_free(options);
  cloog_state_free(state); // the input is freed inside
}


int main(int argc, char* argv[]) {
  osl_scop_p scop;
  FILE* input;
  FILE* output;

  // Process arguments
  if (argc != 3) {
    fprintf(stderr, "usage: %s src.scop output.c\n", argv[0]);
    exit(0);
  }

  // Check open files
  input = fopen(argv[1], "r");
  if (input == NULL) {
    fprintf(stderr, "ERROR: Cannot open input file\n");
    exit(1);
  }
  
  output = fopen(argv[2], "w");
  if (output == NULL) {
    fprintf(stderr, "ERROR: Cannot open output file\n");
    exit(1);
  }

  // Process and transform
  osl_interface_p registry = osl_interface_get_default_registry();
  scop = osl_scop_pread(input, registry, OSL_PRECISION_MP);
  print_scop_to_c(output, scop);

  // Clean
  osl_scop_free(scop);  
  fclose(input);
  fclose(output);

  return 0;
}
