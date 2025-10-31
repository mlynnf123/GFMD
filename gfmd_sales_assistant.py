#!/usr/bin/env python3
"""
GFMD Sales Assistant Chatbot - Interactive prospect research
"""

import asyncio
from vertex_ai_swarm_orchestrator import GFMDSwarmOrchestrator
from langchain_google_vertexai import ChatVertexAI

class GFMDSalesAssistant:
    def __init__(self, project_id: str):
        self.orchestrator = GFMDSwarmOrchestrator(project_id=project_id)
        self.chat_model = ChatVertexAI(model="gemini-2.0-flash-exp")
        self.conversation_history = []
    
    async def chat_with_user(self, user_message: str):
        """Handle conversational interaction with sales rep"""
        
        # Determine if this is a prospect research request
        if any(keyword in user_message.lower() for keyword in 
               ["research", "analyze", "prospect", "qualify", "hospital"]):
            return await self.handle_prospect_research(user_message)
        
        # Determine if this is a general GFMD question
        elif any(keyword in user_message.lower() for keyword in 
                 ["product", "centrifuge", "equipment", "pricing"]):
            return await self.handle_product_question(user_message)
        
        # General conversation
        else:
            return await self.handle_general_chat(user_message)
    
    async def handle_prospect_research(self, message: str):
        """Handle prospect research requests"""
        # Extract hospital/organization info from message
        # For demo, use a sample prospect
        
        prospect_data = {
            "organization_name": "Metro Regional Hospital",
            "contact_name": "Dr. Sample User",
            "bed_count": 300,
            "lab_type": "Clinical Chemistry"
        }
        
        # Process the prospect
        result = await self.orchestrator.process_new_prospect(prospect_data)
        
        response = f"""
🏥 **Prospect Analysis Complete**

**Organization**: {prospect_data['organization_name']}
**Workflow ID**: {result.get('workflow_id')}
**Status**: {result.get('status')}

**Recommendations**:
• High-priority prospect for centrifuge upgrades
• Focus on efficiency and reliability benefits
• Contact lab director directly
• Follow up within 48 hours

Would you like me to start the outreach sequence?
"""
        return response
    
    async def handle_product_question(self, message: str):
        """Handle product-related questions"""
        return """
🧪 **GFMD Product Information**

**Silencer Centrifuges**:
• ELITE-F24: High-capacity forensic centrifuge
• TANK: Heavy-duty laboratory centrifuge
• MACH-F10: Compact high-speed model

**Key Benefits**:
• US-manufactured reliability
• Reduced downtime and maintenance
• Enhanced sample processing efficiency
• Comprehensive warranty and support

Need specific pricing or technical specs?
"""
    
    async def handle_general_chat(self, message: str):
        """Handle general conversation"""
        return "I'm here to help with prospect research and GFMD product information. How can I assist you today?"

# Usage in a web interface, Slack bot, or CLI:
# assistant = GFMDSalesAssistant("gen-lang-client-0673146524")
# response = await assistant.chat_with_user("Research Metro Hospital for centrifuge opportunities")
