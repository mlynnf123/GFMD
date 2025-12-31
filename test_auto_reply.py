#!/usr/bin/env python3
"""
Test script for AI Auto-Reply System
Demonstrates automated reply generation
"""

import asyncio
from ai_auto_reply_system import AIAutoReplySystem, GroqReplyAgent

async def test_ai_reply_generation():
    """Test the AI reply generation with sample replies"""
    
    print("🤖 Testing AI Auto-Reply Generation")
    print("=" * 50)
    
    reply_agent = GroqReplyAgent()
    
    # Test scenarios
    test_cases = [
        {
            "name": "Positive Interest",
            "reply_content": "Hi Meranda, I'm interested in learning more about your drug disposal system. Can you tell me more about the costs?",
            "sender_name": "John Smith",
            "original_subject": "Drug disposal costs at Austin PD"
        },
        {
            "name": "Scheduling Request", 
            "reply_content": "Thanks for reaching out. I'd like to schedule a call to discuss this further. What times work for you?",
            "sender_name": "Sarah Johnson",
            "original_subject": "Secure drug disposal for Harris County"
        },
        {
            "name": "Question About Process",
            "reply_content": "How does the destruction process work exactly? Is it DEA compliant?",
            "sender_name": "Mike Rodriguez",
            "original_subject": "Drug disposal discussion"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📧 Test Case: {test_case['name']}")
        print(f"Incoming: {test_case['reply_content'][:60]}...")
        
        # Prepare test data
        task_data = {
            "original_email": {
                "sender_name": test_case['sender_name'],
                "subject": test_case['original_subject']
            },
            "reply_content": test_case['reply_content'],
            "prospect_data": {
                "email": f"{test_case['sender_name'].lower().replace(' ', '.')}@example.com",
                "company_name": "Sample Department"
            }
        }
        
        try:
            # Generate AI reply
            result = await reply_agent.execute(task_data)
            
            if result.get('success'):
                print(f"✅ AI Reply Generated")
                print(f"Subject: {result.get('subject')}")
                print(f"Sentiment: {result.get('sentiment_analysis')}")
                print(f"Suggested Action: {result.get('suggested_next_action')}")
                print("\nReply Body:")
                print("-" * 40)
                print(result.get('reply_body', 'No body generated'))
                print("-" * 40)
            else:
                print("❌ Reply generation failed")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

async def test_reply_monitoring():
    """Test the full auto-reply monitoring system"""
    print("\n🔍 Testing Reply Monitoring System")
    print("=" * 50)
    
    auto_reply_system = AIAutoReplySystem()
    
    # Run a single check for actual replies
    results = await auto_reply_system.run_single_check()
    
    if results:
        print(f"\n📊 Successfully processed {len(results)} actual replies")
        for result in results:
            print(f"   - {result.get('subject')}")
    else:
        print("\n📭 No new replies found to process")

async def main():
    """Main test function"""
    # Test AI reply generation
    await test_ai_reply_generation()
    
    # Test actual reply monitoring  
    await test_reply_monitoring()

if __name__ == "__main__":
    asyncio.run(main())