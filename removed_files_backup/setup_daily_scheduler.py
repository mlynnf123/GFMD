#!/usr/bin/env python3
"""
Daily Scheduler Setup for GFMD Narcon System
Sets up automated daily tasks for campaign management
"""

import schedule
import time
import asyncio
import logging
from datetime import datetime
import json
import os

from campaign_manager import NarconCampaignManager
from email_sequence_orchestrator import run_daily_sequence_processing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('narcon_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NarconScheduler:
    """Automated scheduler for Narcon campaign tasks"""
    
    def __init__(self):
        """Initialize the scheduler"""
        self.campaign_manager = None
        logger.info("🕒 Narcon Scheduler initialized")
    
    async def _get_campaign_manager(self):
        """Get campaign manager instance (lazy loading)"""
        if not self.campaign_manager:
            self.campaign_manager = NarconCampaignManager()
        return self.campaign_manager
    
    def run_daily_maintenance(self):
        """Run daily maintenance tasks (synchronous wrapper)"""
        try:
            logger.info("🚀 Starting scheduled daily maintenance")
            
            # Run async tasks in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                campaign_manager = loop.run_until_complete(self._get_campaign_manager())
                result = loop.run_until_complete(campaign_manager.run_daily_campaign_maintenance())
                
                if result.get("success"):
                    logger.info("✅ Daily maintenance completed successfully")
                    logger.info(f"   Tasks completed: {', '.join(result.get('tasks_completed', []))}")
                    logger.info(f"   Statistics: {result.get('statistics', {})}")
                else:
                    logger.error(f"❌ Daily maintenance failed: {result.get('error')}")
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"❌ Daily maintenance exception: {e}")
    
    def run_sequence_processing(self):
        """Run sequence processing tasks (synchronous wrapper)"""
        try:
            logger.info("🔄 Starting scheduled sequence processing")
            
            # Run async tasks in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(run_daily_sequence_processing())
                
                if result.get("success"):
                    logger.info("✅ Sequence processing completed")
                else:
                    logger.error(f"❌ Sequence processing failed: {result.get('error')}")
                    
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"❌ Sequence processing exception: {e}")
    
    def health_check(self):
        """Simple health check"""
        try:
            logger.info("💚 Scheduler health check - system running normally")
            
            # Log system status
            current_time = datetime.now()
            logger.info(f"   Current time: {current_time}")
            logger.info(f"   Environment: {os.environ.get('ENVIRONMENT', 'development')}")
            logger.info(f"   MongoDB configured: {'MONGODB_CONNECTION_STRING' in os.environ}")
            logger.info(f"   Groq configured: {'GROQ_API_KEY' in os.environ}")
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")


def setup_production_schedule():
    """Set up the production schedule"""
    scheduler = NarconScheduler()
    
    # Schedule daily maintenance at 6 AM
    schedule.every().day.at("06:00").do(scheduler.run_daily_maintenance)
    logger.info("📅 Daily maintenance scheduled for 6:00 AM")
    
    # Schedule sequence processing every 4 hours during business hours
    schedule.every().day.at("08:00").do(scheduler.run_sequence_processing)
    schedule.every().day.at("12:00").do(scheduler.run_sequence_processing) 
    schedule.every().day.at("16:00").do(scheduler.run_sequence_processing)
    logger.info("📅 Sequence processing scheduled for 8 AM, 12 PM, 4 PM")
    
    # Schedule health checks every hour
    schedule.every().hour.do(scheduler.health_check)
    logger.info("📅 Health checks scheduled every hour")
    
    logger.info("✅ Production schedule configured")
    return scheduler

def setup_development_schedule():
    """Set up a development/testing schedule"""
    scheduler = NarconScheduler()
    
    # More frequent runs for testing
    schedule.every(30).minutes.do(scheduler.run_sequence_processing)
    schedule.every(2).hours.do(scheduler.run_daily_maintenance)
    schedule.every(15).minutes.do(scheduler.health_check)
    
    logger.info("✅ Development schedule configured (frequent runs for testing)")
    return scheduler

def run_scheduler():
    """Run the scheduler indefinitely"""
    
    # Determine environment
    environment = os.environ.get('ENVIRONMENT', 'development').lower()
    
    if environment == 'production':
        scheduler = setup_production_schedule()
        logger.info("🏭 Running in PRODUCTION mode")
    else:
        scheduler = setup_development_schedule()
        logger.info("🧪 Running in DEVELOPMENT mode")
    
    logger.info("🚀 Scheduler started - press Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        logger.info("🛑 Scheduler stopped by user")
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "run":
            # Run the scheduler
            run_scheduler()
            
        elif command == "test-daily":
            # Test daily maintenance
            scheduler = NarconScheduler()
            print("🧪 Testing daily maintenance...")
            scheduler.run_daily_maintenance()
            print("✅ Test complete")
            
        elif command == "test-sequence":
            # Test sequence processing
            scheduler = NarconScheduler()
            print("🧪 Testing sequence processing...")
            scheduler.run_sequence_processing()
            print("✅ Test complete")
            
        elif command == "health":
            # Run health check
            scheduler = NarconScheduler()
            scheduler.health_check()
            
        else:
            print("❌ Unknown command")
            print("Usage:")
            print("  python setup_daily_scheduler.py run           # Start the scheduler")
            print("  python setup_daily_scheduler.py test-daily   # Test daily maintenance")
            print("  python setup_daily_scheduler.py test-sequence # Test sequence processing")
            print("  python setup_daily_scheduler.py health       # Run health check")
    else:
        print("GFMD Narcon Daily Scheduler")
        print("===========================")
        print()
        print("This scheduler runs automated tasks for the Narcon campaign system:")
        print("• Daily maintenance (contact processing, reorder predictions)")
        print("• Sequence processing (follow-ups, decision making)")
        print("• Health monitoring")
        print()
        print("Usage:")
        print("  python setup_daily_scheduler.py run           # Start the scheduler")
        print("  python setup_daily_scheduler.py test-daily   # Test daily maintenance")
        print("  python setup_daily_scheduler.py test-sequence # Test sequence processing")
        print("  python setup_daily_scheduler.py health       # Run health check")
        print()
        print("Environment Variables:")
        print("  ENVIRONMENT=production                        # Set to 'production' for prod schedule")
        print("  MONGODB_CONNECTION_STRING=...                 # MongoDB connection")
        print("  GROQ_API_KEY=...                             # Groq API key")