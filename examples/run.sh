#!/bin/bash -e

  #
  # Helper methods
  #

  execute_example() {
    local example
    example=$1

    echo "*** Executing example $example"
    cd "$example"
    for version in *; do
      echo "- Executing $example - $version"
      (
      cd "$version"
      if [ -f "run.sh" ]; then
        ./run.sh
      else
        echo "[WARN] Cannot find run.sh script. Skipping application"
      fi
      )
    done
    cd "${SCRIPT_DIR}"
  }


  #
  # MAIN
  #

  # Set script variables
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  # Launch all examples
  for example in *; do
    if [ "$example" != "xml" ] && [ "$example" != "run.sh" ]; then
      execute_example "$example"
    fi
  done

