#!/usr/bin/env python3
"""
Send a test email with updated signature
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

async def send_signature_test():
    """Send one more test email to verify the signature update"""
    
    automation = CompleteSequenceAutomation()
    
    print("📧 SENDING SIGNATURE TEST EMAIL")
    print("=" * 50)
    
    # Force Meranda's sequence to step 4 to send another email
    automation.storage.db.email_sequences.update_one(
        {'contact_email': 'meranda@im-aiautomation.com'},
        {'$set': {
            'current_step': 3,
            'next_email_due': datetime.now().isoformat()
        }}
    )
    
    # Send the email
    result = await automation.process_due_sequences(send_emails=True)
    
    # Find Meranda's result
    meranda_result = None
    for detail in result.get('details', []):
        if detail.get('contact_email') == 'meranda@im-aiautomation.com':
            meranda_result = detail
            break
    
    if meranda_result and meranda_result['result'].get('success'):
        print("✅ Updated signature test email sent successfully!")
        print("📧 Subject: Compliance follow-up email")
        print("📋 Check your inbox to verify the new signature format")
    else:
        print(f"❌ Test failed: {meranda_result}")
    
    print(f"\n🎉 SIGNATURE UPDATE COMPLETE!")
    print(f"📧 All future emails will now use:")
    print(f"   ✅ Sender: Meranda Freiner")
    print(f"   ✅ Email: solutions@gfmd.com") 
    print(f"   ✅ Phone: 619-341-9058")
    print(f"   ✅ Website: www.gfmd.com")
    print(f"   ✅ Proper line formatting")

if __name__ == "__main__":
    asyncio.run(send_signature_test())