#!/usr/bin/env bash
DIR=${1:-vulnerable}

# Charge les variables du fichier .env (si présent)
if [ -f .env ]; then set -a; source .env; set +a; fi
DIR=${1:-vulnerable}

mkdir -p reports odc-data
docker run --rm \
  -v "$(pwd):/src" \
  -v "$(pwd)/odc-data:/usr/share/dependency-check/data" \
  -v "$(pwd)/reports:/report" \
  owasp/dependency-check \
  --scan "/src/$DIR" --format HTML --out /report \
  --project "tp-devsecops-$DIR"  --enableExperimental --nvdApiKey "${NVD_API_KEY:?Définissez NVD_API_KEY dans .env}"

echo "Rapport : reports/dependency-check-report.html"