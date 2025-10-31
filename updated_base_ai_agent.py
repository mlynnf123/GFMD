#!/usr/bin/env python3
"""
Updated Base AI Agent with Gemini 2.5 Flash
Uses the latest Gemini 2.5 Flash model for enhanced performance
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum

# Updated imports for Gemini 2.5 Flash
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
import google.generativeai as genai

from ai_agent_architecture import AgentRole, AgentCapability, AgentState
from gemini_25_flash_config import Gemini25FlashConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentMessage:
    """Message structure for agent communication"""
    from_agent: str
    to_agent: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

class UpdatedBaseAIAgent(ABC):
    """Updated Base AI Agent using Gemini 2.5 Flash"""
    
    def __init__(self, agent_id: str, role: AgentRole, temperature: float = 0.3):
        self.agent_id = agent_id
        self.role = role
        self.state = AgentState()
        
        # Initialize Gemini 2.5 Flash
        self.gemini_config = Gemini25FlashConfig()
        self.llm = self.gemini_config.get_llm(temperature=temperature)
        self.direct_model = self.gemini_config.get_direct_model()
        
        # Agent capabilities
        self.capabilities: List[AgentCapability] = []
        
        logger.info(f"Initialized {role.value} agent with Gemini 2.5 Flash: {agent_id}")
    
    async def think(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced thinking with Gemini 2.5 Flash"""
        
        try:
            # Create system message based on role
            system_message = self._create_system_message()
            
            # Create user message with context
            user_message = self._create_user_message(input_data)
            
            # Use Gemini 2.5 Flash for reasoning
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_message)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse JSON response
            try:
                result = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback to structured response
                result = {
                    "agent_id": self.agent_id,
                    "role": self.role.value,
                    "response": response.content,
                    "timestamp": datetime.now().isoformat(),
                    "model": "gemini-2.5-flash"
                }
            
            # Track task
            self.state.completed_tasks.append({
                "task_type": input_data.get("task_type", "general"),
                "timestamp": datetime.now().isoformat(),
                "success": True
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Agent {self.agent_id} thinking error: {e}")
            return {
                "error": str(e),
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def _create_system_message(self) -> str:
        """Create role-specific system message"""
        base_message = f"""You are a {self.role.value} AI agent specialized in healthcare sales.
        
Your role: {self.role.value}
Your capabilities: {', '.join([cap.value for cap in self.capabilities])}
Your goal: Assist with GFMD Silencer Centrifuge sales to healthcare facilities.

Key context:
- GFMD Silencer reduces laboratory noise by up to 70%
- Target: Mid-size hospitals (150-500 beds) with noise concerns
- Decision makers: Lab Directors, VP Operations, Equipment Managers
- Focus on ROI, compliance, and staff satisfaction

Always respond with valid JSON unless specifically asked otherwise."""
        
        return base_message
    
    def _create_user_message(self, input_data: Dict[str, Any]) -> str:
        """Create user message from input data"""
        return f"""Please process this task:

Input: {json.dumps(input_data, indent=2)}

Provide a comprehensive analysis and recommendations in JSON format."""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using the agent's capabilities"""
        
        # Add agent context
        enhanced_task = {
            **task,
            "agent_context": {
                "agent_id": self.agent_id,
                "role": self.role.value,
                "capabilities": [cap.value for cap in self.capabilities],
                "model": "gemini-2.5-flash"
            }
        }
        
        # Process with specific implementation
        result = await self.process_task(enhanced_task)
        
        # Add execution metadata
        result["execution_metadata"] = {
            "agent_id": self.agent_id,
            "model": "gemini-2.5-flash",
            "execution_time": datetime.now().isoformat()
        }
        
        return result
    
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a specific task - implemented by subclasses"""
        pass
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "model": "gemini-2.5-flash",
            "capabilities": [cap.value for cap in self.capabilities],
            "completed_tasks": len(self.state.completed_tasks),
            "status": "active",
            "last_updated": datetime.now().isoformat()
        }

# Test the updated agent
async def test_gemini_25_flash_agent():
    """Test the updated agent with Gemini 2.5 Flash"""
    
    class TestAgent(UpdatedBaseAIAgent):
        async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
            return await self.think(task)
    
    print("🧪 Testing Updated AI Agent with Gemini 2.5 Flash")
    print("=" * 60)
    
    # Create test agent
    agent = TestAgent("test_agent_001", AgentRole.RESEARCHER)
    
    # Test task
    test_task = {
        "task_type": "research",
        "organization_name": "Test Medical Center",
        "location": "Dallas, TX",
        "objective": "Analyze this healthcare facility for GFMD sales opportunity"
    }
    
    # Execute task
    result = await agent.execute(test_task)
    
    print("✅ Agent execution complete!")
    print(f"📊 Agent Status: {agent.get_agent_status()}")
    print(f"📝 Result keys: {list(result.keys())}")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_gemini_25_flash_agent())