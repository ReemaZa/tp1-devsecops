#!/usr/bin/env bash
# Scan SonarQube. Usage : SONAR_TOKEN=xxxx ./scripts/02_sonar_scan.sh vulnerable
# Linux : --network=host. Sur Windows/Mac, remplacer par SONAR_HOST_URL=http://host.docker.internal:9000
DIR=${1:-vulnerable}
docker run --rm --network=host \
  -e SONAR_HOST_URL="http://localhost:9000" \
  -e SONAR_TOKEN="$SONAR_TOKEN" \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli \
  -Dsonar.projectKey="tp-devsecops-$DIR" \
  -Dsonar.sources="$DIR"
