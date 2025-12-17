#!/bin/bash

# GFMD Quick Deployment Script for windy-tiger-471523-m5

set -e

# Configuration
PROJECT_ID="windy-tiger-471523-m5"
REGION="us-central1"
SERVICE_NAME="gfmd-email-automation"
IMAGE_NAME="gcr.io/$PROJECT_ID/gfmd-automation"

echo "🚀 GFMD Email Automation - Quick Deploy to $PROJECT_ID"
echo "======================================================"

# Set project
echo "Setting project..."
gcloud config set project $PROJECT_ID

# Enable APIs
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Create service account
echo "Creating service account..."
gcloud iam service-accounts create gfmd-automation-sa \
    --display-name="GFMD Email Automation" \
    --project=$PROJECT_ID \
    2>/dev/null || echo "Service account may already exist"

# Grant permissions
echo "Setting up permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:gfmd-automation-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Create secrets with current values
echo "Creating secrets from your .env file..."

# MongoDB Connection String
echo "Creating MongoDB connection secret..."
MONGODB_CONNECTION=$(grep MONGODB_CONNECTION_STRING .env | cut -d'=' -f2 | tr -d '"')
echo -n "$MONGODB_CONNECTION" | gcloud secrets create gfmd-mongodb-connection \
    --replication-policy="automatic" --data-file=- \
    --project=$PROJECT_ID 2>/dev/null || \
echo -n "$MONGODB_CONNECTION" | gcloud secrets versions add gfmd-mongodb-connection \
    --data-file=- --project=$PROJECT_ID

# MongoDB Password
echo "Creating MongoDB password secret..."
MONGODB_PASSWORD=$(grep MONGODB_PASSWORD .env | cut -d'=' -f2 | tr -d '"')
echo -n "$MONGODB_PASSWORD" | gcloud secrets create gfmd-mongodb-password \
    --replication-policy="automatic" --data-file=- \
    --project=$PROJECT_ID 2>/dev/null || \
echo -n "$MONGODB_PASSWORD" | gcloud secrets versions add gfmd-mongodb-password \
    --data-file=- --project=$PROJECT_ID

# Groq API Key
echo "Creating Groq API secret..."
GROQ_API_KEY=$(grep GROQ_API_KEY .env | cut -d'=' -f2 | tr -d '"')
echo -n "$GROQ_API_KEY" | gcloud secrets create gfmd-groq-api-key \
    --replication-policy="automatic" --data-file=- \
    --project=$PROJECT_ID 2>/dev/null || \
echo -n "$GROQ_API_KEY" | gcloud secrets versions add gfmd-groq-api-key \
    --data-file=- --project=$PROJECT_ID

# Gmail Credentials
echo "Creating Gmail credentials secret..."
gcloud secrets create gfmd-gmail-credentials \
    --replication-policy="automatic" --data-file=gmail_credentials.json \
    --project=$PROJECT_ID 2>/dev/null || \
gcloud secrets versions add gfmd-gmail-credentials \
    --data-file=gmail_credentials.json --project=$PROJECT_ID

echo "✅ All secrets created!"

# Build container
echo "Building container..."
gcloud builds submit --tag $IMAGE_NAME --project=$PROJECT_ID

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 1 \
    --max-instances 1 \
    --no-cpu-throttling \
    --service-account "gfmd-automation-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --set-env-vars "ENVIRONMENT=production" \
    --set-secrets "MONGODB_CONNECTION_STRING=gfmd-mongodb-connection:latest" \
    --set-secrets "MONGODB_PASSWORD=gfmd-mongodb-password:latest" \
    --set-secrets "GROQ_API_KEY=gfmd-groq-api-key:latest" \
    --set-secrets "GMAIL_CREDENTIALS_PATH=gfmd-gmail-credentials:latest" \
    --project=$PROJECT_ID

echo "🎉 Deployment completed!"
echo
echo "📊 Service URL:"
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" --project=$PROJECT_ID

echo
echo "📝 View logs:"
echo "gcloud run logs tail $SERVICE_NAME --region $REGION --project=$PROJECT_ID"