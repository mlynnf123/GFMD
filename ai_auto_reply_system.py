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
        # Initialize RAG system for competitive intelligence
        try:
            from vector_rag_system import VectorRAGSystem
            self.rag_system = VectorRAGSystem()
        except Exception as e:
            print(f"Warning: RAG system not available for replies: {e}")
            self.rag_system = None
    
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
- Answer briefly and professionally using provided knowledge
- Offer to provide more detailed information
- Suggest a call for comprehensive discussion

**COMPETITIVE OBJECTIONS** (we use incinerator, we have vendor, happy with current solution):
- Acknowledge their current solution respectfully
- Use provided competitive knowledge to highlight specific advantages
- Focus on measurable benefits (cost savings, efficiency, compliance)
- Position as potential improvement, not replacement criticism
- Keep door open for future consideration

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

If they say "We use incinerator for drug disposal":
```
Hi Brandi,

I understand you currently use incineration. Many departments we work with initially used incinerators but found significant advantages with our on-site system - typically 30-60% cost reduction, no transportation requirements, and faster processing times.

If budget optimization or operational efficiency ever becomes a priority, I'd be happy to show you a quick comparison.

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

    def _analyze_competitive_objection(self, reply_content: str) -> Dict[str, Any]:
        """Analyze reply for competitive objections and get relevant knowledge"""
        content_lower = reply_content.lower()
        
        # Detect competitive alternatives mentioned
        competitors = {
            "incineration": ["incinerator", "incineration", "burn", "burning"],
            "existing_vendor": ["current vendor", "existing supplier", "already have", "current solution"],
            "take_back_events": ["take back", "takeback", "collection events", "disposal events"],
            "alternative_methods": ["other method", "different way", "another solution"]
        }
        
        detected_competitors = []
        for competitor, keywords in competitors.items():
            if any(keyword in content_lower for keyword in keywords):
                detected_competitors.append(competitor)
        
        return {
            "has_competitive_objection": len(detected_competitors) > 0,
            "competitors_mentioned": detected_competitors,
            "requires_competitive_response": len(detected_competitors) > 0
        }
    
    def _get_competitive_knowledge(self, competitors_mentioned: List[str], reply_content: str) -> str:
        """Get relevant competitive knowledge from RAG system"""
        if not self.rag_system or not competitors_mentioned:
            return ""
        
        try:
            # Build search query based on mentioned competitors
            search_queries = []
            for competitor in competitors_mentioned:
                if competitor == "incineration":
                    search_queries.append("incineration costs vs narc gone benefits on-site disposal")
                elif competitor == "existing_vendor":
                    search_queries.append("narc gone advantages benefits compared other vendors")
                elif competitor == "take_back_events":
                    search_queries.append("take back events vs on-site destruction efficiency")
            
            # Get relevant knowledge
            all_knowledge = []
            for query in search_queries[:2]:  # Limit to top 2 queries
                results = self.rag_system.vector_search(query, limit=3)
                for result in results:
                    content = result.get("content", "")
                    if content and len(content) > 100:
                        all_knowledge.append(content[:400])  # Limit content length
            
            # Also get personalized insights for competitive positioning
            insights = self.rag_system.get_personalized_insights(
                agency_type="police",
                pain_points=[f"{comp} comparison" for comp in competitors_mentioned],
                location="general"
            )
            
            # Combine knowledge sources
            knowledge_context = ""
            if all_knowledge:
                knowledge_context += "COMPETITIVE KNOWLEDGE:\n" + "\n".join(all_knowledge[:2])
            
            for key, value in insights.items():
                if value and "solution" in key:
                    knowledge_context += f"\n{key.upper()}: {value[:300]}"
            
            return knowledge_context[:1200]  # Limit total context length
            
        except Exception as e:
            print(f"Warning: Could not retrieve competitive knowledge: {e}")
            return ""

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
            
            # Analyze for competitive objections
            competitive_analysis = self._analyze_competitive_objection(reply_content)
            
            # Get competitive knowledge if needed
            competitive_knowledge = ""
            if competitive_analysis["requires_competitive_response"]:
                competitive_knowledge = self._get_competitive_knowledge(
                    competitive_analysis["competitors_mentioned"], 
                    reply_content
                )
            
            # Build enhanced reply generation prompt
            reply_prompt = {
                "task": "generate_reply",
                "context": {
                    "original_subject": original_subject,
                    "reply_content": reply_content,
                    "sender_name": sender_name,
                    "first_name": first_name,
                    "company_name": company_name,
                    "prospect_data": prospect_data,
                    "competitive_analysis": competitive_analysis,
                    "competitive_knowledge": competitive_knowledge
                },
                "instruction": "Generate a professional email reply that addresses their specific response. If they mentioned competitive alternatives, use the provided competitive knowledge to highlight specific advantages professionally. Focus on measurable benefits and positioning our solution as a potential improvement. Return valid JSON."
            }
            
            # Generate reply using AI
            result = await self.think(reply_prompt)
            
            if "error" in result:
                return self._create_fallback_reply(reply_content, first_name, original_subject, competitive_analysis)
            
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
            return self._create_fallback_reply(reply_content, first_name, original_subject, competitive_analysis)
            
        except Exception as e:
            logger.error(f"Reply generation failed: {e}")
            return self._create_fallback_reply(
                task.get("reply_content", ""), 
                "there", 
                task.get("original_email", {}).get("subject", ""),
                competitive_analysis
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
    
    def _create_fallback_reply(self, reply_content: str, first_name: str, original_subject: str, competitive_analysis: Dict = None) -> Dict[str, Any]:
        """Create an intelligent fallback reply with competitive handling"""
        greeting = f"Hi {first_name}," if first_name else "Hi there,"
        
        # Check for competitive objections
        content_lower = reply_content.lower()
        
        # Handle specific competitive objections
        if competitive_analysis and competitive_analysis.get("has_competitive_objection"):
            competitors = competitive_analysis.get("competitors_mentioned", [])
            
            if "incineration" in competitors:
                body = f"""{greeting}

I understand you currently use incineration for disposal. Many departments we work with initially used incinerators but found our on-site Narc Gone system offers significant advantages - typically 30-60% cost savings, no transportation requirements, and faster processing times.

If budget optimization or operational efficiency ever becomes a priority, I'd be happy to show you a quick comparison of processes and costs.

Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com"""
                sentiment = "competitive_objection"
                action = "follow_up_later"
                
            elif "existing_vendor" in competitors:
                body = f"""{greeting}

I understand you have an existing solution. Many agencies we work with have found that comparing options periodically helps ensure they're getting the best value and efficiency.

If you're ever interested in seeing how our process compares to your current approach, I'd be happy to provide a brief overview.

Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com"""
                sentiment = "competitive_objection"
                action = "follow_up_later"
                
            else:
                # Generic competitive response
                body = f"""{greeting}

I understand you have an established process. Our Narc Gone system has helped many departments improve their operations through cost savings and increased efficiency.

If you're ever interested in exploring alternatives, I'd be happy to provide information for future reference.

Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com"""
                sentiment = "competitive_objection"
                action = "follow_up_later"
        
        # Handle positive responses
        elif any(word in content_lower for word in ["interested", "yes", "call", "schedule", "more info"]):
            body = f"""{greeting}

Thank you for your interest! I'd be happy to discuss how our Narc Gone system could help your department reduce disposal costs and ensure compliance.

Would you be available for a brief call this week?

Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com"""
            sentiment = "interested"
            action = "schedule_call"
            
        # Handle questions
        elif any(word in content_lower for word in ["how", "what", "cost", "price", "when", "where"]):
            body = f"""{greeting}

Great question! I'd be happy to provide you with detailed information about our Narc Gone system and how it could benefit your department.

Could we schedule a brief call to discuss your specific needs and answer any questions you might have?

Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com"""
            sentiment = "question"
            action = "schedule_call"
            
        # Generic neutral response
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
            "stop", "not a fit", "pass", "no need", "mail not delivered", 
            "failed to deliver"
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
            
            # Check if email is already on suppression list
            from email_reply_monitor import EmailReplyMonitor
            monitor = EmailReplyMonitor()
            
            if monitor.check_suppression_status(sender_email):
                print(f"🚫 Email {sender_email} is already on suppression list - skipping auto-reply")
                self.replied_message_ids.add(message_id)
                return None
            
            # Analyze email for suppression triggers
            content_analysis = monitor.analyze_email_content(reply_content, original_subject)
            if content_analysis['should_suppress']:
                print(f"🚫 Suppression keywords detected: {content_analysis['keywords_found']}")
                print(f"   Reason: {content_analysis['suppression_reason']}")
                
                # Add to suppression list
                source_data = {
                    'message_id': message_id,
                    'subject': original_subject,
                    'analysis': content_analysis,
                    'source': 'auto_reply_system'
                }
                monitor.add_to_suppression_list(sender_email, content_analysis['suppression_reason'], source_data)
                
                # Skip auto-reply
                self.replied_message_ids.add(message_id)
                return None
            
            # Analyze sentiment (backup check)
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