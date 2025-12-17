#!/usr/bin/env python3
"""
Lead Qualification Agent for GFMD Narcon (Groq-powered)
Uses the exact prompts from the AI Agent Prompts guide
"""

from typing import Dict, Any
from groq_base_agent import GroqBaseAgent, AgentRole
import json

class GroqQualificationAgent(GroqBaseAgent):
    """Agent specialized in lead scoring and qualification using production prompts"""

    def __init__(self, agent_id: str = "qualifier_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.QUALIFIER,
            temperature=0.2  # Very low temperature for consistent scoring
        )

    def get_system_prompt(self) -> str:
        return """You are a lead qualification expert for a company selling drug destruction products (Narc Gone) to law enforcement and government agencies. Your task is to analyze a new contact and assign a qualification score from 0 to 100.

**Scoring Criteria:**

*   **Job Title (Weight: 40%):**
    *   High Score (90-100): Property & Evidence Manager, Evidence Supervisor, Quartermaster, anyone with "procurement" or "purchasing" in their title.
    *   Medium Score (60-80): Sheriff, Police Chief, Head of a specific unit (e.g., Narcotics), high-ranking federal officers.
    *   Low Score (20-50): Patrol Officer, Detective, administrative assistant (unless they are an assistant to a key decision-maker).
    *   Very Low Score (0-10): Unrelated roles.

*   **Organization Type (Weight: 30%):**
    *   High Score (90-100): Large city Police Departments (e.g., NYPD, LAPD), federal agencies (DHS, TSA, Border Patrol, Coast Guard), major Sheriff's Offices.
    *   Medium Score (60-80): Mid-sized city police/sheriff departments, state police.
    *   Low Score (30-50): Small town police departments, distributors.

*   **Location (Weight: 20%):**
    *   High Score (80-100): States with high drug seizure rates (e.g., CA, TX, FL, AZ, NY).
    *   Medium Score (50-70): Other states.

*   **Source (Weight: 10%):**
    *   High Score (90-100): Came from a property & evidence trade show list.
    *   Medium Score (50-70): General law enforcement contact list.

**Instructions:**

1.  Analyze the provided contact information based on the scoring criteria.
2.  Calculate a final weighted score.
3.  Determine a priority level based on the score (High: 80+, Medium: 60-79, Low: <60).
4.  Return ONLY a valid JSON object with the following format. Do not include any other text or explanations.

**Output Format:**

```json
{
  "score": <number>,
  "priority": "<High | Medium | Low>",
  "reasoning": "<A brief explanation of why you assigned this score>"
}
```"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute qualification task with production prompt format"""
        try:
            # Extract contact data
            contact_data = task.get("contact_data", {})
            
            # Build the prompt with contact information in exact format from guide
            contact_info = {
                "title": contact_data.get("title", ""),
                "organization": contact_data.get("organization", contact_data.get("company_name", "")),
                "location": {
                    "city": contact_data.get("city", ""),
                    "state": contact_data.get("state", "")
                },
                "source": contact_data.get("source", "general_law_enforcement")
            }

            # Create the full prompt with contact information
            full_prompt = f"""**Contact Information to Analyze:**

```json
{json.dumps(contact_info, indent=2)}
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

            # Parse the response to extract JSON
            response_text = result.get("response", "")
            if isinstance(response_text, str):
                # Extract JSON from response
                try:
                    if "{" in response_text and "}" in response_text:
                        start = response_text.find("{")
                        end = response_text.rfind("}") + 1
                        json_text = response_text[start:end]
                        qualification_result = json.loads(json_text)
                        
                        # Convert to expected format
                        return {
                            "success": True,
                            "qualification_score": qualification_result.get("score", 0),
                            "priority_level": qualification_result.get("priority", "Low").upper(),
                            "qualification_reasoning": qualification_result.get("reasoning", ""),
                            "tokens_used": result.get("tokens_used", 0)
                        }
                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "error": f"Failed to parse qualification JSON: {e}",
                        "raw_response": response_text
                    }

            return {
                "success": False,
                "error": "No valid response received",
                "raw_response": result
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Qualification task failed: {str(e)}"
            }

# Test function
if __name__ == "__main__":
    import asyncio
    
    async def test_qualification():
        agent = GroqQualificationAgent()
        
        # Test contact
        test_contact = {
            "contact_data": {
                "title": "Property & Evidence Manager", 
                "organization": "Austin Police Department",
                "city": "Austin",
                "state": "TX",
                "source": "property_evidence_trade_show"
            }
        }
        
        result = await agent.execute(test_contact)
        print("Qualification Result:")
        print(json.dumps(result, indent=2))
    
    # Run test
    asyncio.run(test_qualification())