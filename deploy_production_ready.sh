#!/bin/bash
# Complete Production Deployment with Full Google Services Integration
set -e

echo "🚀 DEPLOYING PRODUCTION-READY GFMD AGENT SWARM"
echo "=============================================="
echo "📊 Using: Vertex AI + Vector Search + WebSearch LLM + Cloud Run + Cloud Scheduler"
echo "🧠 Model: Gemini 2.5 Pro/Flash"
echo "📈 Monitoring: Vertex AI Monitoring"
echo "🔄 Automation: Daily at 9 AM CST via Cloud Scheduler"
echo ""

# Configuration
PROJECT_ID="windy-tiger-471523-m5"
SERVICE_NAME="gfmd-a2a-swarm-agent"
REGION="us-central1"
CLOUD_RUN_URL="https://gfmd-a2a-swarm-agent-531787444060.us-central1.run.app"

# Set project
gcloud config set project ${PROJECT_ID}

echo "1️⃣ Enabling all required Google Cloud services..."
gcloud services enable \
  cloudrun.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com \
  aiplatform.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com

echo ""
echo "2️⃣ Building and deploying to Cloud Run with optimized settings..."
gcloud builds submit --config=cloudbuild.yaml .

echo ""
echo "3️⃣ Verifying Cloud Scheduler is configured..."
SCHEDULER_STATUS=$(gcloud scheduler jobs describe daily-gfmd-automation --location=${REGION} --format="value(state)" 2>/dev/null || echo "NOT_FOUND")

if [ "$SCHEDULER_STATUS" != "ENABLED" ]; then
    echo "Setting up Cloud Scheduler..."
    gcloud scheduler jobs create http daily-gfmd-automation \
        --schedule="0 9 * * *" \
        --time-zone="America/Chicago" \
        --uri="${CLOUD_RUN_URL}/trigger-daily" \
        --http-method=POST \
        --headers="Content-Type=application/json" \
        --message-body='{"num_prospects": 50}' \
        --location=${REGION}
else
    echo "✅ Cloud Scheduler already configured and ENABLED"
fi

echo ""
echo "4️⃣ Testing health endpoint..."
sleep 10  # Wait for deployment
curl -s "${CLOUD_RUN_URL}/health" | jq '.'

echo ""
echo "5️⃣ Getting service details..."
gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="table(
    metadata.name,
    status.url,
    spec.template.spec.containers[0].image,
    status.conditions[0].status
)"

echo ""
echo "✅ PRODUCTION DEPLOYMENT COMPLETE!"
echo "================================================"
echo "🌐 Service URL: ${CLOUD_RUN_URL}"
echo "🕘 Daily Schedule: 9:00 AM CST (Cloud Scheduler)"
echo "📊 Dashboard: ${CLOUD_RUN_URL}/"
echo "💗 Health Check: ${CLOUD_RUN_URL}/health"
echo "🤖 Agent Status: ${CLOUD_RUN_URL}/agents/status"
echo "📈 Monitoring: ${CLOUD_RUN_URL}/monitoring"
echo ""
echo "🧪 Manual Test Commands:"
echo "# Test daily automation trigger:"
echo "gcloud scheduler jobs run daily-gfmd-automation --location=${REGION}"
echo ""
echo "# Process prospects manually:"
echo "curl -X POST ${CLOUD_RUN_URL}/process-prospects -H 'Content-Type: application/json' -d '{\"num_prospects\": 5}'"
echo ""
echo "# Check logs:"
echo "gcloud run services logs read ${SERVICE_NAME} --region=${REGION}"
echo ""
echo "📈 Next Run: Tomorrow at 9:00 AM CST (automatic)"
echo "🎯 System Status: PRODUCTION READY with full Google Services integration"