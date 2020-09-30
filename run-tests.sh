#!/bin/bash

set -uexo pipefail

cd $(dirname $0)

# Discover satchless apps which contain tests
apps_with_test_dirs=( $(find . | grep 'tests/__init__.py$' | sed 's/\/tests\/__init__\.py//g' | sed 's/\//./g' | sed 's/^\.\.//g') )
apps_with_test_py=( $(find . | grep 'test[a-z_0-9].py$' | sed 's/\/test.*py//g' | sed 's/\//./g' | sed 's/^\.\.//g') )
apps_to_test=( "${apps_with_test_dirs[@]}" "${apps_with_test_py[@]}" )

echo "Running tests for ${apps_to_test[@]}"
if [[ ! -z ${COVERAGE:-} ]]
then
  prefix="coverage run --source=satchless"
else
  prefix="python"
fi
exec $prefix satchless_test/manage.py test ${apps_to_test[@]}
