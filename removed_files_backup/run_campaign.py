#!/usr/bin/env python3
"""
GFMD Campaign Runner - Simple, Groq-Powered
Runs the complete email campaign: AI agents → Gmail sending → tracking
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any
import logging

from simple_storage import SimpleStorage
from groq_coordinator import GroqCoordinator
from automatic_email_sender import AutomaticEmailSender

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GFMDCampaignRunner:
    """Main campaign runner"""

    def __init__(self):
        # Check for Groq API key
        if not os.environ.get('GROQ_API_KEY'):
            raise ValueError("GROQ_API_KEY environment variable not set")

        # Initialize components
        self.storage = SimpleStorage()
        self.coordinator = GroqCoordinator()
        self.email_sender = AutomaticEmailSender()

        logger.info("Campaign runner initialized")

    async def run_campaign(
        self,
        num_prospects: int = 10,
        min_qualification_score: int = 50,
        actually_send_emails: bool = False
    ) -> Dict[str, Any]:
        """
        Run a complete campaign

        Args:
            num_prospects: Number of prospects to process
            min_qualification_score: Minimum score to send email (0-100)
            actually_send_emails: If True, actually send via Gmail. If False, just generate.
        """
        campaign_id = self.storage.start_campaign(f"Campaign {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        logger.info("=" * 70)
        logger.info(f"STARTING CAMPAIGN: {campaign_id}")
        logger.info(f"Prospects to process: {num_prospects}")
        logger.info(f"Min qualification score: {min_qualification_score}")
        logger.info(f"Actually send emails: {actually_send_emails}")
        logger.info("=" * 70)

        # Step 1: Get contacts from storage
        logger.info("\n📋 Step 1: Loading contacts from CSV...")
        contacts = self.storage.get_contacts_for_outreach(limit=num_prospects)

        if not contacts:
            logger.error("No contacts available for outreach")
            return {
                "success": False,
                "error": "No contacts available"
            }

        logger.info(f"✓ Loaded {len(contacts)} contacts")

        # Step 2: Process through AI agents
        logger.info("\n🤖 Step 2: Processing through AI agent pipeline...")
        ai_results = await self.coordinator.process_batch(
            contacts,
            min_score_for_email=min_qualification_score
        )

        # Step 3: Send emails (if enabled)
        emails_sent = 0
        emails_failed = 0

        if actually_send_emails:
            logger.info("\n📧 Step 3: Sending emails via Gmail...")

            for result in ai_results['results']:
                if not result.get('should_send_email'):
                    continue

                if not result.get('email') or not result['email'].get('success'):
                    continue

                # Prepare prospect data for email sender
                prospect = result['prospect']
                email_data = result['email']

                prospect_for_sender = {
                    'contact_name': prospect.get('contact_name', ''),
                    'email': prospect.get('email', ''),
                    'organization_name': email_data.get('company_name', ''),
                    'title': prospect.get('title', ''),
                    'location': f"{prospect.get('city', '')}, {prospect.get('state', '')}".strip(', '),
                    'pain_point': 'laboratory noise and equipment modernization',
                    'facility_type': prospect.get('facility_type', ''),
                    'budget_range': 'equipment upgrade',
                    'department': 'laboratory operations'
                }

                # Send email
                send_result = self.email_sender.send_email_to_prospect(prospect_for_sender)

                if send_result.get('success'):
                    emails_sent += 1
                    logger.info(f"  ✓ Sent to {prospect['email']}")

                    # Record in storage
                    self.storage.record_email_sent(
                        prospect['email'],
                        {
                            "subject": email_data.get('subject', ''),
                            "message_id": send_result.get('message_id', ''),
                            "campaign_id": campaign_id
                        }
                    )
                else:
                    emails_failed += 1
                    logger.error(f"  ✗ Failed to send to {prospect['email']}: {send_result.get('message', 'Unknown error')}")

                    # Record error
                    self.storage.record_email_error(
                        prospect['email'],
                        send_result.get('message', 'Send failed')
                    )

        else:
            logger.info("\n📧 Step 3: Email sending SKIPPED (dry run mode)")
            logger.info(f"   Would have sent {ai_results['emails_generated']} emails")

        # Step 4: Close campaign and report
        self.storage.end_campaign(campaign_id, emails_sent, emails_failed)

        logger.info("\n" + "=" * 70)
        logger.info("CAMPAIGN COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Prospects processed: {ai_results['total_processed']}")
        logger.info(f"Emails generated: {ai_results['emails_generated']}")
        logger.info(f"High priority leads: {ai_results['high_priority_count']}")

        if actually_send_emails:
            logger.info(f"Emails sent: {emails_sent}")
            logger.info(f"Emails failed: {emails_failed}")
        else:
            logger.info(f"Emails that would be sent: {ai_results['emails_generated']}")

        logger.info(f"AI tokens used: {ai_results['total_tokens_used']}")
        logger.info("=" * 70)

        # Return summary
        return {
            "success": True,
            "campaign_id": campaign_id,
            "prospects_processed": ai_results['total_processed'],
            "emails_generated": ai_results['emails_generated'],
            "emails_sent": emails_sent if actually_send_emails else 0,
            "emails_failed": emails_failed if actually_send_emails else 0,
            "high_priority_leads": ai_results['high_priority_count'],
            "tokens_used": ai_results['total_tokens_used'],
            "dry_run": not actually_send_emails,
            "results": ai_results['results']
        }


async def main():
    """Main entry point"""
    import sys

    print("🚀 GFMD AI Campaign Runner (Groq-Powered)")
    print("=" * 70)

    # Parse arguments
    num_prospects = 5  # Default
    actually_send = False

    if len(sys.argv) > 1:
        try:
            num_prospects = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid number of prospects")
            return

    if len(sys.argv) > 2 and sys.argv[2].lower() in ['send', 'true', 'yes']:
        actually_send = True

    print(f"\nConfiguration:")
    print(f"  Prospects: {num_prospects}")
    print(f"  Actually send emails: {actually_send}")
    print()

    if not actually_send:
        print("⚠️  DRY RUN MODE - emails will be generated but not sent")
        print("   To actually send, run: python3 run_campaign.py <number> send")
        print()

    # Run campaign
    runner = GFMDCampaignRunner()
    result = await runner.run_campaign(
        num_prospects=num_prospects,
        min_qualification_score=50,
        actually_send_emails=actually_send
    )

    # Show sample emails
    if result['emails_generated'] > 0:
        print("\n" + "=" * 70)
        print("SAMPLE EMAILS GENERATED:")
        print("=" * 70)

        count = 0
        for r in result['results']:
            if r.get('email') and r['email'].get('success'):
                count += 1
                print(f"\n[Email {count}]")
                print(f"To: {r['email']['recipient_email']}")
                print(f"Subject: {r['email']['subject']}")
                print(f"Score: {r['qualification']['total_score']}/100")
                print(f"\nBody:\n{r['email']['body']}")
                print("-" * 70)

                if count >= 3:  # Show max 3 samples
                    break

    print("\n✅ Campaign completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
