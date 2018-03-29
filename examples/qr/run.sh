#!/bin/bash -e

  # Script global variables
  SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

  for app_version in "${SCRIPT_DIR}"/*/; do
    echo "--- Executing $version"
    (
    cd "$app_version"
    ./run.sh "$@"
    )
  done

