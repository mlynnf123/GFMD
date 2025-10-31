"""
GFMD Firestore Database Service
Manages healthcare contacts and email campaign data in Google Cloud Firestore
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from google.cloud import firestore
from google.cloud.firestore import Client
import json

logger = logging.getLogger(__name__)

class FirestoreService:
    def __init__(self, project_id: str = "windy-tiger-471523-m5"):
        """Initialize Firestore client"""
        self.project_id = project_id
        self.client: Client = firestore.Client(project=project_id)
        
        # Collection references
        self.contacts_ref = self.client.collection('healthcare_contacts')
        self.campaigns_ref = self.client.collection('email_campaigns')
        self.system_ref = self.client.collection('system_state')
        
        logger.info(f"Firestore service initialized for project: {project_id}")
    
    def add_contact(self, contact_data: Dict[str, Any]) -> str:
        """Add a new healthcare contact to Firestore"""
        try:
            # Create contact document with standardized fields
            contact_doc = {
                'email': contact_data.get('Business Email', '').lower().strip(),
                'company_name': contact_data.get('Hospital Name', ''),
                'contact_name': contact_data.get('Executive Name', ''),
                'city': contact_data.get('City', ''),
                'state': contact_data.get('State', ''),
                'phone': contact_data.get('Office Phone', ''),
                'title': contact_data.get('Title', ''),
                'address': contact_data.get('Address', ''),
                
                # Research and AI fields
                'research_completed': False,
                'research_data': {},
                'pain_points': [],
                'qualification_score': 0,
                'company_analysis': {},
                
                # Email tracking
                'last_contacted': None,
                'email_sent_count': 0,
                'email_status': 'pending',  # pending, sent, bounced, opted_out
                'next_contact_date': None,
                
                # Metadata
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'source': 'definitive_healthcare'
            }
            
            # Use email as document ID for easy deduplication
            doc_id = contact_data.get('Business Email', '').lower().strip()
            if not doc_id:
                raise ValueError("Email is required for contact creation")
            
            doc_ref = self.contacts_ref.document(doc_id)
            doc_ref.set(contact_doc)
            
            logger.info(f"Added contact: {contact_doc['company_name']} ({doc_id})")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding contact: {e}")
            raise
    
    def get_contacts_for_outreach(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get contacts that are ready for email outreach - SIMPLIFIED VERSION"""
        try:
            # TEMPORARY FIX: Get ANY contacts with emails, ignore status fields
            logger.info(f"Getting contacts for outreach (limit: {limit})...")
            
            # Get contacts that have emails and haven't been contacted recently
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            # Try simple query first - just get contacts with emails
            simple_query = (self.contacts_ref
                          .where('email', '!=', '')
                          .limit(limit * 2))  # Get more to filter later
            
            contacts = []
            
            # Get contacts and do basic filtering
            for doc in simple_query.stream():
                if len(contacts) >= limit:
                    break
                    
                contact_data = doc.to_dict()
                contact_data['contact_id'] = doc.id
                
                # Basic checks
                email = contact_data.get('email', '').strip()
                if not email or '@' not in email:
                    continue
                    
                # Check if contacted recently (if field exists)
                last_contacted = contact_data.get('last_contacted')
                if last_contacted and hasattr(last_contacted, 'timestamp'):
                    last_contact_date = datetime.fromtimestamp(last_contacted.timestamp())
                    if last_contact_date > thirty_days_ago:
                        continue  # Skip recently contacted
                
                contacts.append(contact_data)
            
            logger.info(f"Found {len(contacts)} contacts available for outreach")
            return contacts[:limit]
            
        except Exception as e:
            logger.error(f"Error getting contacts for outreach: {e}")
            return []
    
    def update_contact_research(self, contact_id: str, research_data: Dict[str, Any]) -> bool:
        """Update contact with research findings"""
        try:
            doc_ref = self.contacts_ref.document(contact_id)
            
            update_data = {
                'research_completed': True,
                'research_data': research_data,
                'pain_points': research_data.get('pain_points', []),
                'qualification_score': research_data.get('qualification_score', 0),
                'company_analysis': research_data.get('company_analysis', {}),
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            doc_ref.update(update_data)
            logger.info(f"Updated research data for contact: {contact_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating contact research: {e}")
            return False
    
    def record_email_sent(self, contact_id: str, email_data: Dict[str, Any]) -> str:
        """Record that an email was sent to a contact"""
        try:
            # Update contact record
            contact_ref = self.contacts_ref.document(contact_id)
            contact_ref.update({
                'last_contacted': firestore.SERVER_TIMESTAMP,
                'email_sent_count': firestore.Increment(1),
                'email_status': 'sent',
                'next_contact_date': datetime.now() + timedelta(days=30),
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            # Create campaign record
            campaign_doc = {
                'contact_id': contact_id,
                'email_subject': email_data.get('subject', ''),
                'email_body': email_data.get('body', ''),
                'personalization_data': email_data.get('personalization', {}),
                'sent_at': firestore.SERVER_TIMESTAMP,
                'status': 'sent',
                'gmail_message_id': email_data.get('message_id', ''),
                'campaign_type': 'daily_outreach'
            }
            
            campaign_ref = self.campaigns_ref.add(campaign_doc)
            campaign_id = campaign_ref[1].id
            
            logger.info(f"Recorded email sent for contact: {contact_id}")
            return campaign_id
            
        except Exception as e:
            logger.error(f"Error recording email sent: {e}")
            return ""
    
    def record_email_error(self, contact_id: str, error_message: str) -> bool:
        """Record that an email failed to send"""
        try:
            contact_ref = self.contacts_ref.document(contact_id)
            contact_ref.update({
                'email_status': 'error',
                'last_error': error_message,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"Recorded email error for contact: {contact_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording email error: {e}")
            return False
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """Get statistics for today's email campaign"""
        try:
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            
            # Count emails sent today
            sent_today_query = (self.campaigns_ref
                              .where('sent_at', '>=', today_start)
                              .where('status', '==', 'sent'))
            
            sent_count = len(list(sent_today_query.stream()))
            
            # Count pending contacts
            pending_query = self.contacts_ref.where('email_status', '==', 'pending')
            pending_count = len(list(pending_query.stream()))
            
            # Count total contacts
            total_contacts = len(list(self.contacts_ref.stream()))
            
            stats = {
                'emails_sent_today': sent_count,
                'pending_contacts': pending_count,
                'total_contacts': total_contacts,
                'last_updated': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return {}
    
    def bulk_import_contacts(self, contacts_list: List[Dict[str, Any]]) -> Dict[str, int]:
        """Bulk import contacts from CSV data"""
        try:
            batch = self.client.batch()
            imported = 0
            skipped = 0
            errors = 0
            
            for contact_data in contacts_list:
                try:
                    email = contact_data.get('Business Email', '').lower().strip()
                    if not email:
                        skipped += 1
                        continue
                    
                    # Check if contact already exists
                    existing_doc = self.contacts_ref.document(email).get()
                    if existing_doc.exists:
                        skipped += 1
                        continue
                    
                    # Create contact document
                    contact_doc = {
                        'email': email,
                        'company_name': contact_data.get('Hospital Name', ''),
                        'contact_name': contact_data.get('Executive Name', ''),
                        'city': contact_data.get('City', ''),
                        'state': contact_data.get('State', ''),
                        'phone': contact_data.get('Office Phone', ''),
                        'title': contact_data.get('Title', ''),
                        'address': contact_data.get('Address', ''),
                        
                        # Initialize fields
                        'research_completed': False,
                        'research_data': {},
                        'pain_points': [],
                        'qualification_score': 0,
                        'company_analysis': {},
                        'last_contacted': None,
                        'email_sent_count': 0,
                        'email_status': 'pending',
                        'next_contact_date': None,
                        'created_at': firestore.SERVER_TIMESTAMP,
                        'updated_at': firestore.SERVER_TIMESTAMP,
                        'source': 'definitive_healthcare'
                    }
                    
                    doc_ref = self.contacts_ref.document(email)
                    batch.set(doc_ref, contact_doc)
                    imported += 1
                    
                    # Commit batch every 500 operations
                    if imported % 500 == 0:
                        batch.commit()
                        batch = self.client.batch()
                        logger.info(f"Imported {imported} contacts so far...")
                        
                except Exception as e:
                    logger.error(f"Error processing contact {contact_data}: {e}")
                    errors += 1
            
            # Commit remaining operations
            if imported % 500 != 0:
                batch.commit()
            
            results = {
                'imported': imported,
                'skipped': skipped,
                'errors': errors
            }
            
            logger.info(f"Bulk import completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk import: {e}")
            return {'imported': 0, 'skipped': 0, 'errors': 1}