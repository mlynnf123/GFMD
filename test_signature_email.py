#!/usr/bin/env python3
"""
Test email to verify signature with new logo
"""

import os
import asyncio
from gmail_integration import GmailIntegration
from groq_email_composer_agent import GroqEmailComposerAgent

# Load environment variables
def load_env():
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    value = value.strip('"')
                    os.environ[key] = value
    except FileNotFoundError:
        pass

load_env()

async def send_test_email():
    """Send test email to verify signature"""
    
    # Set environment
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    
    print("🧪 Testing email signature with new logo...")
    
    # Initialize components
    gmail = GmailIntegration()
    composer = GroqEmailComposerAgent()
    
    # Test prospect data
    test_data = {
        "prospect_data": {
            "contact_name": "Meranda Test",
            "company_name": "Test Organization",
            "location": "Test City, TX",
            "title": "Test Manager",
            "email": "meranda@im-aiautomation.com"
        },
        "sequence_context": {
            "step": 1,
            "type": "initial_contact",
            "focus": "drug_disposal_costs",
            "tone": "professional_direct",
            "call_to_action": "brief_call",
            "is_follow_up": False,
            "previous_emails_sent": 0
        }
    }
    
    # Generate email
    print("📧 Generating test email...")
    email_result = await composer.execute(test_data)
    
    if not email_result.get("success"):
        print(f"❌ Email generation failed: {email_result.get('error')}")
        return
    
    print(f"✅ Email generated successfully")
    print(f"📋 Subject: {email_result.get('subject')}")
    
    # Send email
    print("📤 Sending test email...")
    send_result = gmail.send_email(
        to_email="meranda@im-aiautomation.com",
        subject="[TEST] " + email_result.get("subject"),
        body=email_result.get("body"),
        html_body=email_result.get("html_body")
    )
    
    if send_result.get("success"):
        print("✅ Test email sent successfully!")
        print("📬 Check your inbox to verify the signature and logo display")
    else:
        print(f"❌ Email sending failed: {send_result.get('error')}")

if __name__ == "__main__":
    asyncio.run(send_test_email())