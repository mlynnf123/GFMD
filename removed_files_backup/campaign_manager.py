#!/usr/bin/env python3
"""
Campaign Manager for GFMD Narcon System
High-level campaign management and batch processing
"""

import asyncio
import csv
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

from mongodb_storage import MongoDBStorage
from email_sequence_orchestrator import EmailSequenceOrchestrator
from gmail_integration import GmailIntegration

logger = logging.getLogger(__name__)

class NarconCampaignManager:
    """Manages Narcon outreach campaigns from start to finish"""
    
    def __init__(self):
        """Initialize campaign manager"""
        try:
            self.storage = MongoDBStorage()
            self.orchestrator = EmailSequenceOrchestrator()
            self.gmail = GmailIntegration()
            
            logger.info("✅ Narcon Campaign Manager initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize campaign manager: {e}")
            raise
    
    async def import_contacts_from_csv(self, csv_file_path: str, campaign_name: str) -> Dict[str, Any]:
        """Import contacts from CSV and start qualification process"""
        try:
            logger.info(f"📥 Importing contacts from {csv_file_path}")
            
            # Create campaign record
            campaign_id = self.storage.create_campaign({
                "name": campaign_name,
                "status": "active",
                "targetSegment": {
                    "organizationType": ["police", "sheriff", "federal"],
                    "focus": "narcon_drug_destruction"
                },
                "channels": ["email"]
            })
            
            results = {
                "campaign_id": campaign_id,
                "total_contacts": 0,
                "processed_contacts": 0,
                "qualified_contacts": 0,
                "emails_sent": 0,
                "errors": []
            }
            
            # Read CSV file
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                contacts = list(csv_reader)
                results["total_contacts"] = len(contacts)
                
                logger.info(f"📊 Found {len(contacts)} contacts to process")
                
                # Process contacts in batches to avoid overwhelming APIs
                batch_size = 10
                for i in range(0, len(contacts), batch_size):
                    batch = contacts[i:i + batch_size]
                    
                    logger.info(f"🔄 Processing batch {i//batch_size + 1}/{(len(contacts)-1)//batch_size + 1}")
                    
                    batch_tasks = []
                    for contact_row in batch:
                        # Clean and format contact data
                        contact_data = self._clean_contact_data(contact_row)
                        if contact_data:
                            task = self.orchestrator.process_new_contact(contact_data)
                            batch_tasks.append(task)
                    
                    # Process batch concurrently
                    batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                    
                    # Analyze batch results
                    for result in batch_results:
                        if isinstance(result, Exception):
                            results["errors"].append(str(result))
                        elif isinstance(result, dict) and result.get("success"):
                            results["processed_contacts"] += 1
                            if result.get("qualification_score", 0) >= 60:
                                results["qualified_contacts"] += 1
                            if result.get("email_sent"):
                                results["emails_sent"] += 1
                        else:
                            results["errors"].append(f"Processing failed: {result}")
                    
                    # Brief pause between batches to be respectful to APIs
                    await asyncio.sleep(2)
                
                logger.info(f"✅ Contact import complete: {results['emails_sent']} emails sent")
                return {"success": True, **results}
                
        except Exception as e:
            logger.error(f"❌ Failed to import contacts: {e}")
            return {"success": False, "error": str(e)}
    
    def _clean_contact_data(self, contact_row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Clean and validate contact data from CSV"""
        try:
            # Handle different CSV column naming conventions
            possible_email_fields = ["email", "Email", "EMAIL", "email_address", "EmailAddress"]
            possible_name_fields = ["name", "Name", "full_name", "contact_name", "ContactName"]
            possible_title_fields = ["title", "Title", "job_title", "JobTitle", "position", "Position"]
            possible_org_fields = ["organization", "Organization", "company", "Company", "agency", "Agency"]
            possible_city_fields = ["city", "City", "location", "Location"]
            possible_state_fields = ["state", "State", "st", "ST"]
            
            # Extract email (required)
            email = None
            for field in possible_email_fields:
                if field in contact_row and contact_row[field]:
                    email = contact_row[field].strip()
                    break
            
            if not email or "@" not in email:
                return None
            
            # Extract name and split if needed
            full_name = None
            for field in possible_name_fields:
                if field in contact_row and contact_row[field]:
                    full_name = contact_row[field].strip()
                    break
            
            first_name, last_name = "", ""
            if full_name:
                name_parts = full_name.split()
                first_name = name_parts[0] if name_parts else ""
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            # Extract other fields
            title = ""
            for field in possible_title_fields:
                if field in contact_row and contact_row[field]:
                    title = contact_row[field].strip()
                    break
            
            organization = ""
            for field in possible_org_fields:
                if field in contact_row and contact_row[field]:
                    organization = contact_row[field].strip()
                    break
            
            city = ""
            for field in possible_city_fields:
                if field in contact_row and contact_row[field]:
                    city = contact_row[field].strip()
                    break
            
            state = ""
            for field in possible_state_fields:
                if field in contact_row and contact_row[field]:
                    state = contact_row[field].strip()
                    break
            
            return {
                "email": email.lower(),
                "firstName": first_name,
                "lastName": last_name,
                "title": title,
                "organization": organization,
                "city": city,
                "state": state,
                "source": "csv_import"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to clean contact data: {e}")
            return None
    
    async def run_daily_campaign_maintenance(self) -> Dict[str, Any]:
        """Run daily campaign maintenance tasks"""
        try:
            logger.info("🔄 Starting daily campaign maintenance")
            
            results = {
                "timestamp": datetime.utcnow().isoformat(),
                "tasks_completed": [],
                "statistics": {},
                "errors": []
            }
            
            # Task 1: Process email sequences
            try:
                sequence_results = await self.orchestrator.process_sequence_decisions(limit=100)
                results["tasks_completed"].append("sequence_processing")
                results["statistics"]["sequence_processing"] = sequence_results
            except Exception as e:
                results["errors"].append(f"Sequence processing failed: {e}")
            
            # Task 2: Handle reorder predictions
            try:
                reorder_results = await self.orchestrator.process_reorder_predictions()
                results["tasks_completed"].append("reorder_predictions")
                results["statistics"]["reorder_predictions"] = reorder_results
            except Exception as e:
                results["errors"].append(f"Reorder predictions failed: {e}")
            
            # Task 3: Check for email replies
            try:
                reply_results = await self.check_for_email_replies()
                results["tasks_completed"].append("reply_processing")
                results["statistics"]["reply_processing"] = reply_results
            except Exception as e:
                results["errors"].append(f"Reply processing failed: {e}")
            
            # Task 4: Generate daily report
            try:
                report = await self.generate_campaign_report()
                results["tasks_completed"].append("daily_report")
                results["statistics"]["campaign_metrics"] = report
            except Exception as e:
                results["errors"].append(f"Report generation failed: {e}")
            
            logger.info("✅ Daily campaign maintenance complete")
            return {"success": True, **results}
            
        except Exception as e:
            logger.error(f"❌ Daily maintenance failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_for_email_replies(self) -> Dict[str, Any]:
        """Check for email replies and update contact status"""
        try:
            logger.info("📧 Checking for email replies")
            
            # Get replies from last 7 days
            since_date = (datetime.now() - timedelta(days=7)).strftime("%Y/%m/%d")
            replies = self.gmail.check_for_replies(since_date=since_date, max_results=100)
            
            results = {
                "total_replies": len(replies),
                "processed_replies": 0,
                "interested_leads": 0,
                "errors": []
            }
            
            for reply in replies:
                try:
                    # Extract sender email
                    from_email = reply.get("from", "")
                    if "<" in from_email and ">" in from_email:
                        # Extract email from "Name <email@domain.com>" format
                        from_email = from_email.split("<")[1].split(">")[0].strip()
                    
                    reply_body = reply.get("body", "").lower()
                    
                    # Check if this is an interested reply
                    interested_keywords = [
                        "interested", "tell me more", "pricing", "cost", "demo", 
                        "meeting", "call", "schedule", "budget", "proposal",
                        "yes", "sounds good", "more information"
                    ]
                    
                    unsubscribe_keywords = [
                        "unsubscribe", "remove", "stop", "not interested", 
                        "no thank", "don't contact", "opt out"
                    ]
                    
                    is_interested = any(keyword in reply_body for keyword in interested_keywords)
                    is_unsubscribe = any(keyword in reply_body for keyword in unsubscribe_keywords)
                    
                    # Update contact based on reply type
                    if is_unsubscribe:
                        self.storage.update_contact(from_email, {
                            "status": "unsubscribed",
                            "unsubscribeDate": datetime.utcnow(),
                            "lastReplyDate": datetime.utcnow()
                        })
                    elif is_interested:
                        self.storage.update_contact(from_email, {
                            "status": "interested",
                            "lastReplyDate": datetime.utcnow(),
                            "lastReplyText": reply.get("body", "")
                        })
                        results["interested_leads"] += 1
                    else:
                        self.storage.update_contact(from_email, {
                            "status": "replied",
                            "lastReplyDate": datetime.utcnow(),
                            "lastReplyText": reply.get("body", "")
                        })
                    
                    # Record the reply interaction
                    original_tracking_id = reply.get("original_tracking_id")
                    if original_tracking_id:
                        self.storage.record_email_reply(original_tracking_id, reply.get("body", ""))
                    
                    results["processed_replies"] += 1
                    
                except Exception as e:
                    error_msg = f"Failed to process reply from {reply.get('from', 'unknown')}: {e}"
                    results["errors"].append(error_msg)
                    logger.error(f"❌ {error_msg}")
            
            logger.info(f"✅ Reply processing complete: {results['interested_leads']} interested leads")
            return {"success": True, **results}
            
        except Exception as e:
            logger.error(f"❌ Failed to check replies: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_campaign_report(self) -> Dict[str, Any]:
        """Generate campaign performance report"""
        try:
            logger.info("📊 Generating campaign report")
            
            # Get overall statistics from MongoDB
            total_contacts = self.storage.contacts.count_documents({})
            qualified_contacts = self.storage.contacts.count_documents({"qualificationScore": {"$gte": 60}})
            active_campaigns = self.storage.campaigns.count_documents({"status": "active"})
            
            # Get email statistics
            email_stats = list(self.storage.interactions.aggregate([
                {"$group": {
                    "_id": None,
                    "totalEmailsSent": {"$sum": {"$cond": [{"$eq": ["$type", "email_sent"]}, 1, 0]}},
                    "totalEmailsOpened": {"$sum": {"$cond": [{"$ne": ["$openedAt", None]}, 1, 0]}},
                    "totalEmailsClicked": {"$sum": {"$cond": [{"$ne": ["$clickedLinks", []]}, 1, 0]}},
                    "totalReplies": {"$sum": {"$cond": [{"$ne": ["$repliedAt", None]}, 1, 0]}}
                }}
            ]))
            
            email_metrics = email_stats[0] if email_stats else {
                "totalEmailsSent": 0, "totalEmailsOpened": 0, 
                "totalEmailsClicked": 0, "totalReplies": 0
            }
            
            # Calculate rates
            emails_sent = email_metrics["totalEmailsSent"]
            open_rate = (email_metrics["totalEmailsOpened"] / emails_sent * 100) if emails_sent > 0 else 0
            click_rate = (email_metrics["totalEmailsClicked"] / emails_sent * 100) if emails_sent > 0 else 0
            reply_rate = (email_metrics["totalReplies"] / emails_sent * 100) if emails_sent > 0 else 0
            
            # Get contact status breakdown
            status_breakdown = list(self.storage.contacts.aggregate([
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]))
            
            # Get recent activity (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_activity = {
                "contacts_added": self.storage.contacts.count_documents({"createdAt": {"$gte": week_ago}}),
                "emails_sent": self.storage.interactions.count_documents({
                    "type": "email_sent", 
                    "timestamp": {"$gte": week_ago}
                }),
                "emails_opened": self.storage.interactions.count_documents({
                    "openedAt": {"$gte": week_ago}
                }),
                "replies_received": self.storage.interactions.count_documents({
                    "repliedAt": {"$gte": week_ago}
                })
            }
            
            report = {
                "report_date": datetime.utcnow().isoformat(),
                "overall_stats": {
                    "total_contacts": total_contacts,
                    "qualified_contacts": qualified_contacts,
                    "active_campaigns": active_campaigns
                },
                "email_performance": {
                    "emails_sent": emails_sent,
                    "emails_opened": email_metrics["totalEmailsOpened"],
                    "emails_clicked": email_metrics["totalEmailsClicked"],
                    "replies_received": email_metrics["totalReplies"],
                    "open_rate": round(open_rate, 2),
                    "click_rate": round(click_rate, 2),
                    "reply_rate": round(reply_rate, 2)
                },
                "contact_status_breakdown": {item["_id"]: item["count"] for item in status_breakdown},
                "recent_activity_7_days": recent_activity
            }
            
            logger.info("✅ Campaign report generated")
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate report: {e}")
            return {"error": str(e)}


# CLI interface
if __name__ == "__main__":
    import sys
    
    async def main():
        campaign_manager = NarconCampaignManager()
        
        if len(sys.argv) > 2 and sys.argv[1] == "import":
            # Import contacts from CSV
            csv_file = sys.argv[2]
            campaign_name = sys.argv[3] if len(sys.argv) > 3 else f"Campaign_{datetime.now().strftime('%Y%m%d')}"
            
            result = await campaign_manager.import_contacts_from_csv(csv_file, campaign_name)
            print("Contact Import Result:")
            print(json.dumps(result, indent=2))
            
        elif len(sys.argv) > 1 and sys.argv[1] == "daily":
            # Run daily maintenance
            result = await campaign_manager.run_daily_campaign_maintenance()
            print("Daily Maintenance Result:")
            print(json.dumps(result, indent=2))
            
        elif len(sys.argv) > 1 and sys.argv[1] == "report":
            # Generate report
            report = await campaign_manager.generate_campaign_report()
            print("Campaign Report:")
            print(json.dumps(report, indent=2))
            
        else:
            print("GFMD Narcon Campaign Manager")
            print("Usage:")
            print("  python campaign_manager.py import <csv_file> [campaign_name]  # Import contacts")
            print("  python campaign_manager.py daily                             # Run daily tasks")
            print("  python campaign_manager.py report                            # Generate report")
    
    asyncio.run(main())