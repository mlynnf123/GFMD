# Google Sheets Integration Setup Guide

This guide will help you set up Google Sheets integration to export agent outputs, prospects data, and sent emails instead of using simulation mode.

## Overview

The Google Sheets integration exports data to three worksheets:
1. **Agent Output**: All agent execution results with tracking information
2. **Prospects**: All discovered prospects with qualification scores and details
3. **Sent Emails**: All email communications with tracking and performance data

## Prerequisites

1. Python environment with required packages
2. Google Cloud Project with Sheets API enabled
3. Service Account credentials

## Step 1: Install Required Packages

```bash
pip install -r requirements_google_sheets.txt
```

## Step 2: Set up Google Cloud Project

### Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Note your Project ID

### Enable APIs
1. Navigate to "APIs & Services" > "Library"
2. Search for and enable:
   - **Google Sheets API**
   - **Google Drive API** (required for sharing functionality)

### Create Service Account
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - Name: `gfmd-swarm-agent`
   - Description: `Service account for GFMD Swarm Agent Google Sheets integration`
4. Click "Create and Continue"
5. Skip roles assignment (click "Continue")
6. Click "Done"

### Generate Credentials Key
1. Click on the created service account
2. Go to "Keys" tab
3. Click "Add Key" > "Create New Key"
4. Select "JSON" format
5. Download the credentials file
6. Save it securely (you'll reference this path later)

## Step 3: Configuration Options

Choose one of the following configuration methods:

### Option A: Environment Variables (Recommended)

Set these environment variables in your shell or `.env` file:

```bash
# Required: Path to your service account credentials JSON file
export GOOGLE_SHEETS_CREDENTIALS_FILE="/path/to/your/credentials.json"

# Optional: Customize spreadsheet name
export GOOGLE_SHEETS_SPREADSHEET_NAME="GFMD Swarm Agent Data"

# Optional: Comma-separated list of emails to share the spreadsheet with
export GOOGLE_SHEETS_SHARE_EMAILS="user1@company.com,user2@company.com"
```

### Option B: Service Account Info as Environment Variable

Instead of a file, you can set the entire credentials as an environment variable:

```bash
export GOOGLE_SHEETS_SERVICE_ACCOUNT_INFO='{"type": "service_account", "project_id": "your-project", ...}'
```

### Option C: Default Location

Place your credentials file at the default location:
- **Linux/Mac**: `~/.config/gspread/service_account.json`
- **Windows**: `%APPDATA%\\gspread\\service_account.json`

## Step 4: Test Configuration

Run the configuration test:

```bash
python google_sheets_config.py
```

You should see output like:
```
✅ Google Sheets integration is enabled
📊 Spreadsheet name: GFMD Swarm Agent Data
📁 Credentials file: /path/to/credentials.json
📧 Share with emails: user@company.com
```

## Step 5: Run the Agent with Google Sheets Export

The agent will automatically detect the Google Sheets configuration and use it instead of simulation mode:

```python
from vertex_ai_swarm_orchestrator import GFMDSwarmOrchestrator

# Initialize orchestrator (will auto-detect Google Sheets config)
orchestrator = GFMDSwarmOrchestrator()

# Process a prospect - will export to Google Sheets
result = await orchestrator.process_new_prospect(prospect_data)
```

## Expected Output

When Google Sheets is properly configured, you'll see:

```
✅ Google Sheets integration initialized successfully
✅ Orchestrator Google Sheets export enabled: https://docs.google.com/spreadsheets/d/...
✅ Google Sheets export enabled: https://docs.google.com/spreadsheets/d/...
```

## Worksheets Created

### 1. Agent Output Sheet
Columns include:
- Timestamp, Agent Type, Touchpoint ID, Channel, Recipient Name
- Organization, Contact Info, Content, Status, Tracking ID
- Execution Time, Response Data, Qualification Score, Performance Metrics

### 2. Prospects Sheet
Columns include:
- Timestamp, Name, Email, Phone, Organization, Title, Location
- Industry, Website, LinkedIn, Qualification Score, Lead Source
- Company Size, Technology Stack, Pain Points, Status

### 3. Sent Emails Sheet
Columns include:
- Timestamp, Message ID, From, To, Subject, Content
- Campaign, Status, Tracking Data, Performance Metrics
- Thread ID, Labels, Reply Information

## Troubleshooting

### Common Issues

**1. Authentication Error**
```
❌ Failed to initialize Google Sheets: No valid credentials found
```
**Solution**: Verify your credentials file path and format.

**2. Permission Denied**
```
❌ Failed to export: Insufficient permissions
```
**Solution**: Ensure the Sheets API is enabled in your Google Cloud Project.

**3. Spreadsheet Not Found**
```
❌ SpreadsheetNotFound: The requested spreadsheet was not found
```
**Solution**: The service account needs access to the spreadsheet. Either:
- Let the agent create a new spreadsheet (recommended)
- Manually share an existing spreadsheet with the service account email

**4. Import Error**
```
ModuleNotFoundError: No module named 'gspread'
```
**Solution**: Install the required packages:
```bash
pip install -r requirements_google_sheets.txt
```

### Getting Help

1. **Check Service Account Email**: Find it in your credentials JSON file under `client_email`
2. **Verify API Enablement**: Ensure both Google Sheets API and Google Drive API are enabled
3. **Test Connectivity**: Run `python google_sheets_config.py` to verify configuration
4. **Check Logs**: The agent provides detailed logging for troubleshooting

## Security Notes

- Keep your credentials file secure and never commit it to version control
- Use environment variables in production environments
- Regularly rotate service account keys
- Follow the principle of least privilege when sharing spreadsheets

## Example Integration

```python
import asyncio
from vertex_ai_swarm_orchestrator import GFMDSwarmOrchestrator

async def main():
    # Initialize with Google Sheets integration
    orchestrator = GFMDSwarmOrchestrator()
    
    # Sample prospect data
    prospect = {
        "contact_name": "Dr. Sarah Johnson",
        "email": "sarah.johnson@cityhospital.org",
        "phone": "+1-555-0123",
        "organization_name": "City General Hospital",
        "title": "Laboratory Director",
        "bed_count": 350,
        "lab_type": "full_service",
        "location": "New York, NY"
    }
    
    # Process prospect - automatically exports to Google Sheets
    result = await orchestrator.process_new_prospect(prospect)
    print(f"Processed prospect: {result['success']}")

if __name__ == "__main__":
    asyncio.run(main())
```

The integration will automatically export all prospect data, agent outputs, and email communications to your configured Google Spreadsheet, replacing the previous simulation mode behavior.