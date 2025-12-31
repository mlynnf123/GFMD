#!/usr/bin/env python3
"""
AI-Powered Automated Reply System for GFMD
Detects email replies and generates intelligent, contextual responses using Groq AI
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from gmail_integration import GmailIntegration
from mongodb_storage import MongoDBStorage
from groq_email_composer_agent import GroqEmailComposerAgent
from groq_base_agent import GroqBaseAgent, AgentRole

# Load environment
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

logger = logging.getLogger(__name__)

class GroqReplyAgent(GroqBaseAgent):
    """Specialized agent for generating contextual email replies"""
    
    def __init__(self, agent_id: str = "reply_agent"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.EMAIL_COMPOSER,
            temperature=0.8  # Higher temperature for natural conversation
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Professional Email Reply Agent for GFMD (Global Focus Marketing & Distribution), responding to replies about Narc Gone drug destruction products.

**Your Role**: Generate professional, helpful email replies that continue conversations about GFMD's drug destruction solutions for law enforcement agencies.

**CRITICAL REPLY RULES**:

1. **Greeting**: Use "Hi [FirstName]," (extract from original email if possible)
2. **Tone**: Professional, helpful, conversational (not salesy)
3. **Response Style**: Address their specific response directly
4. **Length**: Keep replies concise (2-3 sentences max)
5. **Next Steps**: Always suggest a concrete next step
6. **Closing**: Always use "Best," followed by signature

**Response Types to Handle**:

**POSITIVE RESPONSES** (interested, want info, schedule call):
- Thank them for their interest
- Suggest specific next step (call, demo, info)
- Be accommodating and helpful

**QUESTIONS** (asking for details, pricing, specs):
- Answer briefly and professionally  
- Offer to provide more detailed information
- Suggest a call for comprehensive discussion

**TIMING REQUESTS** (call me later, busy now):
- Acknowledge their timing preferences
- Offer flexibility
- Suggest easy scheduling options

**NEUTRAL/UNCLEAR** (brief responses, "thanks"):
- Gently probe for their level of interest
- Offer helpful information
- Keep door open for future conversation

**EMAIL STRUCTURE**:
```
Hi [FirstName],

[Direct response to their message - acknowledge what they said]

[Helpful next step or offer]

Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com
```

**EXAMPLE GOOD REPLIES**:

If they say "I'm interested in learning more":
```
Hi Sarah,

Great to hear you're interested! I'd be happy to walk you through how our Narc Gone system works and discuss the specific benefits for Austin PD.

Would you have 15 minutes this week for a brief call?

Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com
```

If they ask "What's the cost?":
```
Hi Mike,

Pricing depends on your department's volume and specific needs, but most agencies see 30-60% cost savings compared to incineration.

I'd love to provide you with a customized quote - could we schedule a quick call to discuss your current disposal process?

Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com
```

**RETURN FORMAT** - Must be valid JSON:
{
  "subject": "Re: [their subject]",
  "reply_body": "Full email reply with greeting and closing",
  "sentiment_analysis": "positive/interested/question/neutral",
  "suggested_next_action": "schedule_call/send_info/follow_up_later"
}"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a reply to an incoming email"""
        try:
            original_email = task.get("original_email", {})
            reply_content = task.get("reply_content", "")
            prospect_data = task.get("prospect_data", {})
            
            # Extract key information
            sender_name = original_email.get("sender_name", "")
            original_subject = original_email.get("subject", "")
            company_name = prospect_data.get("company_name", "")
            
            # Extract first name for greeting
            first_name = self._extract_first_name(sender_name)
            if not first_name and prospect_data.get("email"):
                first_name = self._extract_name_from_email(prospect_data.get("email"))
            
            # Build reply generation prompt
            reply_prompt = {
                "task": "generate_reply",
                "context": {
                    "original_subject": original_subject,
                    "reply_content": reply_content,
                    "sender_name": sender_name,
                    "first_name": first_name,
                    "company_name": company_name,
                    "prospect_data": prospect_data
                },
                "instruction": "Generate a professional, helpful email reply that addresses their response and suggests an appropriate next step. Must be conversational and natural, not salesy. Return valid JSON."
            }
            
            # Generate reply using AI
            result = await self.think(reply_prompt)
            
            if "error" in result:
                return self._create_fallback_reply(reply_content, first_name, original_subject)
            
            # Parse AI response
            if "response" in result and isinstance(result["response"], str):
                try:
                    response_text = result["response"]
                    if "{" in response_text and "}" in response_text:
                        start = response_text.find("{")
                        end = response_text.rfind("}") + 1
                        json_text = response_text[start:end]
                        reply_data = json.loads(json_text)
                        
                        # Ensure required fields
                        reply_data.setdefault("subject", f"Re: {original_subject}")
                        reply_data.setdefault("sentiment_analysis", "neutral")
                        reply_data.setdefault("suggested_next_action", "follow_up_later")
                        
                        reply_data["success"] = True
                        reply_data["recipient_email"] = prospect_data.get("email", "")
                        
                        return reply_data
                except json.JSONDecodeError:
                    pass
            
            # Fallback if parsing fails
            return self._create_fallback_reply(reply_content, first_name, original_subject)
            
        except Exception as e:
            logger.error(f"Reply generation failed: {e}")
            return self._create_fallback_reply(
                task.get("reply_content", ""), 
                "there", 
                task.get("original_email", {}).get("subject", "")
            )
    
    def _extract_first_name(self, full_name: str) -> str:
        """Extract first name from full name"""
        if not full_name or full_name in ['N/A', '', None]:
            return ""
        
        name_parts = full_name.split()
        titles = ['Dr.', 'Dr', 'Mr.', 'Mr', 'Ms.', 'Ms', 'Mrs.', 'Mrs', 'Prof.', 'Prof']
        
        for part in name_parts:
            clean_part = part.strip('.,')
            if clean_part not in titles and clean_part:
                return clean_part
        
        return name_parts[0] if name_parts else ""
    
    def _extract_name_from_email(self, email: str) -> str:
        """Extract potential first name from email address"""
        if not email:
            return ""
        
        try:
            username = email.split('@')[0].lower()
            parts = username.replace('.', ' ').replace('_', ' ').replace('-', ' ').split()
            
            if parts:
                first_part = parts[0]
                first_part = ''.join(c for c in first_part if c.isalpha())
                
                skip_words = ['admin', 'info', 'contact', 'support', 'office', 'dept']
                if first_part not in skip_words and len(first_part) > 1:
                    return first_part.capitalize()
        except:
            pass
        
        return ""
    
    def _create_fallback_reply(self, reply_content: str, first_name: str, original_subject: str) -> Dict[str, Any]:
        """Create a simple fallback reply"""
        greeting = f"Hi {first_name}," if first_name else "Hi there,"
        
        # Simple sentiment analysis
        positive_words = ["interested", "yes", "call", "schedule", "more info"]
        is_positive = any(word in reply_content.lower() for word in positive_words)
        
        if is_positive:
            body = f"""{greeting}

Thank you for your interest! I'd be happy to discuss how our Narc Gone system could help your department reduce disposal costs and ensure compliance.

Would you be available for a brief call this week?

Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com"""
            sentiment = "interested"
            action = "schedule_call"
        else:
            body = f"""{greeting}

Thank you for your response. If you'd like to learn more about our drug destruction solutions, I'm happy to provide additional information at your convenience.

Please let me know if you have any questions.

Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com"""
            sentiment = "neutral"
            action = "follow_up_later"
        
        return {
            "success": True,
            "subject": f"Re: {original_subject}",
            "reply_body": body,
            "sentiment_analysis": sentiment,
            "suggested_next_action": action
        }

class AIAutoReplySystem:
    """Complete automated reply system with AI-powered responses"""
    
    def __init__(self):
        self.gmail = GmailIntegration()
        self.storage = MongoDBStorage()
        self.reply_agent = GroqReplyAgent()
        
        # Reply detection settings
        self.check_interval_minutes = 30  # Check every 30 minutes
        self.sender_email = "solutions@gfmd.com"
        
        # Track which emails we've already replied to
        self.replied_message_ids = set()
        
        logger.info("✅ AI Auto-Reply System initialized")
    
    def analyze_reply_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze the sentiment and intent of a reply"""
        content_lower = content.lower()
        
        # Positive indicators
        positive_words = [
            "interested", "yes", "call me", "schedule", "meeting", "demo", 
            "more info", "tell me more", "sounds good", "available", "when can"
        ]
        
        # Negative indicators  
        negative_words = [
            "not interested", "no thanks", "remove", "unsubscribe", 
            "stop", "not a fit", "pass", "no need"
        ]
        
        # Question indicators
        question_words = [
            "cost", "price", "how much", "what is", "how does", "can you",
            "do you", "specs", "details", "information"
        ]
        
        positive_score = sum(1 for word in positive_words if word in content_lower)
        negative_score = sum(1 for word in negative_words if word in content_lower)
        question_score = sum(1 for word in question_words if word in content_lower)
        
        if negative_score > 0:
            sentiment = "negative"
        elif positive_score > 0:
            sentiment = "positive"
        elif question_score > 0:
            sentiment = "question"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "positive_score": positive_score,
            "negative_score": negative_score,
            "question_score": question_score,
            "should_auto_reply": sentiment in ["positive", "question", "neutral"]
        }
    
    async def check_for_new_replies(self) -> List[Dict]:
        """Check Gmail for new replies to our emails"""
        try:
            # Check for replies in the last hour
            since_date = (datetime.now() - timedelta(hours=2)).strftime("%Y/%m/%d")
            
            print(f"🔍 Checking for replies since {since_date}...")
            
            # Use existing Gmail integration
            replies = self.gmail.check_for_replies(since_date=since_date, max_results=20)
            
            # Filter out replies we've already processed
            new_replies = []
            for reply in replies:
                message_id = reply.get("message_id")
                if message_id and message_id not in self.replied_message_ids:
                    new_replies.append(reply)
            
            print(f"📧 Found {len(new_replies)} new replies to process")
            return new_replies
            
        except Exception as e:
            logger.error(f"Failed to check for replies: {e}")
            return []
    
    async def process_reply(self, reply_data: Dict) -> Optional[Dict]:
        """Process a single reply and generate automated response"""
        try:
            message_id = reply_data.get("message_id")
            sender_email = reply_data.get("from_email", "")
            reply_content = reply_data.get("content", "")
            original_subject = reply_data.get("subject", "")
            
            print(f"\n📨 Processing reply from: {sender_email}")
            print(f"💭 Content preview: {reply_content[:100]}...")
            
            # Analyze sentiment
            sentiment_analysis = self.analyze_reply_sentiment(reply_content)
            print(f"🎯 Sentiment: {sentiment_analysis['sentiment']}")
            
            # Skip auto-reply for negative responses
            if sentiment_analysis["sentiment"] == "negative":
                print("❌ Negative sentiment detected - skipping auto-reply")
                self.replied_message_ids.add(message_id)
                return None
            
            # Find prospect data from database
            prospect_data = self._find_prospect_by_email(sender_email)
            
            # Generate AI reply
            reply_task = {
                "original_email": {
                    "sender_name": reply_data.get("sender_name", ""),
                    "subject": original_subject
                },
                "reply_content": reply_content,
                "prospect_data": prospect_data or {"email": sender_email}
            }
            
            print("🤖 Generating AI reply...")
            ai_response = await self.reply_agent.execute(reply_task)
            
            if not ai_response.get("success"):
                print("❌ AI reply generation failed")
                return None
            
            # Send the reply
            if await self.send_auto_reply(ai_response, sender_email):
                # Mark as processed
                self.replied_message_ids.add(message_id)
                
                # Record in database
                await self._record_auto_reply(reply_data, ai_response, sentiment_analysis)
                
                print(f"✅ Auto-reply sent successfully to {sender_email}")
                return ai_response
            else:
                print(f"❌ Failed to send auto-reply to {sender_email}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to process reply: {e}")
            return None
    
    def _find_prospect_by_email(self, email: str) -> Optional[Dict]:
        """Find prospect data in database by email"""
        try:
            contact = self.storage.db.contacts.find_one({"email": email})
            return contact
        except:
            return None
    
    async def send_auto_reply(self, reply_data: Dict, recipient_email: str) -> bool:
        """Send the automated reply via Gmail"""
        try:
            subject = reply_data.get("subject", "Re: Your inquiry")
            body = reply_data.get("reply_body", "")
            
            # Send email using existing Gmail integration
            result = self.gmail.send_email(
                to_email=recipient_email,
                subject=subject,
                body=body
            )
            
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"Failed to send auto-reply: {e}")
            return False
    
    async def _record_auto_reply(self, original_reply: Dict, ai_response: Dict, sentiment: Dict):
        """Record the auto-reply in database for tracking"""
        try:
            auto_reply_record = {
                "type": "auto_reply",
                "original_message_id": original_reply.get("message_id"),
                "sender_email": original_reply.get("from_email"),
                "original_content": original_reply.get("content"),
                "sentiment_analysis": sentiment,
                "ai_response": {
                    "subject": ai_response.get("subject"),
                    "body": ai_response.get("reply_body"),
                    "suggested_action": ai_response.get("suggested_next_action")
                },
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            # Store in interactions collection
            self.storage.db.interactions.insert_one(auto_reply_record)
            
        except Exception as e:
            logger.error(f"Failed to record auto-reply: {e}")
    
    async def run_continuous_monitoring(self):
        """Run continuous monitoring for replies"""
        print("🚀 Starting AI Auto-Reply Continuous Monitoring")
        print(f"⏰ Checking every {self.check_interval_minutes} minutes")
        print("=" * 60)
        
        while True:
            try:
                # Check for new replies
                replies = await self.check_for_new_replies()
                
                if replies:
                    print(f"\n🎯 Processing {len(replies)} new replies...")
                    
                    for reply in replies:
                        await self.process_reply(reply)
                        
                        # Small delay between processing replies
                        await asyncio.sleep(2)
                else:
                    print("📭 No new replies found")
                
                # Wait before next check
                print(f"\n⏸️ Waiting {self.check_interval_minutes} minutes until next check...")
                await asyncio.sleep(self.check_interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                print(f"❌ Error occurred, waiting 5 minutes before retry...")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def run_single_check(self):
        """Run a single check for replies (for testing)"""
        print("🤖 AI Auto-Reply System - Single Check")
        print("=" * 50)
        
        replies = await self.check_for_new_replies()
        
        if replies:
            print(f"Processing {len(replies)} replies...")
            
            results = []
            for reply in replies:
                result = await self.process_reply(reply)
                if result:
                    results.append(result)
            
            print(f"\n📊 Summary: {len(results)} auto-replies sent successfully")
            return results
        else:
            print("No new replies to process")
            return []

async def main():
    """Main function - run single check or continuous monitoring"""
    import sys
    
    auto_reply = AIAutoReplySystem()
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        await auto_reply.run_continuous_monitoring()
    else:
        await auto_reply.run_single_check()

if __name__ == "__main__":
    import json
    asyncio.run(main())