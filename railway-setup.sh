#!/bin/bash

# Railway Environment Variables Setup
# Run this after: railway login && railway new && railway link

echo "🚂 Setting up Railway environment variables..."

# Set environment variables from .env file
echo "Reading from .env file..."

# Production environment
railway variables --set "ENVIRONMENT=production"

# MongoDB settings
MONGODB_CONNECTION=$(grep MONGODB_CONNECTION_STRING .env | cut -d'=' -f2 | tr -d '"')
MONGODB_PASSWORD=$(grep MONGODB_PASSWORD .env | cut -d'=' -f2 | tr -d '"')
GROQ_API_KEY=$(grep GROQ_API_KEY .env | cut -d'=' -f2 | tr -d '"')

echo "Setting MongoDB connection..."
railway variables --set "MONGODB_CONNECTION_STRING=$MONGODB_CONNECTION"

echo "Setting MongoDB password..."
railway variables --set "MONGODB_PASSWORD=$MONGODB_PASSWORD"

echo "Setting Groq API key..."
railway variables --set "GROQ_API_KEY=$GROQ_API_KEY"

# Gmail credentials path (we'll upload the file separately)
railway variables --set "GMAIL_CREDENTIALS_PATH=/app/gmail_credentials.json"

# Disable tokenizers parallelism for production
railway variables --set "TOKENIZERS_PARALLELISM=false"

# Python settings
railway variables --set "PYTHONUNBUFFERED=1"
railway variables --set "PYTHONPATH=/app"

echo "✅ Environment variables set!"
echo
echo "📝 Next steps:"
echo "1. Deploy with: railway up"
echo "2. Monitor logs with: railway logs"
echo "3. Check status with: railway status"

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up --detach

echo "✅ Deployment started!"
echo "View your deployment: railway open"