#!/usr/bin/env bash
# SAST avec Bandit via Docker. Usage : ./scripts/01_bandit.sh vulnerable   (ou : fixed)
DIR=${1:-vulnerable}
mkdir -p reports
docker run --rm -v "$(pwd):/src" -w /src python:3.12-slim sh -c \
  "pip install -q bandit && bandit -r $DIR -f html -o reports/bandit_$DIR.html ; bandit -r $DIR"
echo "Rapport HTML : reports/bandit_$DIR.html"
