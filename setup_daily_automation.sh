#!/bin/bash
# Setup daily automation for GFMD A2A Swarm Agent

set -e

PROJECT_ID="windy-tiger-471523-m5"
REGION="us-central1"
SERVICE_URL="https://gfmd-a2a-swarm-agent-531787444060.us-central1.run.app"
JOB_NAME="gfmd-daily-automation"

echo "🚀 Setting up Daily Automation for GFMD A2A Swarm Agent"
echo "======================================================="

# Enable Cloud Scheduler API
echo "1️⃣ Enabling Cloud Scheduler API..."
gcloud services enable cloudscheduler.googleapis.com

# Create service account for scheduler if it doesn't exist
echo "2️⃣ Setting up service account for scheduler..."
gcloud iam service-accounts create scheduler-invoker \
    --display-name="Cloud Scheduler Service Account" \
    --description="Service account for Cloud Scheduler to invoke Cloud Run" \
    2>/dev/null || echo "✓ Service account already exists"

# Grant necessary permissions
echo "3️⃣ Granting permissions..."
gcloud run services add-iam-policy-binding gfmd-a2a-swarm-agent \
    --member="serviceAccount:scheduler-invoker@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.invoker" \
    --region=${REGION}

# Create Cloud Scheduler job for 9am CST daily
echo "4️⃣ Creating daily scheduler job..."
gcloud scheduler jobs create http ${JOB_NAME} \
    --location=${REGION} \
    --schedule="0 9 * * *" \
    --time-zone="America/Chicago" \
    --uri="${SERVICE_URL}/api/v1/automation/daily-run" \
    --http-method=POST \
    --headers="Content-Type=application/json" \
    --message-body='{"trigger":"daily_automation","source":"cloud_scheduler","batch_size":50}' \
    --oidc-service-account-email="scheduler-invoker@${PROJECT_ID}.iam.gserviceaccount.com" \
    --attempt-deadline=900s \
    2>/dev/null || echo "✓ Scheduler job already exists"

echo ""
echo "✅ Daily automation setup complete!"
echo "================================================"
echo "🕘 Schedule: Every day at 9:00 AM CST"
echo "🎯 Target: ${SERVICE_URL}/api/v1/automation/daily-run"
echo "📋 Job Name: ${JOB_NAME}"
echo ""
echo "📊 Management commands:"
echo "• View job: gcloud scheduler jobs describe ${JOB_NAME} --location=${REGION}"
echo "• Run now: gcloud scheduler jobs run ${JOB_NAME} --location=${REGION}"
echo "• Pause: gcloud scheduler jobs pause ${JOB_NAME} --location=${REGION}"
echo "• Resume: gcloud scheduler jobs resume ${JOB_NAME} --location=${REGION}"
echo ""
echo "📈 Monitor logs: https://console.cloud.google.com/run/detail/${REGION}/gfmd-a2a-swarm-agent/logs"