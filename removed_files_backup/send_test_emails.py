#!/usr/bin/env python3
"""
Send test emails to meranda@im-aiautomation.com
"""

import os
import asyncio
from datetime import datetime, timedelta
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

async def send_additional_test_emails():
    """Send 2 more test emails to complete the 3 email test"""
    
    automation = CompleteSequenceAutomation()
    
    print("🧪 SENDING ADDITIONAL TEST EMAILS")
    print("=" * 50)
    
    # Find Meranda's sequence
    test_sequence = automation.storage.db.email_sequences.find_one({
        'contact_email': 'meranda@im-aiautomation.com'
    })
    
    if not test_sequence:
        print("❌ Test sequence not found")
        return
    
    contact_id = test_sequence['contact_id']
    current_step = test_sequence.get('current_step', 0)
    
    print(f"📧 Found sequence for Meranda at step {current_step}")
    
    # Send second test email (force step 2)
    print(f"\n📧 Preparing test email 2...")
    automation.storage.db.email_sequences.update_one(
        {'contact_id': contact_id},
        {'$set': {
            'current_step': 1,
            'next_email_due': datetime.now().isoformat()
        }}
    )
    
    result2 = await automation.process_due_sequences(send_emails=True)
    meranda_result2 = None
    for detail in result2.get('details', []):
        if detail.get('contact_email') == 'meranda@im-aiautomation.com':
            meranda_result2 = detail
            break
    
    if meranda_result2 and meranda_result2['result'].get('success'):
        print(f"✅ Test email 2 sent successfully!")
    else:
        print(f"❌ Test email 2 failed: {meranda_result2}")
    
    # Send third test email (force step 3)
    print(f"\n📧 Preparing test email 3...")
    automation.storage.db.email_sequences.update_one(
        {'contact_id': contact_id},
        {'$set': {
            'current_step': 2,
            'next_email_due': datetime.now().isoformat()
        }}
    )
    
    result3 = await automation.process_due_sequences(send_emails=True)
    meranda_result3 = None
    for detail in result3.get('details', []):
        if detail.get('contact_email') == 'meranda@im-aiautomation.com':
            meranda_result3 = detail
            break
    
    if meranda_result3 and meranda_result3['result'].get('success'):
        print(f"✅ Test email 3 sent successfully!")
    else:
        print(f"❌ Test email 3 failed: {meranda_result3}")
    
    print(f"\n🎉 TEST EMAIL SEQUENCE COMPLETE!")
    print(f"📧 3 test emails have been sent to meranda@im-aiautomation.com")
    print(f"📋 Check your inbox to verify delivery and content")
    
    # Show final sequence status
    final_sequence = automation.storage.db.email_sequences.find_one({
        'contact_email': 'meranda@im-aiautomation.com'
    })
    
    if final_sequence:
        emails_sent = final_sequence.get('emails_sent', [])
        print(f"\n📊 Final sequence status:")
        print(f"   Step: {final_sequence.get('current_step')}")
        print(f"   Emails sent: {len(emails_sent)}")
        for email in emails_sent:
            print(f"   - Step {email.get('step')}: {email.get('subject', 'Unknown subject')}")

if __name__ == "__main__":
    asyncio.run(send_additional_test_emails())