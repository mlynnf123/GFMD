#\!/bin/bash
# Setup Cloud Scheduler for daily GFMD automation at 9 AM CST

PROJECT_ID="windy-tiger-471523-m5"
CLOUD_RUN_URL="https://gfmd-a2a-swarm-agent-531787444060.us-central1.run.app"
JOB_NAME="daily-gfmd-automation"

echo "🕘 Setting up Cloud Scheduler for daily automation at 9 AM CST"
echo "============================================================"

# Set project
gcloud config set project ${PROJECT_ID}

# Enable Cloud Scheduler API
gcloud services enable cloudscheduler.googleapis.com

# Delete existing job if it exists
gcloud scheduler jobs delete ${JOB_NAME} --location=us-central1 --quiet 2>/dev/null || true

# Create the daily automation job
gcloud scheduler jobs create http ${JOB_NAME} \
    --schedule="0 9 * * *" \
    --time-zone="America/Chicago" \
    --uri="${CLOUD_RUN_URL}/trigger-daily" \
    --http-method=POST \
    --headers="Content-Type=application/json" \
    --message-body='{"num_prospects": 60}' \
    --location=us-central1

echo "✅ Cloud Scheduler job created successfully\!"
echo "📅 Schedule: Daily at 9:00 AM CST"
echo "🎯 Target: ${CLOUD_RUN_URL}/trigger-daily"
echo ""
echo "📋 To test manually:"
echo "gcloud scheduler jobs run ${JOB_NAME} --location=us-central1"
echo ""
echo "📊 To check job status:"
echo "gcloud scheduler jobs describe ${JOB_NAME} --location=us-central1"
