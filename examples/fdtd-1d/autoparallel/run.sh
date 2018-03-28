#!/bin/bash

  TSIZE=8
  NSIZE=4

  export ComputingUnits=1

  DEBUG_FLAGS=""
  TOOLS_FLAGS=""

  runcompss \
          ${DEBUG_FLAGS} \
          ${TOOLS_FLAGS} \
          --lang=python \
          --project=../xml/project.xml \
          --resources=../xml/resources.xml \
          fdtd-1d.py $TSIZE $NSIZE
