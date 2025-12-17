#!/bin/bash

# GFMD Email Automation - Google Cloud Deployment Script
# This script deploys the email automation system to Google Cloud Run

set -e  # Exit on any error

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME="gfmd-email-automation"
IMAGE_NAME="gcr.io/$PROJECT_ID/gfmd-automation"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 GFMD Email Automation - Google Cloud Deployment${NC}"
echo "=================================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi

# Check if PROJECT_ID is set
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo -e "${YELLOW}⚠️ Please set your PROJECT_ID:${NC}"
    echo "export PROJECT_ID=your-actual-project-id"
    echo "Then run this script again."
    exit 1
fi

echo -e "${BLUE}📋 Configuration:${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Name: $SERVICE_NAME"
echo "Image: $IMAGE_NAME"
echo

# Authenticate and set project
echo -e "${YELLOW}🔐 Setting up Google Cloud project...${NC}"
gcloud config set project $PROJECT_ID
gcloud auth configure-docker

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required Google Cloud APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Create service account
echo -e "${YELLOW}👤 Creating service account...${NC}"
gcloud iam service-accounts create gfmd-automation-sa \
    --display-name="GFMD Email Automation Service Account" \
    --description="Service account for GFMD email automation system" \
    || echo "Service account may already exist"

# Grant necessary permissions
echo -e "${YELLOW}🔑 Setting up permissions...${NC}"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:gfmd-automation-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Create secrets (if they don't exist)
echo -e "${YELLOW}🔒 Setting up secrets...${NC}"
echo "You'll need to create the following secrets manually:"
echo "1. MongoDB connection string"
echo "2. MongoDB password" 
echo "3. Groq API key"
echo "4. Gmail credentials JSON"

# Build and push the container
echo -e "${YELLOW}🐳 Building and pushing container...${NC}"
gcloud builds submit --tag $IMAGE_NAME .

# Deploy to Cloud Run
echo -e "${YELLOW}🌟 Deploying to Cloud Run...${NC}"
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
    --set-secrets "GROQ_API_KEY=gfmd-groq-api-key:latest"

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo
echo -e "${BLUE}📊 Service Information:${NC}"
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"

echo
echo -e "${GREEN}🎉 Your GFMD email automation is now running on Google Cloud!${NC}"
echo "The system will:"
echo "  • Add 20 new contacts daily (business days at 8 AM)"
echo "  • Send emails every 2 business days"
echo "  • Run continuously 24/7"
echo
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Create the required secrets (see secrets-setup.sh)"
echo "2. Monitor logs: gcloud run logs tail $SERVICE_NAME --region $REGION"
echo "3. View service: https://console.cloud.google.com/run"