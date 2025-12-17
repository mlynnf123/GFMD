#!/usr/bin/env python3
"""
Simple CSV/JSON Storage Manager
Replaces Firestore with simple file-based storage
"""

import csv
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SimpleStorage:
    """Simple file-based storage for contacts and campaign tracking"""

    def __init__(
        self,
        contacts_csv: str = "definitive_healthcare_data.csv",
        tracking_file: str = "campaign_tracking.json"
    ):
        self.contacts_csv = contacts_csv
        self.tracking_file = tracking_file

        # Load tracking data
        self.tracking = self._load_tracking()

        logger.info(f"Storage initialized with {self._count_contacts()} contacts")

    def _load_tracking(self) -> Dict[str, Any]:
        """Load campaign tracking data"""
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading tracking file: {e}")
                return self._create_empty_tracking()
        else:
            return self._create_empty_tracking()

    def _create_empty_tracking(self) -> Dict[str, Any]:
        """Create empty tracking structure"""
        return {
            "contacts": {},  # email -> contact tracking data
            "campaigns": [],  # list of campaign runs
            "last_updated": datetime.now().isoformat()
        }

    def _save_tracking(self):
        """Save tracking data to file"""
        try:
            self.tracking["last_updated"] = datetime.now().isoformat()
            with open(self.tracking_file, 'w') as f:
                json.dump(self.tracking, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tracking file: {e}")

    def _count_contacts(self) -> int:
        """Count total contacts in CSV"""
        try:
            with open(self.contacts_csv, 'r', encoding='utf-8') as f:
                return sum(1 for _ in csv.DictReader(f))
        except Exception as e:
            logger.error(f"Error counting contacts: {e}")
            return 0

    def get_contacts_for_outreach(
        self,
        limit: int = 50,
        min_days_since_contact: int = 30
    ) -> List[Dict[str, Any]]:
        """Get contacts ready for outreach"""
        try:
            contacts = []
            cutoff_date = datetime.now() - timedelta(days=min_days_since_contact)

            with open(self.contacts_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    if len(contacts) >= limit:
                        break

                    email = row.get('Business Email', '').strip().lower()

                    # Skip if no email
                    if not email or '@' not in email:
                        continue

                    # Check if already contacted recently
                    contact_tracking = self.tracking["contacts"].get(email, {})
                    last_contacted = contact_tracking.get('last_contacted')

                    if last_contacted:
                        last_contact_date = datetime.fromisoformat(last_contacted)
                        if last_contact_date > cutoff_date:
                            continue  # Skip recently contacted

                    # Add to list
                    contacts.append({
                        'email': email,
                        'contact_name': row.get('Executive Name', ''),
                        'title': row.get('Title', ''),
                        'company_name': row.get('Hospital Name', ''),
                        'city': row.get('City', ''),
                        'state': row.get('State', ''),
                        'phone': row.get('Office Phone', ''),
                        'address': row.get('Address', ''),
                        'facility_type': row.get('Hospital Type', ''),
                        'organization_phone': row.get('Organization Phone', '')
                    })

            logger.info(f"Found {len(contacts)} contacts for outreach")
            return contacts

        except Exception as e:
            logger.error(f"Error getting contacts: {e}")
            return []

    def record_email_sent(
        self,
        email: str,
        campaign_data: Dict[str, Any]
    ) -> bool:
        """Record that an email was sent"""
        try:
            email = email.strip().lower()

            # Update contact tracking
            if email not in self.tracking["contacts"]:
                self.tracking["contacts"][email] = {
                    "email": email,
                    "email_count": 0,
                    "first_contacted": datetime.now().isoformat(),
                    "campaigns": []
                }

            contact = self.tracking["contacts"][email]
            contact["last_contacted"] = datetime.now().isoformat()
            contact["email_count"] += 1
            contact["campaigns"].append({
                "timestamp": datetime.now().isoformat(),
                "subject": campaign_data.get("subject", ""),
                "message_id": campaign_data.get("message_id", ""),
                "status": "sent"
            })

            self._save_tracking()
            logger.info(f"Recorded email sent to {email}")
            return True

        except Exception as e:
            logger.error(f"Error recording email: {e}")
            return False

    def record_email_error(
        self,
        email: str,
        error_message: str
    ) -> bool:
        """Record an email error"""
        try:
            email = email.strip().lower()

            if email not in self.tracking["contacts"]:
                self.tracking["contacts"][email] = {
                    "email": email,
                    "email_count": 0,
                    "campaigns": []
                }

            contact = self.tracking["contacts"][email]
            contact["last_error"] = {
                "timestamp": datetime.now().isoformat(),
                "error": error_message
            }

            self._save_tracking()
            return True

        except Exception as e:
            logger.error(f"Error recording error: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get campaign statistics"""
        try:
            total_contacts = self._count_contacts()
            contacted = len(self.tracking["contacts"])
            never_contacted = total_contacts - contacted

            # Count emails sent today
            today = datetime.now().date().isoformat()
            sent_today = sum(
                1 for contact in self.tracking["contacts"].values()
                for campaign in contact.get("campaigns", [])
                if campaign.get("timestamp", "").startswith(today)
            )

            return {
                "total_contacts": total_contacts,
                "contacted": contacted,
                "never_contacted": never_contacted,
                "sent_today": sent_today,
                "last_updated": self.tracking.get("last_updated", "Never")
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

    def start_campaign(self, campaign_name: str) -> str:
        """Start a new campaign"""
        campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        campaign = {
            "campaign_id": campaign_id,
            "name": campaign_name,
            "started_at": datetime.now().isoformat(),
            "emails_sent": 0,
            "emails_failed": 0,
            "status": "running"
        }

        self.tracking["campaigns"].append(campaign)
        self._save_tracking()

        logger.info(f"Started campaign: {campaign_id}")
        return campaign_id

    def end_campaign(
        self,
        campaign_id: str,
        emails_sent: int,
        emails_failed: int
    ):
        """End a campaign"""
        for campaign in self.tracking["campaigns"]:
            if campaign["campaign_id"] == campaign_id:
                campaign["ended_at"] = datetime.now().isoformat()
                campaign["emails_sent"] = emails_sent
                campaign["emails_failed"] = emails_failed
                campaign["status"] = "completed"
                break

        self._save_tracking()
        logger.info(f"Ended campaign: {campaign_id}")


# Test the storage system
if __name__ == "__main__":
    print("🧪 Testing Simple Storage")
    print("=" * 50)

    storage = SimpleStorage()

    # Get stats
    stats = storage.get_stats()
    print("\n📊 Storage Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Get sample contacts
    print("\n📋 Sample Contacts (first 5):")
    contacts = storage.get_contacts_for_outreach(limit=5)
    for i, contact in enumerate(contacts, 1):
        print(f"\n  {i}. {contact['contact_name']}")
        print(f"     Company: {contact['company_name']}")
        print(f"     Email: {contact['email']}")
        print(f"     Location: {contact['city']}, {contact['state']}")

    print("\n✅ Storage system working!")
