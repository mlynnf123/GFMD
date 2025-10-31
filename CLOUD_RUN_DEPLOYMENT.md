# Cloud Run Deployment Guide

## 🚀 Deploying GFMD A2A Swarm Agent to Google Cloud Run

This guide walks you through deploying your multi-agent AI system to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account**: Ensure you have access to your Google Cloud project
2. **gcloud CLI**: Install the Google Cloud SDK
   ```bash
   # For macOS:
   brew install google-cloud-sdk
   
   # Or download from:
   https://cloud.google.com/sdk/docs/install
   ```

3. **Authentication**: Login to Google Cloud
   ```bash
   gcloud auth login
   ```

## Quick Deploy

1. **Make the deployment script executable**:
   ```bash
   chmod +x deploy_to_cloud_run.sh
   ```

2. **Run the deployment**:
   ```bash
   ./deploy_to_cloud_run.sh
   ```

## Manual Deployment Steps

If you prefer to deploy manually:

### 1. Set Project and Enable APIs

```bash
# Set your project
gcloud config set project windy-tiger-471523-m5

# Enable required APIs
gcloud services enable cloudrun.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 2. Create Secrets

```bash
# Create service account key secret
gcloud secrets create service-account-key \
    --data-file="/Users/merandafreiner/Downloads/windy-tiger-471523-m5-12203afb2f6b.json"

# Create configuration secrets
echo "windy-tiger-471523-m5" | gcloud secrets create vertex-ai-project-id --data-file=-
echo "us-central1" | gcloud secrets create vertex-ai-location --data-file=-
```

### 3. Build and Deploy

```bash
# Submit build
gcloud builds submit --config=cloudbuild.yaml .

# Or deploy directly
gcloud run deploy gfmd-a2a-swarm-agent \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 900 \
    --max-instances 10 \
    --min-instances 1
```

## API Endpoints

Once deployed, your service will have these endpoints:

### Core Endpoints

- `GET /` - Service information and available endpoints
- `GET /health` - Health check
- `GET /api/v1/performance` - Performance metrics

### Agent Operations

- `POST /api/v1/prospect` - Process a single prospect
- `POST /api/v1/prospects/batch` - Batch process multiple prospects
- `POST /api/v1/emails/monitor` - Monitor emails for prospects
- `POST /api/v1/research/company` - Research company information

### Scheduler Control

- `GET /api/v1/scheduler/status` - Get scheduler status
- `POST /api/v1/scheduler/start` - Start daily automation
- `POST /api/v1/scheduler/stop` - Stop daily automation

### Workflow Monitoring

- `GET /api/v1/workflow/{workflow_id}` - Get specific workflow status

## Testing Your Deployment

### 1. Health Check
```bash
curl https://gfmd-a2a-swarm-agent-xxx-uc.a.run.app/health
```

### 2. Process a Prospect
```bash
curl -X POST https://gfmd-a2a-swarm-agent-xxx-uc.a.run.app/api/v1/prospect \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Test Hospital",
    "contact_name": "Dr. Smith",
    "email": "dr.smith@test.org",
    "bed_count": 300,
    "lab_type": "full_service"
  }'
```

### 3. Check Performance
```bash
curl https://gfmd-a2a-swarm-agent-xxx-uc.a.run.app/api/v1/performance
```

## Monitoring

### View Logs
```bash
gcloud run services logs read gfmd-a2a-swarm-agent --region=us-central1
```

### View Metrics
Visit: https://console.cloud.google.com/run/detail/us-central1/gfmd-a2a-swarm-agent/metrics

### Set Up Alerts
1. Go to Cloud Monitoring
2. Create alerts for:
   - High error rate
   - High latency
   - Service downtime

## Scaling Configuration

The service is configured with:
- **Min instances**: 1 (always warm)
- **Max instances**: 10 (auto-scales based on load)
- **Memory**: 2GB per instance
- **CPU**: 2 vCPUs per instance
- **Timeout**: 15 minutes (for long workflows)

## Cost Optimization

1. **Adjust minimum instances**: Set to 0 to save costs when not in use
   ```bash
   gcloud run services update gfmd-a2a-swarm-agent \
       --min-instances 0 \
       --region us-central1
   ```

2. **Schedule scaling**: Use Cloud Scheduler to scale up during business hours

3. **Monitor usage**: Check billing dashboard regularly

## Security Best Practices

1. **Authentication**: Currently allows unauthenticated access. For production:
   ```bash
   gcloud run services update gfmd-a2a-swarm-agent \
       --no-allow-unauthenticated \
       --region us-central1
   ```

2. **API Keys**: Implement API key authentication for production

3. **Secrets**: All sensitive data stored in Secret Manager

## Troubleshooting

### Service Won't Start
- Check logs: `gcloud run services logs read gfmd-a2a-swarm-agent --region=us-central1`
- Verify secrets are created correctly
- Ensure service account has necessary permissions

### High Latency
- Check if Vertex AI quota is sufficient
- Monitor instance CPU/memory usage
- Consider increasing instance resources

### Errors in Logs
- Most common: Missing credentials or incorrect project ID
- Check environment variables are set correctly
- Verify all required APIs are enabled

## Daily Automation

To enable daily automation at 9am CST:

1. **Start scheduler via API**:
   ```bash
   curl -X POST https://gfmd-a2a-swarm-agent-xxx-uc.a.run.app/api/v1/scheduler/start
   ```

2. **Or use Cloud Scheduler** (recommended for production):
   ```bash
   gcloud scheduler jobs create http daily-prospect-run \
       --location us-central1 \
       --schedule "0 9 * * *" \
       --time-zone "America/Chicago" \
       --uri "https://gfmd-a2a-swarm-agent-xxx-uc.a.run.app/api/v1/prospects/batch" \
       --http-method POST \
       --headers "Content-Type=application/json" \
       --message-body '{"prospects": [], "batch_size": 10}'
   ```

## Support

For issues or questions:
1. Check service logs
2. Review error messages in performance metrics
3. Verify all secrets and configurations are correct

Your A2A multi-agent system is now cloud-ready! 🚀