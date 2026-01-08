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
        return """You are an Email Reply Agent for GFMD responding about Narc Gone drug destruction products.

YOUR TASK: Read the incoming email and write a personalized reply that DIRECTLY addresses what they said.

RULES:
1. READ the email content carefully - understand what they're asking/saying
2. WRITE a reply that specifically references their message
3. Keep replies concise (2-4 sentences)
4. Always suggest a next step (call, more info, etc.)
5. Use professional but friendly tone

SIGNATURE - Always end with:
Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com

PRODUCT INFO (use when relevant):
- Narc Gone: On-site drug destruction system for law enforcement
- Benefits: 30-60% cost savings vs incineration, no transportation needed, faster processing
- Compliance: Meets all DEA requirements

OUTPUT FORMAT - Valid JSON only:
{
  "subject": "Re: [original subject]",
  "reply_body": "Hi [Name],\n\n[Your personalized response]\n\nBest,\n\nMeranda Freiner\nsolutions@gfmd.com\n619-341-9058     www.gfmd.com",
  "sentiment_analysis": "positive/question/neutral/competitive_objection",
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
        """Generate a reply to an incoming email - AI ALWAYS analyzes the specific content"""
        import time

        original_email = task.get("original_email", {})
        reply_content = task.get("reply_content", "")
        prospect_data = task.get("prospect_data", {})

        # CRITICAL: Log exactly what we're processing
        print(f"\n{'='*60}")
        print(f"AI REPLY GENERATION - ANALYZING THIS SPECIFIC EMAIL:")
        print(f"{'='*60}")
        print(f"EMAIL CONTENT TO ANALYZE:")
        print(f"{reply_content}")
        print(f"{'='*60}\n")

        # Extract key information
        sender_name = original_email.get("sender_name", "")
        original_subject = original_email.get("subject", "")
        company_name = prospect_data.get("company_name", "")

        # Extract first name for greeting
        first_name = self._extract_first_name(sender_name)
        if not first_name and prospect_data.get("email"):
            first_name = self._extract_name_from_email(prospect_data.get("email"))
        if not first_name:
            first_name = "there"

        # Analyze for competitive objections
        competitive_analysis = self._analyze_competitive_objection(reply_content)

        # Get competitive knowledge if needed
        competitive_knowledge = ""
        if competitive_analysis["requires_competitive_response"]:
            competitive_knowledge = self._get_competitive_knowledge(
                competitive_analysis["competitors_mentioned"],
                reply_content
            )

        # Build the AI prompt - NO TEMPLATES, AI MUST ANALYZE THE ACTUAL CONTENT
        reply_prompt = f"""ANALYZE AND RESPOND TO THIS SPECIFIC EMAIL:

=== EMAIL RECEIVED ===
From: {sender_name}
Subject: {original_subject}
Content:
{reply_content}
=== END EMAIL ===

INSTRUCTIONS:
1. READ the email content above carefully
2. IDENTIFY what they are saying/asking
3. WRITE a personalized reply that DIRECTLY addresses their specific message
4. Reference SPECIFIC things they mentioned in their email

Recipient first name: {first_name}
{f'Competitive context: {competitive_knowledge}' if competitive_knowledge else ''}

REQUIRED JSON FORMAT:
{{
  "subject": "Re: {original_subject}",
  "reply_body": "Hi {first_name},\\n\\n[Your personalized reply that specifically addresses their message]\\n\\nBest,\\n\\nMeranda Freiner\\nsolutions@gfmd.com\\n619-341-9058     www.gfmd.com",
  "sentiment_analysis": "[positive/interested/question/neutral/competitive_objection]",
  "suggested_next_action": "[schedule_call/send_info/follow_up_later]"
}}

CRITICAL: Your reply_body MUST reference specific content from their email. Generic responses are NOT acceptable."""

        # Try up to 3 times to get a valid AI response
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                print(f"AI Generation Attempt {attempt + 1}/{max_retries}...")

                # Call AI with the prompt as a simple string
                result = await self.think({"prompt": reply_prompt})

                print(f"AI Response received: {str(result)[:500]}...")

                # Try to parse the response
                if "error" in result:
                    last_error = result.get("error")
                    print(f"AI returned error: {last_error}")
                    time.sleep(1)
                    continue

                # Handle response - it may already be parsed JSON
                reply_data = None

                if isinstance(result, dict) and "reply_body" in result:
                    reply_data = result
                elif "response" in result and isinstance(result["response"], str):
                    response_text = result["response"]
                    # Extract JSON from response
                    if "{" in response_text and "}" in response_text:
                        start = response_text.find("{")
                        end = response_text.rfind("}") + 1
                        json_text = response_text[start:end]
                        reply_data = json.loads(json_text)
                elif isinstance(result, dict):
                    # Result might already be the parsed data
                    reply_data = result

                if reply_data and "reply_body" in reply_data:
                    # Validate the reply is not generic
                    reply_body = reply_data.get("reply_body", "")

                    print(f"AI Generated Reply:\n{reply_body}")

                    # Ensure required fields
                    reply_data.setdefault("subject", f"Re: {original_subject}")
                    reply_data.setdefault("sentiment_analysis", "neutral")
                    reply_data.setdefault("suggested_next_action", "follow_up_later")
                    reply_data["success"] = True
                    reply_data["recipient_email"] = prospect_data.get("email", "")

                    return reply_data
                else:
                    print(f"AI response missing reply_body, retrying...")
                    last_error = "Response missing reply_body field"

            except json.JSONDecodeError as e:
                last_error = f"JSON parse error: {e}"
                print(f"JSON parsing failed: {e}")
            except Exception as e:
                last_error = str(e)
                print(f"AI call failed: {e}")

            time.sleep(1)  # Brief pause before retry

        # All retries failed - return error, do NOT use template
        print(f"AI FAILED after {max_retries} attempts. Last error: {last_error}")
        return {
            "success": False,
            "error": f"AI analysis failed after {max_retries} attempts: {last_error}",
            "reply_body": None,
            "subject": f"Re: {original_subject}"
        }
    
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
        
        logger.info("AI Auto-Reply System initialized")
    
    def _extract_original_recipient_from_bounce(self, bounce_content: str, subject: str) -> Optional[str]:
        """Extract the original recipient email from bounce message content"""
        import re
        
        # Common patterns in bounce messages
        patterns = [
            r"Your message wasn't delivered to ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
            r"to ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}) because",
            r"delivery to ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}) failed",
            r"<([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>",
            r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\s+(?:address not found|user unknown)"
        ]
        
        # Try to extract from content first
        full_text = f"{bounce_content} {subject}"
        for pattern in patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                email = match.group(1)
                # Validate email format
                if '@' in email and '.' in email.split('@')[1]:
                    return email.lower()
        
        return None

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
            
            print(f"Checking for replies since {since_date}...")
            
            # Use existing Gmail integration
            replies = self.gmail.check_for_replies(since_date=since_date, max_results=20)
            
            # Filter out replies we've already processed
            new_replies = []
            for reply in replies:
                message_id = reply.get("message_id")
                if message_id and message_id not in self.replied_message_ids:
                    new_replies.append(reply)
            
            print(f"Found {len(new_replies)} new replies to process")
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

            print(f"\n{'#'*60}")
            print(f"PROCESSING EMAIL #{message_id}")
            print(f"From: {sender_email}")
            print(f"Subject: {original_subject}")
            print(f"Content length: {len(reply_content)} chars")
            print(f"Full content: {reply_content[:300]}...")
            print(f"{'#'*60}")
            
            # CRITICAL: Check for bounce messages first (before any other processing)
            bounce_senders = ['postmaster', 'mailer-daemon', 'mail-daemon', 'delivery-daemon', 'no-reply']
            bounce_keywords = ['address not found', 'delivery failed', 'mail not delivered', 'undeliverable', 'user unknown', 'mailbox full', 'returned mail']
            
            # Check if sender is a system daemon
            sender_lower = sender_email.lower()
            is_system_bounce = any(daemon in sender_lower for daemon in bounce_senders)
            
            # Check if content contains bounce indicators
            content_lower = f"{reply_content} {original_subject}".lower()
            has_bounce_keywords = any(keyword in content_lower for keyword in bounce_keywords)
            
            if is_system_bounce or has_bounce_keywords:
                print(f"BOUNCE MESSAGE DETECTED from {sender_email}")
                print(f"   System sender: {is_system_bounce}")
                print(f"   Bounce keywords: {has_bounce_keywords}")
                
                # Extract original recipient from bounce message
                original_recipient = self._extract_original_recipient_from_bounce(reply_content, original_subject)
                if original_recipient:
                    print(f"   Original recipient: {original_recipient}")
                    
                    # Add original recipient to suppression list
                    from email_reply_monitor import EmailReplyMonitor
                    monitor = EmailReplyMonitor()
                    monitor.add_to_suppression_list(
                        original_recipient, 
                        'Email delivery failed', 
                        {
                            'bounce_sender': sender_email,
                            'bounce_content': reply_content[:200],
                            'source': 'bounce_detection'
                        }
                    )
                    print(f"   Added {original_recipient} to suppression list")
                
                # Do not process bounce as auto-reply
                self.replied_message_ids.add(message_id)
                return None
            
            # Check if email is already on suppression list
            from email_reply_monitor import EmailReplyMonitor
            monitor = EmailReplyMonitor()
            
            if monitor.check_suppression_status(sender_email):
                print(f"Email {sender_email} is already on suppression list - skipping auto-reply")
                self.replied_message_ids.add(message_id)
                return None
            
            # Analyze email for suppression triggers
            content_analysis = monitor.analyze_email_content(reply_content, original_subject)
            if content_analysis['should_suppress']:
                print(f"Suppression keywords detected: {content_analysis['keywords_found']}")
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
            
            # Check auto-reply limit (max 2 per email address)
            MAX_AUTO_REPLIES = 2
            previous_replies = self._count_auto_replies_sent(sender_email)
            if previous_replies >= MAX_AUTO_REPLIES:
                print(f"AUTO-REPLY LIMIT REACHED: Already sent {previous_replies} auto-replies to {sender_email}")
                print(f"Human intervention required - skipping auto-reply")
                self.replied_message_ids.add(message_id)
                return None

            print(f"Auto-reply count for {sender_email}: {previous_replies}/{MAX_AUTO_REPLIES}")

            # Analyze sentiment (backup check)
            sentiment_analysis = self.analyze_reply_sentiment(reply_content)
            print(f"Sentiment: {sentiment_analysis['sentiment']}")

            # Skip auto-reply for negative responses
            if sentiment_analysis["sentiment"] == "negative":
                print("Negative sentiment detected - skipping auto-reply")
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
            
            print("Generating AI reply...")
            ai_response = await self.reply_agent.execute(reply_task)

            if not ai_response.get("success"):
                error_msg = ai_response.get("error", "Unknown error")
                print(f"AI reply generation FAILED: {error_msg}")
                print(f"Will NOT send any reply to {sender_email} - AI must analyze properly")
                return None
            
            # Send the reply
            if await self.send_auto_reply(ai_response, sender_email):
                # Mark as processed
                self.replied_message_ids.add(message_id)
                
                # Record in database
                await self._record_auto_reply(reply_data, ai_response, sentiment_analysis)
                
                print(f"Auto-reply sent successfully to {sender_email}")
                return ai_response
            else:
                print(f"Failed to send auto-reply to {sender_email}")
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

    def _count_auto_replies_sent(self, email: str) -> int:
        """Count how many auto-replies have been sent to this email address"""
        try:
            count = self.storage.db.interactions.count_documents({
                "type": "auto_reply",
                "sender_email": email,
                "success": True
            })
            return count
        except Exception as e:
            logger.error(f"Failed to count auto-replies for {email}: {e}")
            return 0
    
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
        print("Starting AI Auto-Reply Continuous Monitoring")
        print(f"Checking every {self.check_interval_minutes} minutes")
        print("=" * 60)
        
        while True:
            try:
                # Check for new replies
                replies = await self.check_for_new_replies()
                
                if replies:
                    print(f"\nProcessing {len(replies)} new replies...")
                    
                    for reply in replies:
                        await self.process_reply(reply)
                        
                        # Small delay between processing replies
                        await asyncio.sleep(2)
                else:
                    print("No new replies found")
                
                # Wait before next check
                print(f"\nWaiting {self.check_interval_minutes} minutes until next check...")
                await asyncio.sleep(self.check_interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                print(f"Error occurred, waiting 5 minutes before retry...")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def run_single_check(self):
        """Run a single check for replies (for testing)"""
        print("AI Auto-Reply System - Single Check")
        print("=" * 50)

        replies = await self.check_for_new_replies()

        if replies:
            total_replies = len(replies)
            print(f"\n*** FOUND {total_replies} REPLIES TO PROCESS ***\n")

            results = []
            for index, reply in enumerate(replies, 1):
                print(f"\n>>> Processing reply {index} of {total_replies} <<<")
                result = await self.process_reply(reply)
                if result:
                    results.append(result)
                    print(f">>> Reply {index} processed successfully <<<")
                else:
                    print(f">>> Reply {index} skipped (suppressed/bounce/negative) <<<")

                # Small delay between processing
                await asyncio.sleep(1)

            print(f"\n{'='*50}")
            print(f"SUMMARY: {len(results)} auto-replies sent out of {total_replies} total")
            print(f"{'='*50}")
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