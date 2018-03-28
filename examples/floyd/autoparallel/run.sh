#!/bin/bash

  NSIZE=4

  export ComputingUnits=1

  DEBUG_FLAGS="-dg"
  TOOLS_FLAGS=""

  runcompss \
          ${DEBUG_FLAGS} \
          ${TOOLS_FLAGS} \
          --lang=python \
          --project=../xml/project.xml \
          --resources=../xml/resources.xml \
          floyd.py $NSIZE
