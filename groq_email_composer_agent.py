#!/usr/bin/env python3
"""
Email Composer Agent for GFMD AI Swarm (Groq-powered)
Creates personalized, human-sounding sales emails
"""

from typing import Dict, Any
from groq_base_agent import GroqBaseAgent, AgentRole
import json
import re

class GroqEmailComposerAgent(GroqBaseAgent):
    """Agent specialized in composing personalized sales emails"""

    def __init__(self, agent_id: str = "composer_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.EMAIL_COMPOSER,
            temperature=0.7  # Moderate temperature for natural writing
        )

    def get_system_prompt(self) -> str:
        return """You are an Email Composer Agent for GFMD Medical Devices, a B2B sales professional writing to healthcare laboratory directors.

**Your Mission**: Write personalized, professional emails that sound like they're from a real sales rep - NOT from AI.

**CRITICAL RULES - MUST FOLLOW**:

1. **Greeting**: ALWAYS use "Hi [FirstName]," (never "Hello", never "Dear")
2. **Closing**: ALWAYS use "Best," (nothing else)
3. **NO emojis or bullet points** in the email body
4. **NO AI words**: Avoid "leverage", "utilize", "cutting-edge", "state-of-the-art", "innovative solutions", "game-changing", "synergy", "streamline", "optimize", "robust", "seamless"
5. **Keep it SHORT**: 4-5 sentences max
6. **Sound human**: Write like a real person, not a marketing robot

**Email Structure**:
```
Subject: [Natural, specific subject - NO buzzwords]

Hi [FirstName],

[2-3 sentences max: Brief intro + specific pain point they have + how GFMD helps]

[1 sentence: Simple call to action - ask if they're open to a quick call]

Best,
Mark Thompson
GFMD Medical Devices
mark@gfmdmedical.com
(555) 123-4567
```

**About GFMD**:
- Manufactures noise-reducing centrifuge equipment for medical laboratories
- Target customers: hospital lab directors, equipment managers
- Main value props: Reduces lab noise, improves staff satisfaction, OSHA compliance, compact design

**Example Good Email**:
```
Subject: Reducing lab noise at Methodist Hospital

Hi Sarah,

I noticed Methodist recently expanded its lab operations. Many hospitals your size tell us their biggest challenge is centrifuge noise affecting adjacent patient areas.

We make centrifuges that run 40% quieter than standard models. Might be worth a quick conversation?

Best,
Mark Thompson
```

**RETURN FORMAT** - Must be valid JSON:
{
  "subject": "Natural subject line",
  "body": "Full email body with greeting and closing",
  "personalization_notes": "What was personalized",
  "first_name": "Extracted first name"
}
"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email composition task"""
        try:
            # Extract data
            prospect_data = task.get("prospect_data", {})
            research_findings = task.get("research_findings", {})
            qualification = task.get("qualification_score", {})

            # Extract key info
            contact_name = prospect_data.get("contact_name", "")
            company_name = self._clean_company_name(prospect_data.get("company_name", ""))
            location = prospect_data.get("location", "")
            title = prospect_data.get("title", "")

            # Get pain points and talking points
            pain_points = research_findings.get("pain_points", [])
            talking_points = qualification.get("key_talking_points", [])

            # Build composition prompt
            composition_prompt = {
                "task": "compose_email",
                "prospect": {
                    "contact_name": contact_name,
                    "company_name": company_name,
                    "location": location,
                    "title": title
                },
                "insights": {
                    "pain_points": pain_points[:2],  # Top 2 only
                    "talking_points": talking_points[:2],
                    "qualification_score": qualification.get("total_score", 0)
                },
                "instruction": "Write a SHORT, human-sounding B2B sales email following ALL the rules above. Return valid JSON."
            }

            # Call Groq AI
            result = await self.think(composition_prompt)

            # Parse response
            if "error" in result:
                return self._create_fallback_email(prospect_data, research_findings)

            # If response is wrapped, extract JSON
            if "response" in result and isinstance(result["response"], str):
                try:
                    response_text = result["response"]
                    if "{" in response_text and "}" in response_text:
                        start = response_text.find("{")
                        end = response_text.rfind("}") + 1
                        json_text = response_text[start:end]
                        result = json.loads(json_text)
                except:
                    return self._create_fallback_email(prospect_data, research_findings)

            # Ensure required fields
            first_name = self._extract_first_name(contact_name)
            result.setdefault("first_name", first_name)
            result.setdefault("subject", f"Lab equipment discussion - {company_name}")

            # Ensure body has proper greeting/closing
            body = result.get("body", "")
            body = self._ensure_proper_format(body, first_name)
            result["body"] = body

            result.setdefault("personalization_notes", f"Personalized for {title} at {company_name}")
            result["success"] = True
            result["recipient_email"] = prospect_data.get("email", "")
            result["company_name"] = company_name

            return result

        except Exception as e:
            return self._create_fallback_email(prospect_data, research_findings, error=str(e))

    def _extract_first_name(self, full_name: str) -> str:
        """Extract first name from full name"""
        if not full_name:
            return "there"

        # Remove titles
        titles = ['Dr.', 'Dr', 'Mr.', 'Mr', 'Ms.', 'Ms', 'Mrs.', 'Mrs', 'Prof.', 'Prof']
        name_parts = full_name.split()

        for part in name_parts:
            clean_part = part.strip('.,')
            if clean_part not in titles and clean_part:
                return clean_part

        return name_parts[0] if name_parts else "there"

    def _clean_company_name(self, company_name: str) -> str:
        """Clean company name - remove (FKA...) and (AKA...) parts"""
        if not company_name:
            return company_name

        # Remove (AKA ...) and (FKA ...) patterns
        pattern = r'\s*\([AF]KA[^)]*\)'
        cleaned = re.sub(pattern, '', company_name).strip()
        return cleaned

    def _ensure_proper_format(self, body: str, first_name: str) -> str:
        """Ensure email has proper greeting and closing"""
        # Check for greeting
        if not body.strip().startswith("Hi "):
            body = f"Hi {first_name},\n\n" + body.lstrip()

        # Check for closing
        if "Best," not in body:
            body = body.rstrip() + "\n\nBest,\nMark Thompson\nGFMD Medical Devices\nmark@gfmdmedical.com\n(555) 123-4567"

        return body

    def _create_fallback_email(
        self,
        prospect_data: Dict[str, Any],
        research_findings: Dict[str, Any],
        error: str = None
    ) -> Dict[str, Any]:
        """Create a simple fallback email"""
        contact_name = prospect_data.get("contact_name", "")
        company_name = self._clean_company_name(prospect_data.get("company_name", ""))
        first_name = self._extract_first_name(contact_name)

        subject = f"Lab equipment discussion - {company_name}"

        body = f"""Hi {first_name},

I work with hospital labs on reducing equipment noise and improving operations. Many facilities your size have found our centrifuges helpful for addressing noise concerns.

Would you be open to a brief call to discuss?

Best,
Mark Thompson
GFMD Medical Devices
mark@gfmdmedical.com
(555) 123-4567"""

        return {
            "success": True,
            "subject": subject,
            "body": body,
            "first_name": first_name,
            "personalization_notes": "Fallback template used",
            "recipient_email": prospect_data.get("email", ""),
            "company_name": company_name
        }


# Test the email composer agent
async def test_email_composer():
    """Test the email composer agent"""
    import os

    print("✉️ Testing Email Composer Agent")
    print("=" * 50)

    if not os.environ.get('GROQ_API_KEY'):
        print("❌ GROQ_API_KEY not set")
        return

    agent = GroqEmailComposerAgent()

    # Simulate full prospect data
    test_prospect = {
        "company_name": "Abbott Northwestern Hospital (FKA Old Hospital)",
        "location": "Minneapolis, MN",
        "facility_type": "Short Term Acute Care Hospital",
        "title": "Laboratory Medical Director",
        "contact_name": "Dr. Lauren Anthony",
        "email": "lauren.anthony@allina.com"
    }

    test_research = {
        "pain_points": [
            "Noise levels from existing centrifuge equipment",
            "Space constraints in laboratory",
            "OSHA compliance concerns"
        ]
    }

    test_qualification = {
        "total_score": 90,
        "key_talking_points": [
            "Addressing noise levels with quiet equipment",
            "Optimizing laboratory space",
            "OSHA compliance solutions"
        ]
    }

    print(f"\n📝 Composing email for: {test_prospect['contact_name']}")
    print(f"   Company: {test_prospect['company_name']}")

    result = await agent.execute({
        "prospect_data": test_prospect,
        "research_findings": test_research,
        "qualification_score": test_qualification
    })

    if result.get("success"):
        print(f"\n✅ Email composed!")
        print(f"\n📧 Subject: {result.get('subject')}")
        print(f"\n📄 Body:\n{'-' * 50}")
        print(result.get('body'))
        print(f"{'-' * 50}")
        print(f"\n🧠 Tokens used: {agent.state['total_tokens_used']}")
    else:
        print(f"\n❌ Composition failed")


if __name__ == "__main__":
    import asyncio
    import os
    os.environ['GROQ_API_KEY'] = 'your_groq_api_key_here'
    asyncio.run(test_email_composer())
