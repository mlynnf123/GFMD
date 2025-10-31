#!/usr/bin/env python3
"""
Simplified Cloud Run main that bypasses Google Sheets dependencies
"""
import asyncio
import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify

# Set up the environment for Google Cloud
os.environ['GOOGLE_CLOUD_PROJECT'] = 'windy-tiger-471523-m5'

# Add path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from firestore_service import FirestoreService
from automatic_email_sender import AutomaticEmailSender

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

class CloudRunEmailSystem:
    """Simplified email system for Cloud Run"""
    
    def __init__(self):
        self.firestore_service = FirestoreService()
        self.email_sender = AutomaticEmailSender()
        
    async def run_email_campaign(self, num_prospects=10):
        """Run email campaign without complex AI processing"""
        results = {
            "contacts_processed": 0,
            "emails_sent": 0,
            "emails_failed": 0,
            "execution_time": None,
            "success": False
        }
        
        start_time = datetime.now()
        
        try:
            # Get contacts from Firestore
            contacts = self.firestore_service.get_contacts_for_outreach(limit=num_prospects)
            logger.info(f"Retrieved {len(contacts)} contacts for email campaign")
            
            for contact in contacts:
                try:
                    results["contacts_processed"] += 1
                    
                    # Prepare prospect data
                    prospect = {
                        "contact_name": f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
                        "email": contact['email'],
                        "organization_name": contact['company_name'],
                        "title": contact.get('title', 'Healthcare Professional')
                    }
                    
                    # Send email
                    result = self.email_sender.send_email_to_prospect(prospect)
                    
                    if result.get("success"):
                        results["emails_sent"] += 1
                        logger.info(f"Email sent to {contact['email']}")
                        
                        # Update Firestore
                        self.firestore_service.record_email_sent(
                            contact['email'],
                            {
                                "subject": f"Laboratory Equipment Discussion - {contact['company_name']}",
                                "timestamp": datetime.now().isoformat(),
                                "recipient": contact['email'],
                                "message_id": result.get('message_id')
                            }
                        )
                    else:
                        results["emails_failed"] += 1
                        logger.error(f"Email failed for {contact['email']}: {result.get('message', 'Unknown error')}")
                        self.firestore_service.record_email_error(
                            contact['email'],
                            result.get('message', 'Send failed')
                        )
                        
                except Exception as e:
                    results["emails_failed"] += 1
                    logger.error(f"Error processing contact {contact.get('email', 'Unknown')}: {e}")
                    
            end_time = datetime.now()
            results["execution_time"] = str(end_time - start_time)
            results["success"] = results["emails_sent"] > 0
            
            logger.info(f"Campaign completed: {results['emails_sent']} emails sent, {results['emails_failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Campaign failed: {e}")
            results["error"] = str(e)
            return results

# Initialize the system
email_system = CloudRunEmailSystem()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "service": "GFMD AI Swarm Agent",
        "status": "healthy",
        "version": "2.2-cloud-run",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/v1/automation/daily-run', methods=['POST'])
def api_daily_run():
    """Cloud Run daily automation endpoint"""
    try:
        logger.info("Cloud Scheduler triggered daily automation")
        
        # Get request data
        data = request.get_json() or {}
        num_prospects = data.get('num_prospects', 10)
        
        # Run email campaign
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                email_system.run_email_campaign(num_prospects=num_prospects)
            )
        finally:
            loop.close()
        
        return jsonify({
            "success": results.get("success", False),
            "system": "cloud-run-firestore",
            "timestamp": datetime.now().isoformat(),
            "triggered_by": "cloud_scheduler_api",
            "results": results
        })
        
    except Exception as e:
        logger.error(f"API automation failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "system": "cloud-run-firestore",
            "timestamp": datetime.now().isoformat(),
            "triggered_by": "cloud_scheduler_api"
        }), 500

@app.route('/api/v1/stats', methods=['GET'])
def api_stats():
    """System statistics endpoint"""
    try:
        # Get basic stats from Firestore
        contacts = email_system.firestore_service.get_contacts_for_outreach(limit=1)
        
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "system": "cloud-run-firestore",
            "stats": {
                "contacts_available": len(contacts) > 0,
                "email_system": "operational",
                "firestore": "connected"
            }
        })
        
    except Exception as e:
        logger.error(f"Stats failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))