#!/usr/bin/env python3
"""
GFMD Email System Overview
Comprehensive overview of the email automation system, database contents, and recent activity
"""

import os
import sys
from datetime import datetime, timedelta
from mongodb_storage import MongoDBStorage
from gmail_integration import GmailIntegration

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

def print_header(title):
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}")

def print_subheader(title):
    print(f"\n{'-'*60}")
    print(f"{title}")
    print(f"{'-'*60}")

def get_system_overview():
    """Get comprehensive system overview"""
    try:
        storage = MongoDBStorage()
        gmail = GmailIntegration()
        
        print_header("GFMD EMAIL AUTOMATION SYSTEM OVERVIEW")
        
        # System Status
        print_subheader("SYSTEM STATUS")
        print(f"✅ MongoDB Connection: Connected to '{storage.db.name}'")
        print(f"✅ Gmail Integration: {'Connected' if gmail.service else 'Not Connected'}")
        
        # Database Collections Overview
        print_subheader("DATABASE COLLECTIONS")
        collections = storage.db.list_collection_names()
        for collection_name in collections:
            count = storage.db[collection_name].count_documents({})
            print(f"📁 {collection_name}: {count} records")
        
        # Contact Statistics
        print_subheader("CONTACT STATISTICS")
        total_contacts = storage.contacts.count_documents({})
        print(f"Total Contacts: {total_contacts}")
        
        # Contact status breakdown
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        status_stats = list(storage.contacts.aggregate(status_pipeline))
        for stat in status_stats:
            status = stat['_id'] or 'Unknown'
            count = stat['count']
            print(f"  - {status}: {count}")
        
        # Organization type breakdown
        org_pipeline = [
            {"$group": {"_id": "$organizationType", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        org_stats = list(storage.contacts.aggregate(org_pipeline))
        print("\nOrganization Types:")
        for stat in org_stats:
            org_type = stat['_id'] or 'Unknown'
            count = stat['count']
            print(f"  - {org_type}: {count}")
        
        # Email Sequence Statistics
        print_subheader("EMAIL SEQUENCE STATUS")
        total_sequences = storage.db.email_sequences.count_documents({})
        active_sequences = storage.db.email_sequences.count_documents({"status": "active"})
        completed_sequences = storage.db.email_sequences.count_documents({"status": "completed"})
        replied_sequences = storage.db.email_sequences.count_documents({"status": "replied"})
        
        print(f"Total Sequences: {total_sequences}")
        print(f"Active Sequences: {active_sequences}")
        print(f"Completed Sequences: {completed_sequences}")
        print(f"Replied Sequences: {replied_sequences}")
        
        # Step distribution for active sequences
        step_pipeline = [
            {"$match": {"status": "active"}},
            {"$group": {"_id": "$current_step", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        step_stats = list(storage.db.email_sequences.aggregate(step_pipeline))
        print("\nStep Distribution (Active Sequences):")
        for stat in step_stats:
            step = stat['_id']
            count = stat['count']
            print(f"  - Step {step}: {count} contacts")
        
        # Email Interaction Statistics
        print_subheader("EMAIL INTERACTION STATISTICS")
        total_emails = storage.interactions.count_documents({"type": "email_sent"})
        print(f"Total Emails Sent: {total_emails}")
        
        # Recent activity (last 30 days)
        since_30_days = datetime.utcnow() - timedelta(days=30)
        emails_30_days = storage.interactions.count_documents({
            "type": "email_sent",
            "timestamp": {"$gte": since_30_days}
        })
        print(f"Emails Sent (Last 30 Days): {emails_30_days}")
        
        # Email tracking stats
        opens = storage.interactions.count_documents({
            "type": "email_sent",
            "openedAt": {"$exists": True}
        })
        clicks = storage.interactions.count_documents({
            "type": "email_sent", 
            "clickedLinks": {"$exists": True, "$ne": []}
        })
        replies = storage.interactions.count_documents({
            "type": "email_sent",
            "repliedAt": {"$exists": True}
        })
        
        print(f"Email Opens: {opens}")
        print(f"Email Clicks: {clicks}")
        print(f"Email Replies: {replies}")
        
        # Calculate engagement rates
        if total_emails > 0:
            open_rate = (opens / total_emails) * 100
            click_rate = (clicks / total_emails) * 100
            reply_rate = (replies / total_emails) * 100
            
            print(f"\nEngagement Rates:")
            print(f"  - Open Rate: {open_rate:.1f}%")
            print(f"  - Click Rate: {click_rate:.1f}%")
            print(f"  - Reply Rate: {reply_rate:.1f}%")
        
        # Recent Email Activity
        print_subheader("RECENT EMAIL ACTIVITY (Last 24 Hours)")
        since_24h = datetime.utcnow() - timedelta(hours=24)
        
        recent_sequences = list(storage.db.email_sequences.find({
            "updated_at": {"$gte": since_24h.isoformat()}
        }).sort("updated_at", -1).limit(10))
        
        if recent_sequences:
            for i, seq in enumerate(recent_sequences, 1):
                contact_email = seq.get('contact_email', 'Unknown')
                current_step = seq.get('current_step', 0)
                emails_sent_count = len(seq.get('emails_sent', []))
                last_updated = seq.get('updated_at', 'Unknown')
                
                print(f"{i:2d}. {contact_email}")
                print(f"    Step: {current_step} | Emails: {emails_sent_count} | Updated: {last_updated}")
        else:
            print("No email activity in the last 24 hours")
        
        # Upcoming Due Sequences
        print_subheader("UPCOMING DUE SEQUENCES (Next 24 Hours)")
        next_24h = datetime.utcnow() + timedelta(hours=24)
        
        due_sequences = list(storage.db.email_sequences.find({
            "status": "active",
            "next_email_due": {
                "$gte": datetime.utcnow().isoformat(),
                "$lte": next_24h.isoformat()
            }
        }).sort("next_email_due", 1).limit(10))
        
        if due_sequences:
            for i, seq in enumerate(due_sequences, 1):
                contact_email = seq.get('contact_email', 'Unknown')
                next_due = seq.get('next_email_due', 'Unknown')
                current_step = seq.get('current_step', 0)
                
                print(f"{i:2d}. {contact_email}")
                print(f"    Next Step: {current_step + 1} | Due: {next_due}")
        else:
            print("No sequences due in the next 24 hours")
        
        # Sample Recent Email Content
        print_subheader("SAMPLE RECENT EMAIL CONTENT")
        recent_with_content = storage.db.email_sequences.find_one({
            "emails_sent": {"$exists": True, "$ne": []}
        })
        
        if recent_with_content:
            contact_email = recent_with_content.get('contact_email', 'Unknown')
            emails_sent = recent_with_content.get('emails_sent', [])
            
            if emails_sent:
                latest_email = emails_sent[-1]
                print(f"Recent Email Example:")
                print(f"  To: {contact_email}")
                print(f"  Subject: {latest_email.get('subject', 'No subject')}")
                print(f"  Step: {latest_email.get('step', 'N/A')}")
                print(f"  Sent: {latest_email.get('sent_at', 'Unknown')}")
                print(f"  Actually Sent: {'Yes' if latest_email.get('actually_sent', False) else 'No (dry run)'}")
        
        # Gmail Activity
        if gmail.service:
            print_subheader("RECENT GMAIL ACTIVITY")
            try:
                recent_gmail = gmail.get_sent_emails(query="from:me", max_results=5)
                if recent_gmail:
                    print(f"Last {len(recent_gmail)} emails sent via Gmail:")
                    for email in recent_gmail:
                        print(f"  - To: {email.get('to', 'Unknown')} | Subject: {email.get('subject', 'No subject')}")
                else:
                    print("No recent Gmail activity found")
            except Exception as e:
                print(f"Error retrieving Gmail activity: {e}")
        
        # System Health Summary
        print_subheader("SYSTEM HEALTH SUMMARY")
        print("✅ Database: Operational")
        print(f"✅ Gmail: {'Operational' if gmail.service else 'Not Connected'}")
        print(f"📊 Active Campaigns: {active_sequences} sequences running")
        print(f"📧 Recent Activity: {emails_30_days} emails in last 30 days")
        print(f"⏰ Pending: {len(due_sequences) if 'due_sequences' in locals() else 0} emails due in next 24 hours")
        
        return True
        
    except Exception as e:
        print(f"❌ Error getting system overview: {e}")
        return False

def main():
    """Main function"""
    print("🔍 GFMD EMAIL SYSTEM OVERVIEW")
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = get_system_overview()
    
    if success:
        print(f"\n{'='*80}")
        print("Overview complete. System is operational.")
        print(f"{'='*80}")
    else:
        print(f"\n{'='*80}")
        print("⚠️ Some errors occurred during overview generation.")
        print(f"{'='*80}")

if __name__ == "__main__":
    main()