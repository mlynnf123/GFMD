#!/usr/bin/env python3
"""
Research Agent for GFMD AI Swarm
Specializes in gathering intelligence on healthcare prospects
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from base_ai_agent import BaseAIAgent
from ai_agent_architecture import AgentRole
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_google_vertexai import VertexAI
from langsmith import traceable

class ResearchAgent(BaseAIAgent):
    """Agent specialized in prospect research and intelligence gathering"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.RESEARCHER,
            temperature=0.3  # Slightly higher for creative research
        )
        
        # Initialize research tools
        self.tools = self._initialize_tools()
        
        # Research focus areas for GFMD
        self.research_areas = [
            "laboratory operations",
            "centrifuge equipment",
            "noise complaints",
            "facility size and beds",
            "recent expansions or renovations",
            "equipment procurement",
            "decision makers",
            "budget cycles"
        ]
    
    def get_system_prompt(self) -> str:
        return """You are a Research Agent for GFMD (Global Forensic Medical Devices), specializing in B2B intelligence gathering for healthcare facilities.

Your mission is to research potential customers for GFMD's noise-reducing centrifuge equipment. Focus on:

1. **Facility Profile**: Size (beds), lab volume, specialties, recent growth
2. **Decision Makers**: Lab directors, equipment managers, procurement officers
3. **Pain Points**: Noise issues, space constraints, compliance concerns, staff complaints
4. **Buying Signals**: Equipment age, renovation plans, budget announcements, RFPs
5. **Budget Indicators**: Financial health, recent purchases, funding sources

For Texas healthcare facilities, pay special attention to:
- Mid-size facilities (150-500 beds) - our sweet spot
- Active laboratory operations
- Recent Joint Commission visits or compliance issues
- Facilities NOT locked into GPO contracts

Always return findings as structured JSON with these keys:
- organization_profile: Basic facility information
- decision_makers: Key contacts with titles and potential influence
- pain_points: Specific problems GFMD can solve
- buying_signals: Indicators of purchase readiness
- qualification_notes: Your assessment of fit
- research_confidence: low/medium/high based on data quality
- sources: Where information was found"""
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize research tools (simulated for now)"""
        # In production, these would connect to real APIs
        # For now, we'll use the LLM's knowledge with structured prompts
        
        def search_facility_info(query: str) -> str:
            """Simulated facility search"""
            return f"Searching for facility information: {query}"
        
        def search_decision_makers(organization: str) -> str:
            """Simulated decision maker search"""
            return f"Searching for decision makers at: {organization}"
        
        def search_news_and_updates(organization: str) -> str:
            """Simulated news search"""
            return f"Searching recent news for: {organization}"
        
        return [
            Tool(
                name="facility_search",
                func=search_facility_info,
                description="Search for healthcare facility information"
            ),
            Tool(
                name="people_search",
                func=search_decision_makers,
                description="Find decision makers at healthcare organizations"
            ),
            Tool(
                name="news_search",
                func=search_news_and_updates,
                description="Search recent news and updates about facilities"
            )
        ]
    
    @traceable(name="research_prospect")
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a research task"""
        
        # Extract research parameters
        organization_name = task.get("organization_name", "")
        location = task.get("location", "")
        facility_type = task.get("facility_type", "healthcare facility")
        
        # Build comprehensive research query
        research_query = {
            "target_organization": organization_name,
            "location": location,
            "facility_type": facility_type,
            "research_objectives": [
                f"Find information about {organization_name}'s laboratory operations",
                f"Identify decision makers for laboratory equipment at {organization_name}",
                f"Discover any noise-related issues or complaints at {organization_name}",
                f"Determine facility size, bed count, and lab volume",
                f"Find recent equipment purchases or renovation projects",
                f"Assess budget and purchasing timeline indicators"
            ]
        }
        
        # Use LLM to conduct research
        research_results = await self.think(research_query)
        
        # Enhance with specific GFMD insights
        enhanced_results = await self._enhance_for_gfmd(research_results, organization_name)
        
        # Add metadata
        enhanced_results["research_metadata"] = {
            "researched_by": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "organization": organization_name,
            "location": location
        }
        
        return enhanced_results
    
    async def _enhance_for_gfmd(self, research_results: Dict[str, Any], organization: str) -> Dict[str, Any]:
        """Enhance research with GFMD-specific insights"""
        
        enhancement_prompt = {
            "research_results": research_results,
            "enhance_for": "GFMD centrifuge sales",
            "focus_areas": [
                "How noise reduction would benefit this facility",
                "Specific departments that would value quiet equipment",
                "Compliance or accreditation benefits",
                "ROI calculation factors",
                "Competitive advantages of switching to GFMD"
            ],
            "organization": organization
        }
        
        enhancements = await self.think(enhancement_prompt)
        
        # Merge enhancements with original research
        research_results["gfmd_insights"] = enhancements.get("insights", {})
        research_results["value_proposition"] = enhancements.get("value_proposition", "")
        research_results["approach_strategy"] = enhancements.get("approach_strategy", "")
        
        return research_results
    
    async def research_batch(self, prospects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Research multiple prospects in parallel"""
        
        research_tasks = []
        for prospect in prospects:
            task = {
                "organization_name": prospect.get("organization_name", ""),
                "location": prospect.get("location", ""),
                "facility_type": prospect.get("facility_type", "healthcare facility")
            }
            research_tasks.append(self.process_task(task))
        
        # Run research in parallel
        results = await asyncio.gather(*research_tasks)
        
        return results
    
    async def deep_dive_research(self, organization: str, focus_area: str) -> Dict[str, Any]:
        """Conduct deep research on a specific aspect"""
        
        deep_dive_query = {
            "organization": organization,
            "deep_dive_focus": focus_area,
            "questions": [
                f"What are the specific details about {focus_area} at {organization}?",
                f"Who are the key stakeholders involved in {focus_area}?",
                f"What challenges or opportunities exist related to {focus_area}?",
                f"What is the timeline and urgency around {focus_area}?",
                f"How does {focus_area} align with GFMD's value proposition?"
            ]
        }
        
        deep_results = await self.think(deep_dive_query)
        
        return {
            "organization": organization,
            "focus_area": focus_area,
            "findings": deep_results,
            "timestamp": datetime.now().isoformat()
        }

# Standalone research function for testing
async def research_prospect(organization_name: str, location: str) -> Dict[str, Any]:
    """Standalone function to research a single prospect"""
    
    agent = ResearchAgent("research_001")
    
    task = {
        "organization_name": organization_name,
        "location": location,
        "facility_type": "hospital"
    }
    
    result = await agent.execute(task)
    return result

# Test the research agent
async def test_research_agent():
    """Test the research agent with a sample prospect"""
    
    print("🔍 Testing Research Agent")
    print("=" * 60)
    
    # Test single prospect research
    test_prospect = {
        "organization_name": "Dallas Regional Medical Center",
        "location": "Dallas, TX",
        "facility_type": "Regional Medical Center"
    }
    
    agent = ResearchAgent("research_test_001")
    result = await agent.execute(test_prospect)
    
    print("\n📊 Research Results:")
    print(json.dumps(result, indent=2))
    
    # Test batch research
    print("\n🔍 Testing Batch Research")
    test_batch = [
        {"organization_name": "Houston Methodist Hospital", "location": "Houston, TX"},
        {"organization_name": "Austin Medical Center", "location": "Austin, TX"}
    ]
    
    batch_results = await agent.research_batch(test_batch)
    print(f"\n✅ Researched {len(batch_results)} prospects")

if __name__ == "__main__":
    asyncio.run(test_research_agent())