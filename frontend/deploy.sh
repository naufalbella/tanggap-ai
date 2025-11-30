#!/bin/bash

# TanggapAI Frontend Deployment Script

set -e

echo "🚀 Deploying TanggapAI Frontend..."

# Get Backend URL
echo "📡 Getting Backend URL..."
export BACKEND_URL=$(gcloud run services describe tanggap-ai-backend \
    --region=europe-west1 \
    --format='value(status.url)')

if [ -z "$BACKEND_URL" ]; then
    echo "❌ Error: Backend not found. Deploy backend first."
    exit 1
fi

echo "✅ Backend URL: $BACKEND_URL"

# Create config.js file with backend URL
echo "📝 Creating config.js with backend URL..."
cat > config.js << EOF
// Auto-generated configuration file
// This file is created during deployment
window.BACKEND_URL = '${BACKEND_URL}';
EOF

echo "✅ Config file created"

# Deploy frontend
echo "📦 Deploying frontend to Cloud Run..."
gcloud run deploy tanggap-ai-frontend \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --timeout 60

# Get frontend URL
export FRONTEND_URL=$(gcloud run services describe tanggap-ai-frontend \
    --region=europe-west1 \
    --format='value(status.url)')

echo ""
echo "✅ Frontend deployed successfully!"
echo "📍 Frontend URL: $FRONTEND_URL"
echo "📍 Backend URL: $BACKEND_URL"
echo ""
echo "🌐 Open in browser:"
echo "open $FRONTEND_URL"
echo ""
echo "✅ Configuration:"
echo "   Frontend will automatically connect to: $BACKEND_URL"

# Clean up local config file
rm -f config.js
echo ""
echo "✅ Deployment complete!"
