#!/bin/bash

  NSIZE=8
  TSIZE=1

  export ComputingUnits=1

  DEBUG_FLAGS="-d"
  TOOLS_FLAGS="-g"

  runcompss \
          ${DEBUG_FLAGS} \
          ${TOOLS_FLAGS} \
          --lang=python \
          --project=../xml/project.xml \
          --resources=../xml/resources.xml \
          jacobi-2d.py $NSIZE $TSIZE
