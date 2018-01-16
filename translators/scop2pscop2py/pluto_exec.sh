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
  MODE_OPTS= #"--silent" #"--debug" #"--moredebug"

  # Execute PLUTO
  $PLC \
    "$src" \
    --readscop \
    "${BASIC_OPTS}" \
    "${ADV_OPTS}" \
    "${MODE_OPTS}" \
    -o "$output"
  ev=$?
 
  if [ "$ev" -ne 0 ]; then
    echo "ERROR: PLUTO raised error $ev on translation"
    echo "Aborting..."
    exit $ev
  fi

  # Exit with last command status
  exit

