#!/bin/bash -e

  # Script global variables
  SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  RESULTS_DIR="${SCRIPT_DIR}"/../results/local/sequential
  APP_NAME=center_of_mass_sequential

  rm -rf "${RESULTS_DIR}"
  mkdir -p "${RESULTS_DIR}"

  # Run application
  # shellcheck disable=SC2086
  python center_of_mass.py > ${RESULTS_DIR}/${APP_NAME}.out
  
