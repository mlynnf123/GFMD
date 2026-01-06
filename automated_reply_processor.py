#!/usr/bin/env python3
"""
Automated Email Reply Processor for GFMD
Runs periodically to check for email replies and process suppressions automatically.
"""

import os
import sys
import time
import logging
import schedule
from datetime import datetime, timedelta
from email_reply_monitor import EmailReplyMonitor
from suppression_integration import SuppressionManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_reply_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedReplyProcessor:
    """Automated processor for handling email replies and suppressions"""
    
    def __init__(self):
        """Initialize the automated processor"""
        try:
            self.reply_monitor = EmailReplyMonitor()
            self.suppression_manager = SuppressionManager()
            self.last_run = None
            logger.info("🤖 Automated Reply Processor initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize processor: {e}")
            raise
    
    def process_recent_replies(self):
        """Process replies from the last check period"""
        try:
            start_time = datetime.utcnow()
            logger.info("🔍 Starting automated reply processing...")
            
            # Determine how far back to check
            if self.last_run:
                # Check since last run, plus 10 minutes buffer
                hours_since_last = (start_time - self.last_run).total_seconds() / 3600
                days_back = max(0.1, hours_since_last / 24)  # At least 0.1 days (2.4 hours)
            else:
                # First run - check last 24 hours
                days_back = 1
            
            logger.info(f"📧 Checking replies from last {days_back:.1f} days")
            
            # Process Gmail replies
            stats = self.reply_monitor.process_gmail_replies(days_back=days_back)
            
            # Log results
            logger.info(f"✅ Reply processing complete:")
            logger.info(f"   - Replies checked: {stats['replies_checked']}")
            logger.info(f"   - New suppressions: {stats['suppressions_added']}")
            logger.info(f"   - Bounces detected: {stats['bounces_detected']}")
            logger.info(f"   - Complaints detected: {stats['complaints_detected']}")
            
            # Update last run time
            self.last_run = start_time
            
            # Store processing stats
            processing_record = {
                'processed_at': start_time,
                'period_checked_days': days_back,
                'stats': stats,
                'processing_time_seconds': (datetime.utcnow() - start_time).total_seconds()
            }
            
            self.suppression_manager.storage.db.reply_processing_log.insert_one(processing_record)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error processing replies: {e}")
            return {'error': str(e)}
    
    def daily_suppression_report(self):
        """Generate and log daily suppression report"""
        try:
            logger.info("📊 Generating daily suppression report...")
            
            report = self.suppression_manager.get_suppression_report(days=1)
            
            logger.info("📋 Daily Suppression Summary:")
            logger.info(f"   - New suppressions today: {report.get('recent_suppressions', 0)}")
            logger.info(f"   - Total active suppressions: {report.get('total_active_suppressions', 0)}")
            logger.info(f"   - Bounces today: {report.get('recent_bounces', 0)}")
            logger.info(f"   - Blocked sends today: {report.get('blocked_sends', 0)}")
            
            # Log suppression reasons
            reasons = report.get('suppression_reasons', {})
            if reasons:
                logger.info("   - Suppression reasons:")
                for reason, count in reasons.items():
                    logger.info(f"     * {reason}: {count}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating daily report: {e}")
            return {}
    
    def weekly_maintenance(self):
        """Perform weekly maintenance tasks"""
        try:
            logger.info("🔧 Running weekly suppression maintenance...")
            
            # Clean up old processing logs (keep last 30 days)
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            deleted_logs = self.suppression_manager.storage.db.reply_processing_log.delete_many({
                'processed_at': {'$lt': cutoff_date}
            })
            
            deleted_blocks = self.suppression_manager.storage.db.email_blocks.delete_many({
                'blocked_at': {'$lt': cutoff_date}
            })
            
            # Generate weekly report
            weekly_report = self.suppression_manager.get_suppression_report(days=7)
            
            logger.info("✅ Weekly maintenance complete:")
            logger.info(f"   - Cleaned up {deleted_logs.deleted_count} old processing logs")
            logger.info(f"   - Cleaned up {deleted_blocks.deleted_count} old block records")
            logger.info(f"   - Weekly suppressions: {weekly_report.get('recent_suppressions', 0)}")
            logger.info(f"   - Weekly bounces: {weekly_report.get('recent_bounces', 0)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in weekly maintenance: {e}")
            return False
    
    def run_manual_check(self):
        """Run manual reply check for immediate processing"""
        print("🔍 Running manual reply check...")
        stats = self.process_recent_replies()
        
        if 'error' not in stats:
            print("✅ Manual check complete:")
            print(f"   - Replies checked: {stats['replies_checked']}")
            print(f"   - New suppressions: {stats['suppressions_added']}")
            print(f"   - Bounces detected: {stats['bounces_detected']}")
            print(f"   - Complaints detected: {stats['complaints_detected']}")
        else:
            print(f"❌ Manual check failed: {stats['error']}")
        
        return stats

def setup_schedule():
    """Set up the automated schedule for reply processing"""
    processor = AutomatedReplyProcessor()
    
    # Schedule reply processing every 2 hours during business hours
    schedule.every(2).hours.do(processor.process_recent_replies)
    
    # Daily suppression report at 9 AM
    schedule.every().day.at("09:00").do(processor.daily_suppression_report)
    
    # Weekly maintenance on Sundays at 2 AM
    schedule.every().sunday.at("02:00").do(processor.weekly_maintenance)
    
    logger.info("⏰ Automated reply processing schedule configured:")
    logger.info("   - Reply checks: Every 2 hours")
    logger.info("   - Daily reports: 9:00 AM")
    logger.info("   - Weekly maintenance: Sundays 2:00 AM")
    
    return processor

def run_scheduler():
    """Run the automated scheduler continuously"""
    print("🤖 Starting GFMD Automated Reply Processor")
    print("=" * 50)
    
    try:
        processor = setup_schedule()
        
        print("✅ Scheduler started successfully")
        print("📧 Monitoring for email replies and managing suppressions...")
        print("💤 Press Ctrl+C to stop")
        
        # Run initial check
        print("\n🔄 Running initial reply check...")
        processor.process_recent_replies()
        
        # Start the scheduler loop
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for scheduled tasks
            
    except KeyboardInterrupt:
        print("\n⏹️ Scheduler stopped by user")
        logger.info("Automated reply processor stopped by user")
    except Exception as e:
        print(f"\n❌ Scheduler error: {e}")
        logger.error(f"Scheduler error: {e}")

def main():
    """Main function with command options"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "run":
            # Run the continuous scheduler
            run_scheduler()
            
        elif command == "check":
            # Run manual reply check
            processor = AutomatedReplyProcessor()
            processor.run_manual_check()
            
        elif command == "report":
            # Generate suppression report
            processor = AutomatedReplyProcessor()
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            report = processor.suppression_manager.get_suppression_report(days)
            
            print(f"📊 Suppression Report (Last {days} days)")
            print("=" * 50)
            print(f"Recent suppressions: {report.get('recent_suppressions', 0)}")
            print(f"Total active suppressions: {report.get('total_active_suppressions', 0)}")
            print(f"Recent bounces: {report.get('recent_bounces', 0)}")
            print(f"Blocked sends: {report.get('blocked_sends', 0)}")
            
            reasons = report.get('suppression_reasons', {})
            if reasons:
                print("\nSuppression reasons:")
                for reason, count in reasons.items():
                    print(f"  - {reason}: {count}")
                    
        elif command == "setup":
            # Setup the suppression system
            from setup_suppression_system import main as setup_main
            setup_main()
            
        else:
            print("❌ Unknown command. Available commands:")
            print("  run    - Start automated reply processor")
            print("  check  - Run manual reply check")
            print("  report [days] - Generate suppression report")
            print("  setup  - Setup suppression system database")
    else:
        print("🤖 GFMD Automated Reply Processor")
        print("=" * 40)
        print("Usage:")
        print("  python3 automated_reply_processor.py run")
        print("  python3 automated_reply_processor.py check")
        print("  python3 automated_reply_processor.py report [days]")
        print("  python3 automated_reply_processor.py setup")

if __name__ == "__main__":
    main()