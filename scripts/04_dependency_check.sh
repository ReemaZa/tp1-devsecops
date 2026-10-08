#!/usr/bin/env bash
# SCA avec OWASP Dependency-Check. Usage : NVD_API_KEY=xxx ./scripts/04_dependency_check.sh vulnerable
# La 1re exécution télécharge la base NVD (10-30 min). Une clé API gratuite accélère beaucoup :
# https://nvd.nist.gov/developers/request-an-api-key
DIR=${1:-vulnerable}
mkdir -p reports odc-data
docker run --rm \
  -v "$(pwd):/src" \
  -v "$(pwd)/odc-data:/usr/share/dependency-check/data" \
  -v "$(pwd)/reports:/report" \
  owasp/dependency-check \
  --scan "/src/$DIR" --format HTML --out /report \
  --project "tp-devsecops-$DIR" --nvdApiKey "$NVD_API_KEY"
echo "Rapport : reports/dependency-check-report.html"
