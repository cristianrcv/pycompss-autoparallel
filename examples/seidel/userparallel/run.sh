#!/bin/bash

  NSIZE=8
  TSIZE=1

  export ComputingUnits=1

  DEBUG_FLAGS="-dg"
  TOOLS_FLAGS=""

  runcompss \
          ${DEBUG_FLAGS} \
          ${TOOLS_FLAGS} \
          --lang=python \
          --project=../xml/project.xml \
          --resources=../xml/resources.xml \
          seidel.py $NSIZE $TSIZE
