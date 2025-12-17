#!/usr/bin/env python3
"""
Personalization Agent for GFMD Narcon (Groq-powered)
Uses the exact prompts from the AI Agent Prompts guide
"""

from typing import Dict, Any
from groq_base_agent import GroqBaseAgent, AgentRole
import json

class GroqPersonalizationAgent(GroqBaseAgent):
    """Agent specialized in personalizing email templates using production prompts"""

    def __init__(self, agent_id: str = "personalizer_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.EMAIL_COMPOSER,
            temperature=0.7  # Moderate temperature for natural writing
        )

    def get_system_prompt(self) -> str:
        return """You are an expert B2G (Business-to-Government) copywriter specializing in writing cold outreach emails to law enforcement and government officials. Your tone is professional, direct, and respectful.

**Your Goal:** Personalize the provided email template for the given contact.

**Product Information (Narc Gone):**

*   **What it is:** A chemical drug destruction product that safely and completely destroys seized narcotics, including Schedule I & II substances like fentanyl, heroin, and cocaine, as well as cannabis.
*   **Key Differentiator 1 (Credibility):** Co-developed and tested with the Department of Homeland Security (DHS).
*   **Key Differentiator 2 (Effectiveness):** Independent lab tests show complete destruction with no detectable residues, outperforming competitors like RX Destroyer which can leave measurable amounts behind.
*   **Key Differentiator 3 (Cost Savings):** Eliminates the need for expensive and time-consuming incineration processes (which require multiple officers, multi-day trips, and high costs).

**Instructions:**

1.  Read the email template and identify the personalization points (e.g., `{{pain_point}}`, `{{local_reference}}`).
2.  Based on the contact's information, dynamically insert relevant details.
3.  **Personalization Ideas:**
    *   If their title is "Evidence Manager," mention the challenges of evidence room storage.
    *   Reference their specific city or department (e.g., "for the Austin Police Department").
    *   Mention a known pain point for law enforcement, like the high cost of incineration or the risk of drug diversion from storage.
    *   If the template asks for it, highlight the DHS co-development, as this builds immense credibility with this audience.
4.  Keep the email concise and under 120 words.
5.  Do not change the core message of the template, only enhance it with personalization.
6.  Return ONLY the final, personalized email body as a single block of text. Do not include a subject line, greeting (like "Hi John,"), or sign-off.

**Output Format:**

A single block of text representing the final email body."""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute personalization task with production prompt format"""
        try:
            # Extract data
            contact_data = task.get("contact_data", {})
            email_template = task.get("email_template", {})
            
            # Build contact info in exact format from guide
            contact_info = {
                "firstName": contact_data.get("firstName", contact_data.get("first_name", "")),
                "title": contact_data.get("title", ""),
                "organization": contact_data.get("organization", contact_data.get("company_name", "")),
                "location": {
                    "city": contact_data.get("city", ""),
                    "state": contact_data.get("state", "")
                }
            }

            # Create the full prompt with exact format
            full_prompt = f"""**Contact to Email:**

```json
{json.dumps(contact_info, indent=2)}
```

**Email Template to Personalize:**

```
{email_template.get('body', '')}
```

{self.get_system_prompt()}"""

            # Call Groq AI
            result = await self.think({"prompt": full_prompt})

            # Ensure we have a valid response
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }

            # Extract the personalized email body
            personalized_body = result.get("response", "")
            
            if personalized_body:
                return {
                    "success": True,
                    "personalized_body": personalized_body.strip(),
                    "tokens_used": result.get("tokens_used", 0)
                }
            else:
                return {
                    "success": False,
                    "error": "No personalized content generated",
                    "raw_response": result
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Personalization task failed: {str(e)}"
            }

# Test function
if __name__ == "__main__":
    import asyncio
    
    async def test_personalization():
        agent = GroqPersonalizationAgent()
        
        # Test data
        test_task = {
            "contact_data": {
                "firstName": "Sarah",
                "title": "Property & Evidence Manager", 
                "organization": "Austin Police Department",
                "city": "Austin",
                "state": "TX"
            },
            "email_template": {
                "body": "I noticed {{organization}} processes significant drug evidence volumes. Many departments tell us incineration costs are straining budgets. Our Narc Gone system destroys drugs on-site for 30% less than traditional methods. {{pain_point}} Worth a brief conversation about potential savings?"
            }
        }
        
        result = await agent.execute(test_task)
        print("Personalization Result:")
        print(json.dumps(result, indent=2))
        
        if result.get("success"):
            print("\nPersonalized Email:")
            print(result["personalized_body"])
    
    # Run test
    asyncio.run(test_personalization())