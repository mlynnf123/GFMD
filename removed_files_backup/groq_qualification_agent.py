#!/usr/bin/env python3
"""
Qualification Agent for GFMD AI Swarm (Groq-powered)
Scores and prioritizes leads based on research findings
"""

from typing import Dict, Any
from groq_base_agent import GroqBaseAgent, AgentRole
import json

class GroqQualificationAgent(GroqBaseAgent):
    """Agent specialized in lead scoring and qualification"""

    def __init__(self, agent_id: str = "qualifier_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.QUALIFIER,
            temperature=0.2  # Very low temperature for consistent scoring
        )

    def get_system_prompt(self) -> str:
        return """You are a Qualification Agent for GFMD Medical Devices, responsible for scoring and prioritizing law enforcement agency prospects for Narc Gone drug destruction products.

Your job is to evaluate prospects based on research findings and assign a qualification score from 0-100.

**Scoring Criteria:**

1. **Agency Fit (0-30 points)**
   - Large police departments (200+ officers): 30 points
   - Medium departments (50-200 officers): 25 points
   - Sheriff's offices with evidence ops: 25 points
   - Federal agencies (DEA, DHS, ICE): 30 points
   - Small departments (<50): 15 points

2. **Pain Points Match (0-25 points)**
   - High incineration costs mentioned: 25 points
   - Evidence storage capacity issues: 20 points
   - Budget pressure/cost reduction goals: 20 points
   - Disposal logistics challenges: 15 points
   - Generic disposal needs: 10 points

3. **Buying Signals (0-25 points)**
   - Active procurement process: 25 points
   - Budget cycle timing: 20 points
   - New evidence facility/renovation: 20 points
   - Cost reduction initiatives: 18 points
   - Policy changes requiring compliance: 15 points
   - No clear signals: 5 points

4. **Decision Maker Access (0-20 points)**
   - Property & Evidence Manager: 20 points
   - Department Commander/Chief: 18 points
   - Evidence Technician/Supervisor: 15 points
   - Procurement/Admin contact: 12 points
   - Unknown decision maker: 5 points

**Priority Classification:**
- 70-100 points: HIGH PRIORITY (immediate outreach)
- 50-69 points: MEDIUM PRIORITY (qualified lead)
- Below 50 points: LOW PRIORITY (nurture/skip)

**CRITICAL**: Return results as valid JSON:
{
  "total_score": 75,
  "priority_level": "HIGH",
  "agency_fit_score": 25,
  "pain_points_score": 20,
  "buying_signals_score": 15,
  "decision_maker_score": 15,
  "qualification_reasoning": "Detailed explanation of scoring",
  "recommended_action": "send_email/nurture/skip",
  "key_talking_points": ["cost_savings", "on_site_destruction", "dea_compliance"]
}
"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute qualification task"""
        try:
            # Extract data
            prospect_data = task.get("prospect_data", {})
            research_findings = task.get("research_findings", {})

            # Build qualification prompt
            qualification_prompt = {
                "task": "qualify_prospect",
                "prospect": {
                    "company_name": prospect_data.get("company_name", ""),
                    "location": prospect_data.get("location", ""),
                    "facility_type": prospect_data.get("facility_type", ""),
                    "contact_title": prospect_data.get("title", ""),
                    "contact_name": prospect_data.get("contact_name", "")
                },
                "research": {
                    "organization_profile": research_findings.get("organization_profile", ""),
                    "pain_points": research_findings.get("pain_points", []),
                    "buying_signals": research_findings.get("buying_signals", []),
                    "decision_makers": research_findings.get("decision_makers", ""),
                    "research_confidence": research_findings.get("research_confidence", "medium")
                },
                "instruction": "Score this prospect using the criteria above and return valid JSON with all required fields."
            }

            # Call Groq AI
            result = await self.think(qualification_prompt)

            # Parse response
            if "error" in result:
                return self._create_default_score(prospect_data, low=True)

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
                    return self._create_default_score(prospect_data)

            # Ensure required fields
            result.setdefault("total_score", 60)
            result.setdefault("priority_level", self._get_priority_level(result.get("total_score", 60)))
            result.setdefault("facility_fit_score", 20)
            result.setdefault("pain_points_score", 15)
            result.setdefault("buying_signals_score", 15)
            result.setdefault("decision_maker_score", 10)
            result.setdefault("qualification_reasoning", "Standard healthcare facility qualification")
            result.setdefault("recommended_action", "send_email" if result["total_score"] >= 50 else "skip")
            result.setdefault("key_talking_points", [
                "Noise reduction in laboratory environments",
                "Equipment efficiency and modernization",
                "Staff satisfaction and compliance"
            ])

            result["success"] = True
            return result

        except Exception as e:
            return self._create_default_score(prospect_data, low=True, error=str(e))

    def _get_priority_level(self, score: int) -> str:
        """Determine priority level from score"""
        if score >= 70:
            return "HIGH"
        elif score >= 50:
            return "MEDIUM"
        else:
            return "LOW"

    def _create_default_score(
        self,
        prospect_data: Dict[str, Any],
        low: bool = False,
        error: str = None
    ) -> Dict[str, Any]:
        """Create a default qualification score"""
        score = 40 if low else 60

        return {
            "success": True,
            "total_score": score,
            "priority_level": self._get_priority_level(score),
            "facility_fit_score": 15 if low else 20,
            "pain_points_score": 10 if low else 15,
            "buying_signals_score": 10 if low else 15,
            "decision_maker_score": 5 if low else 10,
            "qualification_reasoning": error if error else "Standard qualification applied",
            "recommended_action": "skip" if low else "send_email",
            "key_talking_points": [
                "Laboratory noise reduction solutions",
                "Modern centrifuge technology",
                "Healthcare facility optimization"
            ]
        }


# Test the qualification agent
async def test_qualification_agent():
    """Test the qualification agent"""
    import os

    print("🎯 Testing Qualification Agent")
    print("=" * 50)

    if not os.environ.get('GROQ_API_KEY'):
        print("❌ GROQ_API_KEY not set")
        return

    agent = GroqQualificationAgent()

    # Simulate prospect data and research findings
    test_prospect = {
        "company_name": "Abbott Northwestern Hospital",
        "location": "Minneapolis, MN",
        "facility_type": "Short Term Acute Care Hospital",
        "title": "Laboratory Medical Director",
        "contact_name": "Dr. Lauren Anthony"
    }

    test_research = {
        "organization_profile": "630-bed acute care hospital with active lab operations",
        "pain_points": [
            "Noise levels from existing centrifuge equipment",
            "Space constraints in laboratory",
            "Compliance concerns with OSHA noise regulations"
        ],
        "buying_signals": [
            "Recent hospital expansion plans",
            "Aging laboratory equipment due for replacement",
            "Budget allocations for equipment upgrades"
        ],
        "decision_makers": "Laboratory Medical Director",
        "research_confidence": "high"
    }

    print(f"\n📋 Qualifying: {test_prospect['company_name']}")

    result = await agent.execute({
        "prospect_data": test_prospect,
        "research_findings": test_research
    })

    if result.get("success"):
        print(f"\n✅ Qualification completed!")
        print(f"\n📊 Total Score: {result.get('total_score')}/100")
        print(f"🎯 Priority: {result.get('priority_level')}")
        print(f"📈 Action: {result.get('recommended_action')}")
        print(f"\n💬 Reasoning: {result.get('qualification_reasoning', 'N/A')[:200]}...")
        print(f"\n🔑 Key Talking Points:")
        for point in result.get("key_talking_points", [])[:3]:
            print(f"   • {point}")
        print(f"\n🧠 Tokens used: {agent.state['total_tokens_used']}")
    else:
        print(f"\n❌ Qualification failed")


if __name__ == "__main__":
    import asyncio
    import os
    os.environ['GROQ_API_KEY'] = 'your_groq_api_key_here'
    asyncio.run(test_qualification_agent())
