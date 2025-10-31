#!/usr/bin/env python3
"""
Base AI Agent Class for GFMD Swarm
Provides core functionality for all specialized agents
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass, field
import logging

from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_google_vertexai import ChatVertexAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback
from langsmith import traceable

from ai_agent_architecture import AgentRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentMessage:
    """Standard message format for agent communication"""
    from_agent: str
    to_agent: str
    message_type: str  # request, response, notification
    content: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    correlation_id: Optional[str] = None

@dataclass
class AgentState:
    """Tracks agent state and history"""
    agent_id: str
    role: AgentRole
    status: str = "idle"  # idle, working, waiting
    current_task: Optional[Dict[str, Any]] = None
    completed_tasks: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)

class BaseAIAgent(ABC):
    """Base class for all AI agents in the swarm"""
    
    def __init__(
        self, 
        agent_id: str,
        role: AgentRole,
        model_name: str = "gemini-2.0-flash-exp",
        temperature: float = 0.2
    ):
        self.agent_id = agent_id
        self.role = role
        self.state = AgentState(agent_id=agent_id, role=role)
        
        # Initialize LangChain components
        self.llm = ChatVertexAI(
            model=model_name,
            temperature=temperature,
            max_output_tokens=2048,
            response_format={"type": "json_object"}  # Ensure JSON responses
        )
        
        # Memory for conversation context
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Message queue for async communication
        self.message_queue: asyncio.Queue = asyncio.Queue()
        
        # Callbacks for agent events
        self.callbacks: Dict[str, List[Callable]] = {
            "on_task_start": [],
            "on_task_complete": [],
            "on_error": []
        }
        
        logger.info(f"Initialized {role.value} agent: {agent_id}")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Each agent must define its system prompt"""
        pass
    
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Each agent must implement task processing logic"""
        pass
    
    @traceable(name="agent_think")
    async def think(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Core thinking process using LLM"""
        self.state.status = "working"
        
        try:
            # Build prompt
            prompt = PromptTemplate(
                template=self.get_system_prompt() + "\n\nInput: {input}\n\nOutput:",
                input_variables=["input"]
            )
            
            # Create chain
            chain = LLMChain(llm=self.llm, prompt=prompt, memory=self.memory)
            
            # Execute
            response = await chain.arun(input=json.dumps(input_data))
            
            # Parse JSON response
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # Fallback for non-JSON responses
                result = {"response": response}
            
            return result
            
        except Exception as e:
            logger.error(f"Agent {self.agent_id} thinking error: {e}")
            self.state.errors.append({
                "error": str(e),
                "task": input_data,
                "timestamp": datetime.now().isoformat()
            })
            raise
        finally:
            self.state.status = "idle"
    
    async def receive_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle incoming messages from other agents"""
        logger.info(f"Agent {self.agent_id} received message from {message.from_agent}")
        
        if message.message_type == "request":
            # Process the request
            result = await self.process_task(message.content)
            
            # Send response
            response = AgentMessage(
                from_agent=self.agent_id,
                to_agent=message.from_agent,
                message_type="response",
                content=result,
                correlation_id=message.correlation_id
            )
            return response
        
        elif message.message_type == "notification":
            # Handle notifications (e.g., status updates)
            await self.handle_notification(message)
            return None
        
        return None
    
    async def handle_notification(self, message: AgentMessage):
        """Handle notification messages"""
        logger.info(f"Agent {self.agent_id} handling notification: {message.content}")
        # Override in subclasses for specific handling
    
    def add_callback(self, event: str, callback: Callable):
        """Register callbacks for agent events"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    async def emit_event(self, event: str, data: Any):
        """Emit events to registered callbacks"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                await callback(self, data)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state"""
        return {
            "agent_id": self.state.agent_id,
            "role": self.state.role.value,
            "status": self.state.status,
            "current_task": self.state.current_task,
            "completed_tasks": len(self.state.completed_tasks),
            "errors": len(self.state.errors)
        }
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """Get conversation history from memory"""
        return self.memory.chat_memory.messages
    
    async def collaborate_with(self, other_agent: 'BaseAIAgent', task: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with another agent on a task"""
        message = AgentMessage(
            from_agent=self.agent_id,
            to_agent=other_agent.agent_id,
            message_type="request",
            content=task,
            correlation_id=f"{self.agent_id}_{datetime.now().timestamp()}"
        )
        
        response = await other_agent.receive_message(message)
        if response:
            return response.content
        return {}
    
    @traceable(name="agent_execute")
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method with event handling"""
        try:
            # Emit start event
            await self.emit_event("on_task_start", task)
            self.state.current_task = task
            
            # Process the task
            result = await self.process_task(task)
            
            # Record completion
            self.state.completed_tasks.append({
                "task": task,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            self.state.current_task = None
            
            # Emit complete event
            await self.emit_event("on_task_complete", result)
            
            return result
            
        except Exception as e:
            # Emit error event
            await self.emit_event("on_error", {"error": str(e), "task": task})
            raise

# Example concrete implementation
class ExampleAgent(BaseAIAgent):
    """Example implementation of a concrete agent"""
    
    def get_system_prompt(self) -> str:
        return """You are an example agent in the GFMD swarm.
Your task is to process inputs and return structured JSON responses.
Always be helpful and accurate."""
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a specific task"""
        # Use the think method to leverage LLM
        result = await self.think(task)
        
        # Add any agent-specific processing
        result["processed_by"] = self.agent_id
        result["timestamp"] = datetime.now().isoformat()
        
        return result

# Test the base agent
async def test_base_agent():
    """Test the base agent functionality"""
    agent = ExampleAgent("example_001", AgentRole.RESEARCHER)
    
    test_task = {
        "action": "analyze",
        "target": "Test Medical Center",
        "requirements": "Find basic information"
    }
    
    result = await agent.execute(test_task)
    print(f"Result: {json.dumps(result, indent=2)}")
    print(f"State: {json.dumps(agent.get_state(), indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_base_agent())