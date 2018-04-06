#!/bin/bash -e


  #
  # HELPER FUNCTIONS
  #

  wait_and_get_jobID() {
    sleep 6s
    job_dependency=$(squeue | grep "$(whoami)" | sort -n - | tail -n 1 | awk '{ print $1 }')
    echo "Last Job ID: ${job_dependency}"
  }


  #
  # MAIN
  #

  # Script global variables
  SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

  # Script arguments
  tracing=${1:-true}
  graph=${2:-true}
  log_level=${3:-off}

  # Application variables
  NSIZES=(1000)
  NUM_NODES=(2)
  EXEC_TIMES=(10)

  cpus_per_node=48

  job_dependency=None
  for i in "${!NSIZES[@]}"; do
    nsize=${NSIZES[$i]}
    num_nodes=${NUM_NODES[$i]}
    execution_time=${EXEC_TIMES[$i]}

    for app_version in "${SCRIPT_DIR}"/*/; do
      echo "--- Enqueueing ${app_version}"
      (
      cd "$app_version"
      ./enqueue.sh "${job_dependency}" "${num_nodes}" "${execution_time}" "${cpus_per_node}" "${tracing}" "${graph}" "${log_level}" "${nsize}"
      wait_and_get_jobID
      )
    done
  done
