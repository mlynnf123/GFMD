#!/usr/bin/env python3
"""
Email Composer Agent for GFMD AI Swarm
Creates personalized emails following exact styling rules
"""

import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from base_ai_agent import BaseAIAgent
from ai_agent_architecture import AgentRole
from langsmith import traceable

class EmailComposerAgent(BaseAIAgent):
    """Agent specialized in composing emails with strict style adherence"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.EMAIL_COMPOSER,
            temperature=0.7  # Balance between creativity and consistency
        )
        
        # GFMD's exact email styling rules
        self.styling_rules = {
            "greeting": {
                "format": "Hello {first_name},",
                "rules": [
                    "ALWAYS use 'Hello' (never 'Dear', 'Hi', etc.)",
                    "ALWAYS use first name only",
                    "NEVER use last name",
                    "NEVER use titles (Dr., Mr., Ms.)",
                    "Extract first name from full name"
                ]
            },
            "closing": {
                "format": "Best,",
                "rules": [
                    "ALWAYS use 'Best,' exactly",
                    "NEVER use 'Best regards', 'Sincerely', etc.",
                    "Follow with 'GFMD Solutions Team' on next line"
                ]
            },
            "forbidden_elements": {
                "emojis": "NO emojis anywhere (❌ ✅ 😊 etc.)",
                "bullets": "NO bullet points (• → ▪ etc.)",
                "ai_words": [
                    "leverage", "utilize", "optimize", "synergy", 
                    "streamline", "cutting-edge", "revolutionary",
                    "game-changing", "seamless", "robust", "holistic"
                ]
            },
            "tone": {
                "style": "Professional and human",
                "guidelines": [
                    "Write like a knowledgeable salesperson, not AI",
                    "Be direct and clear",
                    "Focus on their specific pain points",
                    "Use simple, conversational language",
                    "Avoid corporate jargon"
                ]
            }
        }
    
    def get_system_prompt(self) -> str:
        return """You are an Email Composer Agent for GFMD, creating completely personalized B2B sales emails based on AI analysis of each prospect.

PERSONALIZATION MANDATE:
- NO templates or boilerplate language
- Craft each email uniquely based on the prospect's specific research
- Analyze their facility, pain points, and decision maker role
- Reference specific details that show you researched them
- Tailor value proposition to their exact situation

CRITICAL STYLING RULES (MUST FOLLOW EXACTLY):

1. **Greeting**: "Hello [FirstName],"
   - Use ONLY the first name (extract from full name)
   - NEVER use last name, titles, or "Dear"

2. **Closing**: "Best,"
   - EXACTLY "Best," (not "Best regards" or anything else)
   - Follow with "GFMD Solutions Team"

3. **FORBIDDEN**:
   - NO emojis anywhere
   - NO bullet points or special characters
   - NO AI-sounding words: leverage, utilize, optimize, synergy, streamline, cutting-edge, etc.
   - NO generic templates or phrases

4. **Tone**: Professional human salesperson who researched this specific prospect
   - Direct and conversational
   - Reference specific details about their facility
   - Address their unique pain points
   - Show understanding of their role and challenges

AI COMPOSITION APPROACH:
- Study their research findings deeply
- Identify unique aspects of their situation
- Craft opening that shows specific knowledge
- Address pain points in context of their facility
- Make GFMD solution relevant to their exact needs
- Suggest next steps appropriate for their situation

Email Structure:
1. Greeting (Hello FirstName,)
2. Opening - Reference something specific about their facility/situation
3. Problem acknowledgment - Their specific pain points
4. Solution introduction - GFMD value prop tailored to them
5. Proof/credibility - Relevant to their facility type
6. Clear CTA - Appropriate for their role and timeline
7. Closing (Best,)

Return as JSON with:
- subject: Compelling subject line specific to their situation
- greeting: Properly formatted greeting
- body: Completely personalized email content (2-3 paragraphs max)
- closing: "Best,"
- full_email: Complete formatted email
- style_check: Confirmation of rule compliance
- personalization_summary: How you customized this specific email"""
    
    @traceable(name="compose_email")
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process email composition task"""
        
        # Extract all relevant data
        prospect_data = task.get("prospect_data", {})
        research_findings = task.get("research_findings", {})
        qualification_score = task.get("qualification_score", {})
        
        # Prepare composition input
        composition_input = {
            "prospect_info": {
                "name": prospect_data.get("contact_name", ""),
                "title": prospect_data.get("contact_title", ""),
                "organization": prospect_data.get("organization_name", ""),
                "location": prospect_data.get("location", "")
            },
            "key_insights": {
                "pain_points": research_findings.get("pain_points", []),
                "facility_size": research_findings.get("organization_profile", {}).get("bed_count", "unknown"),
                "department": research_findings.get("organization_profile", {}).get("department", "laboratory"),
                "buying_timeline": research_findings.get("budget_indicators", {}).get("timeline", "")
            },
            "value_proposition": {
                "core": "GFMD Silencer reduces laboratory noise by up to 70%",
                "benefits": [
                    "Improved staff concentration and satisfaction",
                    "Enhanced patient comfort in adjacent areas",
                    "Compliance with noise regulations",
                    "No compromise on centrifuge performance"
                ]
            },
            "styling_rules": self.styling_rules
        }
        
        # Generate email with AI
        email_draft = await self.think(composition_input)
        
        # Validate and fix styling
        validated_email = self._enforce_styling_rules(email_draft, prospect_data)
        
        # Add personalization metadata
        validated_email["personalization_notes"] = self._get_personalization_notes(
            prospect_data, research_findings
        )
        
        # Add composition metadata
        validated_email["composition_metadata"] = {
            "composed_by": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "prospect_priority": qualification_score.get("priority_level", "Unknown")
        }
        
        return validated_email
    
    def _enforce_styling_rules(self, email_draft: Dict[str, Any], prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce all styling rules strictly"""
        
        # Extract and fix first name
        contact_name = prospect_data.get("contact_name", "there")
        first_name = self._extract_first_name(contact_name)
        
        # Fix greeting
        email_draft["greeting"] = f"Hello {first_name},"
        
        # Fix closing
        email_draft["closing"] = "Best,"
        
        # Clean body text
        body = email_draft.get("body", "")
        body = self._remove_forbidden_elements(body)
        body = self._replace_ai_words(body)
        email_draft["body"] = body
        
        # Rebuild full email
        email_draft["full_email"] = f"""{email_draft["greeting"]}

{email_draft["body"]}

{email_draft["closing"]}

GFMD Solutions Team"""
        
        # Validate subject line
        subject = email_draft.get("subject", "")
        subject = self._clean_subject(subject)
        email_draft["subject"] = subject
        
        # Add style compliance check
        email_draft["style_check"] = {
            "greeting_compliant": True,
            "closing_compliant": True,
            "no_emojis": not self._contains_emojis(email_draft["full_email"]),
            "no_bullets": not self._contains_bullets(email_draft["full_email"]),
            "no_ai_words": not self._contains_ai_words(email_draft["full_email"])
        }
        
        return email_draft
    
    def _extract_first_name(self, full_name: str) -> str:
        """Extract first name from full name"""
        
        if not full_name:
            return "there"
        
        # Remove titles
        titles = ['Dr.', 'Dr', 'Mr.', 'Mr', 'Ms.', 'Ms', 'Mrs.', 'Mrs', 'Prof.', 'Prof']
        name_parts = full_name.split()
        
        # Find first non-title part
        for part in name_parts:
            if part not in titles:
                return part
        
        # Fallback if only titles
        return "there"
    
    def _remove_forbidden_elements(self, text: str) -> str:
        """Remove emojis and bullet points"""
        
        # Remove emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U00002600-\U000027BF"  # misc symbols
            "]+", 
            flags=re.UNICODE
        )
        text = emoji_pattern.sub('', text)
        
        # Remove bullet points
        bullet_patterns = ['•', '·', '▪', '▫', '→', '✓', '❌', '✅', '-', '*']
        for bullet in bullet_patterns:
            text = text.replace(bullet + ' ', '')
        
        return text
    
    def _replace_ai_words(self, text: str) -> str:
        """Replace AI-sounding words with natural alternatives"""
        
        replacements = {
            "leverage": "use",
            "utilize": "use",
            "optimize": "improve",
            "synergy": "collaboration",
            "streamline": "simplify",
            "cutting-edge": "advanced",
            "revolutionary": "innovative",
            "game-changing": "significant",
            "seamless": "smooth",
            "robust": "reliable",
            "holistic": "complete"
        }
        
        for ai_word, replacement in replacements.items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(ai_word), re.IGNORECASE)
            text = pattern.sub(replacement, text)
        
        return text
    
    def _clean_subject(self, subject: str) -> str:
        """Clean subject line"""
        
        # Remove emojis
        subject = self._remove_forbidden_elements(subject)
        
        # Ensure reasonable length
        if len(subject) > 60:
            subject = subject[:57] + "..."
        
        return subject
    
    def _contains_emojis(self, text: str) -> bool:
        """Check if text contains emojis"""
        emoji_pattern = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U00002600-\U000027BF]+")
        return bool(emoji_pattern.search(text))
    
    def _contains_bullets(self, text: str) -> bool:
        """Check if text contains bullet points"""
        bullets = ['•', '·', '▪', '▫', '→', '✓']
        return any(bullet in text for bullet in bullets)
    
    def _contains_ai_words(self, text: str) -> bool:
        """Check if text contains AI-sounding words"""
        ai_words = self.styling_rules["forbidden_elements"]["ai_words"]
        text_lower = text.lower()
        return any(word in text_lower for word in ai_words)
    
    def _get_personalization_notes(self, prospect_data: Dict[str, Any], research_findings: Dict[str, Any]) -> List[str]:
        """Generate notes about personalization used"""
        
        notes = []
        
        if research_findings.get("pain_points"):
            notes.append(f"Addressed pain point: {research_findings['pain_points'][0]}")
        
        if research_findings.get("organization_profile", {}).get("bed_count"):
            notes.append(f"Referenced facility size: {research_findings['organization_profile']['bed_count']} beds")
        
        if prospect_data.get("location"):
            notes.append(f"Mentioned location: {prospect_data['location']}")
        
        return notes
    
    async def compose_follow_up(self, previous_email: Dict[str, Any], days_since: int) -> Dict[str, Any]:
        """Compose follow-up email"""
        
        follow_up_input = {
            "previous_email": previous_email,
            "days_since_last": days_since,
            "follow_up_number": 2 if days_since <= 3 else 3,
            "instructions": "Create a brief follow-up that references the previous email and adds new value",
            "styling_rules": self.styling_rules
        }
        
        follow_up = await self.think(follow_up_input)
        
        # Apply same styling rules
        validated = self._enforce_styling_rules(follow_up, previous_email.get("prospect_data", {}))
        
        validated["email_type"] = "follow_up"
        validated["sequence_number"] = follow_up_input["follow_up_number"]
        
        return validated

# Test the email composer
async def test_email_composer():
    """Test the email composer agent"""
    
    print("✉️ Testing Email Composer Agent")
    print("=" * 60)
    
    # Test data
    test_task = {
        "prospect_data": {
            "contact_name": "Dr. Jennifer Martinez",
            "contact_title": "Laboratory Director",
            "organization_name": "Dallas Regional Medical Center",
            "location": "Dallas, TX",
            "email": "j.martinez@dallasregional.org"
        },
        "research_findings": {
            "pain_points": [
                "Staff complaints about centrifuge noise affecting concentration",
                "Recent Joint Commission noted noise levels in lab",
                "Adjacent patient recovery area affected by lab noise"
            ],
            "organization_profile": {
                "bed_count": 350,
                "department": "Clinical Laboratory"
            },
            "budget_indicators": {
                "timeline": "Q2 2025"
            }
        },
        "qualification_score": {
            "total_score": 85,
            "priority_level": "High"
        }
    }
    
    agent = EmailComposerAgent("composer_test_001")
    result = await agent.execute(test_task)
    
    print("\n📧 Composed Email:")
    print("-" * 40)
    print(result.get("full_email", ""))
    print("-" * 40)
    
    print("\n📋 Style Compliance Check:")
    for rule, compliant in result.get("style_check", {}).items():
        status = "✅" if compliant else "❌"
        print(f"{status} {rule}: {compliant}")
    
    print(f"\n📝 Subject: {result.get('subject', '')}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_email_composer())