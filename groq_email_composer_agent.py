#!/usr/bin/env python3
"""
Email Composer Agent for GFMD AI Swarm (Groq-powered)
Creates personalized, human-sounding sales emails
"""

from typing import Dict, Any
from groq_base_agent import GroqBaseAgent, AgentRole
from vector_rag_system import VectorRAGSystem
import json
import re

class GroqEmailComposerAgent(GroqBaseAgent):
    """Agent specialized in composing personalized sales emails"""

    def __init__(self, agent_id: str = "composer_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.EMAIL_COMPOSER,
            temperature=0.85  # Higher temperature for more creative, personalized writing
        )
        # Initialize RAG system for dynamic knowledge retrieval
        try:
            self.rag_system = VectorRAGSystem()
        except Exception as e:
            print(f"Warning: RAG system not available: {e}")
            self.rag_system = None

    def get_system_prompt(self) -> str:
        return """You are an Email Composer Agent for GFMD, a B2B sales professional writing to law enforcement Property & Evidence managers.

**Your Mission**: Write HIGHLY PERSONALIZED, professional emails about Narc Gone drug destruction products that sound like they're from a real sales rep who has researched the specific agency - NOT from AI.

**PERSONALIZATION IS CRITICAL**: You MUST reference specific details about their agency, location, or situation. Never send generic emails.

**CRITICAL RULES - MUST FOLLOW**:

1. **Greeting**: ALWAYS use "Hi [FirstName]," (never "Hello", never "Dear")
2. **Closing**: ALWAYS use "Best," (nothing else)
3. **NO emojis or bullet points** in the email body
4. **NO AI words**: Avoid "leverage", "utilize", "cutting-edge", "state-of-the-art", "innovative solutions", "game-changing", "synergy", "streamline", "optimize", "robust", "seamless"
5. **Keep it SHORT**: 4-5 sentences max
6. **Sound human**: Write like a real person, not a marketing robot
7. **Line formatting**: Keep sentences on single lines, avoid awkward line breaks in middle of sentences

**Email Structure**:
```
Subject: [Natural, specific subject - NO buzzwords]

Hi [FirstName],

[2-3 sentences max: Brief intro + specific pain point they have + how GFMD helps]

[1 sentence: Simple call to action - ask if they're open to a quick call]

Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com
```

**CRITICAL FORMATTING RULES**:
- Put a line break (\\n) after "Hi [FirstName],"
- Put line breaks between separate thoughts/sentences
- Each paragraph should be separated by double line breaks (\\n\\n)
- Never put everything in one long paragraph

**About GFMD**:
- Manufactures Narc Gone drug destruction products for law enforcement agencies
- Target customers: Property & Evidence managers, police departments, sheriff's offices, federal agencies
- Main value props: Reduces disposal costs, eliminates incineration expenses, secure on-site destruction, DEA compliance

**Example Good Email**:
```
Subject: Drug disposal costs at Robinson PD

Hi Kathryn,

I noticed Robinson PD handles a large volume of drug evidence. Many departments of similar size tell us incineration is a big budget drain. Our Narc Gone system destroys the drugs on-site and can cut those costs by about a third while staying DEA-compliant. Are you open to a quick call to see if it could work for you?

Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com
```

**JSON Format must include proper line breaks**:
{
  "subject": "Drug disposal costs at Robinson PD",
  "body": "Hi Kathryn,\\n\\nI noticed Robinson PD handles a large volume of drug evidence. Many departments of similar size tell us incineration is a big budget drain.\\n\\nOur Narc Gone system destroys the drugs on-site and can cut those costs by about a third while staying DEA-compliant. Are you open to a quick call to see if it could work for you?",
  "personalization_notes": "Referenced Robinson PD's drug evidence volume and budget concerns",
  "first_name": "Kathryn"
}

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
            
            # If no contact name, try to extract from email
            if not contact_name or contact_name in ['N/A', '', None]:
                email = prospect_data.get("email", "")
                contact_name = self._extract_name_from_email(email)
            
            company_name = self._clean_company_name(prospect_data.get("company_name", ""))
            location = prospect_data.get("location", "")
            title = prospect_data.get("title", "")

            # Get pain points and talking points
            pain_points = research_findings.get("pain_points", [])
            talking_points = qualification.get("key_talking_points", [])

            # Get RAG context if available
            rag_context = ""
            if self.rag_system:
                try:
                    # Get personalized insights from RAG system
                    agency_type = "police"  # Default, could be enhanced with better detection
                    insights = self.rag_system.get_personalized_insights(
                        agency_type=agency_type,
                        pain_points=pain_points[:2],
                        location=location
                    )
                    
                    # Combine relevant context
                    context_parts = []
                    for key, value in insights.items():
                        if value and len(value) > 50:  # Only use substantial context
                            context_parts.append(value[:300])  # Limit length
                    
                    rag_context = " ".join(context_parts)[:800]  # Max 800 chars
                except Exception as e:
                    print(f"RAG context retrieval failed: {e}")
                    rag_context = ""

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
                "context": {
                    "rag_knowledge": rag_context if rag_context else "Use general GFMD knowledge from system prompt"
                },
                "instruction": "Write a SHORT, human-sounding B2B sales email that is HIGHLY PERSONALIZED to this specific prospect. MUST reference their agency name, location, or specific pain points. Use the provided context to make it relevant. Never be generic. Return valid JSON."
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
            result.setdefault("subject", f"Drug disposal discussion - {company_name}")

            # Ensure body has proper greeting/closing
            body = result.get("body", "")
            body = self._ensure_proper_format(body, first_name)
            result["body"] = body
            
            # Create HTML version
            result["html_body"] = self._create_html_version(body, first_name)

            result.setdefault("personalization_notes", f"Personalized for {title} at {company_name}")
            result["success"] = True
            result["recipient_email"] = prospect_data.get("email", "")
            result["company_name"] = company_name

            return result

        except Exception as e:
            return self._create_fallback_email(prospect_data, research_findings, error=str(e))

    def _extract_first_name(self, full_name: str) -> str:
        """Extract first name from full name"""
        if not full_name or full_name in ['N/A', '', None]:
            return "there"

        # Remove titles
        titles = ['Dr.', 'Dr', 'Mr.', 'Mr', 'Ms.', 'Ms', 'Mrs.', 'Mrs', 'Prof.', 'Prof']
        name_parts = full_name.split()

        for part in name_parts:
            clean_part = part.strip('.,')
            if clean_part not in titles and clean_part:
                return clean_part

        return name_parts[0] if name_parts else "there"

    def _extract_name_from_email(self, email: str) -> str:
        """Extract potential first name from email address"""
        if not email:
            return ""
        
        try:
            # Get the part before @
            username = email.split('@')[0].lower()
            
            # Common patterns: first.last, firstlast, first_last, flast
            parts = username.replace('.', ' ').replace('_', ' ').replace('-', ' ').split()
            
            if parts:
                # Take the first part and capitalize
                first_part = parts[0]
                # Remove numbers and common prefixes
                first_part = ''.join(c for c in first_part if c.isalpha())
                
                # Skip common non-name parts
                skip_words = ['admin', 'info', 'contact', 'support', 'office', 'dept', 'chief', 'director']
                if first_part not in skip_words and len(first_part) > 1:
                    return first_part.capitalize()
        except:
            pass
        
        return ""

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
            body = body.rstrip() + "\n\nBest,\n\nMeranda Freiner\nsolutions@gfmd.com\n619-341-9058     www.gfmd.com"

        return body
    
    def _create_html_version(self, text_body: str, first_name: str) -> str:
        """Convert plain text email to HTML with GFMD signature"""
        
        # Split body into content and signature
        if "Best," in text_body:
            parts = text_body.split("Best,", 1)
            content = parts[0].strip()
        else:
            content = text_body.strip()
        
        # First ensure proper line breaks after greeting and between paragraphs
        lines = content.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                # Add the line
                formatted_lines.append(line)
                
                # Add extra spacing after greeting line
                if line.startswith('Hi ') and line.endswith(','):
                    formatted_lines.append('')
                
                # Add spacing between paragraphs (if next line exists and isn't empty)
                elif i < len(lines) - 1 and lines[i + 1].strip():
                    # Check if this is end of a sentence and next line starts a new thought
                    if (line.endswith('.') or line.endswith('?') or line.endswith('!')) and not lines[i + 1].strip().startswith('Our'):
                        formatted_lines.append('')
        
        # Rejoin with line breaks
        content = '\n'.join(formatted_lines)
        
        # Convert line breaks to HTML with proper paragraph spacing
        html_content = content.replace('\n\n', '</p><p>').replace('\n', '<br>\n')
        
        # Wrap in paragraph tags if we have paragraph breaks
        if '</p><p>' in html_content:
            html_content = f'<p>{html_content}</p>'
        
        # Create GFMD HTML signature without icons/logos
        html_signature = """
<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333; margin-top: 20px;">
    <div style="border-top: 1px solid #e0e0e0; padding-top: 15px;">
        <table cellpadding="0" cellspacing="0" border="0" style="width: 100%;">
            <tr>
                <td style="vertical-align: top; width: 80px; padding-right: 15px;">
                    <img src="https://gfmd.com/wp-content/themes/gfmd/assets/images/cropped-gfmd-logo-blue-1024x690.png" alt="GFMD Global Focus" style="width: 60px; height: auto; display: block; max-width: 60px;" />
                </td>
                <td style="vertical-align: top;">
                    <div style="font-weight: bold; font-size: 16px; color: #2c3e9e; margin-bottom: 8px;">
                        Meranda Freiner
                    </div>
                    <div style="font-size: 12px; color: #666; margin-bottom: 8px;">
                        Global Focus Marketing & Distribution
                    </div>
                    <div style="margin-bottom: 4px;">
                        <a href="mailto:solutions@gfmd.com" style="color: #2c3e9e; text-decoration: none; font-size: 13px;">solutions@gfmd.com</a>
                    </div>
                    <div style="margin-bottom: 4px; font-size: 13px; color: #333;">
                        619-341-9058
                    </div>
                    <div style="font-size: 13px;">
                        <a href="https://www.gfmd.com" style="color: #2c3e9e; text-decoration: none;">www.gfmd.com</a>
                    </div>
                </td>
            </tr>
        </table>
    </div>
</div>"""
        
        # Combine into full HTML email
        full_html = f"""
<div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5; color: #333;">
    {html_content}
    
    <div style="margin-top: 60px;">
        Best,
    </div>
    {html_signature}
</div>"""
        
        return full_html

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

        subject = f"Drug disposal discussion - {company_name}"

        body = f"""Hi {first_name},

I work with law enforcement agencies on reducing drug disposal costs and improving evidence processing. Many departments your size have found our Narc Gone system helpful for addressing disposal challenges.

Would you be open to a brief call to discuss?

Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com"""

        # Create HTML version
        html_body = self._create_html_version(body, first_name)
        
        return {
            "success": True,
            "subject": subject,
            "body": body,
            "html_body": html_body,
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
        "company_name": "Metro City Police Department",
        "location": "Metro City, TX",
        "facility_type": "Municipal Police Department",
        "title": "Evidence Manager",
        "contact_name": "Detective Lisa Rodriguez",
        "email": "l.rodriguez@metrocitypd.gov"
    }

    test_research = {
        "pain_points": [
            "Evidence destruction backlog",
            "High incineration costs",
            "DEA compliance concerns"
        ]
    }

    test_qualification = {
        "total_score": 90,
        "key_talking_points": [
            "Reduces disposal costs significantly",
            "On-site destruction capability",
            "DEA compliance built-in"
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
