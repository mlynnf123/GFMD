#!/usr/bin/env python3
"""
Referral Request Agent for GFMD Narcon (Groq-powered)
Generates personalized referral request emails using production prompts
"""

from typing import Dict, Any
from groq_base_agent import GroqBaseAgent, AgentRole
import json

class GroqReferralAgent(GroqBaseAgent):
    """Agent specialized in generating referral request emails"""

    def __init__(self, agent_id: str = "referral_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.EMAIL_COMPOSER,
            temperature=0.7  # Moderate temperature for natural, friendly writing
        )

    def get_system_prompt(self) -> str:
        return """You are an expert in customer relationships and B2B sales. Your task is to write a personalized, polite, and non-pushy email asking a satisfied customer for a referral.

**Instructions:**

1.  Write a short and friendly email to the customer.
2.  Start by expressing gratitude for their continued business (mentioning they are a valued customer).
3.  Gently ask if they know any other Property & Evidence Managers or officials in similar departments who might also benefit from Narc Gone.
4.  Make it easy for them to say no. Use phrases like "No worries if no one comes to mind, but I thought I would ask."
5.  Keep the email under 100 words.
6.  Return ONLY the final, personalized email body as a single block of text. Do not include a subject line, greeting, or sign-off.

**Output Format:**

A single block of text representing the final email body."""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute referral request generation"""
        try:
            # Extract customer data
            customer_data = task.get("customer_data", {})
            
            # Build customer info in exact format from guide
            customer_info = {
                "firstName": customer_data.get("firstName", customer_data.get("first_name", "")),
                "organization": customer_data.get("organization", customer_data.get("company_name", "")),
                "orderCount": customer_data.get("orderCount", len(customer_data.get("orders", [])))
            }

            # Create the full prompt
            full_prompt = f"""**Customer Information:**

```json
{json.dumps(customer_info, indent=2)}
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

            # Extract the referral email body
            email_body = result.get("response", "")
            
            if email_body:
                # Create complete email with greeting and sign-off
                complete_email = f"Hi {customer_info['firstName']},\n\n{email_body.strip()}\n\nThanks so much,\nMeranda"
                
                return {
                    "success": True,
                    "email_body": email_body.strip(),
                    "complete_email": complete_email,
                    "subject": "A quick question",
                    "tokens_used": result.get("tokens_used", 0)
                }
            else:
                return {
                    "success": False,
                    "error": "No referral content generated",
                    "raw_response": result
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Referral request task failed: {str(e)}"
            }

# Test function
if __name__ == "__main__":
    import asyncio
    
    async def test_referral_agent():
        agent = GroqReferralAgent()
        
        # Test customer data
        test_task = {
            "customer_data": {
                "firstName": "Sarah",
                "organization": "Austin Police Department",
                "orderCount": 3,
                "orders": [
                    {"date": "2024-06-01", "quantity": 2},
                    {"date": "2024-09-15", "quantity": 3},
                    {"date": "2024-12-01", "quantity": 2}
                ]
            }
        }
        
        result = await agent.execute(test_task)
        print("Referral Agent Result:")
        print(json.dumps(result, indent=2))
        
        if result.get("success"):
            print("\nComplete Referral Email:")
            print(result["complete_email"])
    
    # Run test
    asyncio.run(test_referral_agent())