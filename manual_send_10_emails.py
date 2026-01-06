#!/usr/bin/env python3
"""
Manual Email Sender - Send 10 emails to new contacts
Uses fallback email templates when AI generation fails
"""

import os
import asyncio
from datetime import datetime, timedelta
from mongodb_storage import MongoDBStorage
from gmail_integration import GmailIntegration
from business_day_utils import BusinessDayCalculator

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

class ManualEmailSender:
    def __init__(self):
        self.storage = MongoDBStorage()
        self.gmail = GmailIntegration()
        self.business_day_calc = BusinessDayCalculator()

    def get_new_contacts(self, count=10):
        """Get contacts that haven't been emailed yet"""
        # Get contacts already in sequences
        active_sequences = list(self.storage.db.email_sequences.find(
            {"status": {"$in": ["active", "completed"]}},
            {"contact_id": 1}
        ))
        
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
        new_contacts = list(self.storage.db.contacts.find(query_filter).limit(count))
        
        return new_contacts

    def create_simple_email(self, contact):
        """Create a simple email for the contact"""
        email = contact.get('email', '')
        company_name = contact.get('company_name', 'your department')
        contact_name = contact.get('contact_name', '')
        
        # Extract first name
        first_name = "there"
        if contact_name:
            name_parts = contact_name.split()
            for part in name_parts:
                clean_part = part.strip('.,')
                if clean_part and clean_part not in ['Dr.', 'Dr', 'Mr.', 'Mr', 'Ms.', 'Ms', 'Mrs.', 'Mrs']:
                    first_name = clean_part
                    break
        
        subject = f"Drug disposal discussion - {company_name}"
        
        body = f"""Hi {first_name},

I understand that managing drug evidence and disposal can be a challenge for law enforcement agencies like {company_name}. Our Narc Gone system is designed to securely destroy illicit narcotics and prescription medications on-site, reducing the need for incineration and associated costs.

Would you be open to a quick call to discuss how our system can help {company_name}?

Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com"""

        return {
            'subject': subject,
            'body': body,
            'recipient_email': email,
            'first_name': first_name,
            'company_name': company_name
        }

    async def send_emails_to_new_contacts(self, count=10, actually_send=True):
        """Send emails to new contacts and create sequences"""
        print(f"\n📧 Preparing to send {count} emails to new contacts...")
        
        # Get new contacts
        new_contacts = self.get_new_contacts(count)
        
        if not new_contacts:
            print("❌ No new contacts available")
            return {"success": False, "message": "No new contacts available"}
        
        print(f"✅ Found {len(new_contacts)} new contacts")
        
        sent_count = 0
        results = []
        
        for i, contact in enumerate(new_contacts):
            try:
                print(f"\n📨 Processing contact {i+1}/{len(new_contacts)}: {contact.get('email', 'unknown')}")
                
                # Create email
                email_data = self.create_simple_email(contact)
                
                if actually_send:
                    # Send email via Gmail
                    send_result = self.gmail.send_email(
                        to_email=email_data['recipient_email'],
                        subject=email_data['subject'],
                        body=email_data['body']
                    )
                    
                    if send_result.get('success'):
                        print(f"✅ Email sent successfully")
                        sent_count += 1
                        
                        # Create email sequence record
                        contact_id = str(contact['_id'])
                        next_email_due = self.business_day_calc.add_business_days(datetime.now(), 3)
                        
                        sequence_data = {
                            "contact_id": contact_id,
                            "sequence_name": "narc_gone_law_enforcement",
                            "current_step": 1,
                            "status": "active",
                            "created_at": datetime.now().isoformat(),
                            "updated_at": datetime.now().isoformat(),
                            "next_email_due": next_email_due.isoformat(),
                            "last_email_sent": datetime.now().isoformat(),
                            "reply_received": False,
                            "reply_date": None,
                            "emails_sent": [{
                                "step": 1,
                                "sent_at": datetime.now().isoformat(),
                                "subject": email_data['subject'],
                                "template_type": "initial",
                                "actually_sent": True
                            }]
                        }
                        
                        # Insert sequence
                        self.storage.db.email_sequences.insert_one(sequence_data)
                        
                        results.append({
                            "contact_email": email_data['recipient_email'],
                            "company": email_data['company_name'],
                            "subject": email_data['subject'],
                            "success": True
                        })
                    else:
                        print(f"❌ Failed to send email: {send_result.get('error', 'Unknown error')}")
                        results.append({
                            "contact_email": email_data['recipient_email'],
                            "success": False,
                            "error": send_result.get('error', 'Unknown error')
                        })
                else:
                    print(f"📧 DRY RUN - Would send email with subject: {email_data['subject']}")
                    results.append({
                        "contact_email": email_data['recipient_email'],
                        "subject": email_data['subject'],
                        "dry_run": True
                    })
                    
            except Exception as e:
                print(f"❌ Error processing contact: {e}")
                results.append({
                    "contact_email": contact.get('email', 'unknown'),
                    "success": False,
                    "error": str(e)
                })
        
        print(f"\n📊 Summary:")
        print(f"   Emails sent: {sent_count}")
        print(f"   Total processed: {len(results)}")
        
        return {
            "success": True,
            "sent": sent_count,
            "processed": len(results),
            "details": results
        }

async def main():
    """Main function to send 10 emails"""
    sender = ManualEmailSender()
    
    print("🚀 Manual Email Sender - Sending 10 emails to new contacts")
    print("=" * 60)
    
    # Send emails (set to True to actually send, False for dry run)
    result = await sender.send_emails_to_new_contacts(count=10, actually_send=True)
    
    if result.get('success'):
        print(f"\n✅ Process completed successfully!")
        print(f"📧 Emails sent: {result.get('sent', 0)}")
    else:
        print(f"\n❌ Process failed: {result.get('message', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())