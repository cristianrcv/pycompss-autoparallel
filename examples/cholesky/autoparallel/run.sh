#!/bin/bash

  MSIZE=4
  BSIZE=4

  export ComputingUnits=1

  DEBUG_FLAGS="-d"
  TOOLS_FLAGS="-g"

  runcompss \
          ${DEBUG_FLAGS} \
          ${TOOLS_FLAGS} \
          --lang=python \
          --project=../../xml/project.xml \
          --resources=../../xml/resources.xml \
          cholesky.py $MSIZE $BSIZE
