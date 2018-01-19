#!/bin/bash

  #
  # HELPER FUNCTIONS
  #

  # Run a coverage report for a module
  run() {
    coverage run --omit="/usr/lib/*" nose_tests.py
    coverage report -m
  }


  #
  # MAIN
  #

  # Run coverage on decorator
  (cd decorator || exit 1; run)

  # Run coverage on each translator
  (cd translators/code_loader || exit 1; run)
  (cd translators/code_replacer || exit 1; run)
  (cd translators/py2pycompss || exit 1; run)
  (cd translators/py2scop || exit 1; run)
  (cd translators/scop2pscop2py || exit 1; run)
  (cd translators/scop_types || exit 1; run)

  # Combine all reports
  coverage combine \
          decorator/.coverage \
          translators/code_loader/.coverage \
          translators/code_replacer/.coverage \
          translators/py2pycompss/.coverage \
          translators/py2scop/.coverage \
          translators/scop2pscop2py/.coverage \
          translators/scop_types/.coverage
  ev=$?
  if [ "$ev" -ne 0 ]; then
          echo "[ERROR] Coverage combine failed with exit value: $ev"
          exit $ev
  fi

  # Generate XML file
  coverage xml
  ev=$?
  if [ "$ev" -ne 0 ]; then
          echo "[ERROR] Coverage XML generation failed with exit value: $ev"
          exit $ev
  fi

  # Exit all ok
  exit 0

