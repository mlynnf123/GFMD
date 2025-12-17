#!/usr/bin/env python3
"""
Test HTML Email with GFMD Signature
"""

import os
import asyncio
from datetime import datetime
from complete_sequence_automation import CompleteSequenceAutomation

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

async def test_html_email():
    automation = CompleteSequenceAutomation()
    
    # Force Meranda's sequence to step 5
    automation.storage.db.email_sequences.update_one(
        {'contact_email': 'meranda@im-aiautomation.com'},
        {'$set': {
            'current_step': 4,
            'next_email_due': datetime.now().isoformat()
        }}
    )
    
    # Send email
    result = await automation.process_due_sequences(send_emails=True)
    
    print("📧 HTML signature test email sent to meranda@im-aiautomation.com!")
    print("🎨 Features: Professional HTML formatting, GFMD branding, clickable links")
    
asyncio.run(test_html_email())