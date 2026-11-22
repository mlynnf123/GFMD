#!/usr/bin/env python3
"""
Complete Email Sequence Automation System
Ready-to-use email sequence automation with MongoDB, Gmail, and Groq AI
"""

import os
import asyncio
import schedule
import time
import threading
import random
import numpy as np
from datetime import datetime, timedelta
from mongodb_storage import MongoDBStorage
from email_sequence_templates import EmailSequenceTemplates
from groq_email_composer_agent import GroqEmailComposerAgent
from gmail_integration import GmailIntegration
from business_day_utils import BusinessDayCalculator

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

class CompleteSequenceAutomation:
    """Complete email sequence automation system"""

    # Campaigns that should NOT auto-add new contacts
    PAUSED_CAMPAIGNS = {"narc_gone", "spectrum"}

    # Map campaign names to their sequence template names
    CAMPAIGN_SEQUENCE_MAP = {
        "narc_gone": "narc_gone_law_enforcement",
        "centrifuge": "centrifuge_hospital_labs",
        "spectrum": "spectrum_snf_ltc",
    }

    def __init__(self):
        print("Initializing Complete Email Sequence Automation...")

        self.storage = MongoDBStorage()
        self.templates = EmailSequenceTemplates()
        self.email_composer = GroqEmailComposerAgent(agent_id="automation_composer")
        self.gmail = GmailIntegration()
        self.business_day_calc = BusinessDayCalculator()

        # Initialize auto-reply system
        try:
            from ai_auto_reply_system import AIAutoReplySystem
            self.auto_reply_system = AIAutoReplySystem()
        except ImportError:
            self.auto_reply_system = None
            print("Auto-reply system not available")

        print("All components initialized successfully")
        print(f"Gmail: {self.gmail.service is not None}")
        print(f"MongoDB: Connected to {self.storage.db.name}")
        
    def _strip_email_boilerplate(self, body: str) -> str:
        """Strip greeting and signature, returning only the pitch content for comparison"""
        if not body:
            return ""
        lines = body.strip().split('\n')
        # Strip "Hi Name," greeting
        start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("Hi ") and line.strip().endswith(","):
                start = i + 1
                break
        # Strip everything from "Best," onward
        end = len(lines)
        for i, line in enumerate(lines):
            if line.strip() == "Best,":
                end = i
                break
        pitch_lines = [l.strip() for l in lines[start:end] if l.strip()]
        return " ".join(pitch_lines)

    def _check_email_similarity(self, new_email: dict, previous_emails: list) -> dict:
        """Check if the new email is too similar to any previously sent email using embeddings"""
        try:
            if not self.email_composer.rag_system:
                return {"similar": False}

            new_pitch = self._strip_email_boilerplate(new_email.get("body", ""))
            if not new_pitch:
                return {"similar": False}

            new_embedding = self.email_composer.rag_system.generate_embedding(new_pitch)
            if new_embedding is None:
                return {"similar": False}

            max_similarity = 0.0
            most_similar_step = 0

            for prev in previous_emails:
                prev_pitch = self._strip_email_boilerplate(prev.get("body", ""))
                if not prev_pitch:
                    continue
                prev_embedding = self.email_composer.rag_system.generate_embedding(prev_pitch)
                if prev_embedding is None:
                    continue
                similarity = float(np.dot(new_embedding, prev_embedding))
                if similarity > max_similarity:
                    max_similarity = similarity
                    most_similar_step = prev.get("step", 0)

            return {
                "similar": max_similarity >= 0.75,
                "max_similarity": round(max_similarity, 4),
                "most_similar_step": most_similar_step
            }
        except Exception as e:
            print(f"   Similarity check failed ({e}), proceeding with send")
            return {"similar": False}

    def add_contact_and_start_sequence(self, contact_data: dict) -> dict:
        """Add a contact and start email sequence"""
        try:
            # Add contact to database
            contact_id = self.storage.add_contact(contact_data)
            print(f"✅ Added contact: {contact_data.get('name')} -> {contact_id}")
            
            # Start sequence
            result = self.start_sequence_for_contact(str(contact_id))
            
            if result.get("success"):
                print(f"📧 Started sequence for {contact_data.get('email')}")
                return {"success": True, "contact_id": str(contact_id), "sequence_started": True}
            else:
                return {"success": False, "error": result.get("error")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def start_sequence_for_contact(self, contact_id: str, campaign: str = "narc_gone") -> dict:
        """Start email sequence for existing contact"""
        if campaign not in self.CAMPAIGN_SEQUENCE_MAP:
            return {"success": False, "error": f"Unsupported campaign: {campaign}"}
        if campaign == "spectrum" and os.environ.get("GFMD_SPECTRUM_ENROLLMENT_ENABLED") != "1":
            return {"success": False, "error": "Spectrum enrollment is disabled"}
        try:
            # Get contact
            from bson import ObjectId
            contact = self.storage.contacts.find_one({"_id": ObjectId(contact_id)})
            if not contact:
                return {"success": False, "error": "Contact not found"}

            contact_email = contact.get("email", "")
            sequence_name = self.CAMPAIGN_SEQUENCE_MAP.get(campaign, "narc_gone_law_enforcement")

            # Check if sequence already exists for this contact+campaign
            existing = self.storage.db.email_sequences.find_one({
                "contact_id": contact_id,
                "campaign": campaign
            })
            if existing:
                return {"success": False, "error": f"Sequence already exists for {campaign} (status: {existing.get('status')})"}

            # Create sequence state
            sequence_state = {
                'contact_id': contact_id,
                'contact_email': contact_email,
                'campaign': campaign,
                'sequence_name': sequence_name,
                'current_step': 0,
                'status': 'active',
                'emails_sent': [],
                'last_email_sent': None,
                'next_email_due': (self._initial_spectrum_due() if campaign == "spectrum" else datetime.now().isoformat()),
                'reply_received': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            # Insert new sequence (not upsert - never overwrite existing)
            result = self.storage.db.email_sequences.insert_one(sequence_state)

            return {"success": True, "contact_id": contact_id, "campaign": campaign}

        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def process_due_sequences(self, send_emails: bool = True) -> dict:
        """Process all sequences that are due for next email"""
        try:
            now = datetime.now()

            # Minimum hours between emails to same contact (prevents duplicate sends)
            min_hours_between_emails = 20  # At least 20 hours between any emails
            min_email_time = (now - timedelta(hours=min_hours_between_emails)).isoformat()

            # Find due sequences that:
            # 1. Are active
            # 2. next_email_due has passed
            # 3. Haven't been emailed in the last 20 hours (prevents duplicates)
            # 4. Aren't currently being processed
            due_sequences = list(self.storage.db.email_sequences.find({
                "status": "active",
                "next_email_due": {"$lte": now.isoformat()},
                "$or": [
                    {"last_email_sent": {"$exists": False}},
                    {"last_email_sent": None},
                    {"last_email_sent": {"$lt": min_email_time}}
                ],
                "processing": {"$ne": True}  # Not currently being processed
            }))
            
            results = {"processed": 0, "sent": 0, "errors": 0, "details": []}
            
            # Process in smaller batches to avoid rate limits
            batch_size = 5  # Process 5 emails at a time
            for i in range(0, len(due_sequences), batch_size):
                batch = due_sequences[i:i + batch_size]
                
                for sequence in batch:
                    try:
                        result = await self._process_single_sequence(sequence, send_emails)
                        results["processed"] += 1
                        
                        if result.get("success"):
                            if result.get("action") == "sent" or result.get("actually_sent") is True:
                                results["sent"] += 1
                            elif result.get("action") == "completed":
                                print(f"✅ Completed sequence for {sequence.get('contact_email')}")
                        else:
                            results["errors"] += 1
                            print(f"❌ Error: {result.get('error')}")
                        
                        results["details"].append({
                            "contact_email": sequence.get("contact_email"),
                            "step": sequence.get("current_step", 0) + 1,
                            "result": result
                        })
                        
                        # Add delay between each email to respect rate limits
                        if send_emails:
                            await asyncio.sleep(12)  # 5 emails per minute max
                        
                    except Exception as e:
                        results["errors"] += 1
                        print(f"❌ Error processing sequence: {e}")
                        
                        # If rate limit error, wait longer
                        if "rate_limit" in str(e).lower():
                            print("⏳ Rate limit hit, waiting 60 seconds...")
                            await asyncio.sleep(60)
                
                # Pause between batches 
                if i + batch_size < len(due_sequences):
                    print(f"⏳ Processed batch {i//batch_size + 1}, waiting 30s before next batch...")
                    await asyncio.sleep(30)
            
            if results["processed"] > 0:
                print(f"📧 Processed {results['processed']} sequences, sent {results['sent']} emails")
            
            return results
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_single_sequence(self, sequence: dict, send_emails: bool = True) -> dict:
        """Process a single email sequence"""
        if sequence.get("campaign") == "spectrum":
            # Keep Spectrum failures out of the legacy unconditional unlock path.
            from spectrum_worker import process_spectrum_sequence
            return await process_spectrum_sequence(self, sequence, send_emails)
        if send_emails and os.environ.get("GFMD_EMAIL_SEND_ENABLED") != "1":
            return {"success": False, "action": "disabled", "error": "Email sending is disabled pending approval"}
        if send_emails and not self.gmail.service:
            return {"success": False, "error": "Gmail authentication unavailable; sequence unchanged"}
        try:
            contact_id = sequence["contact_id"]
            current_step = sequence.get("current_step", 0)
            next_step = current_step + 1
            # Use raw campaign value for DB queries (None matches missing field)
            campaign_raw = sequence.get("campaign")
            campaign = campaign_raw or "narc_gone"
            sequence_name = sequence.get("sequence_name", self.CAMPAIGN_SEQUENCE_MAP.get(campaign, "narc_gone_law_enforcement"))
            # A worker with older templates must leave newer campaigns untouched.
            config = self.templates.get_sequence_config(sequence_name)
            if not config or config.get("campaign") != campaign:
                return {
                    "success": False,
                    "error": f"Unsupported sequence configuration: {campaign}/{sequence_name}",
                }
            template = self.templates.get_email_template(sequence_name, next_step)
            if not template:
                return {
                    "success": False,
                    "error": f"Missing template for {sequence_name} step {next_step}; sequence unchanged",
                }
            # Build query filter that matches the actual document
            campaign_filter = {"contact_id": contact_id, "campaign": campaign_raw}

            # ATOMIC LOCK: Try to acquire processing lock for this sequence
            # This prevents duplicate sends from concurrent scheduler runs
            lock_result = self.storage.db.email_sequences.find_one_and_update(
                {
                    **campaign_filter,
                    "status": "active",
                    "processing": {"$ne": True},
                    "current_step": current_step  # Ensure step hasn't changed
                },
                {
                    "$set": {
                        "processing": True,
                        "processing_started": datetime.now().isoformat()
                    }
                },
                return_document=True  # Return updated document
            )

            if not lock_result:
                # Another process is handling this sequence, skip it
                print(f"   Skipping {sequence.get('contact_email')} - already being processed or step changed")
                return {"success": True, "action": "skipped", "reason": "concurrent_processing"}

            # Double-check last email wasn't sent recently (belt and suspenders)
            last_sent = lock_result.get("last_email_sent")
            if last_sent:
                last_sent_dt = datetime.fromisoformat(last_sent) if isinstance(last_sent, str) else last_sent
                hours_since_last = (datetime.now() - last_sent_dt).total_seconds() / 3600
                if hours_since_last < 20:
                    # Release lock and skip
                    self.storage.db.email_sequences.update_one(
                        campaign_filter,
                        {"$set": {"processing": False}}
                    )
                    print(f"   Skipping {sequence.get('contact_email')} - last email was {hours_since_last:.1f} hours ago")
                    return {"success": True, "action": "skipped", "reason": "too_recent"}

            # Get contact data
            from bson import ObjectId
            contact = self.storage.contacts.find_one({"_id": ObjectId(contact_id)})
            if not contact:
                # Release lock
                self.storage.db.email_sequences.update_one(
                    campaign_filter,
                    {"$set": {"processing": False}}
                )
                return {"success": False, "error": "Contact not found"}

            # CRITICAL: Check if contact is on suppression list
            contact_email = contact.get("email", "").lower()
            is_suppressed = self.storage.db.suppression_list.find_one({
                'email': contact_email,
                'status': 'active'
            })

            if is_suppressed:
                # Contact is suppressed - stop sequence immediately
                self.storage.db.email_sequences.update_one(
                    campaign_filter,
                    {"$set": {
                        "status": "suppressed",
                        "stopped_at": datetime.now().isoformat(),
                        "stop_reason": is_suppressed.get("reason", "On suppression list"),
                        "processing": False,
                        "updated_at": datetime.now().isoformat()
                    }}
                )
                print(f"   Stopped sequence for suppressed contact: {contact_email}")
                return {"success": True, "action": "suppressed", "email": contact_email}

            # Check if contact status is suppressed (belt and suspenders)
            if contact.get("status") == "suppressed":
                self.storage.db.email_sequences.update_one(
                    campaign_filter,
                    {"$set": {
                        "status": "suppressed",
                        "stopped_at": datetime.now().isoformat(),
                        "stop_reason": contact.get("suppression_reason", "Contact marked as suppressed"),
                        "processing": False,
                        "updated_at": datetime.now().isoformat()
                    }}
                )
                print(f"   Stopped sequence for suppressed contact: {contact_email}")
                return {"success": True, "action": "suppressed", "email": contact_email}

            # Get previous emails for context (to avoid repetition)
            previous_emails = sequence.get("emails_sent", [])

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
                    "campaign": campaign,
                    "step": template["step"],
                    "type": template["type"],
                    "focus": template["focus"],
                    "tone": template["tone"],
                    "call_to_action": template["call_to_action"],
                    "is_follow_up": template["step"] > 1,
                    "previous_emails_sent": len(previous_emails),
                    "previous_emails": previous_emails  # Pass full email history for differentiation
                }
            }
            
            # Generate email with similarity check retry loop
            max_attempts = 3 if next_step > 1 and previous_emails else 1
            best_result = None
            best_similarity = 1.0
            similarity_meta = {"max_similarity": 0.0, "retries": 0, "passed": True}

            for attempt in range(max_attempts):
                email_result = await self.email_composer.execute(task)

                if not email_result.get("subject") or not email_result.get("body"):
                    if attempt < max_attempts - 1:
                        continue
                    return {"success": False, "error": "Email generation failed"}

                # Skip similarity check for step 1 (no previous emails)
                if next_step <= 1 or not previous_emails:
                    best_result = email_result
                    break

                sim = self._check_email_similarity(email_result, previous_emails)
                sim_score = sim.get("max_similarity", 0.0)

                if sim_score < best_similarity:
                    best_similarity = sim_score
                    best_result = email_result

                if not sim.get("similar", False):
                    similarity_meta = {"max_similarity": sim_score, "retries": attempt, "passed": True}
                    break

                # Too similar -- retry with rejection context
                similarity_meta = {"max_similarity": sim_score, "retries": attempt + 1, "passed": False}
                print(f"   Similarity too high ({sim_score:.2f}) with step {sim.get('most_similar_step')}, retrying ({attempt + 1}/{max_attempts - 1})...")
                task["sequence_context"]["similarity_rejection"] = {
                    "rejected_subject": email_result.get("subject", ""),
                    "similarity_score": sim_score,
                    "most_similar_step": sim.get("most_similar_step", 0)
                }
            else:
                # All attempts exceeded threshold -- use the least similar one
                print(f"   Warning: All {max_attempts} attempts exceeded similarity threshold, using best ({best_similarity:.2f})")
                similarity_meta["passed"] = False

            email_result = best_result
            if not email_result or not email_result.get("subject") or not email_result.get("body"):
                return {"success": False, "error": "Email generation failed"}
            
            # Send email if requested
            if send_emails and self.gmail.service:
                try:
                    # Build threading kwargs for follow-up emails (steps 2+)
                    threading_kwargs = {}
                    if next_step > 1 and previous_emails:
                        # Find the most recent previous email with Gmail IDs
                        for prev_email in reversed(previous_emails):
                            if prev_email.get("gmail_message_id") and prev_email.get("gmail_thread_id"):
                                headers = self.gmail.get_message_thread_headers(prev_email["gmail_message_id"])
                                if not headers.get("success") or headers.get("thread_id") != prev_email["gmail_thread_id"]:
                                    return {"success": False, "error": "Could not verify parent Gmail thread; sequence unchanged"}
                                threading_kwargs["thread_id"] = headers["thread_id"]
                                threading_kwargs["in_reply_to"] = headers["rfc_message_id"]
                                email_result["subject"] = headers["subject"]
                                break

                    send_result = self.gmail.send_email(
                        to_email=contact.get("email"),
                        subject=email_result.get("subject"),
                        body=email_result.get("body"),
                        html_body=email_result.get("html_body"),
                        **threading_kwargs
                    )
                    
                    if send_result.get("success"):
                        print(f"📧 Sent email {next_step} to {contact.get('email')}")
                        print(f"   Subject: {email_result.get('subject')}")
                    else:
                        return {"success": False, "error": f"Email sending failed: {send_result.get('error')}"}
                        
                except Exception as e:
                    return {"success": False, "error": f"Email sending error: {str(e)}"}
            else:
                print(f"📧 [DRY RUN] Would send email {next_step} to {contact.get('email')}")
                print(f"   Subject: {email_result.get('subject')}")
            
            # Update sequence state
            email_record = {
                "step": next_step,
                "sent_at": datetime.now().isoformat(),
                "subject": email_result.get("subject"),
                "body": email_result.get("body"),
                "template_type": template.get("type"),
                "actually_sent": send_emails and self.gmail.service is not None,
                "similarity_check": similarity_meta
            }

            # Store Gmail IDs for threading follow-up emails
            if send_emails and self.gmail.service and send_result.get("success"):
                email_record["gmail_message_id"] = send_result.get("message_id")
                email_record["gmail_thread_id"] = send_result.get("thread_id")

            emails_sent = sequence.get("emails_sent", [])
            emails_sent.append(email_record)
            
            # Calculate next email due date using business days
            next_template = self.templates.get_email_template(sequence_name, next_step + 1)
            if next_template:
                wait_business_days = next_template.get("wait_days", 2)
                next_due = self.business_day_calc.add_business_days(datetime.now(), wait_business_days)
                # Ensure it's during good email hours (9 AM - 6 PM)
                next_email_due = self.business_day_calc.get_next_good_email_time(next_due).isoformat()
                sequence_status = "active"
            else:
                # No more emails - sequence is complete!
                next_email_due = None
                sequence_status = "completed"
                print(f"   ✅ Sequence completed for {contact.get('email')}")

            # Update database - release processing lock and update state
            update_data = {
                "current_step": next_step,
                "last_email_sent": datetime.now().isoformat(),
                "emails_sent": emails_sent,
                "next_email_due": next_email_due,
                "status": sequence_status,
                "processing": False,
                "updated_at": datetime.now().isoformat()
            }

            # If completed, add completion timestamp and flag the contact
            if sequence_status == "completed":
                update_data["completed_at"] = datetime.now().isoformat()
                # Mark contact as sequence_completed for permanent protection
                self.storage.contacts.update_one(
                    {"_id": ObjectId(contact_id)},
                    {"$set": {"status": "sequence_completed", "sequence_completed_at": datetime.now().isoformat()}}
                )

            self.storage.db.email_sequences.update_one(
                campaign_filter,
                {"$set": update_data}
            )

            return {"success": True, "action": "sent" if sequence_status == "active" else "completed", "step": next_step}

        except Exception as e:
            # Release lock on error
            try:
                self.storage.db.email_sequences.update_one(
                    {"contact_id": sequence.get("contact_id"), "campaign": sequence.get("campaign")},
                    {"$set": {"processing": False}}
                )
            except:
                pass
            return {"success": False, "error": str(e)}
    
    def _initial_spectrum_due(self):
        from datetime import timezone
        from spectrum_campaign import next_spectrum_due
        return next_spectrum_due(datetime.now(timezone.utc), 1).isoformat()

    async def add_daily_new_contacts(self, count: int = 10, campaign: str = "narc_gone") -> dict:
        """Add new contacts daily from available contact pool"""
        if campaign not in self.CAMPAIGN_SEQUENCE_MAP:
            return {"success": False, "error": f"Unsupported campaign: {campaign}"}
        try:
            # Check if this campaign is paused for auto-add
            if campaign in self.PAUSED_CAMPAIGNS:
                print(f"\nCampaign '{campaign}' is paused for auto-add -- skipping")
                return {"success": True, "added": 0, "message": f"Campaign '{campaign}' is paused for new contacts"}

            print(f"\nAdding {count} new contacts to {campaign} sequences...")

            sequence_name = self.CAMPAIGN_SEQUENCE_MAP.get(campaign, "narc_gone_law_enforcement")

            # Find contacts that already have sequences for this campaign
            active_sequences = list(self.storage.db.email_sequences.find(
                {
                    "campaign": campaign,
                    "status": {"$in": ["active", "completed", "suppressed", "replied", "deduped"]}
                },
                {"contact_id": 1}
            ))

            # Convert to ObjectIds for query
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

            # Find contacts for this campaign without sequences
            query_filter = {"campaign": campaign}
            if active_contact_ids:
                query_filter["_id"] = {"$nin": active_contact_ids}
            available_contacts = list(self.storage.contacts.find(query_filter).limit(count))

            if not available_contacts:
                print("No new contacts available to add to sequences")
                return {"success": True, "added": 0, "message": "No available contacts"}

            added_count = 0
            results = []

            # Add up to requested count
            for contact in available_contacts[:count]:
                try:
                    contact_id = str(contact["_id"])
                    result = self.start_sequence_for_contact(contact_id, campaign=campaign)

                    if result.get("success"):
                        added_count += 1
                        print(f"Started sequence for {contact.get('email', 'unknown')} ({campaign})")
                        results.append({
                            "contact_id": contact_id,
                            "email": contact.get("email"),
                            "success": True
                        })
                    else:
                        print(f"Failed to start sequence for {contact.get('email', 'unknown')}: {result.get('error')}")
                        results.append({
                            "contact_id": contact_id,
                            "email": contact.get("email"),
                            "success": False,
                            "error": result.get("error")
                        })

                except Exception as e:
                    print(f"Error processing contact {contact.get('email', 'unknown')}: {e}")

            print(f"Added {added_count} new contacts to {campaign} sequences")

            return {
                "success": True,
                "added": added_count,
                "total_requested": count,
                "available_contacts": len(available_contacts),
                "campaign": campaign,
                "results": results
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_sequence_stats(self) -> dict:
        """Get comprehensive sequence statistics"""
        try:
            total = self.storage.db.email_sequences.count_documents({})
            active = self.storage.db.email_sequences.count_documents({"status": "active"})
            completed = self.storage.db.email_sequences.count_documents({"status": "completed"})
            replied = self.storage.db.email_sequences.count_documents({"status": "replied"})
            
            # Get step distribution
            pipeline = [
                {"$match": {"status": "active"}},
                {"$group": {"_id": "$current_step", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ]
            step_distribution = list(self.storage.db.email_sequences.aggregate(pipeline))
            
            return {
                "success": True,
                "total_sequences": total,
                "active": active,
                "completed": completed,
                "replied": replied,
                "response_rate": round((replied / total * 100) if total > 0 else 0, 2),
                "step_distribution": step_distribution,
                "gmail_connected": self.gmail.service is not None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def cleanup_stuck_sequences(self) -> dict:
        """Clean up stuck processing locks and fix duplicate sequences"""
        try:
            # Reset any stuck processing locks (older than 1 hour)
            one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            stuck_result = self.storage.db.email_sequences.update_many(
                {
                    "processing": True,
                    "processing_started": {"$lt": one_hour_ago}
                },
                {"$set": {"processing": False}}
            )

            # Find duplicate sequences (same contact_email with multiple active sequences)
            pipeline = [
                {"$match": {"status": "active"}},
                {"$group": {
                    "_id": "$contact_email",
                    "count": {"$sum": 1},
                    "sequences": {"$push": {"id": "$_id", "step": "$current_step", "updated": "$updated_at"}}
                }},
                {"$match": {"count": {"$gt": 1}}}
            ]
            duplicates = list(self.storage.db.email_sequences.aggregate(pipeline))

            deduped_count = 0
            for dup in duplicates:
                # Keep the sequence with highest step or most recent update
                sequences = sorted(dup["sequences"], key=lambda x: (x.get("step", 0), x.get("updated", "")), reverse=True)
                # Mark all but the first (best) as completed to stop duplicates
                for seq in sequences[1:]:
                    self.storage.db.email_sequences.update_one(
                        {"_id": seq["id"]},
                        {"$set": {"status": "deduped", "deduped_at": datetime.now().isoformat()}}
                    )
                    deduped_count += 1

            print(f"Cleanup: Reset {stuck_result.modified_count} stuck locks, deduped {deduped_count} sequences")

            return {
                "success": True,
                "stuck_locks_reset": stuck_result.modified_count,
                "duplicates_fixed": deduped_count
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def start_background_scheduler(self):
        """Start background processing every hour and daily contact addition"""
        def run_scheduler():
            # Run cleanup at startup
            print("Running startup cleanup...")
            self.cleanup_stuck_sequences()

            # Schedule cleanup every 4 hours
            schedule.every(4).hours.do(self.cleanup_stuck_sequences)

            # Schedule processing every hour
            schedule.every().hour.do(self._scheduled_processing)
            
            # Schedule at specific times for better control (adjusted for CST = UTC-6)
            schedule.every().day.at("15:00").do(self._scheduled_processing)  # 9 AM CST
            schedule.every().day.at("15:15").do(self._scheduled_processing)  # Observed Spectrum UTC anchor; sending remains opt-in.
            schedule.every().day.at("19:00").do(self._scheduled_processing)  # 1 PM CST
            schedule.every().day.at("23:00").do(self._scheduled_processing)  # 5 PM CST
            
            # Schedule daily contact addition (every business day at 8 AM CST = 14:00 UTC)
            schedule.every().monday.at("14:00").do(self._add_daily_contacts)
            schedule.every().tuesday.at("14:00").do(self._add_daily_contacts)
            schedule.every().wednesday.at("14:00").do(self._add_daily_contacts)
            schedule.every().thursday.at("14:00").do(self._add_daily_contacts)
            schedule.every().friday.at("14:00").do(self._add_daily_contacts)
            
            # Add auto-reply monitoring every 2 hours
            schedule.every(2).hours.do(self._check_auto_replies)

            # Add daily bounce/suppression scan at 6 AM CST = 12:00 UTC
            schedule.every().day.at("12:00").do(self._scan_for_bounces)

            print("Background scheduler started")
            print("   - Processing every hour")
            print("   - Special runs at 9 AM, 1 PM, 5 PM CST")
            print("   - Daily contact addition: Monday-Friday at 8 AM CST (10 new contacts)")
            print("   - Auto-reply monitoring: Every 2 hours")
            print("   - Daily email scan (bounces + replies): 6 AM CST")
            print("   - Cleanup (stuck locks + duplicates): Every 4 hours")
            print("   - Email timing: Every 2 business days")
            print("   - Duplicate prevention: 20-hour minimum between emails to same contact")
            
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        # Run scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def _scheduled_processing(self):
        """Scheduled processing function"""
        print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')} - Running scheduled sequence processing...")
        
        # Run async processing in sync context
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.process_due_sequences(send_emails=True))
            loop.close()
            
            if result.get("error") or result.get("errors", 0):
                print(f"Scheduled processing failed: {result.get('error') or str(result['errors']) + ' sequence error(s)'}")
            elif result.get("sent", 0) > 0:
                print(f"📧 Scheduled run: Sent {result['sent']} emails")
            else:
                print("📧 Scheduled run: No emails due")
                
        except Exception as e:
            print(f"❌ Scheduled processing error: {e}")
    
    def _add_daily_contacts(self):
        """Scheduled daily contact addition function -- runs for all campaigns"""
        print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M')} - Running daily contact addition...")

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            for campaign in self.CAMPAIGN_SEQUENCE_MAP:
                result = loop.run_until_complete(self.add_daily_new_contacts(count=10, campaign=campaign))
                if result.get("added", 0) > 0:
                    print(f"Daily run: Added {result['added']} new contacts to {campaign} sequences")
                else:
                    msg = result.get("message", "No new contacts added")
                    print(f"Daily run ({campaign}): {msg}")

            loop.close()

        except Exception as e:
            print(f"Daily contact addition error: {e}")
    
    def _check_auto_replies(self):
        """Scheduled auto-reply checking function"""
        print(f"\n🤖 {datetime.now().strftime('%Y-%m-%d %H:%M')} - Checking for email replies...")

        if self.auto_reply_system:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(self.auto_reply_system.run_single_check())
                loop.close()

                if results:
                    sent = sum(r.get("actually_sent") is True for r in results)
                    review = sum(r.get("action") == "human_review" for r in results)
                    print(f"Auto-reply run: {sent} sent, {review} queued for review")
                else:
                    print("Auto-reply run: No new replies to process")

            except Exception as e:
                print(f"Auto-reply check error: {e}")
        else:
            print("Auto-reply system not available")

    def _scan_for_bounces(self):
        """Daily scan for bounces, replies, and suppression list updates"""
        print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M')} - Running daily email scan (bounces + replies)...")

        try:
            from email_reply_monitor import EmailReplyMonitor

            monitor = EmailReplyMonitor()
            # Scan last 7 days for bounces and replies
            stats = monitor.process_gmail_replies(days_back=7)

            print(f"Email scan complete:")
            print(f"   - Emails checked: {stats.get('replies_checked', 0)}")
            print(f"   - Bounces detected: {stats.get('bounces_detected', 0)}")
            print(f"   - New suppressions: {stats.get('suppressions_added', 0)}")

            # Update sequences to 'replied' status based on interactions
            replied_contacts = list(self.storage.db.interactions.distinct('sender_email', {
                'type': 'auto_reply',
                'sender_email': {
                    '$not': {'$regex': 'postmaster|mailer-daemon|noreply|donotreply', '$options': 'i'}
                }
            }))

            sequences_updated = 0
            for email in replied_contacts:
                result = self.storage.db.email_sequences.update_many(
                    {'contact_email': email.lower(), 'status': 'active'},
                    {'$set': {'status': 'replied', 'reply_received': True, 'replied_at': datetime.now()}}
                )
                sequences_updated += result.modified_count

            if sequences_updated > 0:
                print(f"   - Sequences marked as replied: {sequences_updated}")

            # Get current reply stats
            total_sequences = self.storage.db.email_sequences.count_documents({})
            unique_repliers = len(replied_contacts)
            reply_rate = (unique_repliers / total_sequences * 100) if total_sequences > 0 else 0

            print(f"   - Total unique repliers: {unique_repliers}")
            print(f"   - Current reply rate: {reply_rate:.1f}%")

            # Log to database
            self.storage.db.system_logs.insert_one({
                'type': 'daily_email_scan',
                'timestamp': datetime.now(),
                'stats': {
                    **stats,
                    'sequences_marked_replied': sequences_updated,
                    'unique_repliers': unique_repliers,
                    'reply_rate': round(reply_rate, 1)
                }
            })

        except Exception as e:
            print(f"Daily email scan error: {e}")

async def main():
    """Main function for testing and running"""
    import sys
    
    automation = CompleteSequenceAutomation()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "add" and len(sys.argv) >= 6:
            # Add contact and start sequence
            contact = {
                "name": sys.argv[2],
                "email": sys.argv[3], 
                "organization": sys.argv[4],
                "title": sys.argv[5],
                "location": sys.argv[6] if len(sys.argv) > 6 else ""
            }
            result = automation.add_contact_and_start_sequence(contact)
            print(f"Add contact result: {result}")
            
        elif command == "process":
            # Process due sequences
            send = len(sys.argv) > 2 and sys.argv[2] == "send"
            result = await automation.process_due_sequences(send_emails=send)
            print(f"Process result: {result}")
            
        elif command == "stats":
            # Get statistics
            stats = automation.get_sequence_stats()
            print(f"Stats: {stats}")
            
        elif command == "add_contacts":
            # Add daily contacts manually
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            result = await automation.add_daily_new_contacts(count)
            print(f"Add contacts result: {result}")
            
        elif command == "schedule":
            # Start background scheduler
            automation.start_background_scheduler()
            print("🔄 Background scheduler running. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n⏹️ Scheduler stopped")
                
        elif command == "demo":
            # Demo with test contacts
            test_contacts = [
                {
                    "name": "Chief Sarah Johnson",
                    "email": "chief.johnson@testpd.gov",
                    "organization": "Test City Police Department", 
                    "title": "Chief of Police",
                    "location": "Test City, TX"
                },
                {
                    "name": "Sheriff Mike Rodriguez",
                    "email": "sheriff.rodriguez@testcounty.gov",
                    "organization": "Test County Sheriff's Office",
                    "title": "Sheriff", 
                    "location": "Test County, TX"
                }
            ]
            
            for contact in test_contacts:
                result = automation.add_contact_and_start_sequence(contact)
                print(f"Added: {contact['name']} -> {result.get('success')}")
            
            # Show stats
            stats = automation.get_sequence_stats()
            print(f"\nDemo stats: {stats}")
            
        else:
            print("Usage:")
            print("  python3 complete_sequence_automation.py add 'Name' 'email@domain.com' 'Organization' 'Title' 'Location'")
            print("  python3 complete_sequence_automation.py process [send]")
            print("  python3 complete_sequence_automation.py stats")
            print("  python3 complete_sequence_automation.py add_contacts [count]  # Default: 20")
            print("  python3 complete_sequence_automation.py schedule")
            print("  python3 complete_sequence_automation.py demo")
    else:
        # Default: show stats and process
        stats = automation.get_sequence_stats()
        print(f"Current stats: {stats}")
        
        result = await automation.process_due_sequences(send_emails=False)
        print(f"Process result (dry run): {result}")

if __name__ == "__main__":
    asyncio.run(main())
