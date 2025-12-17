#!/usr/bin/env python3
"""
Sequence Manager Agent for GFMD Narcon (Groq-powered)
Decides next actions based on engagement history using production prompts
"""

from typing import Dict, Any
from groq_base_agent import GroqBaseAgent, AgentRole
from datetime import datetime, timedelta
import json

class GroqSequenceManager(GroqBaseAgent):
    """Agent specialized in managing email sequences and deciding next actions"""

    def __init__(self, agent_id: str = "sequence_mgr_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.COORDINATOR,
            temperature=0.2  # Low temperature for consistent decision-making
        )

    def get_system_prompt(self) -> str:
        return """You are an AI sales strategist managing an automated outreach campaign. Your job is to analyze a contact's recent engagement and decide the next logical step in the sequence.

**Decision-Making Rules:**

1.  **If `hasReplied` is `true`:** The sequence is over. The next action is always `end_sequence` and the status should be `Engaged`.
2.  **If the last interaction was `email_opened` or `email_clicked` but there has been no reply for 3+ days:** The lead is warm. The next action should be `send_case_study` to provide more value.
3.  **If 3+ emails have been sent with no opens or clicks:** The email channel is cold. The next action should be `try_linkedin` to switch channels.
4.  **If the last email was sent 2-3 days ago with no interaction:** It's time for a standard follow-up. The next action is `send_standard_follow_up`.
5.  **If the last email was sent 7+ days ago with no interaction:** The lead is likely cold. The next action is `send_breakup_email` to try and re-engage one last time.
6.  **If none of the above apply:** The system should wait. The next action is `wait`.

**Instructions:**

1.  Analyze the provided system state and contact history.
2.  Apply the decision-making rules to determine the single best next action.
3.  Return ONLY a valid JSON object with the following format. Do not include any other text or explanations.

**Output Format:**

```json
{
  "nextAction": "<send_case_study | try_linkedin | send_standard_follow_up | send_breakup_email | end_sequence | wait>",
  "reasoning": "<A brief explanation for your decision>"
}
```"""

    def _calculate_days_since_interaction(self, last_interaction_timestamp: str) -> int:
        """Calculate days since last interaction"""
        try:
            if not last_interaction_timestamp:
                return 999  # Very high number if no timestamp
            
            # Parse timestamp (assuming ISO format)
            last_time = datetime.fromisoformat(last_interaction_timestamp.replace('Z', '+00:00'))
            now = datetime.now()
            
            # Calculate difference
            delta = now - last_time
            return delta.days
        except:
            return 999  # Default to high number on error

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sequence management decision"""
        try:
            # Extract data
            contact_data = task.get("contact_data", {})
            last_interaction = task.get("last_interaction", {})
            engagement_summary = task.get("engagement_summary", {})

            # Build system state in exact format from guide
            system_state = {
                "contactId": contact_data.get("_id", ""),
                "status": contact_data.get("status", "Cold Outreach"),
                "lastInteraction": {
                    "type": last_interaction.get("type", ""),
                    "channel": last_interaction.get("channel", "email"),
                    "timestamp": last_interaction.get("timestamp", "")
                },
                "engagementSummary": {
                    "totalEmailsSent": engagement_summary.get("totalEmailsSent", 0),
                    "totalEmailsOpened": engagement_summary.get("totalEmailsOpened", 0),
                    "totalEmailsClicked": engagement_summary.get("totalEmailsClicked", 0),
                    "hasReplied": engagement_summary.get("hasReplied", False)
                }
            }

            # Create the full prompt
            full_prompt = f"""**System State & Contact History:**

```json
{json.dumps(system_state, indent=2)}
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
                try:
                    if "{" in response_text and "}" in response_text:
                        start = response_text.find("{")
                        end = response_text.rfind("}") + 1
                        json_text = response_text[start:end]
                        decision_result = json.loads(json_text)
                        
                        return {
                            "success": True,
                            "next_action": decision_result.get("nextAction", "wait"),
                            "reasoning": decision_result.get("reasoning", ""),
                            "tokens_used": result.get("tokens_used", 0),
                            "contact_id": system_state["contactId"]
                        }
                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "error": f"Failed to parse sequence decision JSON: {e}",
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
                "error": f"Sequence management task failed: {str(e)}"
            }

# Test function
if __name__ == "__main__":
    import asyncio
    
    async def test_sequence_manager():
        agent = GroqSequenceManager()
        
        # Test scenario: Email opened 4 days ago, no reply
        test_task = {
            "contact_data": {
                "_id": "contact_123",
                "status": "Cold Outreach"
            },
            "last_interaction": {
                "type": "email_opened",
                "channel": "email",
                "timestamp": (datetime.now() - timedelta(days=4)).isoformat()
            },
            "engagement_summary": {
                "totalEmailsSent": 2,
                "totalEmailsOpened": 1,
                "totalEmailsClicked": 0,
                "hasReplied": False
            }
        }
        
        result = await agent.execute(test_task)
        print("Sequence Manager Result:")
        print(json.dumps(result, indent=2))
    
    # Run test
    asyncio.run(test_sequence_manager())