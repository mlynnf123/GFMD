#!/usr/bin/env python3
"""
Research Agent for GFMD AI Swarm (Groq-powered)
Specializes in gathering intelligence on law enforcement prospects
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
        return """You are a Research Agent for GFMD (Global Forensic Medical Devices), specializing in B2B intelligence gathering for law enforcement and government agencies.

Your mission is to research potential customers for GFMD's Narcon drug destruction products. Focus on:

1. **Agency Profile**: Size, evidence volume, jurisdiction type, location insights
2. **Decision Makers**: Property & Evidence managers, procurement officers, department heads
3. **Pain Points**: Drug disposal costs, incineration expenses, storage limitations, compliance burdens
4. **Buying Signals**: Budget cycles, evidence backlogs, policy changes, cost reduction initiatives
5. **Geographic Insights**: Regional drug seizure trends, agency funding, regulatory environment

For law enforcement agencies, pay special attention to:
- Police departments (50+ officers) - GFMD's target size
- Sheriff's offices with evidence operations
- Federal agencies (DEA, DHS, ICE, CBP)
- Locations with high drug seizure volumes
- Agencies seeking cost-effective disposal alternatives

**IMPORTANT**: Return findings as valid JSON with these exact keys:
{
  "organization_profile": "Brief agency description and jurisdiction size",
  "decision_makers": "Key contacts and their roles (Property & Evidence, Procurement)",
  "pain_points": ["List", "of", "drug", "disposal", "challenges"],
  "buying_signals": ["List", "of", "budget", "and", "policy", "indicators"],
  "qualification_notes": "Your assessment of Narcon fit and agency potential",
  "research_confidence": "low/medium/high",
  "location_insights": "Regional drug seizure trends and agency funding"
}

Base your research on:
- Law enforcement industry knowledge  
- Drug seizure trends and volumes
- Agency budget cycles and procurement processes
- Evidence management challenges
- Cost pressures on incineration disposal
"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research task"""
        try:
            # Extract prospect information
            company_name = task.get("company_name", "")
            location = task.get("location", "")
            agency_type = task.get("agency_type", task.get("facility_type", ""))
            title = task.get("title", "")

            # Build research prompt
            research_prompt = {
                "task": "research_law_enforcement_prospect",
                "agency_name": company_name,
                "location": location,
                "agency_type": agency_type,
                "contact_title": title,
                "research_focus": [
                    "Analyze agency size and drug seizure volume potential",
                    "Identify pain points related to drug evidence disposal costs",
                    "Assess budget cycles and procurement processes", 
                    "Determine Property & Evidence manager influence and needs",
                    "Evaluate Narcon MX/CX fit for this agency's requirements"
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
                            "pain_points": ["Evidence disposal costs", "Incineration expenses"],
                            "buying_signals": ["Evidence backlog", "Budget constraints"],
                            "qualification_notes": response_text[-200:],
                            "research_confidence": "medium"
                        }
                except:
                    pass

            # Ensure required fields exist
            result.setdefault("organization_profile", f"{facility_type} in {location}")
            result.setdefault("decision_makers", title if title else "Laboratory Director")
            result.setdefault("pain_points", ["Evidence destruction costs", "Disposal efficiency"])
            result.setdefault("buying_signals", ["Active law enforcement", "Budget awareness"])
            result.setdefault("qualification_notes", "Standard law enforcement agency prospect")
            result.setdefault("research_confidence", "medium")
            result.setdefault("location_insights", f"Law enforcement region in {location}")

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
