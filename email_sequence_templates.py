#!/usr/bin/env python3
"""
Email Sequence Templates for GFMD Narc Gone Sales Campaign
Defines sequence templates with different messaging strategies for each follow-up
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

class EmailSequenceTemplates:
    """Manages email sequence templates and timing"""
    
    def __init__(self):
        self.sequences = {
            "narc_gone_law_enforcement": {
                "name": "Narc Gone Law Enforcement Outreach",
                "description": "6-email sequence for law enforcement agencies",
                "timing_days": [0, 2, 4, 6, 8, 10],  # Business days between emails (every 2 business days)
                "emails": [
                    {
                        "step": 1,
                        "type": "initial",
                        "wait_days": 0,
                        "subject_template": "Evidence destruction at {company_name}",
                        "focus": "pain_point_introduction",
                        "tone": "professional_introduction",
                        "call_to_action": "quick_call",
                        "prompts": {
                            "system_addition": """This is the FIRST email in the sequence. Focus on:
- Identifying a specific pain point they likely have
- Brief introduction to Narc Gone benefits
- Soft call to action for a call
- Keep it short and professional"""
                        }
                    },
                    {
                        "step": 2,
                        "type": "value_follow_up",
                        "wait_days": 2,
                        "subject_template": "Quick follow-up on {company_name} drug disposal",
                        "focus": "cost_savings_details",
                        "tone": "helpful_follow_up",
                        "call_to_action": "specific_meeting",
                        "prompts": {
                            "system_addition": """This is the SECOND email (follow-up #1). Focus on:
- Reference previous email without being pushy
- Provide specific cost savings data or case study
- More specific value proposition
- Suggest a specific time for call"""
                        }
                    },
                    {
                        "step": 3,
                        "type": "case_study_follow_up",
                        "wait_days": 4,
                        "subject_template": "How {similar_agency} cut disposal costs 40%",
                        "focus": "social_proof_case_study",
                        "tone": "story_based",
                        "call_to_action": "brief_demo",
                        "prompts": {
                            "system_addition": """This is the THIRD email (follow-up #2). Focus on:
- Share a relevant case study or success story
- Use social proof (similar agency type/size)
- Make it story-based, not salesy
- Offer a brief demo or consultation"""
                        }
                    },
                    {
                        "step": 4,
                        "type": "compliance_follow_up",
                        "wait_days": 6,
                        "subject_template": "DEA compliance question for {company_name}",
                        "focus": "compliance_regulatory",
                        "tone": "helpful_expert",
                        "call_to_action": "compliance_consultation",
                        "prompts": {
                            "system_addition": """This is the FOURTH email (follow-up #3). Focus on:
- Address compliance/regulatory concerns
- Position as compliance expert
- Offer compliance consultation
- Reference DEA requirements"""
                        }
                    },
                    {
                        "step": 5,
                        "type": "budget_season_follow_up",
                        "wait_days": 8,
                        "subject_template": "Budget planning for {company_name}",
                        "focus": "budget_planning_timing",
                        "tone": "timing_focused",
                        "call_to_action": "budget_discussion",
                        "prompts": {
                            "system_addition": """This is the FIFTH email (follow-up #4). Focus on:
- Budget planning season/timing
- ROI and cost justification
- Help with budget requests
- Planning for next fiscal year"""
                        }
                    },
                    {
                        "step": 6,
                        "type": "final_attempt",
                        "wait_days": 10,
                        "subject_template": "Final note about Narc Gone for {company_name}",
                        "focus": "respectful_final_attempt",
                        "tone": "graceful_exit",
                        "call_to_action": "future_contact",
                        "prompts": {
                            "system_addition": """This is the FINAL email (follow-up #5). Focus on:
- Acknowledge they're busy/may not be interested
- Mention this is the last email in sequence
- One final value statement
- Leave door open for future contact"""
                        }
                    }
                ]
            }
        }
    
    def get_sequence_config(self, sequence_name: str = "narc_gone_law_enforcement") -> Dict[str, Any]:
        """Get configuration for a specific sequence"""
        return self.sequences.get(sequence_name, {})
    
    def get_email_template(self, sequence_name: str, step: int) -> Dict[str, Any]:
        """Get template for specific email in sequence"""
        sequence = self.sequences.get(sequence_name, {})
        emails = sequence.get("emails", [])
        
        for email in emails:
            if email["step"] == step:
                return email
        
        return {}
    
    def get_next_email_timing(self, sequence_name: str, current_step: int) -> int:
        """Get days to wait before next email"""
        sequence = self.sequences.get(sequence_name, {})
        timing = sequence.get("timing_days", [])
        
        if current_step < len(timing):
            return timing[current_step]
        
        return None  # No more emails in sequence
    
    def generate_subject_variables(self, contact_data: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, str]:
        """Generate variables for subject line templates"""
        company_name = contact_data.get("company_name", "your department")
        
        # Clean company name for subject
        if "police" in company_name.lower():
            similar_agency = "Dallas PD"
        elif "sheriff" in company_name.lower():
            similar_agency = "Orange County Sheriff"
        elif any(fed in company_name.lower() for fed in ["dea", "cbp", "border", "customs", "federal"]):
            similar_agency = "CBP San Diego"
        else:
            similar_agency = "Phoenix Police"
        
        return {
            "company_name": company_name,
            "similar_agency": similar_agency
        }

# Example sequence state tracking
class SequenceState:
    """Tracks the state of an email sequence for a contact"""
    
    def __init__(self, contact_id: str, sequence_name: str = "narc_gone_law_enforcement"):
        self.contact_id = contact_id
        self.sequence_name = sequence_name
        self.current_step = 0
        self.status = "not_started"  # not_started, active, paused, completed, replied, opted_out
        self.emails_sent = []
        self.last_email_sent = None
        self.next_email_due = None
        self.reply_received = False
        self.reply_date = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        return {
            "contact_id": self.contact_id,
            "sequence_name": self.sequence_name,
            "current_step": self.current_step,
            "status": self.status,
            "emails_sent": self.emails_sent,
            "last_email_sent": self.last_email_sent.isoformat() if self.last_email_sent else None,
            "next_email_due": self.next_email_due.isoformat() if self.next_email_due else None,
            "reply_received": self.reply_received,
            "reply_date": self.reply_date.isoformat() if self.reply_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SequenceState":
        """Create from dictionary (MongoDB data)"""
        state = cls(data["contact_id"], data["sequence_name"])
        state.current_step = data.get("current_step", 0)
        state.status = data.get("status", "not_started")
        state.emails_sent = data.get("emails_sent", [])
        state.reply_received = data.get("reply_received", False)
        
        # Parse datetime strings
        if data.get("last_email_sent"):
            state.last_email_sent = datetime.fromisoformat(data["last_email_sent"])
        if data.get("next_email_due"):
            state.next_email_due = datetime.fromisoformat(data["next_email_due"])
        if data.get("reply_date"):
            state.reply_date = datetime.fromisoformat(data["reply_date"])
        if data.get("created_at"):
            state.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            state.updated_at = datetime.fromisoformat(data["updated_at"])
            
        return state

# Test function
if __name__ == "__main__":
    templates = EmailSequenceTemplates()
    
    print("📧 GFMD Email Sequence Templates")
    print("=" * 50)
    
    sequence = templates.get_sequence_config()
    print(f"Sequence: {sequence['name']}")
    print(f"Timing: {sequence['timing_days']} days")
    print()
    
    for email in sequence["emails"]:
        print(f"Email {email['step']}: {email['type']}")
        print(f"  Wait: {email['wait_days']} days")
        print(f"  Focus: {email['focus']}")
        print(f"  Subject: {email['subject_template']}")
        print()