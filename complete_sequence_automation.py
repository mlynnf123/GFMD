#!/usr/bin/env python3
"""
Complete Email Sequence Automation System
Ready-to-use email sequence automation with MongoDB, Gmail, and Groq AI
"""

import os
import asyncio
import schedule
import time
import threading
import random
from datetime import datetime, timedelta
from mongodb_storage import MongoDBStorage
from email_sequence_templates import EmailSequenceTemplates
from groq_email_composer_agent import GroqEmailComposerAgent
from gmail_integration import GmailIntegration
from business_day_utils import BusinessDayCalculator

# Load environment variables
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

class CompleteSequenceAutomation:
    """Complete email sequence automation system"""
    
    def __init__(self):
        print("🚀 Initializing Complete Email Sequence Automation...")
        
        self.storage = MongoDBStorage()
        self.templates = EmailSequenceTemplates()
        self.email_composer = GroqEmailComposerAgent(agent_id="automation_composer")
        self.gmail = GmailIntegration()
        self.business_day_calc = BusinessDayCalculator()
        
        # Initialize auto-reply system
        try:
            from ai_auto_reply_system import AIAutoReplySystem
            self.auto_reply_system = AIAutoReplySystem()
        except ImportError:
            self.auto_reply_system = None
            print("⚠️ Auto-reply system not available")
        
        print("✅ All components initialized successfully")
        print(f"📧 Gmail: {self.gmail.service is not None}")
        print(f"🗄️ MongoDB: Connected to {self.storage.db.name}")
        
    def add_contact_and_start_sequence(self, contact_data: dict) -> dict:
        """Add a contact and start email sequence"""
        try:
            # Add contact to database
            contact_id = self.storage.add_contact(contact_data)
            print(f"✅ Added contact: {contact_data.get('name')} -> {contact_id}")
            
            # Start sequence
            result = self.start_sequence_for_contact(str(contact_id))
            
            if result.get("success"):
                print(f"📧 Started sequence for {contact_data.get('email')}")
                return {"success": True, "contact_id": str(contact_id), "sequence_started": True}
            else:
                return {"success": False, "error": result.get("error")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def start_sequence_for_contact(self, contact_id: str) -> dict:
        """Start email sequence for existing contact"""
        try:
            # Get contact
            from bson import ObjectId
            contact = self.storage.contacts.find_one({"_id": ObjectId(contact_id)})
            if not contact:
                return {"success": False, "error": "Contact not found"}
            
            contact_email = contact.get("email", "")
            
            # Check if sequence already exists
            existing = self.storage.db.email_sequences.find_one({"contact_id": contact_id})
            if existing and existing.get("status") == "active":
                return {"success": False, "error": "Sequence already active"}
            
            # Create sequence state
            sequence_state = {
                'contact_id': contact_id,
                'contact_email': contact_email,
                'sequence_name': 'narc_gone_law_enforcement',
                'current_step': 0,
                'status': 'active',
                'emails_sent': [],
                'last_email_sent': None,
                'next_email_due': datetime.now().isoformat(),
                'reply_received': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Save to database
            result = self.storage.db.email_sequences.update_one(
                {"contact_id": contact_id},
                {"$set": sequence_state},
                upsert=True
            )
            
            return {"success": True, "contact_id": contact_id}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def process_due_sequences(self, send_emails: bool = True) -> dict:
        """Process all sequences that are due for next email"""
        try:
            now = datetime.now()
            
            # Find due sequences
            due_sequences = list(self.storage.db.email_sequences.find({
                "status": "active",
                "next_email_due": {"$lte": now.isoformat()}
            }))
            
            results = {"processed": 0, "sent": 0, "errors": 0, "details": []}
            
            # Process in smaller batches to avoid rate limits
            batch_size = 5  # Process 5 emails at a time
            for i in range(0, len(due_sequences), batch_size):
                batch = due_sequences[i:i + batch_size]
                
                for sequence in batch:
                    try:
                        result = await self._process_single_sequence(sequence, send_emails)
                        results["processed"] += 1
                        
                        if result.get("success"):
                            if result.get("action") == "sent":
                                results["sent"] += 1
                            elif result.get("action") == "completed":
                                print(f"✅ Completed sequence for {sequence.get('contact_email')}")
                        else:
                            results["errors"] += 1
                            print(f"❌ Error: {result.get('error')}")
                        
                        results["details"].append({
                            "contact_email": sequence.get("contact_email"),
                            "step": sequence.get("current_step", 0) + 1,
                            "result": result
                        })
                        
                        # Add delay between each email to respect rate limits
                        if send_emails:
                            await asyncio.sleep(12)  # 5 emails per minute max
                        
                    except Exception as e:
                        results["errors"] += 1
                        print(f"❌ Error processing sequence: {e}")
                        
                        # If rate limit error, wait longer
                        if "rate_limit" in str(e).lower():
                            print("⏳ Rate limit hit, waiting 60 seconds...")
                            await asyncio.sleep(60)
                
                # Pause between batches 
                if i + batch_size < len(due_sequences):
                    print(f"⏳ Processed batch {i//batch_size + 1}, waiting 30s before next batch...")
                    await asyncio.sleep(30)
            
            if results["processed"] > 0:
                print(f"📧 Processed {results['processed']} sequences, sent {results['sent']} emails")
            
            return results
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_single_sequence(self, sequence: dict, send_emails: bool = True) -> dict:
        """Process a single email sequence"""
        try:
            contact_id = sequence["contact_id"]
            current_step = sequence.get("current_step", 0)
            next_step = current_step + 1
            
            # Get email template
            template = self.templates.get_email_template("narc_gone_law_enforcement", next_step)
            if not template:
                # Sequence complete
                self.storage.db.email_sequences.update_one(
                    {"contact_id": contact_id},
                    {"$set": {"status": "completed", "updated_at": datetime.now().isoformat()}}
                )
                return {"success": True, "action": "completed"}
            
            # Get contact data
            from bson import ObjectId
            contact = self.storage.contacts.find_one({"_id": ObjectId(contact_id)})
            if not contact:
                return {"success": False, "error": "Contact not found"}
            
            # Generate email
            task = {
                "prospect_data": {
                    "contact_name": contact.get("name", ""),
                    "company_name": contact.get("organization", ""),
                    "location": contact.get("location", ""),
                    "title": contact.get("title", ""),
                    "email": contact.get("email", "")
                },
                "sequence_context": {
                    "step": template["step"],
                    "type": template["type"],
                    "focus": template["focus"],
                    "tone": template["tone"],
                    "call_to_action": template["call_to_action"],
                    "is_follow_up": template["step"] > 1,
                    "previous_emails_sent": len(sequence.get("emails_sent", []))
                }
            }
            
            email_result = await self.email_composer.execute(task)
            
            if not email_result.get("subject") or not email_result.get("body"):
                return {"success": False, "error": "Email generation failed"}
            
            # Send email if requested
            if send_emails and self.gmail.service:
                try:
                    send_result = self.gmail.send_email(
                        to_email=contact.get("email"),
                        subject=email_result.get("subject"),
                        body=email_result.get("body"),
                        html_body=email_result.get("html_body")
                    )
                    
                    if send_result.get("success"):
                        print(f"📧 Sent email {next_step} to {contact.get('email')}")
                        print(f"   Subject: {email_result.get('subject')}")
                    else:
                        return {"success": False, "error": f"Email sending failed: {send_result.get('error')}"}
                        
                except Exception as e:
                    return {"success": False, "error": f"Email sending error: {str(e)}"}
            else:
                print(f"📧 [DRY RUN] Would send email {next_step} to {contact.get('email')}")
                print(f"   Subject: {email_result.get('subject')}")
            
            # Update sequence state
            emails_sent = sequence.get("emails_sent", [])
            emails_sent.append({
                "step": next_step,
                "sent_at": datetime.now().isoformat(),
                "subject": email_result.get("subject"),
                "template_type": template.get("type"),
                "actually_sent": send_emails and self.gmail.service is not None
            })
            
            # Calculate next email due date using business days
            next_template = self.templates.get_email_template("narc_gone_law_enforcement", next_step + 1)
            if next_template:
                wait_business_days = next_template.get("wait_days", 2)
                next_due = self.business_day_calc.add_business_days(datetime.now(), wait_business_days)
                # Ensure it's during good email hours (9 AM - 6 PM)
                next_email_due = self.business_day_calc.get_next_good_email_time(next_due).isoformat()
            else:
                next_email_due = None
            
            # Update database
            self.storage.db.email_sequences.update_one(
                {"contact_id": contact_id},
                {"$set": {
                    "current_step": next_step,
                    "last_email_sent": datetime.now().isoformat(),
                    "emails_sent": emails_sent,
                    "next_email_due": next_email_due,
                    "updated_at": datetime.now().isoformat()
                }}
            )
            
            return {"success": True, "action": "sent", "step": next_step}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def add_daily_new_contacts(self, count: int = 10) -> dict:
        """Add new contacts daily from available contact pool"""
        try:
            print(f"\n📊 Adding {count} new contacts to sequences...")
            
            # Find contacts that don't have active sequences
            active_sequences = list(self.storage.db.email_sequences.find(
                {"status": {"$in": ["active", "completed"]}},
                {"contact_id": 1}
            ))
            
            # Convert to ObjectIds for query
            from bson import ObjectId
            active_contact_ids = []
            for seq in active_sequences:
                try:
                    if isinstance(seq["contact_id"], str):
                        active_contact_ids.append(ObjectId(seq["contact_id"]))
                    else:
                        active_contact_ids.append(seq["contact_id"])
                except:
                    pass
            
            # Find contacts without sequences
            query_filter = {"_id": {"$nin": active_contact_ids}} if active_contact_ids else {}
            available_contacts = list(self.storage.contacts.find(query_filter).limit(count))
            
            if not available_contacts:
                print("📭 No new contacts available to add to sequences")
                return {"success": True, "added": 0, "message": "No available contacts"}
            
            added_count = 0
            results = []
            
            # Add up to requested count
            for contact in available_contacts[:count]:
                try:
                    contact_id = str(contact["_id"])
                    result = self.start_sequence_for_contact(contact_id)
                    
                    if result.get("success"):
                        added_count += 1
                        print(f"✅ Started sequence for {contact.get('email', 'unknown')}")
                        results.append({
                            "contact_id": contact_id,
                            "email": contact.get("email"),
                            "success": True
                        })
                    else:
                        print(f"❌ Failed to start sequence for {contact.get('email', 'unknown')}: {result.get('error')}")
                        results.append({
                            "contact_id": contact_id,
                            "email": contact.get("email"),
                            "success": False,
                            "error": result.get("error")
                        })
                        
                except Exception as e:
                    print(f"❌ Error processing contact {contact.get('email', 'unknown')}: {e}")
            
            print(f"📈 Added {added_count} new contacts to sequences")
            
            return {
                "success": True,
                "added": added_count,
                "total_requested": count,
                "available_contacts": len(available_contacts),
                "results": results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_sequence_stats(self) -> dict:
        """Get comprehensive sequence statistics"""
        try:
            total = self.storage.db.email_sequences.count_documents({})
            active = self.storage.db.email_sequences.count_documents({"status": "active"})
            completed = self.storage.db.email_sequences.count_documents({"status": "completed"})
            replied = self.storage.db.email_sequences.count_documents({"status": "replied"})
            
            # Get step distribution
            pipeline = [
                {"$match": {"status": "active"}},
                {"$group": {"_id": "$current_step", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ]
            step_distribution = list(self.storage.db.email_sequences.aggregate(pipeline))
            
            return {
                "success": True,
                "total_sequences": total,
                "active": active,
                "completed": completed,
                "replied": replied,
                "response_rate": round((replied / total * 100) if total > 0 else 0, 2),
                "step_distribution": step_distribution,
                "gmail_connected": self.gmail.service is not None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def start_background_scheduler(self):
        """Start background processing every hour and daily contact addition"""
        def run_scheduler():
            # Schedule processing every hour
            schedule.every().hour.do(self._scheduled_processing)
            
            # Schedule at specific times for better control (adjusted for CST = UTC-6)
            schedule.every().day.at("15:00").do(self._scheduled_processing)  # 9 AM CST
            schedule.every().day.at("19:00").do(self._scheduled_processing)  # 1 PM CST
            schedule.every().day.at("23:00").do(self._scheduled_processing)  # 5 PM CST
            
            # Schedule daily contact addition (every business day at 8 AM CST = 14:00 UTC)
            schedule.every().monday.at("14:00").do(self._add_daily_contacts)
            schedule.every().tuesday.at("14:00").do(self._add_daily_contacts)
            schedule.every().wednesday.at("14:00").do(self._add_daily_contacts)
            schedule.every().thursday.at("14:00").do(self._add_daily_contacts)
            schedule.every().friday.at("14:00").do(self._add_daily_contacts)
            
            # Add auto-reply monitoring every 2 hours 
            schedule.every(2).hours.do(self._check_auto_replies)
            
            print("⏰ Background scheduler started")
            print("   - Processing every hour")
            print("   - Special runs at 9 AM, 1 PM, 5 PM CST") 
            print("   - Daily contact addition: Monday-Friday at 8 AM CST (10 new contacts)")
            print("   - Auto-reply monitoring: Every 2 hours")
            print("   - Email timing: Every 2 business days")
            
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        # Run scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def _scheduled_processing(self):
        """Scheduled processing function"""
        print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')} - Running scheduled sequence processing...")
        
        # Run async processing in sync context
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.process_due_sequences(send_emails=True))
            loop.close()
            
            if result.get("sent", 0) > 0:
                print(f"📧 Scheduled run: Sent {result['sent']} emails")
            else:
                print("📧 Scheduled run: No emails due")
                
        except Exception as e:
            print(f"❌ Scheduled processing error: {e}")
    
    def _add_daily_contacts(self):
        """Scheduled daily contact addition function"""
        print(f"\n🌅 {datetime.now().strftime('%Y-%m-%d %H:%M')} - Running daily contact addition...")
        
        # Run async contact addition in sync context
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.add_daily_new_contacts(count=10))
            loop.close()
            
            if result.get("added", 0) > 0:
                print(f"📈 Daily run: Added {result['added']} new contacts to sequences")
            else:
                print("📭 Daily run: No new contacts added")
                
        except Exception as e:
            print(f"❌ Daily contact addition error: {e}")
    
    def _check_auto_replies(self):
        """Scheduled auto-reply checking function"""
        print(f"\n🤖 {datetime.now().strftime('%Y-%m-%d %H:%M')} - Checking for email replies...")
        
        if self.auto_reply_system:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(self.auto_reply_system.run_single_check())
                loop.close()
                
                if results:
                    print(f"✅ Auto-reply run: Sent {len(results)} intelligent replies")
                else:
                    print("📭 Auto-reply run: No new replies to process")
                    
            except Exception as e:
                print(f"❌ Auto-reply check error: {e}")
        else:
            print("⚠️ Auto-reply system not available")

async def main():
    """Main function for testing and running"""
    import sys
    
    automation = CompleteSequenceAutomation()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "add" and len(sys.argv) >= 6:
            # Add contact and start sequence
            contact = {
                "name": sys.argv[2],
                "email": sys.argv[3], 
                "organization": sys.argv[4],
                "title": sys.argv[5],
                "location": sys.argv[6] if len(sys.argv) > 6 else ""
            }
            result = automation.add_contact_and_start_sequence(contact)
            print(f"Add contact result: {result}")
            
        elif command == "process":
            # Process due sequences
            send = len(sys.argv) > 2 and sys.argv[2] == "send"
            result = await automation.process_due_sequences(send_emails=send)
            print(f"Process result: {result}")
            
        elif command == "stats":
            # Get statistics
            stats = automation.get_sequence_stats()
            print(f"Stats: {stats}")
            
        elif command == "add_contacts":
            # Add daily contacts manually
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            result = await automation.add_daily_new_contacts(count)
            print(f"Add contacts result: {result}")
            
        elif command == "schedule":
            # Start background scheduler
            automation.start_background_scheduler()
            print("🔄 Background scheduler running. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n⏹️ Scheduler stopped")
                
        elif command == "demo":
            # Demo with test contacts
            test_contacts = [
                {
                    "name": "Chief Sarah Johnson",
                    "email": "chief.johnson@testpd.gov",
                    "organization": "Test City Police Department", 
                    "title": "Chief of Police",
                    "location": "Test City, TX"
                },
                {
                    "name": "Sheriff Mike Rodriguez",
                    "email": "sheriff.rodriguez@testcounty.gov",
                    "organization": "Test County Sheriff's Office",
                    "title": "Sheriff", 
                    "location": "Test County, TX"
                }
            ]
            
            for contact in test_contacts:
                result = automation.add_contact_and_start_sequence(contact)
                print(f"Added: {contact['name']} -> {result.get('success')}")
            
            # Show stats
            stats = automation.get_sequence_stats()
            print(f"\nDemo stats: {stats}")
            
        else:
            print("Usage:")
            print("  python3 complete_sequence_automation.py add 'Name' 'email@domain.com' 'Organization' 'Title' 'Location'")
            print("  python3 complete_sequence_automation.py process [send]")
            print("  python3 complete_sequence_automation.py stats")
            print("  python3 complete_sequence_automation.py add_contacts [count]  # Default: 20")
            print("  python3 complete_sequence_automation.py schedule")
            print("  python3 complete_sequence_automation.py demo")
    else:
        # Default: show stats and process
        stats = automation.get_sequence_stats()
        print(f"Current stats: {stats}")
        
        result = await automation.process_due_sequences(send_emails=False)
        print(f"Process result (dry run): {result}")

if __name__ == "__main__":
    asyncio.run(main())