#!/usr/bin/env bash
set -e

echo "Running black formatting"
if [[ -n "${CI}" ]]; then
  FLAGS="--check"
fi

black "$@" ${FLAGS} src tests
