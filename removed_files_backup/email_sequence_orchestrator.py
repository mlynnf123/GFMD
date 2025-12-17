#!/usr/bin/env python3
"""
Email Sequence Orchestrator for GFMD Narc Gone Campaign
Manages automated email sequences with timing, reply detection, and follow-ups
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from mongodb_storage import MongoDBStorage
from email_sequence_templates import EmailSequenceTemplates, SequenceState
from groq_email_composer_agent import GroqEmailComposerAgent
from automatic_email_sender import AutomaticEmailSender
import asyncio
import json

logger = logging.getLogger(__name__)

class EmailSequenceOrchestrator:
    """Orchestrates automated email sequences with timing and reply handling"""
    
    def __init__(self):
        self.storage = MongoDBStorage()
        self.templates = EmailSequenceTemplates()
        self.email_composer = GroqEmailComposerAgent(agent_id="sequence_composer")
        self.email_sender = AutomaticEmailSender()
        
        # Sequence settings
        self.default_sequence = "narc_gone_law_enforcement"
        self.check_replies = True
        
        logger.info("✅ Email Sequence Orchestrator initialized")
    
    async def start_sequence(self, contact_id: str, sequence_name: str = None) -> Dict[str, Any]:
        """Start a new email sequence for a contact"""
        try:
            if not sequence_name:
                sequence_name = self.default_sequence
            
            # Check if contact already has active sequence
            existing_state = await self._get_sequence_state(contact_id)
            if existing_state and existing_state.status == "active":
                return {
                    "success": False,
                    "error": "Contact already has active sequence",
                    "current_step": existing_state.current_step
                }
            
            # Create new sequence state
            state = SequenceState(contact_id, sequence_name)
            state.status = "active"
            state.next_email_due = datetime.now()  # Send first email immediately
            
            # Save state
            await self._save_sequence_state(state)
            
            logger.info(f"📧 Started sequence '{sequence_name}' for contact {contact_id}")
            
            return {
                "success": True,
                "sequence_name": sequence_name,
                "contact_id": contact_id,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to start sequence: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_sequences(self) -> Dict[str, Any]:
        """Process all active sequences and send emails when due"""
        try:
            # Get all active sequences that are due for next email
            due_sequences = await self._get_due_sequences()
            
            results = {
                "processed": 0,
                "sent": 0,
                "errors": 0,
                "completed": 0,
                "details": []
            }
            
            for state in due_sequences:
                result = await self._process_single_sequence(state)
                results["processed"] += 1
                
                if result.get("success"):
                    if result.get("action") == "sent":
                        results["sent"] += 1
                    elif result.get("action") == "completed":
                        results["completed"] += 1
                else:
                    results["errors"] += 1
                
                results["details"].append({
                    "contact_id": state.contact_id,
                    "step": state.current_step + 1,
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
            
            # Find contact by email
            contact = await self.storage.find_contact_by_email(contact_email)
            if not contact:
                return {"success": False, "error": "Contact not found"}
            
            # Get sequence state
            state = await self._get_sequence_state(contact["_id"])
            if not state:
                return {"success": False, "error": "No active sequence found"}
            
            # Update state
            state.status = "replied"
            state.reply_received = True
            state.reply_date = reply_date
            state.updated_at = datetime.now()
            
            # Save state
            await self._save_sequence_state(state)
            
            # Log interaction
            await self.storage.log_interaction(
                contact["_id"],
                "email_reply",
                {"reply_content": reply_content, "sequence_step": state.current_step}
            )
            
            logger.info(f"📬 Reply received from {contact_email}, sequence paused at step {state.current_step}")
            
            return {
                "success": True,
                "action": "paused",
                "contact_id": contact["_id"],
                "sequence_step": state.current_step
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to handle reply: {e}")
            return {"success": False, "error": str(e)}
    
    async def _process_single_sequence(self, state: SequenceState) -> Dict[str, Any]:
        """Process a single sequence and send next email if due"""
        try:
            # Check if reply was received
            if state.reply_received or state.status == "replied":
                return {"success": True, "action": "skipped", "reason": "reply_received"}
            
            # Get next email template
            next_step = state.current_step + 1
            template = self.templates.get_email_template(state.sequence_name, next_step)
            
            if not template:
                # Sequence complete
                state.status = "completed"
                state.updated_at = datetime.now()
                await self._save_sequence_state(state)
                return {"success": True, "action": "completed"}
            
            # Get contact data
            contact = await self.storage.get_contact(state.contact_id)
            if not contact:
                return {"success": False, "error": "Contact not found"}
            
            # Generate email
            email_result = await self._generate_sequence_email(contact, template, state)
            
            if not email_result.get("success"):
                return {"success": False, "error": email_result.get("error")}
            
            # Send email
            send_result = await self._send_sequence_email(contact, email_result, template, state)
            
            if send_result.get("success"):
                # Update sequence state
                state.current_step = next_step
                state.last_email_sent = datetime.now()
                state.emails_sent.append({
                    "step": next_step,
                    "sent_at": datetime.now().isoformat(),
                    "subject": email_result.get("subject"),
                    "template_type": template.get("type")
                })
                
                # Schedule next email
                next_template = self.templates.get_email_template(state.sequence_name, next_step + 1)
                if next_template:
                    wait_days = next_template.get("wait_days", 7)
                    state.next_email_due = datetime.now() + timedelta(days=wait_days)
                else:
                    state.next_email_due = None  # No more emails
                
                state.updated_at = datetime.now()
                await self._save_sequence_state(state)
                
                return {"success": True, "action": "sent", "step": next_step}
            else:
                return {"success": False, "error": send_result.get("error")}
            
        except Exception as e:
            logger.error(f"❌ Failed to process sequence for {state.contact_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_sequence_email(self, contact: Dict[str, Any], template: Dict[str, Any], state: SequenceState) -> Dict[str, Any]:
        """Generate email content for sequence step"""
        try:
            # Build task for email composer with sequence context
            task = {
                "prospect_data": {
                    "contact_name": contact.get("name", ""),
                    "company_name": contact.get("organization", ""),
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
                    "previous_emails_sent": len(state.emails_sent)
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
    
    async def _send_sequence_email(self, contact: Dict[str, Any], email_content: Dict[str, Any], template: Dict[str, Any], state: SequenceState) -> Dict[str, Any]:
        """Send the sequence email"""
        try:
            # Use the automatic email sender
            send_result = self.email_sender.send_email(
                to_email=contact["email"],
                subject=email_content["subject"],
                body=email_content["body"],
                tracking_data={
                    "contact_id": contact["_id"],
                    "sequence_name": state.sequence_name,
                    "sequence_step": template["step"],
                    "template_type": template["type"]
                }
            )
            
            if send_result.get("success"):
                # Log interaction
                await self.storage.log_interaction(
                    contact["_id"],
                    "email_sent",
                    {
                        "sequence_step": template["step"],
                        "template_type": template["type"],
                        "subject": email_content["subject"],
                        "message_id": send_result.get("message_id")
                    }
                )
            
            return send_result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_due_sequences(self) -> List[SequenceState]:
        """Get all sequences that are due for next email"""
        try:
            now = datetime.now()
            
            # Query MongoDB for due sequences
            cursor = self.storage.db.email_sequences.find({
                "status": "active",
                "next_email_due": {"$lte": now}
            })
            
            sequences = []
            async for doc in cursor:
                state = SequenceState.from_dict(doc)
                sequences.append(state)
            
            return sequences
            
        except Exception as e:
            logger.error(f"❌ Failed to get due sequences: {e}")
            return []
    
    async def _get_sequence_state(self, contact_id: str) -> Optional[SequenceState]:
        """Get sequence state for a contact"""
        try:
            doc = await self.storage.db.email_sequences.find_one({"contact_id": contact_id})
            if doc:
                return SequenceState.from_dict(doc)
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get sequence state: {e}")
            return None
    
    async def _save_sequence_state(self, state: SequenceState):
        """Save sequence state to MongoDB"""
        try:
            await self.storage.db.email_sequences.update_one(
                {"contact_id": state.contact_id},
                {"$set": state.to_dict()},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to save sequence state: {e}")
            raise

if __name__ == "__main__":
    async def test():
        orchestrator = EmailSequenceOrchestrator()
        print("Email Sequence Orchestrator initialized")
        
    import asyncio
    asyncio.run(test())