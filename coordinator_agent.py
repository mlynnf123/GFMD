#!/usr/bin/env python3
"""
Coordinator Agent for GFMD AI Swarm
Orchestrates the entire agent workflow and manages task distribution
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from base_ai_agent import BaseAIAgent, AgentMessage
from ai_agent_architecture import AgentRole
from research_agent import ResearchAgent
from qualification_agent import QualificationAgent
from email_composer_agent import EmailComposerAgent
from langsmith import traceable

class WorkflowStage(Enum):
    """Workflow stages for prospect processing"""
    INTAKE = "intake"
    RESEARCH = "research"
    QUALIFICATION = "qualification"
    EMAIL_COMPOSITION = "email_composition"
    REVIEW = "review"
    COMPLETE = "complete"

class CoordinatorAgent(BaseAIAgent):
    """Master coordinator that orchestrates the entire agent swarm"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.COORDINATOR,
            temperature=0.2  # Low temperature for consistent decision-making
        )
        
        # Initialize the swarm
        self.agents = self._initialize_swarm()
        
        # Workflow tracking
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        
        # Performance metrics
        self.metrics = {
            "prospects_processed": 0,
            "emails_generated": 0,
            "high_priority_leads": 0,
            "average_processing_time": 0,
            "errors": 0
        }
    
    def _initialize_swarm(self) -> Dict[AgentRole, BaseAIAgent]:
        """Initialize all specialized agents"""
        return {
            AgentRole.RESEARCHER: ResearchAgent("researcher_001"),
            AgentRole.QUALIFIER: QualificationAgent("qualifier_001"),
            AgentRole.EMAIL_COMPOSER: EmailComposerAgent("composer_001")
        }
    
    def get_system_prompt(self) -> str:
        return """You are the Coordinator Agent for GFMD's AI sales swarm, responsible for orchestrating the entire lead generation and outreach workflow.

Your responsibilities:
1. **Task Decomposition**: Break down prospect processing into appropriate subtasks
2. **Agent Assignment**: Assign tasks to the right specialized agents
3. **Quality Control**: Ensure outputs meet GFMD standards
4. **Workflow Management**: Track progress and handle exceptions
5. **Decision Making**: Determine next steps based on results

Workflow Stages:
1. INTAKE - Receive new prospects to process
2. RESEARCH - Assign to Research Agent for intelligence gathering
3. QUALIFICATION - Send research + prospect to Qualification Agent
4. EMAIL_COMPOSITION - High-scoring leads go to Email Composer
5. REVIEW - Final quality check
6. COMPLETE - Ready for sending

Decision Criteria:
- Only compose emails for prospects scoring 60+ (Medium/High priority)
- Prioritize High priority prospects for immediate processing
- Flag any data quality issues for human review

Return decisions as JSON with:
- next_stage: The next workflow stage
- assigned_agent: Which agent to activate (if any)
- priority: Processing priority (high/medium/low)
- quality_notes: Any quality concerns
- decision_reasoning: Why this decision was made"""
    
    @traceable(name="coordinate_workflow")
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process coordination task"""
        
        task_type = task.get("type", "process_prospects")
        
        if task_type == "process_prospects":
            return await self._process_prospects_batch(task.get("prospects", []))
        elif task_type == "workflow_decision":
            return await self._make_workflow_decision(task.get("workflow_state", {}))
        elif task_type == "quality_review":
            return await self._perform_quality_review(task.get("outputs", {}))
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _process_prospects_batch(self, prospects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a batch of prospects through the entire workflow"""
        
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        batch_results = {
            "batch_id": batch_id,
            "total_prospects": len(prospects),
            "processed": [],
            "errors": [],
            "summary": {}
        }
        
        print(f"🎯 Coordinator processing batch of {len(prospects)} prospects")
        
        # Process each prospect through the workflow
        for prospect in prospects:
            try:
                result = await self._process_single_prospect(prospect)
                batch_results["processed"].append(result)
                
                # Update metrics
                if result.get("qualification", {}).get("priority_level") == "High":
                    self.metrics["high_priority_leads"] += 1
                if result.get("email"):
                    self.metrics["emails_generated"] += 1
                    
            except Exception as e:
                batch_results["errors"].append({
                    "prospect": prospect.get("organization_name", "Unknown"),
                    "error": str(e)
                })
                self.metrics["errors"] += 1
        
        # Generate batch summary
        batch_results["summary"] = self._generate_batch_summary(batch_results)
        
        return batch_results
    
    async def _process_single_prospect(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single prospect through all stages"""
        
        workflow_id = f"wf_{datetime.now().timestamp()}"
        workflow_state = {
            "workflow_id": workflow_id,
            "prospect": prospect_data,
            "current_stage": WorkflowStage.INTAKE,
            "results": {},
            "start_time": datetime.now()
        }
        
        self.active_workflows[workflow_id] = workflow_state
        
        try:
            # Stage 1: Research
            print(f"  🔍 Researching {prospect_data.get('organization_name', 'Unknown')}")
            research_result = await self._execute_research(prospect_data)
            workflow_state["results"]["research"] = research_result
            workflow_state["current_stage"] = WorkflowStage.RESEARCH
            
            # Stage 2: Qualification
            print(f"  🎯 Qualifying prospect")
            qualification_result = await self._execute_qualification(
                prospect_data, research_result
            )
            workflow_state["results"]["qualification"] = qualification_result
            workflow_state["current_stage"] = WorkflowStage.QUALIFICATION
            
            # Decision point: Should we compose an email?
            if qualification_result.get("total_score", 0) >= 60:
                # Stage 3: Email Composition
                print(f"  ✉️ Composing email (Score: {qualification_result.get('total_score')})")
                email_result = await self._execute_email_composition(
                    prospect_data, research_result, qualification_result
                )
                workflow_state["results"]["email"] = email_result
                workflow_state["current_stage"] = WorkflowStage.EMAIL_COMPOSITION
            else:
                print(f"  ⏭️ Skipping email (Score: {qualification_result.get('total_score')} < 60)")
                workflow_state["results"]["email"] = None
            
            # Stage 4: Review
            review_result = await self._perform_final_review(workflow_state)
            workflow_state["results"]["review"] = review_result
            workflow_state["current_stage"] = WorkflowStage.COMPLETE
            
            # Calculate processing time
            processing_time = (datetime.now() - workflow_state["start_time"]).total_seconds()
            
            # Compile final result
            final_result = {
                "prospect": prospect_data,
                "research": research_result,
                "qualification": qualification_result,
                "email": workflow_state["results"].get("email"),
                "review": review_result,
                "processing_time": processing_time,
                "workflow_id": workflow_id
            }
            
            # Update metrics
            self.metrics["prospects_processed"] += 1
            
            return final_result
            
        finally:
            # Clean up workflow tracking
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
    
    async def _execute_research(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research stage"""
        researcher = self.agents[AgentRole.RESEARCHER]
        
        research_task = {
            "organization_name": prospect_data.get("organization_name", ""),
            "location": prospect_data.get("location", ""),
            "facility_type": prospect_data.get("facility_type", "healthcare")
        }
        
        return await researcher.execute(research_task)
    
    async def _execute_qualification(
        self, 
        prospect_data: Dict[str, Any], 
        research_findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute qualification stage"""
        qualifier = self.agents[AgentRole.QUALIFIER]
        
        qualification_task = {
            "prospect_data": prospect_data,
            "research_findings": research_findings
        }
        
        return await qualifier.execute(qualification_task)
    
    async def _execute_email_composition(
        self,
        prospect_data: Dict[str, Any],
        research_findings: Dict[str, Any],
        qualification_score: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute email composition stage"""
        composer = self.agents[AgentRole.EMAIL_COMPOSER]
        
        composition_task = {
            "prospect_data": prospect_data,
            "research_findings": research_findings,
            "qualification_score": qualification_score
        }
        
        return await composer.execute(composition_task)
    
    async def _perform_final_review(self, workflow_state: Dict[str, Any]) -> Dict[str, Any]:
        """Perform final quality review"""
        
        review_input = {
            "workflow_state": workflow_state,
            "review_checklist": [
                "Is the research comprehensive?",
                "Is the qualification score justified?",
                "Does the email follow styling rules?",
                "Are there any red flags or concerns?",
                "Is this ready for sending?"
            ]
        }
        
        review_result = await self.think(review_input)
        
        return {
            "approved": review_result.get("approved", True),
            "confidence": review_result.get("confidence", "high"),
            "notes": review_result.get("notes", []),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_batch_summary(self, batch_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics for a batch"""
        
        processed = batch_results["processed"]
        
        # Calculate statistics
        high_priority = sum(1 for p in processed 
                          if p.get("qualification", {}).get("priority_level") == "High")
        medium_priority = sum(1 for p in processed 
                            if p.get("qualification", {}).get("priority_level") == "Medium")
        emails_created = sum(1 for p in processed if p.get("email") is not None)
        avg_score = sum(p.get("qualification", {}).get("total_score", 0) 
                       for p in processed) / len(processed) if processed else 0
        
        return {
            "total_processed": len(processed),
            "high_priority_count": high_priority,
            "medium_priority_count": medium_priority,
            "emails_created": emails_created,
            "average_qualification_score": round(avg_score, 1),
            "error_count": len(batch_results["errors"]),
            "success_rate": f"{(len(processed) / batch_results['total_prospects'] * 100):.1f}%"
        }
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """Get current status of the swarm"""
        
        agent_statuses = {}
        for role, agent in self.agents.items():
            agent_statuses[role.value] = agent.get_state()
        
        return {
            "coordinator_metrics": self.metrics,
            "active_workflows": len(self.active_workflows),
            "agent_statuses": agent_statuses,
            "swarm_health": "operational"
        }
    
    async def optimize_workflow(self) -> Dict[str, Any]:
        """Use AI to suggest workflow optimizations"""
        
        optimization_input = {
            "current_metrics": self.metrics,
            "recent_performance": "Last 100 prospects",
            "request": "Suggest optimizations to improve efficiency and quality"
        }
        
        optimizations = await self.think(optimization_input)
        
        return {
            "suggestions": optimizations.get("suggestions", []),
            "priority_changes": optimizations.get("priority_changes", []),
            "workflow_adjustments": optimizations.get("workflow_adjustments", [])
        }

# Main orchestration function
async def process_prospects_with_ai_swarm(prospects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Main entry point for processing prospects with the AI swarm"""
    
    print("🤖 Initializing GFMD AI Agent Swarm")
    print("=" * 60)
    
    # Initialize coordinator
    coordinator = CoordinatorAgent("coordinator_001")
    
    # Process prospects
    results = await coordinator.execute({
        "type": "process_prospects",
        "prospects": prospects
    })
    
    # Get swarm status
    status = coordinator.get_swarm_status()
    
    print("\n📊 Swarm Processing Complete")
    print(f"✅ Processed: {results['summary']['total_processed']} prospects")
    print(f"📧 Emails Created: {results['summary']['emails_created']}")
    print(f"⭐ High Priority: {results['summary']['high_priority_count']}")
    
    return {
        "results": results,
        "swarm_status": status
    }

# Test the coordinator
async def test_coordinator():
    """Test the coordinator agent"""
    
    print("🎯 Testing Coordinator Agent")
    print("=" * 60)
    
    # Test prospects
    test_prospects = [
        {
            "organization_name": "Dallas Regional Medical Center",
            "location": "Dallas, TX",
            "contact_name": "Dr. Sarah Johnson",
            "contact_title": "Laboratory Director",
            "email": "s.johnson@dallasregional.org"
        },
        {
            "organization_name": "Houston Community Hospital",
            "location": "Houston, TX",
            "contact_name": "Michael Chen",
            "contact_title": "VP Operations",
            "email": "m.chen@houstoncomm.org"
        }
    ]
    
    # Process with swarm
    results = await process_prospects_with_ai_swarm(test_prospects)
    
    print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_coordinator())