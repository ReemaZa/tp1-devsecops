#!/usr/bin/env bash
DIR=${1:-vulnerable}

# Charge les variables du fichier .env (si présent)
if [ -f .env ]; then set -a; source .env; set +a; fi

docker run --rm \
  -e SONAR_HOST_URL="http://host.docker.internal:9000" \
  -e SONAR_TOKEN="${SONAR_TOKEN:?Définissez SONAR_TOKEN dans .env}" \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli \
  -Dsonar.projectKey="tp-devsecops-$DIR" \
  -Dsonar.sources="$DIR"