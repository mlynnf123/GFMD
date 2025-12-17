#!/usr/bin/env python3
"""
Email Sequence Scheduler for GFMD Narc Gone Campaign
Runs as a background service to process email sequences on schedule
"""

from typing import Dict, Any
import asyncio
import logging
import schedule
import time
from datetime import datetime, timedelta
from email_sequence_orchestrator import EmailSequenceOrchestrator
from reply_detector import ReplyDetector
import json

logger = logging.getLogger(__name__)

class SequenceScheduler:
    """Schedules and manages automated email sequence processing"""
    
    def __init__(self):
        self.orchestrator = EmailSequenceOrchestrator()
        self.reply_detector = ReplyDetector()
        
        # Scheduling settings
        self.email_check_interval = 60  # Check every 60 minutes for due emails
        self.reply_check_interval = 15  # Check every 15 minutes for replies
        self.stats_interval = 24 * 60   # Generate stats every 24 hours
        
        # Operating hours (24/7 for now, can be restricted later)
        self.start_hour = 8   # 8 AM
        self.end_hour = 18    # 6 PM
        self.timezone = "America/New_York"
        
        self.running = False
        
        logger.info("✅ Sequence Scheduler initialized")
    
    def start(self):
        """Start the scheduler"""
        logger.info("🚀 Starting Email Sequence Scheduler...")
        
        # Schedule email processing
        schedule.every().hour.do(self._schedule_email_processing)
        
        # Schedule reply checking
        schedule.every(15).minutes.do(self._schedule_reply_checking)
        
        # Schedule daily stats
        schedule.every().day.at("09:00").do(self._schedule_daily_stats)
        
        self.running = True
        
        # Run the scheduler loop
        self._run_scheduler()
    
    def stop(self):
        """Stop the scheduler"""
        logger.info("⏹️ Stopping Email Sequence Scheduler...")
        self.running = False
        schedule.clear()
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("🛑 Scheduler stopped by user")
                self.stop()
                break
                
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                time.sleep(60)  # Wait before retrying
    
    def _schedule_email_processing(self):
        """Schedule email processing (runs in thread)"""
        try:
            # Check if we're in business hours (optional)
            if self._is_business_hours():
                asyncio.run(self._process_due_emails())
            else:
                logger.info("⏰ Outside business hours, skipping email processing")
                
        except Exception as e:
            logger.error(f"❌ Error in scheduled email processing: {e}")
    
    def _schedule_reply_checking(self):
        """Schedule reply checking (runs in thread)"""
        try:
            asyncio.run(self._check_for_replies())
        except Exception as e:
            logger.error(f"❌ Error in scheduled reply checking: {e}")
    
    def _schedule_daily_stats(self):
        """Schedule daily statistics generation"""
        try:
            asyncio.run(self._generate_daily_stats())
        except Exception as e:
            logger.error(f"❌ Error in scheduled stats generation: {e}")
    
    async def _process_due_emails(self):
        """Process all due email sequences"""
        try:
            logger.info("📧 Processing due email sequences...")
            
            result = await self.orchestrator.process_sequences()
            
            if result.get("success"):
                logger.info(
                    f"✅ Processed {result.get('processed', 0)} sequences, "
                    f"sent {result.get('sent', 0)} emails, "
                    f"completed {result.get('completed', 0)} sequences"
                )
            else:
                logger.error(f"❌ Failed to process sequences: {result.get('error')}")
                
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing due emails: {e}")
            return {"success": False, "error": str(e)}
    
    async def _check_for_replies(self):
        """Check for email replies and update sequences"""
        try:
            logger.info("📬 Checking for email replies...")
            
            result = await self.reply_detector.check_for_replies()
            
            if result.get("success"):
                replies_found = result.get("replies_found", 0)
                if replies_found > 0:
                    logger.info(f"📧 Found {replies_found} replies")
                
            return result
            
        except Exception as e:
            logger.error(f"❌ Error checking for replies: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_daily_stats(self):
        """Generate and log daily statistics"""
        try:
            logger.info("📊 Generating daily statistics...")
            
            # Get sequence stats
            sequence_stats = await self.orchestrator.get_sequence_stats()
            
            # Get reply stats
            reply_stats = await self.reply_detector.get_reply_stats(1)  # Last 24 hours
            
            stats = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "sequence_stats": sequence_stats,
                "reply_stats": reply_stats
            }
            
            logger.info(f"📈 Daily Stats: {json.dumps(stats, indent=2)}")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error generating daily stats: {e}")
            return {"success": False, "error": str(e)}
    
    def _is_business_hours(self) -> bool:
        """Check if current time is within business hours"""
        now = datetime.now()
        current_hour = now.hour
        
        # For now, allow 24/7 operation
        # return self.start_hour <= current_hour < self.end_hour
        return True
    
    async def run_once(self) -> Dict[str, Any]:
        """Run one cycle of processing (useful for testing)"""
        try:
            logger.info("🔄 Running single processing cycle...")
            
            # Process due emails
            email_result = await self._process_due_emails()
            
            # Check for replies
            reply_result = await self._check_for_replies()
            
            return {
                "success": True,
                "email_processing": email_result,
                "reply_checking": reply_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error in single processing cycle: {e}")
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        return {
            "running": self.running,
            "email_check_interval": self.email_check_interval,
            "reply_check_interval": self.reply_check_interval,
            "business_hours": f"{self.start_hour}:00 - {self.end_hour}:00",
            "timezone": self.timezone,
            "next_runs": [str(job) for job in schedule.jobs]
        }

# CLI interface for running the scheduler
async def main():
    """Main function for running the scheduler"""
    import sys
    
    scheduler = SequenceScheduler()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "start":
            scheduler.start()
            
        elif command == "once":
            result = await scheduler.run_once()
            print(json.dumps(result, indent=2))
            
        elif command == "status":
            status = scheduler.get_status()
            print(json.dumps(status, indent=2))
            
        else:
            print("Usage: python sequence_scheduler.py [start|once|status]")
    else:
        # Default: run once for testing
        result = await scheduler.run_once()
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())