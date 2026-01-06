#!/usr/bin/env python3
"""
View Recent Emails Script
Simple script to view recently generated and sent emails from the GFMD system
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
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

class EmailViewer:
    """View recent emails from database and Gmail"""
    
    def __init__(self):
        try:
            self.storage = MongoDBStorage()
            print("✅ Connected to MongoDB")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.storage = None
            
        try:
            self.gmail = GmailIntegration()
            print("✅ Connected to Gmail")
        except Exception as e:
            print(f"⚠️ Gmail connection failed: {e}")
            self.gmail = None
    
    def view_recent_database_emails(self, days: int = 7, limit: int = 20):
        """View recent email records from MongoDB"""
        if not self.storage:
            print("❌ No database connection")
            return
            
        try:
            print(f"\n📧 Recent Email Records (Last {days} days)")
            print("=" * 80)
            
            # Calculate date range
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Get email interactions from database
            query = {
                "type": "email_sent",
                "timestamp": {"$gte": since_date}
            }
            
            emails = list(self.storage.interactions.find(query)
                         .sort("timestamp", -1)
                         .limit(limit))
            
            if not emails:
                print(f"📭 No emails found in the last {days} days")
                return
                
            print(f"Found {len(emails)} email records:")
            print()
            
            for i, email in enumerate(emails, 1):
                print(f"{i}. To: {email.get('contactEmail', 'Unknown')}")
                print(f"   Subject: {email.get('subject', 'No subject')}")
                print(f"   Sent: {email.get('timestamp', 'Unknown time')}")
                print(f"   Campaign: {email.get('campaignId', 'N/A')}")
                print(f"   Sequence Step: {email.get('sequenceStep', 'N/A')}")
                
                # Check for opens/clicks
                if email.get('openedAt'):
                    print(f"   📖 Opened: {email.get('openedAt')}")
                if email.get('clickedLinks'):
                    print(f"   🔗 Clicks: {len(email.get('clickedLinks', []))}")
                if email.get('repliedAt'):
                    print(f"   💬 Replied: {email.get('repliedAt')}")
                
                print()
                
        except Exception as e:
            print(f"❌ Error viewing database emails: {e}")
    
    def view_recent_gmail_emails(self, limit: int = 10):
        """View recent sent emails from Gmail"""
        if not self.gmail or not self.gmail.service:
            print("❌ No Gmail connection")
            return
            
        try:
            print(f"\n📤 Recent Gmail Sent Emails (Last {limit})")
            print("=" * 80)
            
            emails = self.gmail.get_sent_emails(
                query="from:me",
                max_results=limit
            )
            
            if not emails:
                print("📭 No sent emails found in Gmail")
                return
                
            print(f"Found {len(emails)} sent emails:")
            print()
            
            for i, email in enumerate(emails, 1):
                print(f"{i}. To: {email.get('to', 'Unknown')}")
                print(f"   Subject: {email.get('subject', 'No subject')}")
                print(f"   Date: {email.get('date', 'Unknown date')}")
                print(f"   Message ID: {email.get('id', 'N/A')}")
                print()
                
        except Exception as e:
            print(f"❌ Error viewing Gmail emails: {e}")
    
    def view_sequence_status(self, limit: int = 15):
        """View current email sequence status"""
        if not self.storage:
            print("❌ No database connection")
            return
            
        try:
            print(f"\n🔄 Current Email Sequence Status (Top {limit})")
            print("=" * 80)
            
            # Get active sequences
            sequences = list(self.storage.db.email_sequences.find({
                "status": "active"
            }).sort("updated_at", -1).limit(limit))
            
            if not sequences:
                print("📭 No active email sequences found")
                return
                
            print(f"Found {len(sequences)} active sequences:")
            print()
            
            for i, seq in enumerate(sequences, 1):
                contact_email = seq.get('contact_email', 'Unknown')
                current_step = seq.get('current_step', 0)
                emails_sent = len(seq.get('emails_sent', []))
                next_due = seq.get('next_email_due', 'N/A')
                
                print(f"{i}. Contact: {contact_email}")
                print(f"   Current Step: {current_step} | Emails Sent: {emails_sent}")
                print(f"   Next Email Due: {next_due}")
                print(f"   Last Updated: {seq.get('updated_at', 'N/A')}")
                print()
                
        except Exception as e:
            print(f"❌ Error viewing sequence status: {e}")
    
    def view_contact_email_history(self, email: str):
        """View email history for a specific contact"""
        if not self.storage:
            print("❌ No database connection")
            return
            
        try:
            print(f"\n📧 Email History for {email}")
            print("=" * 80)
            
            # Get contact info
            contact = self.storage.get_contact_by_email(email)
            if not contact:
                print(f"❌ Contact not found: {email}")
                return
                
            print(f"Contact: {contact.get('firstName', '')} {contact.get('lastName', '')}")
            print(f"Organization: {contact.get('organization', 'N/A')}")
            print(f"Status: {contact.get('status', 'N/A')}")
            print()
            
            # Get email interactions
            emails = list(self.storage.interactions.find({
                "contactEmail": email.lower(),
                "type": "email_sent"
            }).sort("timestamp", -1))
            
            if not emails:
                print(f"📭 No email history found for {email}")
                return
                
            print(f"Email History ({len(emails)} emails):")
            print()
            
            for i, email_record in enumerate(emails, 1):
                print(f"{i}. Subject: {email_record.get('subject', 'No subject')}")
                print(f"   Sent: {email_record.get('timestamp', 'Unknown time')}")
                print(f"   Campaign: {email_record.get('campaignId', 'N/A')}")
                print(f"   Step: {email_record.get('sequenceStep', 'N/A')}")
                
                if email_record.get('openedAt'):
                    print(f"   📖 Opened: {email_record.get('openedAt')}")
                if email_record.get('repliedAt'):
                    print(f"   💬 Replied: {email_record.get('repliedAt')}")
                
                print()
                
        except Exception as e:
            print(f"❌ Error viewing contact email history: {e}")
    
    def get_campaign_stats(self):
        """Get overall campaign statistics"""
        if not self.storage:
            print("❌ No database connection")
            return
            
        try:
            print("\n📊 Campaign Statistics")
            print("=" * 80)
            
            # Total emails sent
            total_emails = self.storage.interactions.count_documents({"type": "email_sent"})
            print(f"Total Emails Sent: {total_emails}")
            
            # Last 30 days
            since_30_days = datetime.utcnow() - timedelta(days=30)
            emails_30_days = self.storage.interactions.count_documents({
                "type": "email_sent",
                "timestamp": {"$gte": since_30_days}
            })
            print(f"Emails Last 30 Days: {emails_30_days}")
            
            # Opens and clicks
            opens = self.storage.interactions.count_documents({
                "type": "email_sent",
                "openedAt": {"$exists": True}
            })
            
            clicks = self.storage.interactions.count_documents({
                "type": "email_sent",
                "clickedLinks": {"$exists": True, "$ne": []}
            })
            
            replies = self.storage.interactions.count_documents({
                "type": "email_sent",
                "repliedAt": {"$exists": True}
            })
            
            print(f"Email Opens: {opens}")
            print(f"Email Clicks: {clicks}")
            print(f"Email Replies: {replies}")
            
            # Calculate rates
            if total_emails > 0:
                open_rate = (opens / total_emails) * 100
                click_rate = (clicks / total_emails) * 100
                reply_rate = (replies / total_emails) * 100
                
                print(f"\nOpen Rate: {open_rate:.1f}%")
                print(f"Click Rate: {click_rate:.1f}%")
                print(f"Reply Rate: {reply_rate:.1f}%")
            
            # Active sequences
            active_sequences = self.storage.db.email_sequences.count_documents({"status": "active"})
            completed_sequences = self.storage.db.email_sequences.count_documents({"status": "completed"})
            
            print(f"\nActive Sequences: {active_sequences}")
            print(f"Completed Sequences: {completed_sequences}")
            
        except Exception as e:
            print(f"❌ Error getting campaign stats: {e}")

def main():
    """Main function"""
    print("🔍 GFMD Email Viewer")
    print("=" * 50)
    
    viewer = EmailViewer()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "recent":
            # Show recent database emails
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            viewer.view_recent_database_emails(days, limit)
            
        elif command == "gmail":
            # Show recent Gmail emails
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            viewer.view_recent_gmail_emails(limit)
            
        elif command == "sequences":
            # Show sequence status
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 15
            viewer.view_sequence_status(limit)
            
        elif command == "contact":
            # Show contact email history
            if len(sys.argv) > 2:
                email = sys.argv[2]
                viewer.view_contact_email_history(email)
            else:
                print("❌ Usage: python3 view_recent_emails.py contact <email>")
                
        elif command == "stats":
            # Show campaign statistics
            viewer.get_campaign_stats()
            
        else:
            print("❌ Unknown command. Available commands:")
            print("  recent [days] [limit] - View recent database emails")
            print("  gmail [limit] - View recent Gmail sent emails")
            print("  sequences [limit] - View current sequence status")
            print("  contact <email> - View email history for specific contact")
            print("  stats - View campaign statistics")
    else:
        # Default: show all info
        viewer.get_campaign_stats()
        viewer.view_recent_database_emails(7, 10)
        viewer.view_sequence_status(10)

if __name__ == "__main__":
    main()