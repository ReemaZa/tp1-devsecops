#!/usr/bin/env bash
# SCA rapide avec pip-audit. Usage : ./scripts/03_sca_pip_audit.sh vulnerable
DIR=${1:-vulnerable}
docker run --rm -v "$(pwd):/src" -w /src python:3.12-slim sh -c \
  "pip install -q pip-audit && pip-audit -r $DIR/requirements.txt"
