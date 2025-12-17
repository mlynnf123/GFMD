#!/usr/bin/env python3
"""
Production Email Sequence Runner
Sends automated email sequences using MongoDB and Groq AI
"""

import os
import asyncio
from datetime import datetime, timedelta
from mongodb_storage import MongoDBStorage
from email_sequence_templates import EmailSequenceTemplates
from groq_email_composer_agent import GroqEmailComposerAgent
from automatic_email_sender import AutomaticEmailSender

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

class ProductionSequenceRunner:
    """Production email sequence automation"""
    
    def __init__(self):
        self.storage = MongoDBStorage()
        self.templates = EmailSequenceTemplates()
        self.email_composer = GroqEmailComposerAgent(agent_id="prod_composer")
        self.email_sender = AutomaticEmailSender()
        
    def start_sequence_for_contact(self, contact_email: str) -> dict:
        """Start email sequence for a contact (sync version)"""
        try:
            # Get contact from database
            contact = self.storage.find_contact_by_email(contact_email)
            if not contact:
                return {"success": False, "error": "Contact not found"}
            
            # Check if sequence already exists
            existing = self.storage.db.email_sequences.find_one({"contact_id": str(contact["_id"])})
            if existing and existing.get("status") == "active":
                return {"success": False, "error": "Sequence already active"}
            
            # Create sequence state
            sequence_state = {
                'contact_id': str(contact["_id"]),
                'contact_email': contact_email,
                'sequence_name': 'narc_gone_law_enforcement',
                'current_step': 0,
                'status': 'active',
                'emails_sent': [],
                'last_email_sent': None,
                'next_email_due': datetime.now().isoformat(),
                'reply_received': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Save to database
            result = self.storage.db.email_sequences.update_one(
                {"contact_id": str(contact["_id"])},
                {"$set": sequence_state},
                upsert=True
            )
            
            print(f"✅ Started sequence for {contact_email}")
            return {"success": True, "contact_id": str(contact["_id"])}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def process_due_sequences(self) -> dict:
        """Process all sequences that are due for next email"""
        try:
            now = datetime.now()
            
            # Find due sequences
            due_sequences = list(self.storage.db.email_sequences.find({
                "status": "active",
                "next_email_due": {"$lte": now.isoformat()}
            }))
            
            results = {"processed": 0, "sent": 0, "errors": 0, "details": []}
            
            for sequence in due_sequences:
                try:
                    result = await self._process_single_sequence(sequence)
                    results["processed"] += 1
                    
                    if result.get("success"):
                        if result.get("action") == "sent":
                            results["sent"] += 1
                    else:
                        results["errors"] += 1
                    
                    results["details"].append({
                        "contact_email": sequence.get("contact_email"),
                        "step": sequence.get("current_step", 0) + 1,
                        "result": result
                    })
                    
                except Exception as e:
                    results["errors"] += 1
                    print(f"❌ Error processing sequence: {e}")
            
            print(f"📧 Processed {results['processed']} sequences, sent {results['sent']} emails")
            return results
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_single_sequence(self, sequence: dict) -> dict:
        """Process a single email sequence"""
        try:
            contact_id = sequence["contact_id"]
            current_step = sequence.get("current_step", 0)
            next_step = current_step + 1
            
            # Get email template
            template = self.templates.get_email_template("narc_gone_law_enforcement", next_step)
            if not template:
                # Sequence complete
                self.storage.db.email_sequences.update_one(
                    {"contact_id": contact_id},
                    {"$set": {"status": "completed", "updated_at": datetime.now().isoformat()}}
                )
                return {"success": True, "action": "completed"}
            
            # Get contact data
            contact = self.storage.get_contact(contact_id)
            if not contact:
                return {"success": False, "error": "Contact not found"}
            
            # Generate email
            task = {
                "prospect_data": {
                    "contact_name": contact.get("name", ""),
                    "company_name": contact.get("organization", ""),
                    "location": contact.get("location", ""),
                    "title": contact.get("title", ""),
                    "email": contact.get("email", "")
                },
                "sequence_context": {
                    "step": template["step"],
                    "type": template["type"],
                    "focus": template["focus"],
                    "tone": template["tone"],
                    "call_to_action": template["call_to_action"],
                    "is_follow_up": template["step"] > 1,
                    "previous_emails_sent": len(sequence.get("emails_sent", []))
                }
            }
            
            email_result = await self.email_composer.execute(task)
            
            if not email_result.get("subject") or not email_result.get("body"):
                return {"success": False, "error": "Email generation failed"}
            
            # For now, log the email (add actual sending when Gmail is configured)
            print(f"📧 [DRY RUN] Would send email {next_step} to {contact.get('email')}")
            print(f"   Subject: {email_result.get('subject')}")
            
            # Update sequence state
            emails_sent = sequence.get("emails_sent", [])
            emails_sent.append({
                "step": next_step,
                "sent_at": datetime.now().isoformat(),
                "subject": email_result.get("subject"),
                "template_type": template.get("type")
            })
            
            # Calculate next email due date
            next_template = self.templates.get_email_template("narc_gone_law_enforcement", next_step + 1)
            if next_template:
                wait_days = next_template.get("wait_days", 7)
                next_due = datetime.now() + timedelta(days=wait_days)
                next_email_due = next_due.isoformat()
            else:
                next_email_due = None
            
            # Update database
            self.storage.db.email_sequences.update_one(
                {"contact_id": contact_id},
                {"$set": {
                    "current_step": next_step,
                    "last_email_sent": datetime.now().isoformat(),
                    "emails_sent": emails_sent,
                    "next_email_due": next_email_due,
                    "updated_at": datetime.now().isoformat()
                }}
            )
            
            return {"success": True, "action": "sent", "step": next_step}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_sequence_stats(self) -> dict:
        """Get sequence statistics"""
        try:
            total = self.storage.db.email_sequences.count_documents({})
            active = self.storage.db.email_sequences.count_documents({"status": "active"})
            completed = self.storage.db.email_sequences.count_documents({"status": "completed"})
            replied = self.storage.db.email_sequences.count_documents({"status": "replied"})
            
            return {
                "success": True,
                "total_sequences": total,
                "active": active,
                "completed": completed,
                "replied": replied,
                "response_rate": round((replied / total * 100) if total > 0 else 0, 2)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

async def main():
    """Main function for running sequences"""
    import sys
    
    runner = ProductionSequenceRunner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "start" and len(sys.argv) > 2:
            email = sys.argv[2]
            result = runner.start_sequence_for_contact(email)
            print(f"Start sequence result: {result}")
            
        elif command == "process":
            result = await runner.process_due_sequences()
            print(f"Process result: {result}")
            
        elif command == "stats":
            stats = runner.get_sequence_stats()
            print(f"Stats: {stats}")
            
        else:
            print("Usage:")
            print("  python3 production_sequence_runner.py start <email>")
            print("  python3 production_sequence_runner.py process")
            print("  python3 production_sequence_runner.py stats")
    else:
        # Default: process sequences
        result = await runner.process_due_sequences()
        print(f"Process result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
