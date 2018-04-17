#!/bin/bash -e


  #
  # HELPER FUNCTIONS
  #

  #
  # MAIN
  #

  # Script global variables
  SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

  # Script arguments
  job_log_file=${1:-experiments.log}
  job_results_file=${2:-./results/mn/results.summary}
  move_traces=${3:-true}

  # Initialize results log file
  echo "JOB_ID		VERSION		MSIZE	BSIZE	TRACING	TOTAL_TIME	INIT_TIME	COMP_TIME	NUM_TASKS" > "${job_results_file}"

  first=0
  while read -r line; do
    # Skip header
    if [ "$first" -eq 0 ]; then
      first=1
      continue
    fi

    # Get job log file information
    job_id=$(echo "$line" | awk '{ print $1 }')
    version=$(echo "$line" | awk '{ print $2 }')
    msize=$(echo "$line" | awk '{ print $3 }')
    bsize=$(echo "$line" | awk '{ print $4 }')
    tracing=$(echo "$line" | awk '{ print $5 }')

    # Get job output information
    job_output=${SCRIPT_DIR}/results/mn/${version}/compss-${job_id}.out
    total_time=$(grep "TOTAL_TIME" "${job_output}" | awk '{ print $NF }' | cat)
    init_time=$(grep "INIT_TIME" "${job_output}" | awk '{ print $NF }' | cat)
    comp_time=$(grep "MULT_TIME" "${job_output}" | awk '{ print $NF }' | cat)
    num_tasks=$(grep "Total executed tasks:" "${job_output}" | awk '{ print $NF }' | cat)

    # Print results
    echo "${job_id}       ${version}        ${msize}	${bsize}	${tracing}	${total_time}	${init_time}	${comp_time}	${num_tasks}" >> "${job_results_file}"

    # Move traces to its location
    if [ "${move_traces}" == "true" ] && [ "$tracing" == "true" ]; then
      trace_path=${SCRIPT_DIR}/results/mn/${version}/.COMPSs/${job_id}/trace
      new_trace_path=${SCRIPT_DIR}/results/mn/${version}/trace-${job_id}
      new_trace_basename=matmul-${version}-${job_id}-${msize}-${bsize}
      mkdir -p "${new_trace_path}"
      if [[ $(find "${trace_path}" -name "*.prv") != "" ]]; then
        cp "${trace_path}"/*.prv "${new_trace_path}"/"${new_trace_basename}".prv
        cp "${trace_path}"/*.pcf "${new_trace_path}"/"${new_trace_basename}".pcf
        cp "${trace_path}"/*.row "${new_trace_path}"/"${new_trace_basename}".row
      fi
    fi
  done < "${job_log_file}"
