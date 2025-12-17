#!/bin/bash

# GFMD Email Automation - Secrets Setup Script
# This script creates the required secrets in Google Secret Manager

set -e  # Exit on any error

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔒 GFMD Email Automation - Secrets Setup${NC}"
echo "============================================"

# Check if PROJECT_ID is set
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo -e "${RED}❌ Please set your PROJECT_ID:${NC}"
    echo "export PROJECT_ID=your-actual-project-id"
    exit 1
fi

echo -e "${YELLOW}Setting up secrets for project: $PROJECT_ID${NC}"
echo

# Function to create secret if it doesn't exist
create_secret() {
    local secret_name=$1
    local description=$2
    
    if gcloud secrets describe $secret_name >/dev/null 2>&1; then
        echo -e "${YELLOW}Secret '$secret_name' already exists${NC}"
    else
        echo -e "${GREEN}Creating secret: $secret_name${NC}"
        gcloud secrets create $secret_name --replication-policy="automatic" --data-file=-
    fi
}

# MongoDB Connection String
echo -e "${BLUE}📊 Setting up MongoDB connection string...${NC}"
echo "Enter your MongoDB connection string:"
echo "Example: mongodb+srv://username:password@cluster0.xyz.mongodb.net/?appName=Cluster0"
read -r MONGODB_CONNECTION
echo -n "$MONGODB_CONNECTION" | gcloud secrets create gfmd-mongodb-connection --replication-policy="automatic" --data-file=- || \
echo -n "$MONGODB_CONNECTION" | gcloud secrets versions add gfmd-mongodb-connection --data-file=-

# MongoDB Password
echo -e "${BLUE}🔑 Setting up MongoDB password...${NC}"
echo "Enter your MongoDB password:"
read -rs MONGODB_PASSWORD
echo -n "$MONGODB_PASSWORD" | gcloud secrets create gfmd-mongodb-password --replication-policy="automatic" --data-file=- || \
echo -n "$MONGODB_PASSWORD" | gcloud secrets versions add gfmd-mongodb-password --data-file=-

# Groq API Key
echo -e "${BLUE}🤖 Setting up Groq API key...${NC}"
echo "Enter your Groq API key:"
read -rs GROQ_API_KEY
echo -n "$GROQ_API_KEY" | gcloud secrets create gfmd-groq-api-key --replication-policy="automatic" --data-file=- || \
echo -n "$GROQ_API_KEY" | gcloud secrets versions add gfmd-groq-api-key --data-file=-

# Gmail Credentials
echo -e "${BLUE}📧 Setting up Gmail credentials...${NC}"
echo "Please upload your gmail_credentials.json file"
echo "File path to gmail_credentials.json:"
read -r GMAIL_CREDS_PATH

if [ -f "$GMAIL_CREDS_PATH" ]; then
    gcloud secrets create gfmd-gmail-credentials --replication-policy="automatic" --data-file="$GMAIL_CREDS_PATH" || \
    gcloud secrets versions add gfmd-gmail-credentials --data-file="$GMAIL_CREDS_PATH"
    echo -e "${GREEN}✅ Gmail credentials uploaded${NC}"
else
    echo -e "${RED}❌ Gmail credentials file not found: $GMAIL_CREDS_PATH${NC}"
    exit 1
fi

echo
echo -e "${GREEN}✅ All secrets configured successfully!${NC}"
echo
echo -e "${BLUE}📋 Created secrets:${NC}"
gcloud secrets list --filter="name~gfmd-"

echo
echo -e "${YELLOW}🔐 Secret access test:${NC}"
echo "Testing secret access..."
gcloud secrets versions access latest --secret="gfmd-mongodb-connection" >/dev/null && echo "✅ MongoDB connection: OK"
gcloud secrets versions access latest --secret="gfmd-mongodb-password" >/dev/null && echo "✅ MongoDB password: OK"
gcloud secrets versions access latest --secret="gfmd-groq-api-key" >/dev/null && echo "✅ Groq API key: OK"
gcloud secrets versions access latest --secret="gfmd-gmail-credentials" >/dev/null && echo "✅ Gmail credentials: OK"

echo
echo -e "${GREEN}🎉 Secrets setup completed!${NC}"
echo "You can now run the deployment script: ./deploy.sh"