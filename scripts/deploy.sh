#!/usr/bin/env bash
set -e

gcloud run deploy betting-api \
  --source . \
  --region us-west1 \
  --allow-unauthenticated \
  --set-env-vars "DATABASE_URL=${DATABASE_URL},ODDS_API_KEY=${ODDS_API_KEY},ADMIN_API_KEY=${ADMIN_API_KEY}"
