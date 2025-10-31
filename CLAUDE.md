# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GFMD AI Swarm Agent System - An enterprise-grade automated B2B sales outreach platform for medical device sales using Google Cloud and Vertex AI.

## Development Commands

### Deployment
```bash
# Deploy to Google Cloud Run
./deploy_to_cloud_run.sh

# Production deployment with all checks
./deploy_production_ready.sh

# Configure daily automation
./setup_daily_automation.sh

# Manual deployment
./manual_deploy.sh
```

### Testing
```bash
# Test Google Search integration
python test_google_search_integration.py

# Test AI models
python test_perplexity_models.py

# Test Firestore database
python test_firestore.py

# Verify production readiness
python production_verification_test.py

# Run production system locally
python production_system_enhanced.py
```

### Local Development
```bash
# Install all dependencies
pip install -r requirements.txt
pip install -r requirements_google_sheets.txt
pip install -r requirements_api.txt

# Setup authentication for Firestore
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/google_sheets_credentials.json"

# Migrate data to Firestore (first time only)
python simple_migrate.py

# Run Flask API locally
python main.py

# Test email sender
python automatic_email_sender.py
```

## Architecture

### Multi-Agent System
The system uses a coordinated swarm of AI agents:

1. **Coordinator Agent** (`coordinator_agent.py`) - Orchestrates the entire workflow
2. **Research Agent** (`research_agent.py`) - Performs web research on healthcare facilities
3. **Qualification Agent** (`qualification_agent.py`) - Scores and prioritizes leads
4. **Email Composer Agent** (`email_composer_agent.py`) - Creates personalized emails

### Core Components
- **Flask API** (`main.py`) - RESTful endpoints for Cloud Run deployment
- **Production System** (`production_system_enhanced.py`) - Main orchestration logic
- **Daily Scheduler** (`daily_scheduler.py`) - Automated campaign management
- **Email Sender** (`automatic_email_sender.py`) - Gmail API integration
- **Monitoring System** (`agent_monitoring_system.py`) - Performance tracking

### Data Flow
1. Healthcare contacts loaded from Definitive Healthcare CSV (`definitive_healthcare_data.csv`) into Firestore database
2. Enhanced via Google Custom Search API and stored in Firestore
3. AI agents analyze and personalize content using Firestore data
4. Emails sent via Gmail API with tracking in Firestore
5. Results logged to both Firestore and Google Sheets

### Database (Firestore)
- **Contact Management**: Persistent storage for 10K+ healthcare contacts
- **Research Cache**: AI research findings stored for reuse
- **Email Tracking**: Deduplication and campaign history
- **Daily Limits**: Automated 50-email daily limits with 30-day intervals

## Key Configuration

### Environment Variables
```bash
GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
VERTEX_AI_PROJECT_ID="your-project-id"
VERTEX_AI_LOCATION="us-central1"
```

### Required Google Cloud APIs
- Vertex AI API
- Cloud Run API
- Gmail API
- Google Sheets API
- Custom Search API
- Cloud Scheduler API

## Production Requirements

- **Vertex AI**: Use Gemini 2.5 or higher models exclusively
- **Data Integrity**: NEVER generate fake emails - all contacts must be from verified healthcare sources
- **Deployment**: Always use Google Cloud services (Cloud Run, Vertex AI, etc.) - no local files for production
- **Testing**: Test comprehensively before deployment including API integrations and AI responses

## Agent Communication Protocol

Agents communicate using the A2A (Agent-to-Agent) protocol with structured messages:
- Research findings passed from Research Agent to Qualification Agent
- Qualification scores passed to Email Composer Agent
- All communications logged for monitoring

## Common Tasks

### Adding New Healthcare Contacts
1. Update the Definitive Healthcare CSV file
2. Ensure email validation is in place
3. Deploy updated system

### Modifying Email Templates
1. Edit prompts in `email_composer_agent.py`
2. Test with `test_perplexity_models.py`
3. Deploy after verification

### Monitoring Performance
1. Check Google Cloud Monitoring dashboards
2. Review Google Sheets logs
3. Analyze agent performance metrics in `agent_monitoring_system.py`