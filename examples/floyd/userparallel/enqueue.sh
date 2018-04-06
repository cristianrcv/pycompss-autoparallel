#!/bin/bash -e                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                               
  # Script variables                                                                                                                                                                                                                                                           
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  EXEC_FILE=${SCRIPT_DIR}/floyd.py
  WORK_DIR=${SCRIPT_DIR}/results/mn/
  LOCAL_PYTHONPATH=${SCRIPT_DIR}

  # Script arguments
  if [ $# -ne 0 ] && [ $# -ne 8 ]; then
    echo "ERROR: Incorrect number of parameters"
    exit 1
  fi
  job_dependency=${1:-None}
  num_nodes=${2:-2}
  execution_time=${3:-10}
  cpus_per_node=${4:-48}
  tracing=${5:-true}
  graph=${6:-true}
  log_level=${7:-off}

  nsize=${8:-1000}

  # Setup Execution environment
  if [ ! -d "${WORK_DIR}" ]; then
    mkdir "${WORK_DIR}"
  fi

  export ComputingUnits=1

  # Enqueue job
  enqueue_compss \
    --job_dependency="${job_dependency}" \
    --exec_time="${execution_time}" \
    --num_nodes="${num_nodes}" \
    --cpus_per_node="${cpus_per_node}" \
    --log_level="${log_level}" \
    --tracing="${tracing}" \
    --graph="${graph}" \
    --master_working_dir="${WORK_DIR}" \
    --worker_working_dir=scratch \
    --base_log_dir="${WORK_DIR}" \
    --lang=python \
    --node_memory=50000 \
    --pythonpath="${LOCAL_PYTHONPATH}" \
    --qos=debug \
    "$EXEC_FILE" "$nsize"

  # Params: job_dependency num_nodes execution_time cpus_per_node tracing graph log_level NSIZE
  # Example: ./enqueue.sh None 2 10 48 false false off 1000
