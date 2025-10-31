# Gmail Integration Setup for GFMD Agents

## 🚀 **Quick Setup (5 minutes)**

### Step 1: Install Gmail API Dependencies
```bash
.venv/bin/python -m pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 2: Enable Gmail API in Google Cloud Console

1. **Go to Google Cloud Console**: https://console.cloud.google.com
2. **Select your project**: `gen-lang-client-0673146524` 
3. **Navigate to APIs & Services > Library**
4. **Search for "Gmail API"**
5. **Click "Enable"**

### Step 3: Create OAuth 2.0 Credentials

1. **Go to APIs & Services > Credentials**
2. **Click "+ CREATE CREDENTIALS" > OAuth client ID**
3. **Application type**: Desktop application
4. **Name**: "GFMD Swarm Agents Gmail"
5. **Click "CREATE"**

### Step 4: Download Credentials

1. **Click the download button** next to your new credential
2. **Save the file as**: `gmail_credentials.json`
3. **Move it to**: `/Users/merandafreiner/gfmd_swarm_agent/gmail_credentials.json`

### Step 5: Test the Integration

```bash
cd /Users/merandafreiner/gfmd_swarm_agent
.venv/bin/python gmail_integration.py
```

This will:
- Open your browser for Gmail authorization
- Create `gmail_token.json` for future use
- Confirm the integration is working

## 📧 **Usage in Your Agents**

### Basic Email Sending:
```python
from gmail_integration import GmailIntegration

# Initialize Gmail
gmail = GmailIntegration()

# Send email
result = gmail.send_email(
    to_email="prospect@hospital.com",
    subject="GFMD Centrifuge Solutions for Your Lab",
    body="Your personalized email content here..."
)

if result['success']:
    print(f"✅ Email sent! Message ID: {result['message_id']}")
else:
    print(f"❌ Failed: {result['error']}")
```

### GFMD-Specific Outreach:
```python
# For your agent-generated content
prospect = {
    'email': 'lab.director@hospital.com',
    'contact_name': 'Dr. Sarah Johnson',
    'organization_name': 'Metro General Hospital'
}

result = gmail.send_gfmd_outreach_email(
    prospect=prospect,
    email_content=agent_generated_email,
    subject="Laboratory Efficiency Solutions - GFMD",
    sender_name="GFMD Sales Team"
)
```

## 🔧 **Integrating with Your Existing Agents**

### Update vertex_ai_outreach_agent.py:

Replace the simulation code with real Gmail sending:

```python
from gmail_integration import GmailIntegration

class MultiChannelOutreachAgent:
    def __init__(self, project_id: str):
        self.gmail = GmailIntegration()
        # ... rest of your init code
    
    async def execute_email_outreach(self, prospect_data, email_content):
        # Replace simulation with real sending
        result = self.gmail.send_gfmd_outreach_email(
            prospect=prospect_data,
            email_content=email_content,
            subject=f"Laboratory Solutions for {prospect_data['organization_name']}",
            sender_name="GFMD Sales Team"
        )
        
        return {
            'channel': 'email',
            'status': 'sent' if result['success'] else 'failed',
            'message_id': result.get('message_id'),
            'error': result.get('error')
        }
```

## 🔐 **Security & Best Practices**

### OAuth Token Management:
- `gmail_credentials.json` - Keep secure, contains OAuth client credentials
- `gmail_token.json` - Auto-generated, contains access/refresh tokens
- Both files should be added to `.gitignore`

### Rate Limiting:
Gmail API allows:
- **250 quota units per user per second**
- **1 quota unit per email sent**
- **Roughly 250 emails per second maximum**

### Email Deliverability:
- Use a professional "From" name
- Include proper email signatures
- Monitor bounce rates
- Follow CAN-SPAM compliance

## 📊 **Tracking & Monitoring**

### Email Status Tracking:
```python
# Check sent emails
sent_emails = gmail.get_sent_emails(query="from:me", max_results=50)

for email in sent_emails:
    print(f"To: {email.get('to')}")
    print(f"Subject: {email.get('subject')}")  
    print(f"Date: {email.get('date')}")
```

### Integration with Agent Results:
Your agent results will now include real email delivery data:
```python
{
    'email_results': {
        'sent': True,
        'message_id': 'gmail-message-id-123',
        'recipient': 'prospect@hospital.com',
        'subject': 'GFMD Laboratory Solutions',
        'sent_at': '2025-01-09T10:30:00Z'
    }
}
```

## ⚡ **Quick Test Command**

Once set up, test your integration:

```bash
# Test Gmail authentication
.venv/bin/python -c "
from gmail_integration import GmailIntegration
gmail = GmailIntegration()
print('✅ Gmail integration working!')
"
```

## 🎯 **Next Steps After Setup**

1. **Test with a few manual emails** first
2. **Monitor delivery and responses**  
3. **Gradually enable automation** in your agents
4. **Add response tracking** and follow-up sequences
5. **Scale up** to full automated outreach

Your GFMD agents will now send **real, personalized emails** to hospital prospects automatically! 🚀