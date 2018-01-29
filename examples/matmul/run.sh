#!/bin/bash

  runcompss \
          -d \
          --lang=python \
          --project=./xml/project.xml \
          --resources=./xml/resources.xml \
          matmul.py

