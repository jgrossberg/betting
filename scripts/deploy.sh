#!/usr/bin/env bash
set -e

# Load .env file
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi

gcloud run deploy betting-api \
  --source . \
  --region us-west1 \
  --allow-unauthenticated \
  --set-env-vars "DATABASE_URL=${DATABASE_URL},ODDS_API_KEY=${ODDS_API_KEY},ADMIN_API_KEY=${ADMIN_API_KEY}"
