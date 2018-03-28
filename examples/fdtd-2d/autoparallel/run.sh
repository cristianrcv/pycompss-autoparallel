#!/bin/bash

  NXSIZE=4
  NYSIZE=4
  TSIZE=8

  export ComputingUnits=1

  DEBUG_FLAGS=""
  TOOLS_FLAGS=""

  runcompss \
          ${DEBUG_FLAGS} \
          ${TOOLS_FLAGS} \
          --lang=python \
          --project=../xml/project.xml \
          --resources=../xml/resources.xml \
          fdtd-2d.py $NXSIZE $NYSIZE $TSIZE
