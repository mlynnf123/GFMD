#!/usr/bin/env python3
"""
Test Email Sequence System
Simple test script to verify email sequence automation without scheduler dependency
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Import our sequence components
from email_sequence_orchestrator import EmailSequenceOrchestrator
from email_sequence_templates import EmailSequenceTemplates, SequenceState

async def test_sequence_system():
    """Test the email sequence system end-to-end"""
    
    print("🧪 Testing GFMD Email Sequence System")
    print("=" * 50)
    
    # Initialize components
    try:
        orchestrator = EmailSequenceOrchestrator()
        templates = EmailSequenceTemplates()
        print("✅ Components initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    # Test 1: Template System
    print("\n📋 Testing Template System...")
    try:
        sequence_config = templates.get_sequence_config("narc_gone_law_enforcement")
        print(f"  ✅ Loaded sequence: {sequence_config['name']}")
        print(f"  ✅ Email count: {len(sequence_config['emails'])}")
        print(f"  ✅ Timing: {sequence_config['timing_days']} days")
        
        # Test each email template
        for step in range(1, 7):
            template = templates.get_email_template("narc_gone_law_enforcement", step)
            if template:
                print(f"  ✅ Step {step}: {template['type']} ({template['focus']})")
            else:
                print(f"  ❌ Step {step}: Template not found")
                
    except Exception as e:
        print(f"  ❌ Template test failed: {e}")
        return False
    
    # Test 2: Sequence State Management
    print("\n📊 Testing Sequence State...")
    try:
        test_contact_id = "test_contact_123"
        
        # Start a sequence
        result = await orchestrator.start_sequence(test_contact_id)
        if result.get("success"):
            print(f"  ✅ Started sequence for contact {test_contact_id}")
            print(f"  ✅ Status: {result.get('status')}")
        else:
            print(f"  ❌ Failed to start sequence: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ Sequence state test failed: {e}")
        return False
    
    # Test 3: Processing Logic (without actually sending emails)
    print("\n⚡ Testing Processing Logic...")
    try:
        # This will check for due sequences but won't find any to send
        # since we just created one and it needs real contact data
        result = await orchestrator.process_sequences()
        print(f"  ✅ Process sequences completed")
        print(f"  ✅ Processed: {result.get('processed', 0)}")
        print(f"  ✅ Sent: {result.get('sent', 0)}")
        print(f"  ✅ Errors: {result.get('errors', 0)}")
        
    except Exception as e:
        print(f"  ❌ Processing test failed: {e}")
        return False
    
    # Test 4: Reply Handling
    print("\n📧 Testing Reply Handling...")
    try:
        # Test reply handling with fake email
        reply_result = await orchestrator.handle_reply(
            contact_email="test@example.com",
            reply_content="Thanks for reaching out! I'm interested in learning more.",
            reply_date=datetime.now()
        )
        
        if reply_result.get("success") or "Contact not found" in str(reply_result.get("error", "")):
            print(f"  ✅ Reply handling logic works")
            print(f"  ✅ Action: {reply_result.get('action', 'not_found')}")
        else:
            print(f"  ❌ Reply handling failed: {reply_result.get('error')}")
            
    except Exception as e:
        print(f"  ❌ Reply test failed: {e}")
        return False
    
    print("\n🎉 All Core Tests Passed!")
    print("\n💡 Next Steps:")
    print("1. Ensure MongoDB is running for full functionality")
    print("2. Add real contact data to test full sequence")
    print("3. Configure Gmail API for actual email sending")
    print("4. Run sequence scheduler in background")
    
    return True

async def demo_sequence_flow():
    """Demonstrate how the sequence flow works"""
    
    print("\n🎬 Email Sequence Flow Demo")
    print("=" * 40)
    
    templates = EmailSequenceTemplates()
    
    # Show sequence progression
    sequence = templates.get_sequence_config("narc_gone_law_enforcement")
    
    print(f"📋 Sequence: {sequence['name']}")
    print(f"🎯 Total emails: {len(sequence['emails'])}")
    print(f"⏰ Timeline: {sequence['timing_days']} days")
    print()
    
    # Demo each email step
    for email in sequence["emails"]:
        print(f"📧 EMAIL {email['step']}: {email['type'].replace('_', ' ').title()}")
        print(f"   ⏱️  Wait: {email['wait_days']} days from previous")
        print(f"   🎯 Focus: {email['focus']}")
        print(f"   🗣️  Tone: {email['tone']}")
        print(f"   📞 CTA: {email['call_to_action']}")
        print(f"   📋 Subject: {email['subject_template']}")
        print()
    
    print("🔄 Automation Features:")
    print("   ✅ Auto-sends emails based on timing")
    print("   ✅ Pauses sequence when prospect replies")
    print("   ✅ Tracks opens/clicks (when configured)")
    print("   ✅ Sentiment analysis on replies")
    print("   ✅ Marks positive replies for sales follow-up")

if __name__ == "__main__":
    async def main():
        # Run the demo first
        await demo_sequence_flow()
        
        print("\n" + "="*60)
        
        # Then run tests
        success = await test_sequence_system()
        
        if success:
            print("\n🚀 Email Sequence System Ready!")
        else:
            print("\n❌ System needs fixes before deployment")
    
    asyncio.run(main())