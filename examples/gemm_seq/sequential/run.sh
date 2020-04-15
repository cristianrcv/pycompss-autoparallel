#!/bin/bash -e

  # Script global variables
  SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  RESULTS_DIR="${SCRIPT_DIR}"/../results/local/sequential

  rm -rf "${RESULTS_DIR}"
  mkdir -p "${RESULTS_DIR}"

  # Application arguments
  MSIZE=4

  # Run application
  python gemm.py $MSIZE

