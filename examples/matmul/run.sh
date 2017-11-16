#!/bin/bash

  runcompss \
          --lang=python \
          -d \
          --project=./xml/project.xml \
          --resources=./xml/resources.xml \
          matmul.py

