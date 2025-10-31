#!/usr/bin/env python3
"""
Research Agent for GFMD AI Swarm (Groq-powered)
Specializes in gathering intelligence on healthcare prospects
"""

from typing import Dict, Any
from groq_base_agent import GroqBaseAgent, AgentRole
import json

class GroqResearchAgent(GroqBaseAgent):
    """Agent specialized in prospect research and intelligence gathering"""

    def __init__(self, agent_id: str = "researcher_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.RESEARCHER,
            temperature=0.3  # Lower temperature for factual research
        )

    def get_system_prompt(self) -> str:
        return """You are a Research Agent for GFMD (Global Forensic Medical Devices), specializing in B2B intelligence gathering for healthcare facilities.

Your mission is to research potential customers for GFMD's noise-reducing centrifuge equipment. Focus on:

1. **Facility Profile**: Size, lab volume, specialties, location insights
2. **Decision Makers**: Lab directors, equipment managers, procurement officers
3. **Pain Points**: Noise issues, space constraints, compliance concerns, staff complaints
4. **Buying Signals**: Equipment age, renovation plans, budget indicators
5. **Geographic Insights**: Regional healthcare trends, competitive landscape

For healthcare facilities, pay special attention to:
- Mid-size facilities (150-500 beds) - GFMD's sweet spot
- Active laboratory operations
- Locations in growing healthcare markets
- Facilities likely needing equipment upgrades

**IMPORTANT**: Return findings as valid JSON with these exact keys:
{
  "organization_profile": "Brief facility description and size",
  "decision_makers": "Key contacts and their roles",
  "pain_points": ["List", "of", "specific", "problems"],
  "buying_signals": ["List", "of", "purchase", "indicators"],
  "qualification_notes": "Your assessment of fit",
  "research_confidence": "low/medium/high",
  "location_insights": "Regional market analysis"
}

Base your research on:
- Healthcare industry knowledge
- Geographic and regional trends
- Facility type and size indicators
- Market positioning
"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research task"""
        try:
            # Extract prospect information
            company_name = task.get("company_name", "")
            location = task.get("location", "")
            facility_type = task.get("facility_type", "")
            title = task.get("title", "")

            # Build research prompt
            research_prompt = {
                "task": "research_prospect",
                "company_name": company_name,
                "location": location,
                "facility_type": facility_type,
                "contact_title": title,
                "research_focus": [
                    "Analyze facility characteristics and likely lab needs",
                    "Identify pain points related to laboratory equipment and noise",
                    "Assess buying signals based on facility type and location",
                    "Determine decision maker roles and influence",
                    "Provide qualification assessment for GFMD products"
                ]
            }

            # Call Groq AI
            result = await self.think(research_prompt)

            # Ensure we have a valid response
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }

            # If response is wrapped in "response" key, try to parse it
            if "response" in result and isinstance(result["response"], str):
                try:
                    # Try to extract JSON from response
                    response_text = result["response"]
                    # Look for JSON block
                    if "{" in response_text and "}" in response_text:
                        start = response_text.find("{")
                        end = response_text.rfind("}") + 1
                        json_text = response_text[start:end]
                        result = json.loads(json_text)
                    else:
                        # Create structured response from text
                        result = {
                            "organization_profile": response_text[:200],
                            "pain_points": ["Laboratory noise concerns", "Equipment efficiency"],
                            "buying_signals": ["Active laboratory operations"],
                            "qualification_notes": response_text[-200:],
                            "research_confidence": "medium"
                        }
                except:
                    pass

            # Ensure required fields exist
            result.setdefault("organization_profile", f"{facility_type} in {location}")
            result.setdefault("decision_makers", title if title else "Laboratory Director")
            result.setdefault("pain_points", ["Laboratory noise reduction", "Equipment modernization"])
            result.setdefault("buying_signals", ["Active lab operations", "Mid-market facility"])
            result.setdefault("qualification_notes", "Standard healthcare facility prospect")
            result.setdefault("research_confidence", "medium")
            result.setdefault("location_insights", f"Healthcare market in {location}")

            result["success"] = True
            result["researched_at"] = self.state.get("tasks_completed", 0)

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "organization_profile": "Error during research",
                "pain_points": [],
                "buying_signals": [],
                "qualification_notes": f"Research failed: {e}",
                "research_confidence": "low"
            }


# Test the research agent
async def test_research_agent():
    """Test the research agent"""
    import os

    print("🔍 Testing Research Agent")
    print("=" * 50)

    if not os.environ.get('GROQ_API_KEY'):
        print("❌ GROQ_API_KEY not set")
        return

    agent = GroqResearchAgent()

    test_prospect = {
        "company_name": "Abbott Northwestern Hospital",
        "location": "Minneapolis, MN",
        "facility_type": "Short Term Acute Care Hospital",
        "title": "Laboratory Medical Director"
    }

    print(f"\n📋 Researching: {test_prospect['company_name']}")
    print(f"   Location: {test_prospect['location']}")
    print(f"   Type: {test_prospect['facility_type']}")

    result = await agent.execute(test_prospect)

    if result.get("success"):
        print("\n✅ Research completed!")
        print(f"\n📊 Profile: {result.get('organization_profile', 'N/A')}")
        print(f"\n💡 Pain Points:")
        for point in result.get("pain_points", [])[:3]:
            print(f"   • {point}")
        print(f"\n🎯 Buying Signals:")
        for signal in result.get("buying_signals", [])[:3]:
            print(f"   • {signal}")
        print(f"\n📈 Confidence: {result.get('research_confidence', 'N/A')}")
        print(f"\n🧠 Tokens used: {agent.state['total_tokens_used']}")
    else:
        print(f"\n❌ Research failed: {result.get('error')}")


if __name__ == "__main__":
    import asyncio
    import os
    os.environ['GROQ_API_KEY'] = 'your_groq_api_key_here'
    asyncio.run(test_research_agent())
