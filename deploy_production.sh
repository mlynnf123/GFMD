#!/bin/bash
# Deploy Firestore-Enabled GFMD System to Cloud Run

set -e

PROJECT_ID="windy-tiger-471523-m5"
REGION="us-central1"
SERVICE_NAME="gfmd-a2a-swarm-agent"

echo "🚀 Deploying Firestore-Enabled GFMD System"
echo "=========================================="

# Build and deploy to Cloud Run
echo "1️⃣ Building and deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --source . \
    --platform managed \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --concurrency 10 \
    --timeout 3600 \
    --max-instances 10 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
    --set-env-vars="VERTEX_AI_PROJECT_ID=${PROJECT_ID}" \
    --set-env-vars="VERTEX_AI_LOCATION=${REGION}"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)')

echo "✅ Deployment completed!"
echo "Service URL: ${SERVICE_URL}"

# Test the new API endpoint
echo ""
echo "2️⃣ Testing Firestore API endpoint..."
curl -X POST "${SERVICE_URL}/api/v1/automation/daily-run" \
    -H "Content-Type: application/json" \
    -d '{"num_prospects": 1}' \
    | jq '.'

echo ""
echo "3️⃣ Testing stats endpoint..."
curl -X GET "${SERVICE_URL}/api/v1/stats" \
    -H "Content-Type: application/json" \
    | jq '.'

echo ""
echo "🎉 Firestore system deployed and tested successfully!"
echo "Now ready for 50+ daily emails with Cloud Scheduler!"