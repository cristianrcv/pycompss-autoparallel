#!/bin/bash 

  #
  # Usage function
  #
  usage() {
    echo "ERROR: Incorrect parameters"
    echo "Usage: $0 <source> <output>"
    exit 1
  }


  #
  # MAIN
  #

  # Parse arguments
  if [ $# -ne 2 ]; then
    usage
  fi
  src=$1
  output=$2

  # Set script variables
  PLUTO_DIR=/opt/COMPSs/Dependencies/pluto/
  PLC=polycc #${PLUTO_DIR}/bin/polycc

  BASIC_OPTS="--tile --parallel"
  ADV_OPTS= #"--rar --lastwriter"
  MODE_OPTS="--debug" #"--silent" #"--debug" #"--moredebug"

  # TODO: Add option to polycc command --writescop
  # Execute PLUTO
  $PLC \
    "$src" \
    --readscop \
    "${BASIC_OPTS}" \
    "${ADV_OPTS}" \
    "${MODE_OPTS}" \
    -o "$output"
  ev=$?
 
  # Check PLUTO status
  if [ "$ev" -ne 0 ]; then
    echo "ERROR: PLUTO raised error $ev on translation"
    echo "Aborting..."
    exit $ev
  fi

  # TODO: Add option to polycc command instead of redirecting the debug mode
  # Move cloog file to output file
  mv "${output}".pluto.cloog "${output}"

  # Exit with last command status
  exit

