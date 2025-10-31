#!/usr/bin/env python3
"""
Run Today's Manual Email Campaign - 50 Healthcare Contacts
"""
import asyncio
import os
import sys
from datetime import datetime
import logging

# Set environment variables
os.environ['GOOGLE_CLOUD_PROJECT'] = 'windy-tiger-471523-m5'

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from firestore_service import FirestoreService
from automatic_email_sender import AutomaticEmailSender

logging.basicConfig(level=logging.INFO)

def run_today_campaign():
    """Run today's email campaign to 50 healthcare contacts"""
    print("🚀 GFMD AI Swarm Agent - Today's Email Campaign")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    print(f"🎯 Target: 50 emails to healthcare decision-makers")
    print(f"🏥 Focus: B2B medical device sales outreach")
    print("=" * 60)
    
    try:
        # Setup authentication
        creds_file = '/Users/merandafreiner/gfmd_swarm_agent/google_sheets_credentials.json'
        if os.path.exists(creds_file):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_file
            print("✅ Google Cloud credentials configured")
        
        # Initialize services
        print("\n🔥 Initializing production services...")
        firestore_service = FirestoreService()
        email_sender = AutomaticEmailSender()
        
        # Check system status
        print(f"   ✅ Firestore: Connected to project windy-tiger-471523-m5")
        print(f"   ✅ Gmail API: {'Authenticated' if email_sender.gmail else 'Not available'}")
        print(f"   ✅ Daily limits: {'OK' if email_sender.can_send_more_emails() else 'Reached'}")
        
        if not email_sender.gmail or not email_sender.can_send_more_emails():
            print("❌ Cannot proceed - email service not available")
            return None
        
        # Get 50 contacts for today's campaign
        print("\n📋 Retrieving 50 healthcare contacts from Firestore...")
        contacts = firestore_service.get_contacts_for_outreach(limit=50)
        print(f"📊 Retrieved {len(contacts)} contacts for today's campaign")
        
        if len(contacts) < 50:
            print(f"⚠️ Only {len(contacts)} contacts available (target: 50)")
        
        # Campaign statistics
        campaign_stats = {
            "total_contacts": len(contacts),
            "emails_sent": 0,
            "emails_failed": 0,
            "start_time": datetime.now(),
            "healthcare_systems": set(),
            "message_ids": []
        }
        
        # Process each healthcare contact
        print(f"\n📧 Starting email campaign to {len(contacts)} healthcare facilities...")
        print("-" * 60)
        
        for i, contact in enumerate(contacts, 1):
            try:
                company = contact.get('company_name', 'Unknown Healthcare Facility')
                email = contact.get('email', 'unknown@example.com')
                
                print(f"📧 {i:2d}/{len(contacts)} - {company}")
                print(f"    📨 To: {email}")
                
                # Track healthcare systems
                campaign_stats["healthcare_systems"].add(company)
                
                # Prepare prospect data
                prospect = {
                    "contact_name": f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
                    "email": email,
                    "organization_name": company,
                    "title": contact.get('title', 'Healthcare Professional')
                }
                
                # Send the email
                result = email_sender.send_email_to_prospect(prospect)
                
                if result.get("success"):
                    campaign_stats["emails_sent"] += 1
                    message_id = result.get('message_id', 'N/A')
                    campaign_stats["message_ids"].append(message_id)
                    
                    print(f"    ✅ Email sent successfully!")
                    print(f"    📬 Message ID: {message_id}")
                    
                    # Update Firestore with delivery tracking
                    firestore_service.record_email_sent(
                        email,
                        {
                            "subject": f"Laboratory Equipment Discussion - {company}",
                            "timestamp": datetime.now().isoformat(),
                            "recipient": email,
                            "message_id": message_id,
                            "campaign": "manual_daily_run",
                            "campaign_date": datetime.now().strftime('%Y-%m-%d')
                        }
                    )
                    print(f"    📊 Firestore updated")
                else:
                    campaign_stats["emails_failed"] += 1
                    error_msg = result.get('message', result.get('error', 'Unknown error'))
                    print(f"    ❌ Email failed: {error_msg}")
                    
                    # Record error in Firestore
                    firestore_service.record_email_error(email, error_msg)
                
                print()  # Add spacing between contacts
                
            except Exception as e:
                campaign_stats["emails_failed"] += 1
                print(f"    ❌ Error processing contact: {e}")
                firestore_service.record_email_error(email, str(e))
                print()
        
        # Calculate final statistics
        campaign_stats["end_time"] = datetime.now()
        campaign_stats["duration"] = campaign_stats["end_time"] - campaign_stats["start_time"]
        success_rate = (campaign_stats["emails_sent"] / campaign_stats["total_contacts"]) * 100 if campaign_stats["total_contacts"] > 0 else 0
        
        # Display final results
        print("=" * 60)
        print("📊 TODAY'S CAMPAIGN RESULTS")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"⏰ Duration: {campaign_stats['duration']}")
        print(f"🏥 Healthcare Systems Contacted: {len(campaign_stats['healthcare_systems'])}")
        print(f"📧 Total Emails Attempted: {campaign_stats['total_contacts']}")
        print(f"✅ Emails Sent Successfully: {campaign_stats['emails_sent']}")
        print(f"❌ Email Failures: {campaign_stats['emails_failed']}")
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if campaign_stats["emails_sent"] >= 40:
            print("\n🎉 EXCELLENT CAMPAIGN RESULTS!")
            print("✅ Successfully reached 40+ healthcare decision-makers")
        elif campaign_stats["emails_sent"] >= 25:
            print("\n✅ GOOD CAMPAIGN RESULTS!")
            print("📈 Solid outreach to healthcare facilities")
        else:
            print(f"\n⚠️ PARTIAL CAMPAIGN")
            print(f"📊 {campaign_stats['emails_sent']} emails sent")
        
        print(f"\n📬 Message IDs for tracking:")
        for i, msg_id in enumerate(campaign_stats["message_ids"][:5], 1):
            print(f"   {i}. {msg_id}")
        if len(campaign_stats["message_ids"]) > 5:
            print(f"   ... and {len(campaign_stats['message_ids']) - 5} more")
        
        print(f"\n🗄️ All results stored in Firestore database")
        print(f"📈 Ready for tomorrow's automated campaign")
        
        return campaign_stats
        
    except Exception as e:
        print(f"\n❌ Campaign failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Run today's campaign
    results = run_today_campaign()
    
    if results:
        print(f"\n🎯 Campaign completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if results.get('emails_sent', 0) >= 40:
            print("🏆 OUTSTANDING SUCCESS!")
        elif results.get('emails_sent', 0) >= 25:
            print("✅ SOLID RESULTS!")
        else:
            print(f"📊 CAMPAIGN COMPLETED: {results.get('emails_sent', 0)} emails sent")
    else:
        print("\n❌ Campaign failed - check logs for details")