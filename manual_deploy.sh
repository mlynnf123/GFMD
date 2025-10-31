#!/bin/bash
# Manual deployment approach for when APIs need to be enabled first

set -e

PROJECT_ID="windy-tiger-471523-m5"
SERVICE_NAME="gfmd-a2a-swarm-agent"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Manual Deployment - GFMD A2A Swarm Agent"
echo "============================================"

echo "Please ensure these APIs are enabled in the Google Cloud Console:"
echo "1. Cloud Build API: https://console.developers.google.com/apis/api/cloudbuild.googleapis.com/overview?project=${PROJECT_ID}"
echo "2. Cloud Run API: https://console.developers.google.com/apis/api/run.googleapis.com/overview?project=${PROJECT_ID}"
echo "3. Secret Manager API: https://console.developers.google.com/apis/api/secretmanager.googleapis.com/overview?project=${PROJECT_ID}"
echo ""

read -p "Have you enabled all the required APIs? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please enable the APIs first, then run this script again."
    exit 1
fi

echo "1️⃣ Building container image..."
gcloud builds submit --tag ${IMAGE_NAME} .

echo "2️⃣ Creating secrets..."
# Create service account key secret
gcloud secrets create service-account-key \
    --data-file="/Users/merandafreiner/Downloads/windy-tiger-471523-m5-12203afb2f6b.json" \
    --replication-policy="automatic" \
    2>/dev/null || echo "✓ Secret 'service-account-key' already exists"

# Create configuration secrets
echo "${PROJECT_ID}" | gcloud secrets create vertex-ai-project-id \
    --data-file=- \
    --replication-policy="automatic" \
    2>/dev/null || echo "✓ Secret 'vertex-ai-project-id' already exists"

echo "us-central1" | gcloud secrets create vertex-ai-location \
    --data-file=- \
    --replication-policy="automatic" \
    2>/dev/null || echo "✓ Secret 'vertex-ai-location' already exists"

echo "3️⃣ Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 900 \
    --max-instances 10 \
    --min-instances 1 \
    --set-env-vars "GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account.json" \
    --update-secrets "GOOGLE_APPLICATION_CREDENTIALS=service-account-key:latest"

echo "4️⃣ Getting service URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --format='value(status.url)')

echo ""
echo "✅ Deployment complete!"
echo "========================"
echo "🌐 Service URL: ${SERVICE_URL}"
echo ""
echo "🧪 Test endpoints:"
echo "curl ${SERVICE_URL}/health"
echo "curl ${SERVICE_URL}/api/v1/performance"
echo ""
echo "📊 View in console:"
echo "https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/metrics?project=${PROJECT_ID}"