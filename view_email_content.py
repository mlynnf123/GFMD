#!/usr/bin/env python3
"""
View Email Content Script
View the actual content of emails generated and sent by the GFMD system
"""

import os
import sys
from mongodb_storage import MongoDBStorage
from gmail_integration import GmailIntegration
from datetime import datetime, timedelta

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

def view_recent_email_content(limit=5):
    """View the content of recently generated emails"""
    try:
        storage = MongoDBStorage()
        print("✅ Connected to MongoDB")
        
        print(f"\n📧 Recent Email Content (Last {limit} emails)")
        print("=" * 100)
        
        # Get recent sequences with email content
        sequences = list(storage.db.email_sequences.find({
            "emails_sent": {"$exists": True, "$ne": []}
        }).sort('updated_at', -1).limit(limit))
        
        if not sequences:
            print("📭 No email content found in sequences")
            return
            
        for i, seq in enumerate(sequences, 1):
            contact_email = seq.get('contact_email', 'Unknown')
            emails_sent = seq.get('emails_sent', [])
            
            if not emails_sent:
                continue
                
            # Get the most recent email for this contact
            latest_email = emails_sent[-1]
            
            print(f"\n{i}. EMAIL TO: {contact_email}")
            print("-" * 80)
            print(f"Subject: {latest_email.get('subject', 'No subject')}")
            print(f"Sent: {latest_email.get('sent_at', 'Unknown time')}")
            print(f"Step: {latest_email.get('step', 'N/A')}")
            print(f"Actually Sent: {'✅ Yes' if latest_email.get('actually_sent', False) else '❌ No (dry run)'}")
            print(f"Template Type: {latest_email.get('template_type', 'N/A')}")
            print("\nEMAIL CONTENT:")
            print("~" * 80)
            
            # Try to get the email body from interactions collection
            interaction = storage.interactions.find_one({
                "contactEmail": contact_email.lower(),
                "type": "email_sent",
                "sequenceStep": latest_email.get('step', 1)
            })
            
            if interaction and interaction.get('emailBody'):
                print(interaction.get('emailBody'))
            else:
                # If not in interactions, try to regenerate or show placeholder
                print("[Email body not stored in database]")
                print("Note: Email content is generated in real-time and may not be stored.")
                
                # Try to get contact info and show what the email would contain
                contact = storage.get_contact_by_email(contact_email)
                if contact:
                    print(f"\nContact Info Used:")
                    print(f"- Name: {contact.get('firstName', '')} {contact.get('lastName', '')}")
                    print(f"- Organization: {contact.get('organization', 'N/A')}")
                    print(f"- Title: {contact.get('title', 'N/A')}")
                    print(f"- Location: {contact.get('city', 'N/A')}, {contact.get('state', 'N/A')}")
            
            print("=" * 100)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def view_gmail_sent_content(limit=5):
    """View content of emails actually sent via Gmail"""
    try:
        gmail = GmailIntegration()
        print("✅ Connected to Gmail")
        
        print(f"\n📤 Recent Gmail Sent Email Content (Last {limit} emails)")
        print("=" * 100)
        
        # Get recent sent emails
        emails = gmail.get_sent_emails(query="from:me", max_results=limit)
        
        if not emails:
            print("📭 No sent emails found in Gmail")
            return
            
        for i, email in enumerate(emails, 1):
            print(f"\n{i}. GMAIL EMAIL")
            print("-" * 80)
            print(f"To: {email.get('to', 'Unknown')}")
            print(f"Subject: {email.get('subject', 'No subject')}")
            print(f"Date: {email.get('date', 'Unknown date')}")
            print(f"Message ID: {email.get('id', 'N/A')}")
            
            # Try to get full message content
            try:
                if gmail.service:
                    msg = gmail.service.users().messages().get(
                        userId='me',
                        id=email['id'],
                        format='full'
                    ).execute()
                    
                    # Extract email body
                    body = gmail._extract_message_body(msg.get('payload', {}))
                    
                    if body:
                        print("\nEMAIL CONTENT:")
                        print("~" * 80)
                        print(body[:1000] + "..." if len(body) > 1000 else body)
                    else:
                        print("\nEMAIL CONTENT: [Unable to extract body]")
                        
            except Exception as e:
                print(f"\nEMAIL CONTENT: [Error retrieving: {e}]")
                
            print("=" * 100)
            
    except Exception as e:
        print(f"❌ Gmail Error: {e}")

def view_specific_contact_emails(email_address):
    """View all emails for a specific contact"""
    try:
        storage = MongoDBStorage()
        print("✅ Connected to MongoDB")
        
        print(f"\n📧 All Emails for: {email_address}")
        print("=" * 100)
        
        # Get sequence for this contact
        sequence = storage.db.email_sequences.find_one({"contact_email": email_address})
        
        if not sequence:
            print(f"❌ No sequence found for {email_address}")
            return
            
        emails_sent = sequence.get('emails_sent', [])
        
        if not emails_sent:
            print(f"📭 No emails sent to {email_address}")
            return
            
        print(f"Found {len(emails_sent)} emails:")
        
        for i, email_record in enumerate(emails_sent, 1):
            print(f"\n{i}. EMAIL STEP {email_record.get('step', 'N/A')}")
            print("-" * 80)
            print(f"Subject: {email_record.get('subject', 'No subject')}")
            print(f"Sent: {email_record.get('sent_at', 'Unknown time')}")
            print(f"Actually Sent: {'✅ Yes' if email_record.get('actually_sent', False) else '❌ No (dry run)'}")
            print(f"Template Type: {email_record.get('template_type', 'N/A')}")
            
            # Try to find the interaction record
            interaction = storage.interactions.find_one({
                "contactEmail": email_address.lower(),
                "type": "email_sent",
                "sequenceStep": email_record.get('step', 1)
            })
            
            if interaction:
                print(f"Campaign ID: {interaction.get('campaignId', 'N/A')}")
                print(f"Message ID: {interaction.get('messageId', 'N/A')}")
                
                if interaction.get('openedAt'):
                    print(f"📖 Opened: {interaction.get('openedAt')}")
                if interaction.get('repliedAt'):
                    print(f"💬 Replied: {interaction.get('repliedAt')}")
            
            print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🔍 GFMD Email Content Viewer")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "recent":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            view_recent_email_content(limit)
            
        elif command == "gmail":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            view_gmail_sent_content(limit)
            
        elif command == "contact":
            if len(sys.argv) > 2:
                email = sys.argv[2]
                view_specific_contact_emails(email)
            else:
                print("❌ Usage: python3 view_email_content.py contact <email>")
                
        else:
            print("❌ Unknown command. Available commands:")
            print("  recent [limit] - View recent email content from database")
            print("  gmail [limit] - View recent sent email content from Gmail")
            print("  contact <email> - View all emails for specific contact")
    else:
        # Default: show recent email content
        view_recent_email_content(5)

if __name__ == "__main__":
    main()