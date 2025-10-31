#!/bin/bash
# Deploy GFMD A2A Swarm Agent to Google Cloud Run

set -e

# Configuration
PROJECT_ID="windy-tiger-471523-m5"
SERVICE_NAME="gfmd-a2a-swarm-agent"
REGION="us-central1"
SERVICE_ACCOUNT_KEY_PATH="/Users/merandafreiner/Downloads/windy-tiger-471523-m5-12203afb2f6b.json"

echo "🚀 Deploying GFMD A2A Swarm Agent to Google Cloud Run"
echo "=================================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set the project
echo "1️⃣ Setting project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "2️⃣ Enabling required Google Cloud APIs..."
gcloud services enable cloudrun.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Create secrets for sensitive data
echo "3️⃣ Creating secrets in Secret Manager..."

# Create service account key secret
gcloud secrets create service-account-key \
    --data-file="${SERVICE_ACCOUNT_KEY_PATH}" \
    --replication-policy="automatic" \
    2>/dev/null || echo "Secret 'service-account-key' already exists"

# Create other configuration secrets
echo "${PROJECT_ID}" | gcloud secrets create vertex-ai-project-id \
    --data-file=- \
    --replication-policy="automatic" \
    2>/dev/null || echo "Secret 'vertex-ai-project-id' already exists"

echo "us-central1" | gcloud secrets create vertex-ai-location \
    --data-file=- \
    --replication-policy="automatic" \
    2>/dev/null || echo "Secret 'vertex-ai-location' already exists"

# Build and deploy using Cloud Build
echo "4️⃣ Building and deploying to Cloud Run..."
gcloud builds submit --config=cloudbuild.yaml .

# Get the service URL
echo "5️⃣ Getting service information..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --format='value(status.url)')

echo ""
echo "✅ Deployment complete!"
echo "=================================================="
echo "🌐 Service URL: ${SERVICE_URL}"
echo ""
echo "📋 Next steps:"
echo "1. Test the health endpoint: curl ${SERVICE_URL}/health"
echo "2. View API documentation: ${SERVICE_URL}/docs"
echo "3. Monitor logs: gcloud run services logs read ${SERVICE_NAME} --region=${REGION}"
echo ""
echo "📊 Useful commands:"
echo "- View service details: gcloud run services describe ${SERVICE_NAME} --region=${REGION}"
echo "- Update traffic: gcloud run services update-traffic ${SERVICE_NAME} --region=${REGION}"
echo "- View metrics: https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/metrics"