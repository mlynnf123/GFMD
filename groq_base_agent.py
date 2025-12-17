#!/usr/bin/env python3
"""
Groq-Based AI Agent - Base Class
Replaces Vertex AI with Groq for blazing fast inference
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from groq import Groq

logger = logging.getLogger(__name__)

class AgentRole(Enum):
    """Agent roles in the swarm"""
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    QUALIFIER = "qualifier"
    EMAIL_COMPOSER = "email_composer"

class GroqBaseAgent:
    """Base AI agent using Groq for inference"""

    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        model: str = "openai/gpt-oss-120b",
        temperature: float = 0.7
    ):
        self.agent_id = agent_id
        self.role = role
        self.model = model
        self.temperature = temperature

        # Initialize Groq client
        api_key = os.environ.get('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        self.client = Groq(api_key=api_key)

        # Agent state
        self.state = {
            "agent_id": agent_id,
            "role": role.value,
            "tasks_completed": 0,
            "total_tokens_used": 0,
            "errors": 0,
            "created_at": datetime.now().isoformat()
        }

        logger.info(f"Initialized {role.value} agent: {agent_id}")

    def get_system_prompt(self) -> str:
        """Override this in subclasses"""
        return "You are a helpful AI assistant."

    async def think(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Core thinking function using Groq"""
        try:
            # Build messages
            messages = [
                {
                    "role": "system",
                    "content": self.get_system_prompt()
                },
                {
                    "role": "user",
                    "content": self._format_input(input_data)
                }
            ]

            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=2048
            )

            # Extract response
            content = response.choices[0].message.content

            # Update metrics
            self.state["tasks_completed"] += 1
            self.state["total_tokens_used"] += response.usage.total_tokens

            # Try to parse as JSON, otherwise return as text
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"response": content}

        except Exception as e:
            logger.error(f"Error in {self.role.value} agent: {e}")
            self.state["errors"] += 1
            return {"error": str(e), "success": False}

    def _format_input(self, input_data: Dict[str, Any]) -> str:
        """Format input data as a clear prompt"""
        return json.dumps(input_data, indent=2)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task - override in subclasses"""
        return await self.think(task)

    def get_state(self) -> Dict[str, Any]:
        """Get current agent state"""
        return self.state.copy()

    def reset_state(self):
        """Reset agent state"""
        self.state["tasks_completed"] = 0
        self.state["total_tokens_used"] = 0
        self.state["errors"] = 0

# Test function
async def test_groq_agent():
    """Test the Groq base agent"""
    print("🧪 Testing Groq Base Agent")
    print("=" * 50)

    # Check for API key
    if not os.environ.get('GROQ_API_KEY'):
        print("❌ GROQ_API_KEY not set")
        print("Get your key from: https://console.groq.com/keys")
        return

    try:
        agent = GroqBaseAgent(
            agent_id="test_001",
            role=AgentRole.RESEARCHER,
            temperature=0.3
        )

        test_input = {
            "task": "Summarize what GFMD does",
            "context": "Company focused on Narc Gone drug destruction products for law enforcement agencies"
        }

        print(f"📤 Sending test prompt...")
        result = await agent.think(test_input)

        print(f"✅ Response received!")
        print(f"📊 Tokens used: {agent.state['total_tokens_used']}")
        print(f"📝 Result: {result}")

    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_groq_agent())
