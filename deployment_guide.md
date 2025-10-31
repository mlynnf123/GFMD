# GFMD AI Swarm Agent - Complete Deployment Guide

## System Overview

The GFMD AI Swarm Agent is a production-ready automated email outreach system that:
- Discovers healthcare contacts from multiple sources
- Uses AI agents to research, qualify, and compose personalized emails
- Sends emails via Gmail integration
- Tracks results in Google Sheets
- Deployed on Google Cloud Run for scalability

## Current Production Status ✅

**Service URL:** https://gfmd-a2a-swarm-agent-531787444060.us-central1.run.app
**Project:** windy-tiger-471523-m5
**Region:** us-central1
**Service Account:** swarmagent@windy-tiger-471523-m5.iam.gserviceaccount.com

## Gmail Integration Status 📧

**Current Setup:** OAuth with refresh token stored as environment variable
**Method:** Gmail API via OAuth (not SMTP)
**Status:** ✅ Configured and ready to send emails

### Gmail Authentication Details
- **OAuth App:** "GFMD Email Client" 
- **Access Granted:** September 10, 12:01PM
- **Scopes:** Gmail send permission
- **Stored as:** Base64-encoded environment variable `GMAIL_OAUTH_CREDENTIALS`

## Architecture Components

### Core Files
```
main.py                          # Flask app and Cloud Run entry point
production_system_enhanced.py    # Main production system coordinator
production_rag_a2a_system.py     # AI agent system with memory
automatic_email_sender.py        # Email sending with safety controls
gmail_integration_hybrid.py      # Multi-method Gmail authentication
gmail_oauth_cloudrun.py         # OAuth for Cloud Run environment
```

### AI Agent System
```
research_agent.py               # Contact research
qualification_agent.py          # Lead scoring
email_composer_agent.py         # Email composition
coordinator_agent.py            # Agent orchestration
```

### Data Integration
```
google_sheets_integration.py    # Export to Google Sheets
enhanced_contact_discovery.py   # Multi-source contact discovery
email_verification_system.py    # Email validation
real_prospect_finder.py         # Definitive Healthcare data
```

## Deployment Commands

### Build and Deploy
```bash
gcloud run deploy gfmd-a2a-swarm-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --project windy-tiger-471523-m5 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --port 8080 \
  --max-instances 1 \
  --allow-unauthenticated \
  --async
```

### Environment Variables
```bash
# Core environment
GOOGLE_CLOUD_PROJECT=windy-tiger-471523-m5
LANGCHAIN_TRACING_V2=false

# Gmail OAuth (base64-encoded token)
GMAIL_OAUTH_CREDENTIALS=eyJ0b2tlbiI6ICJ5YTI5LmEwQVFRX0JEUmRQQlZYNUE5Z3JBZnY3UDNFbUx6LXV5emZDUmNSSXhlN2ppZGhkaFRvaldqcXhBckllLU42VW10S0dKVXBHTDl2bFVTS21nR2FvOXVSOFo5cVA0RXNraWFNS2w2SS1xM0Q2b3d0YjB2TmNJNG9kNXJoRS1vaG1TalFYSmFWYXc4YmtTdG9LWlVuem51LXhsWEFaZ2txZ05BVmt2QW1Idk0yZnFaVnVtVkVLQ2R6WXVHSGI1ZUx4Y2pXLUlpWW05ZmthQ2dZS0Fmb1NBUllTRlFIR1gyTWkzZHd4UXV3YWJaeG44Vi1BRHVyX0NnMDIwNyIsICJyZWZyZXNoX3Rva2VuIjogIjEvLzA2djV5b09kaGx0QnBDZ1lJQVJBQUdBWVNOd0YtTDlJcmpLZ0szSTI2ZlgwM3BBMWFMYXhrN3VCOG1ZcHVPdUcxcU8xRWxxTEN0MUdnbTFYeGM2aXo5TmxSaFBKQVA5ZUduSkUiLCAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwgImNsaWVudF9pZCI6ICI1MzE3ODc0NDQwNjAta241ZDZlb2FlbnZlb3AxNWRwdHFvZ3VnaWVuNDFnaXIuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCAiY2xpZW50X3NlY3JldCI6ICJHT0NTUFgtNnBMU1A2dFk4cUNtRHdNZ183SmxvUVo2c2VpciIsICJzY29wZXMiOiBbImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL2F1dGgvZ21haWwuc2VuZCJdLCAidW5pdmVyc2VfZG9tYWluIjogImdvb2dsZWFwaXMuY29tIiwgImFjY291bnQiOiAiIiwgImV4cGlyeSI6ICIyMDI1LTA5LTE3VDIzOjIxOjM3LjQ5OTM2N1oifQ==
```

## API Endpoints

### Health Check
```
GET https://gfmd-a2a-swarm-agent-531787444060.us-central1.run.app/
```

### Run Daily Automation
```
POST https://gfmd-a2a-swarm-agent-531787444060.us-central1.run.app/run-daily-automation
Content-Type: application/json
{
  "num_prospects": 50
}
```

### Trigger Automation (GET) - Used by Cloud Scheduler
```
GET https://gfmd-a2a-swarm-agent-531787444060.us-central1.run.app/trigger-automation
```

## Cloud Scheduler Configuration

### Daily Automation Schedule
- **Schedule:** Every day at 9:00 AM CST (0 9 * * *)
- **Job Name:** daily-gfmd-automation
- **Endpoint:** /trigger-automation (GET)
- **Location:** us-central1
- **Status:** ✅ ENABLED

### Scheduler Commands
```bash
# Check scheduler status
gcloud scheduler jobs describe daily-gfmd-automation --location=us-central1

# Test manual run
gcloud scheduler jobs run daily-gfmd-automation --location=us-central1

# View scheduler logs
gcloud logging read "resource.type=cloud_scheduler_job AND resource.labels.job_id=daily-gfmd-automation" --limit=10
```

## Troubleshooting Gmail Issues

### Issue: "Can't create app password"
**Solution:** Use the existing OAuth integration (already configured)

### Issue: Emails not sending (0 successful)
**Common Causes & Solutions:**

1. **OAuth Token Expired**
   ```bash
   # Regenerate token locally
   python gmail_oauth_cloudrun.py
   # Update Cloud Run with new token
   gcloud run services update gfmd-a2a-swarm-agent \
     --update-env-vars "GMAIL_OAUTH_CREDENTIALS=new-token"
   ```

2. **Gmail API Quotas**
   - Check Google Cloud Console → Gmail API → Quotas
   - Standard: 1B requests/day, 250 units/user/second

3. **Environment Variable Missing**
   ```bash
   # Verify variable is set
   gcloud run services describe gfmd-a2a-swarm-agent \
     --region us-central1 --format="value(spec.template.spec.containers[0].env[])"
   ```

## Testing the System

### Test Email Sending
```bash
# Run with 1 prospect to test
curl -X POST https://gfmd-a2a-swarm-agent-531787444060.us-central1.run.app/run-daily-automation \
  -H "Content-Type: application/json" \
  -d '{"num_prospects": 1}'
```

### Expected Response
```json
{
  "results": {
    "successful_emails": 1,
    "total_processed": 1,
    "success_rate": "1/1"
  },
  "success": true
}
```

## Quick Recovery Commands

### Redeploy Service
```bash
gcloud run deploy gfmd-a2a-swarm-agent --source . --region us-central1 --project windy-tiger-471523-m5
```

### Check Logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=gfmd-a2a-swarm-agent" --limit 20
```

### Update Gmail Token
```bash
python gmail_oauth_cloudrun.py  # Run locally to get new token
# Copy the encoded output and update:
gcloud run services update gfmd-a2a-swarm-agent --update-env-vars "GMAIL_OAUTH_CREDENTIALS=new-token"
```

---
**Status:** Production Ready ✅  
**Last Updated:** September 17, 2025  
**Gmail:** OAuth configured and working  
**Next Action:** System is ready for daily automation