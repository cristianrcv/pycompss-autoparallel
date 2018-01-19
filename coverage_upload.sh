#!/bin/bash -e

  # Check environment variable
  if [ "$CODACY_PROJECT_TOKEN" = "" ]; then
          echo "[WARN] No CODACY_PROJECT_TOKEN variable defined"
          if [ -f ".coverage_token" ]; then
                  echo "[INFO] Loading CODACY_PROJECT_TOKEN from .coverage_token file"
                  cpt=$(cat .coverage_token)
                  export CODACY_PROJECT_TOKEN=$cpt
          else
                  echo echo "[ERROR] Export CODACY_PROJECT_TOKEN variable or set .coverage_token file before running this script"
                  exit 1
          fi
  fi

  # Log token
  echo "[INFO] CODACY_PROJECT_TOKEN=$CODACY_PROJECT_TOKEN"

  # Upload coverage report
  python-codacy-coverage -r coverage.xml

