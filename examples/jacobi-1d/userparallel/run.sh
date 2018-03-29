#!/bin/bash -e

  # Script global variables
  SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  RESULTS_DIR="${SCRIPT_DIR}"/results/local
  LOG_DIR=$HOME/.COMPSs/jacobi1d_userparallel

  rm -rf "${LOG_DIR}"
  rm -rf "${RESULTS_DIR}"
  mkdir -p "${LOG_DIR}"
  mkdir -p "${RESULTS_DIR}"

  # Script parameters
  if [ $# -eq 0 ]; then
    user_flags=""
  else
    user_flags=$*
  fi

  # COMPSs parameters
  DEBUG_FLAGS="-d"
  TOOLS_FLAGS="-g"

  # Application arguments
  NSIZE=8
  TSIZE=1

  export ComputingUnits=1

  # Run application
  # shellcheck disable=SC2086
  runcompss \
          ${DEBUG_FLAGS} \
          ${TOOLS_FLAGS} \
          ${user_flags} \
          --specific_log_dir="${LOG_DIR}" \
          --lang=python \
          --project=../../xml/project.xml \
          --resources=../../xml/resources.xml \
          jacobi-1d.py $NSIZE $TSIZE

  # Copy results
  if [ -f "${LOG_DIR}/monitor/complete_graph.dot" ]; then
    cp "${LOG_DIR}"/monitor/complete_graph.dot "${RESULTS_DIR}"
    gengraph "${RESULTS_DIR}"/complete_graph.dot
    dot -Tpng "${RESULTS_DIR}"/complete_graph.dot > "${RESULTS_DIR}"/complete_graph.png
  fi
  if [ -d "${LOG_DIR}/trace/" ]; then
    cp -r "${LOG_DIR}"/trace "${RESULTS_DIR}"
  fi
