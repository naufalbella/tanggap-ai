#!/bin/bash

# TanggapAI Backend Deployment Script

set -e

echo "🚀 Deploying TanggapAI Backend..."

# Get ADK Agent URL
echo "📡 Getting ADK Agent URL..."
export AGENT_URL=$(gcloud run services describe tanggap-ai-adk-agent \
    --region=europe-west1 \
    --format='value(status.url)')

if [ -z "$AGENT_URL" ]; then
    echo "❌ Error: ADK Agent not found. Deploy ADK Agent first."
    exit 1
fi

echo "✅ ADK Agent URL: $AGENT_URL"

# Deploy backend
echo "📦 Deploying backend to Cloud Run..."
gcloud run deploy tanggap-ai-backend \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --max-instances 10 \
  --timeout 300 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project) \
  --set-env-vars AGENT_URL=$AGENT_URL

# Get backend URL
export BACKEND_URL=$(gcloud run services describe tanggap-ai-backend \
    --region=europe-west1 \
    --format='value(status.url)')

echo ""
echo "✅ Backend deployed successfully!"
echo "📍 Backend URL: $BACKEND_URL"
echo ""
echo "Test the API:"
echo "curl -X POST $BACKEND_URL/api/analyze -H 'Content-Type: application/json' -d '{\"feedback\": \"Website slow during peak hours\"}'"
