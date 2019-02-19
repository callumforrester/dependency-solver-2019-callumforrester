#!/bin/bash
if [ $# == 1 ]; then
    TESTS=$1
else
    TESTS=$(ls -d tests/*)
fi

for f in $TESTS; do
  echo "Running $f"
  ./solve $f/repository.json $f/initial.json $f/constraints.json
done
