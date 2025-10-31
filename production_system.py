#!/usr/bin/env python3
"""
Firestore-Enabled GFMD Production System
Uses Firestore database for contact management and email tracking
"""

import asyncio
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import vertexai
from google.cloud import firestore

from firestore_service import FirestoreService
from production_rag_a2a_system import ProductionGFMDSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Vertex AI
project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'windy-tiger-471523-m5')
vertexai.init(project=project_id, location='us-central1')

class FirestoreProductionSystem:
    """Production system using Firestore for contact management"""
    
    def __init__(self):
        # Set authentication - use local path if exists, otherwise rely on Cloud Run service account
        local_creds = '/Users/merandafreiner/gfmd_swarm_agent/google_sheets_credentials.json'
        if os.path.exists(local_creds):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = local_creds
        # Otherwise, Cloud Run will use the default service account
        
        self.target_daily_emails = 50
        self.firestore_service = FirestoreService()
        self.gfmd_system = ProductionGFMDSystem()
        
        # Daily stats
        self.daily_stats = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "emails_attempted": 0,
            "emails_successful": 0,
            "emails_failed": 0,
            "contacts_processed": 0,
            "research_completed": 0,
            "qualification_scores": []
        }
        
        logger.info("Firestore Production System initialized")
    
    async def run_daily_automation(self, num_prospects: int = 50) -> Dict[str, Any]:
        """
        Run daily automation using Firestore contacts
        
        Args:
            num_prospects: Number of emails to send (default 50)
        """
        try:
            logger.info(f"Starting daily automation for {num_prospects} emails")
            
            # Get contacts ready for outreach from Firestore
            contacts = self.firestore_service.get_contacts_for_outreach(limit=num_prospects)
            
            if not contacts:
                logger.warning("No contacts available for outreach")
                return {
                    "success": False,
                    "message": "No contacts available",
                    "stats": self.daily_stats
                }
            
            logger.info(f"Retrieved {len(contacts)} contacts from Firestore")
            
            # Process each contact through the A2A pipeline
            for i, contact in enumerate(contacts, 1):
                try:
                    logger.info(f"Processing contact {i}/{len(contacts)}: {contact['company_name']}")
                    
                    # Update stats
                    self.daily_stats["contacts_processed"] += 1
                    
                    # Convert Firestore contact to expected format
                    prospect_data = self._convert_firestore_contact(contact)
                    
                    # Run A2A agent pipeline through coordinator
                    result = await self.gfmd_system.coordinator._process_single_prospect(prospect_data)
                    
                    if result.get("success"):
                        # Update contact with research data
                        research_data = {
                            "pain_points": result.get("pain_points", []),
                            "qualification_score": result.get("qualification_score", 0),
                            "company_analysis": result.get("company_analysis", {}),
                            "research_summary": result.get("research_summary", "")
                        }
                        
                        self.firestore_service.update_contact_research(
                            contact['id'], 
                            research_data
                        )
                        
                        self.daily_stats["research_completed"] += 1
                        self.daily_stats["qualification_scores"].append(result.get("qualification_score", 0))
                        
                        # If qualified, send email
                        if result.get("qualification_score", 0) >= 7:
                            email_success = await self._send_personalized_email(contact, result)
                            
                            if email_success:
                                self.daily_stats["emails_successful"] += 1
                                logger.info(f"✅ Email sent successfully to {contact['company_name']}")
                            else:
                                self.daily_stats["emails_failed"] += 1
                                logger.warning(f"❌ Email failed for {contact['company_name']}")
                        else:
                            logger.info(f"⏭️  Contact not qualified (score: {result.get('qualification_score', 0)})")
                    
                    else:
                        logger.warning(f"❌ A2A processing failed for {contact['company_name']}")
                        self.daily_stats["emails_failed"] += 1
                        
                        # Record error in Firestore
                        self.firestore_service.record_email_error(
                            contact['id'],
                            result.get("error", "A2A processing failed")
                        )
                
                except Exception as e:
                    logger.error(f"Error processing contact {contact.get('company_name', 'Unknown')}: {e}")
                    self.daily_stats["emails_failed"] += 1
                    
                    # Record error in Firestore
                    if 'id' in contact:
                        self.firestore_service.record_email_error(contact['id'], str(e))
            
            # Update final stats
            self.daily_stats["emails_attempted"] = self.daily_stats["emails_successful"] + self.daily_stats["emails_failed"]
            
            # Log summary
            logger.info("="*50)
            logger.info("DAILY AUTOMATION COMPLETED")
            logger.info(f"Contacts processed: {self.daily_stats['contacts_processed']}")
            logger.info(f"Research completed: {self.daily_stats['research_completed']}")
            logger.info(f"Emails attempted: {self.daily_stats['emails_attempted']}")
            logger.info(f"Emails successful: {self.daily_stats['emails_successful']}")
            logger.info(f"Emails failed: {self.daily_stats['emails_failed']}")
            
            if self.daily_stats["qualification_scores"]:
                avg_score = sum(self.daily_stats["qualification_scores"]) / len(self.daily_stats["qualification_scores"])
                logger.info(f"Average qualification score: {avg_score:.1f}")
            
            success = self.daily_stats["emails_successful"] > 0
            
            return {
                "success": success,
                "message": f"Sent {self.daily_stats['emails_successful']} emails successfully",
                "stats": self.daily_stats
            }
            
        except Exception as e:
            logger.error(f"Daily automation failed: {e}")
            return {
                "success": False,
                "message": f"Automation failed: {e}",
                "stats": self.daily_stats
            }
    
    def _convert_firestore_contact(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Firestore contact format to expected A2A format"""
        return {
            "Company Name": contact.get("company_name", ""),
            "Contact Name": contact.get("contact_name", ""),
            "Email": contact.get("email", ""),
            "Phone": contact.get("phone", ""),
            "City": contact.get("city", ""),
            "State": contact.get("state", ""),
            "Title": contact.get("title", ""),
            "Address": contact.get("address", ""),
            
            # Include existing research if available
            "research_data": contact.get("research_data", {}),
            "pain_points": contact.get("pain_points", []),
            "qualification_score": contact.get("qualification_score", 0)
        }
    
    async def _send_personalized_email(self, contact: Dict[str, Any], ai_result: Dict[str, Any]) -> bool:
        """Send personalized email and record in Firestore"""
        try:
            # Extract email components from AI result
            email_data = {
                "subject": ai_result.get("email_subject", "Partnership Opportunity - GFMD Medical Devices"),
                "body": ai_result.get("email_body", ""),
                "personalization": {
                    "pain_points": ai_result.get("pain_points", []),
                    "company_analysis": ai_result.get("company_analysis", {}),
                    "qualification_score": ai_result.get("qualification_score", 0)
                }
            }
            
            # Send email via Gmail (using existing system)
            email_sent = await self._send_via_gmail(contact, email_data)
            
            if email_sent:
                # Record successful email in Firestore
                campaign_id = self.firestore_service.record_email_sent(contact['id'], email_data)
                logger.info(f"Email recorded in Firestore with campaign ID: {campaign_id}")
                return True
            else:
                # Record failure
                self.firestore_service.record_email_error(contact['id'], "Gmail send failed")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email to {contact.get('company_name', 'Unknown')}: {e}")
            self.firestore_service.record_email_error(contact['id'], str(e))
            return False
    
    async def _send_via_gmail(self, contact: Dict[str, Any], email_data: Dict[str, Any]) -> bool:
        """Send email via Gmail API with corrected verification and formatting"""
        try:
            # Import corrected email sender with verification and formatting
            from automatic_email_sender import AutomaticEmailSender
            
            # Initialize email sender
            email_sender = AutomaticEmailSender()
            
            # Convert contact to prospect format for verification and styling
            prospect = {
                'contact_name': contact.get('contact_name', ''),
                'email': contact.get('email', ''),
                'organization_name': contact.get('company_name', ''),
                'title': contact.get('title', ''),
                'location': f"{contact.get('city', '')}, {contact.get('state', '')}".strip(', '),
                'pain_point': 'laboratory noise and operational efficiency challenges',
                'facility_type': 'healthcare facility',
                'budget_range': 'operational improvement',
                'department': 'laboratory operations'
            }
            
            # Send email with verification and corrected formatting
            result = email_sender.send_email_to_prospect(prospect)
            
            if result.get('success'):
                logger.info(f"Email sent successfully: {result.get('message_id')}")
                return True
            else:
                logger.error(f"Email failed: {result.get('message')}")
                return False
            
        except Exception as e:
            logger.error(f"Gmail send error: {e}")
            return False
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """Get today's statistics from Firestore"""
        try:
            firestore_stats = self.firestore_service.get_daily_stats()
            
            # Combine with current session stats
            combined_stats = {
                **self.daily_stats,
                "firestore_total_contacts": firestore_stats.get("total_contacts", 0),
                "firestore_pending_contacts": firestore_stats.get("pending_contacts", 0),
                "firestore_emails_sent_today": firestore_stats.get("emails_sent_today", 0)
            }
            
            return combined_stats
            
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return self.daily_stats

async def main():
    """Test the Firestore production system"""
    try:
        system = FirestoreProductionSystem()
        
        # Test with 5 contacts first
        result = await system.run_daily_automation(num_prospects=5)
        
        print("\n" + "="*50)
        print("FIRESTORE PRODUCTION SYSTEM TEST")
        print("="*50)
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        print("\nStats:")
        for key, value in result['stats'].items():
            print(f"  {key}: {value}")
        
        # Get updated stats
        final_stats = system.get_daily_stats()
        print("\nFinal Firestore Stats:")
        for key, value in final_stats.items():
            if key.startswith('firestore_'):
                print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())