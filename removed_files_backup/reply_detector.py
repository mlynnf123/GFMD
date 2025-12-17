#!/usr/bin/env python3
"""
Reply Detection System for GFMD Email Sequences
Monitors Gmail for replies and processes them automatically
"""

from typing import Dict, Any, List, Optional
import logging
import re
from datetime import datetime, timedelta
from gmail_integration import GmailIntegration
from email_sequence_orchestrator import EmailSequenceOrchestrator
import asyncio
import json
import base64
import email
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

class ReplyDetector:
    """Detects and processes email replies to pause sequences"""
    
    def __init__(self):
        self.gmail = GmailIntegration()
        self.orchestrator = EmailSequenceOrchestrator()
        
        # Reply detection settings
        self.check_interval_minutes = 15  # Check every 15 minutes
        self.sender_email = "mark@gfmdmedical.com"  # Our sender email
        
        # Positive reply indicators
        self.positive_indicators = [
            "interested", "yes", "let's talk", "call me", "schedule", 
            "meeting", "demo", "more info", "tell me more", "sounds good",
            "available", "when can", "time to talk", "setup a call"
        ]
        
        # Negative reply indicators
        self.negative_indicators = [
            "not interested", "no thanks", "remove me", "unsubscribe",
            "stop emailing", "not a good fit", "pass", "no need"
        ]
        
        logger.info("✅ Reply Detector initialized")
    
    async def start_monitoring(self):
        """Start continuous monitoring for replies"""
        logger.info("🔍 Starting reply monitoring...")
        
        while True:
            try:
                await self.check_for_replies()
                await asyncio.sleep(self.check_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"❌ Error in reply monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def check_for_replies(self) -> Dict[str, Any]:
        """Check Gmail for new replies and process them"""
        try:
            # Get recent emails sent to our sender email
            query = f"to:{self.sender_email} newer_than:1d"
            
            messages = self.gmail.search_messages(query)
            
            if not messages:
                return {"success": True, "replies_found": 0}
            
            processed_replies = 0
            
            for message in messages[:50]:  # Process max 50 recent messages
                try:
                    # Get message details
                    msg_data = self.gmail.service.users().messages().get(
                        userId='me', 
                        id=message['id']
                    ).execute()
                    
                    # Process the reply
                    reply_result = await self._process_reply_message(msg_data)
                    
                    if reply_result.get("success"):
                        processed_replies += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error processing message {message['id']}: {e}")
                    continue
            
            logger.info(f"📬 Processed {processed_replies} replies")
            
            return {
                "success": True,
                "replies_found": len(messages),
                "replies_processed": processed_replies
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to check for replies: {e}")
            return {"success": False, "error": str(e)}
    
    async def _process_reply_message(self, msg_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single reply message"""
        try:
            # Extract headers
            headers = msg_data.get("payload", {}).get("headers", [])
            
            from_email = None
            subject = None
            date_str = None
            
            for header in headers:
                name = header.get("name", "").lower()
                value = header.get("value", "")
                
                if name == "from":
                    # Extract email from "Name <email@domain.com>" format
                    email_match = re.search(r'<([^>]+)>', value)
                    if email_match:
                        from_email = email_match.group(1).lower()
                    else:
                        from_email = value.lower()
                        
                elif name == "subject":
                    subject = value
                    
                elif name == "date":
                    date_str = value
            
            if not from_email:
                return {"success": False, "error": "No sender email found"}
            
            # Extract message body
            body = self._extract_message_body(msg_data.get("payload", {}))
            
            if not body:
                return {"success": False, "error": "No message body found"}
            
            # Parse date
            reply_date = self._parse_email_date(date_str) if date_str else datetime.now()
            
            # Classify reply sentiment
            sentiment = self._classify_reply_sentiment(body, subject or "")
            
            # Handle the reply
            handle_result = await self.orchestrator.handle_reply(
                contact_email=from_email,
                reply_content=body,
                reply_date=reply_date
            )
            
            if handle_result.get("success"):
                logger.info(f"📧 Reply processed from {from_email}: {sentiment}")
                
                # If it's a positive reply, mark for follow-up
                if sentiment == "positive":
                    await self._mark_for_sales_follow_up(
                        from_email, 
                        body, 
                        handle_result.get("contact_id")
                    )
                
                return {
                    "success": True,
                    "from_email": from_email,
                    "sentiment": sentiment,
                    "contact_id": handle_result.get("contact_id")
                }
            else:
                return {"success": False, "error": handle_result.get("error")}
                
        except Exception as e:
            logger.error(f"❌ Error processing reply message: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_message_body(self, payload: Dict[str, Any]) -> str:
        """Extract text content from email payload"""
        try:
            body = ""
            
            if "parts" in payload:
                for part in payload["parts"]:
                    if part.get("mimeType") == "text/plain":
                        data = part.get("body", {}).get("data", "")
                        if data:
                            body += base64.urlsafe_b64decode(data).decode('utf-8')
                            
            elif payload.get("mimeType") == "text/plain":
                data = payload.get("body", {}).get("data", "")
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
            
            # Clean up common reply artifacts
            body = self._clean_reply_body(body)
            
            return body
            
        except Exception as e:
            logger.error(f"❌ Error extracting message body: {e}")
            return ""
    
    def _clean_reply_body(self, body: str) -> str:
        """Clean up email reply body text"""
        try:
            # Remove quoted text (common patterns)
            lines = body.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                
                # Skip quoted text indicators
                if line.startswith('>') or line.startswith('On ') and 'wrote:' in line:
                    break
                    
                # Skip common signatures
                if any(sig in line.lower() for sig in ['sent from', 'get outlook', 'this email']):
                    break
                    
                if line:  # Only add non-empty lines
                    cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines[:10])  # Limit to first 10 lines
            
        except Exception as e:
            return body[:500]  # Fallback to first 500 chars
    
    def _classify_reply_sentiment(self, body: str, subject: str = "") -> str:
        """Classify reply as positive, negative, or neutral"""
        try:
            text = (body + " " + subject).lower()
            
            # Count positive and negative indicators
            positive_count = sum(1 for indicator in self.positive_indicators if indicator in text)
            negative_count = sum(1 for indicator in self.negative_indicators if indicator in text)
            
            if positive_count > negative_count:
                return "positive"
            elif negative_count > 0:
                return "negative"
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"❌ Error classifying sentiment: {e}")
            return "neutral"
    
    def _parse_email_date(self, date_str: str) -> datetime:
        """Parse email date string to datetime"""
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return datetime.now()
    
    async def _mark_for_sales_follow_up(self, email: str, reply_content: str, contact_id: str):
        """Mark contact for personal sales follow-up"""
        try:
            # Log the positive reply for manual follow-up
            await self.orchestrator.storage.log_interaction(
                contact_id,
                "positive_reply",
                {
                    "reply_content": reply_content,
                    "requires_human_follow_up": True,
                    "priority": "high",
                    "detected_at": datetime.now().isoformat()
                }
            )
            
            logger.info(f"🎯 Marked {email} for human sales follow-up")
            
        except Exception as e:
            logger.error(f"❌ Error marking for follow-up: {e}")
    
    async def get_reply_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get reply statistics for the last N days"""
        try:
            # This would query the database for reply statistics
            since_date = datetime.now() - timedelta(days=days)
            
            stats = await self.orchestrator.storage.db.interactions.aggregate([
                {
                    "$match": {
                        "interaction_type": "email_reply",
                        "created_at": {"$gte": since_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_replies": {"$sum": 1},
                        "positive_replies": {
                            "$sum": {
                                "$cond": [
                                    {"$eq": ["$data.sentiment", "positive"]}, 
                                    1, 
                                    0
                                ]
                            }
                        }
                    }
                }
            ]).to_list(None)
            
            return {
                "success": True,
                "period_days": days,
                "stats": stats[0] if stats else {"total_replies": 0, "positive_replies": 0}
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Test function
async def test_reply_detector():
    """Test the reply detection system"""
    print("📧 Testing Reply Detector")
    print("=" * 40)
    
    detector = ReplyDetector()
    
    # Test checking for replies
    result = await detector.check_for_replies()
    print(f"Reply check result: {result}")
    
    # Test stats
    stats = await detector.get_reply_stats(7)
    print(f"Reply stats: {stats}")

if __name__ == "__main__":
    asyncio.run(test_reply_detector())