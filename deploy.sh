#!/bin/bash
# Deploy GFMD AI Swarm Agent to Cloud Run
# Clean, production-ready deployment

set -e

PROJECT_ID="windy-tiger-471523-m5"
REGION="us-central1"
SERVICE_NAME="gfmd-a2a-swarm-agent"

echo "🚀 GFMD AI Swarm Agent - Production Deployment"
echo "==============================================="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "==============================================="

# Deploy to Cloud Run
echo "📦 Deploying to Cloud Run..."
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

echo ""
echo "✅ Deployment completed!"
echo "Service URL: ${SERVICE_URL}"

# Test the deployment
echo ""
echo "🧪 Testing deployment..."
curl -X GET "${SERVICE_URL}/" | jq '.'

echo ""
echo "🎉 Production deployment successful!"
echo "🔗 Service URL: ${SERVICE_URL}"