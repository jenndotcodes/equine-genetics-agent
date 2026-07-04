#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Deploying Equine Genetics Agent to Google Cloud Run..."
echo "📍 Region: us-central1"
echo "📦 Building and deploying from source..."

# Deploy to Cloud Run
gcloud run deploy equine-genetics-simulator \
  --source . \
  --region us-central1 \
  --timeout=15 \
  --max-instances=1 \
  --allow-unauthenticated

echo "✅ Deployment completed successfully!"
