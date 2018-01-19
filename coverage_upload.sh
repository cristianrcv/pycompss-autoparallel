#!/bin/bash -e

  # Check environment variable
  if [ "$CODACY_PROJECT_TOKEN" = "" ]; then
          echo "[ERROR] Export CODACY_PROJECT_TOKEN variable before running this script"
          exit 1
  fi

  # Upload coverage report
  python-codacy-coverage -r coverage.xml

