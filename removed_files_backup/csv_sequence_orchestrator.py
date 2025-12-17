#!/usr/bin/env python3
"""
CSV-Based Email Sequence Orchestrator for GFMD Narc Gone Campaign
Manages automated email sequences with CSV storage instead of MongoDB
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import json
import os
from simple_storage import SimpleStorage
from email_sequence_templates import EmailSequenceTemplates, SequenceState
from groq_email_composer_agent import GroqEmailComposerAgent
from automatic_email_sender import AutomaticEmailSender
import asyncio

logger = logging.getLogger(__name__)

class CSVSequenceOrchestrator:
    """Orchestrates automated email sequences using CSV storage"""
    
    def __init__(self):
        self.storage = SimpleStorage()
        self.templates = EmailSequenceTemplates()
        self.email_composer = GroqEmailComposerAgent(agent_id="sequence_composer")
        self.email_sender = AutomaticEmailSender()
        
        # Sequence settings
        self.default_sequence = "narc_gone_law_enforcement"
        self.check_replies = True
        
        # CSV files for sequence tracking
        self.sequence_file = "email_sequences.json"
        self.sequences = self._load_sequences()
        
        logger.info("✅ CSV Email Sequence Orchestrator initialized")
    
    def _load_sequences(self) -> Dict[str, Any]:
        """Load sequence states from JSON file"""
        try:
            if os.path.exists(self.sequence_file):
                with open(self.sequence_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading sequences: {e}")
            return {}
    
    def _save_sequences(self):
        """Save sequence states to JSON file"""
        try:
            with open(self.sequence_file, 'w') as f:
                json.dump(self.sequences, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving sequences: {e}")
    
    async def start_sequence(self, contact_email: str, sequence_name: str = None) -> Dict[str, Any]:
        """Start a new email sequence for a contact"""
        try:
            if not sequence_name:
                sequence_name = self.default_sequence
            
            # Check if contact already has active sequence
            existing_state = self._get_sequence_state(contact_email)
            if existing_state and existing_state.get("status") == "active":
                return {
                    "success": False,
                    "error": "Contact already has active sequence",
                    "current_step": existing_state.get("current_step", 0)
                }
            
            # Create new sequence state
            state = {
                "contact_email": contact_email,
                "sequence_name": sequence_name,
                "current_step": 0,
                "status": "active",
                "emails_sent": [],
                "last_email_sent": None,
                "next_email_due": datetime.now().isoformat(),  # Send first email immediately
                "reply_received": False,
                "reply_date": None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Save state
            self.sequences[contact_email] = state
            self._save_sequences()
            
            logger.info(f"📧 Started sequence '{sequence_name}' for contact {contact_email}")
            
            return {
                "success": True,
                "sequence_name": sequence_name,
                "contact_email": contact_email,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to start sequence: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_sequences(self) -> Dict[str, Any]:
        """Process all active sequences and send emails when due"""
        try:
            # Get all active sequences that are due for next email
            due_sequences = self._get_due_sequences()
            
            results = {
                "processed": 0,
                "sent": 0,
                "errors": 0,
                "completed": 0,
                "details": []
            }
            
            for contact_email, state in due_sequences.items():
                result = await self._process_single_sequence(contact_email, state)
                results["processed"] += 1
                
                if result.get("success"):
                    if result.get("action") == "sent":
                        results["sent"] += 1
                    elif result.get("action") == "completed":
                        results["completed"] += 1
                else:
                    results["errors"] += 1
                
                results["details"].append({
                    "contact_email": contact_email,
                    "step": state.get("current_step", 0) + 1,
                    "result": result
                })
            
            logger.info(f"📧 Processed {results['processed']} sequences, sent {results['sent']} emails")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to process sequences: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_reply(self, contact_email: str, reply_content: str, reply_date: datetime = None) -> Dict[str, Any]:
        """Handle reply from contact and pause sequence"""
        try:
            if not reply_date:
                reply_date = datetime.now()
            
            # Get sequence state
            state = self._get_sequence_state(contact_email)
            if not state:
                return {"success": False, "error": "No active sequence found"}
            
            # Update state
            state["status"] = "replied"
            state["reply_received"] = True
            state["reply_date"] = reply_date.isoformat()
            state["updated_at"] = datetime.now().isoformat()
            
            # Save state
            self.sequences[contact_email] = state
            self._save_sequences()
            
            # Add reply to tracking
            tracking = self.storage.get_contact_tracking(contact_email)
            if tracking:
                tracking["interactions"].append({
                    "type": "email_reply",
                    "content": reply_content,
                    "timestamp": reply_date.isoformat(),
                    "sequence_step": state.get("current_step", 0)
                })
                self.storage.update_contact_tracking(contact_email, tracking)
            
            logger.info(f"📬 Reply received from {contact_email}, sequence paused at step {state.get('current_step', 0)}")
            
            return {
                "success": True,
                "action": "paused",
                "contact_email": contact_email,
                "sequence_step": state.get("current_step", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to handle reply: {e}")
            return {"success": False, "error": str(e)}
    
    async def _process_single_sequence(self, contact_email: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single sequence and send next email if due"""
        try:
            # Check if reply was received
            if state.get("reply_received") or state.get("status") == "replied":
                return {"success": True, "action": "skipped", "reason": "reply_received"}
            
            # Get next email template
            next_step = state.get("current_step", 0) + 1
            template = self.templates.get_email_template(state.get("sequence_name"), next_step)
            
            if not template:
                # Sequence complete
                state["status"] = "completed"
                state["updated_at"] = datetime.now().isoformat()
                self.sequences[contact_email] = state
                self._save_sequences()
                return {"success": True, "action": "completed"}
            
            # Get contact data from CSV
            contact = self._get_contact_data(contact_email)
            if not contact:
                return {"success": False, "error": "Contact not found in CSV"}
            
            # Generate email
            email_result = await self._generate_sequence_email(contact, template, state)
            
            if not email_result.get("success"):
                return {"success": False, "error": email_result.get("error")}
            
            # Send email (dry run by default)
            send_result = await self._send_sequence_email(contact, email_result, template, state)
            
            if send_result.get("success"):
                # Update sequence state
                state["current_step"] = next_step
                state["last_email_sent"] = datetime.now().isoformat()
                if "emails_sent" not in state:
                    state["emails_sent"] = []
                
                state["emails_sent"].append({
                    "step": next_step,
                    "sent_at": datetime.now().isoformat(),
                    "subject": email_result.get("subject"),
                    "template_type": template.get("type")
                })
                
                # Schedule next email
                next_template = self.templates.get_email_template(state.get("sequence_name"), next_step + 1)
                if next_template:
                    wait_days = next_template.get("wait_days", 7)
                    next_due = datetime.now() + timedelta(days=wait_days)
                    state["next_email_due"] = next_due.isoformat()
                else:
                    state["next_email_due"] = None  # No more emails
                
                state["updated_at"] = datetime.now().isoformat()
                self.sequences[contact_email] = state
                self._save_sequences()
                
                return {"success": True, "action": "sent", "step": next_step}
            else:
                return {"success": False, "error": send_result.get("error")}
            
        except Exception as e:
            logger.error(f"❌ Failed to process sequence for {contact_email}: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_contact_data(self, contact_email: str) -> Optional[Dict[str, Any]]:
        """Get contact data from CSV"""
        try:
            # Load contacts from CSV
            contacts = self.storage.load_contacts()
            for contact in contacts:
                if contact.get("email", "").lower() == contact_email.lower():
                    return contact
            return None
        except Exception as e:
            logger.error(f"Error getting contact data: {e}")
            return None
    
    async def _generate_sequence_email(self, contact: Dict[str, Any], template: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate email content for sequence step"""
        try:
            # Build task for email composer with sequence context
            task = {
                "prospect_data": {
                    "contact_name": contact.get("contact_name", contact.get("name", "")),
                    "company_name": contact.get("organization", contact.get("company", "")),
                    "location": contact.get("location", ""),
                    "title": contact.get("title", ""),
                    "email": contact.get("email", "")
                },
                "research_findings": contact.get("research_insights", {}),
                "qualification_score": contact.get("qualification", {}),
                "sequence_context": {
                    "step": template["step"],
                    "type": template["type"],
                    "focus": template["focus"],
                    "tone": template["tone"],
                    "call_to_action": template["call_to_action"],
                    "is_follow_up": template["step"] > 1,
                    "previous_emails_sent": len(state.get("emails_sent", []))
                }
            }
            
            result = await self.email_composer.execute(task)
            
            return {
                "success": True,
                "subject": result.get("subject", ""),
                "body": result.get("body", ""),
                "template_step": template["step"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_sequence_email(self, contact: Dict[str, Any], email_content: Dict[str, Any], template: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Send the sequence email (or simulate)"""
        try:
            contact_email = contact.get("email", "")
            
            # For now, just log the email (dry run)
            logger.info(f"📧 [DRY RUN] Sending sequence email {template['step']} to {contact_email}")
            logger.info(f"   Subject: {email_content['subject']}")
            logger.info(f"   Type: {template['type']}")
            
            # Update tracking in CSV system
            tracking_data = {
                "contact_email": contact_email,
                "sequence_name": state.get("sequence_name"),
                "sequence_step": template["step"],
                "template_type": template["type"],
                "subject": email_content["subject"],
                "sent_at": datetime.now().isoformat(),
                "message_id": f"seq_{template['step']}_{contact_email}_{int(datetime.now().timestamp())}"
            }
            
            # Add to storage tracking
            tracking = self.storage.get_contact_tracking(contact_email)
            if not tracking:
                tracking = {"email": contact_email, "interactions": [], "sequences": []}
            
            tracking["interactions"].append({
                "type": "sequence_email_sent",
                "timestamp": datetime.now().isoformat(),
                **tracking_data
            })
            
            self.storage.update_contact_tracking(contact_email, tracking)
            
            return {"success": True, "message_id": tracking_data["message_id"]}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_due_sequences(self) -> Dict[str, Dict[str, Any]]:
        """Get all sequences that are due for next email"""
        try:
            now = datetime.now()
            due_sequences = {}
            
            for contact_email, state in self.sequences.items():
                if (state.get("status") == "active" and 
                    state.get("next_email_due") and
                    datetime.fromisoformat(state["next_email_due"]) <= now):
                    due_sequences[contact_email] = state
            
            return due_sequences
            
        except Exception as e:
            logger.error(f"❌ Failed to get due sequences: {e}")
            return {}
    
    def _get_sequence_state(self, contact_email: str) -> Optional[Dict[str, Any]]:
        """Get sequence state for a contact"""
        return self.sequences.get(contact_email)
    
    def get_sequence_stats(self) -> Dict[str, Any]:
        """Get sequence statistics"""
        try:
            total_sequences = len(self.sequences)
            active = sum(1 for s in self.sequences.values() if s.get("status") == "active")
            completed = sum(1 for s in self.sequences.values() if s.get("status") == "completed")
            replied = sum(1 for s in self.sequences.values() if s.get("status") == "replied")
            
            return {
                "success": True,
                "total_sequences": total_sequences,
                "active": active,
                "completed": completed,
                "replied": replied,
                "response_rate": round((replied / total_sequences * 100) if total_sequences > 0 else 0, 2)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    async def test():
        orchestrator = CSVSequenceOrchestrator()
        print("CSV Email Sequence Orchestrator initialized")
        
        # Test starting a sequence
        result = await orchestrator.start_sequence("test@example.com")
        print(f"Start sequence result: {result}")
        
        # Test processing sequences
        process_result = await orchestrator.process_sequences()
        print(f"Process result: {process_result}")
    
    asyncio.run(test())