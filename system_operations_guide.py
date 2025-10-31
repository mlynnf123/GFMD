#!/usr/bin/env python3
"""
GFMD Swarm Agent System - Operations Guide
Understanding how the system works and different deployment modes.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List

# Import the system components
from vertex_ai_swarm_orchestrator import GFMDSwarmOrchestrator

def demonstrate_operation_modes():
    """
    Show different ways the GFMD Swarm Agent system can operate
    """
    print("🤖 GFMD Swarm Agent System - Operation Modes")
    print("=" * 60)
    
    print("\n1️⃣ MANUAL/API MODE (Current)")
    print("   • Triggered by function calls")
    print("   • Processes one prospect at a time")
    print("   • Returns results immediately")
    print("   • Perfect for CRM integrations")
    
    print("\n2️⃣ BATCH PROCESSING MODE")
    print("   • Processes multiple prospects from a queue")
    print("   • Runs on schedule (hourly, daily)")
    print("   • Handles large volumes efficiently")
    print("   • Good for data imports")
    
    print("\n3️⃣ REAL-TIME MONITORING MODE")
    print("   • Always running, watching for new prospects")
    print("   • Immediate processing as data arrives")
    print("   • Webhook-triggered from CRM/forms")
    print("   • 24/7 lead processing")
    
    print("\n4️⃣ CHATBOT/CONVERSATIONAL MODE")
    print("   • Interactive chat interface")
    print("   • Helps sales reps with prospect research")
    print("   • Answers questions about leads")
    print("   • Provides recommendations on-demand")

async def manual_processing_example():
    """
    Example of current manual processing mode
    """
    print("\n🎯 Manual Processing Example")
    print("-" * 40)
    
    # Initialize the orchestrator
    orchestrator = GFMDSwarmOrchestrator(
        project_id="gen-lang-client-0673146524"
    )
    
    # Example: New prospect comes in from website form
    new_prospect = {
        "organization_name": "City General Hospital",
        "contact_name": "Dr. Lisa Martinez",
        "contact_title": "Chief Laboratory Officer",
        "email": "l.martinez@citygeneral.org",
        "phone": "555-0789",
        "bed_count": 450,
        "lab_type": "Clinical Chemistry, Microbiology",
        "location": "Denver, CO",
        "source": "website_contact_form",
        "urgency": "high"
    }
    
    print(f"📥 New prospect received: {new_prospect['organization_name']}")
    
    # Process the prospect
    result = await orchestrator.process_new_prospect(new_prospect)
    
    print(f"✅ Processing complete: {result.get('workflow_id')}")
    print(f"   Status: {result.get('status')}")
    
    return result

def create_batch_processor():
    """
    Example of how to create a batch processing system
    """
    batch_code = '''#!/usr/bin/env python3
"""
GFMD Batch Processor - Handles multiple prospects from queue
"""

import asyncio
import json
from datetime import datetime
from vertex_ai_swarm_orchestrator import GFMDSwarmOrchestrator

class GFMDBatchProcessor:
    def __init__(self, project_id: str):
        self.orchestrator = GFMDSwarmOrchestrator(project_id=project_id)
        self.batch_size = 10
        self.processed_count = 0
    
    async def process_prospect_batch(self, prospects: list):
        """Process a batch of prospects"""
        results = []
        
        for prospect in prospects[:self.batch_size]:
            try:
                result = await self.orchestrator.process_new_prospect(prospect)
                results.append({
                    "prospect": prospect["organization_name"],
                    "status": "success",
                    "workflow_id": result.get("workflow_id"),
                    "processed_at": datetime.now().isoformat()
                })
                self.processed_count += 1
                
            except Exception as e:
                results.append({
                    "prospect": prospect.get("organization_name", "Unknown"),
                    "status": "error",
                    "error": str(e),
                    "processed_at": datetime.now().isoformat()
                })
        
        return results
    
    def load_prospects_from_csv(self, csv_file: str):
        """Load prospects from CSV file"""
        # Implementation would read CSV and convert to prospect dicts
        pass
    
    def save_batch_results(self, results: list, batch_id: str):
        """Save batch processing results"""
        filename = f"batch_results_{batch_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"📊 Batch results saved: {filename}")

# Usage example:
# processor = GFMDBatchProcessor("gen-lang-client-0673146524")
# prospects = processor.load_prospects_from_csv("new_leads.csv")
# results = await processor.process_prospect_batch(prospects)
'''
    
    with open('gfmd_batch_processor.py', 'w') as f:
        f.write(batch_code)
    
    print("✅ Created gfmd_batch_processor.py")

def create_realtime_monitor():
    """
    Example of real-time monitoring system
    """
    monitor_code = '''#!/usr/bin/env python3
"""
GFMD Real-time Monitor - Always-running prospect processor
"""

import asyncio
import json
import time
from datetime import datetime
from vertex_ai_swarm_orchestrator import GFMDSwarmOrchestrator

class GFMDRealtimeMonitor:
    def __init__(self, project_id: str):
        self.orchestrator = GFMDSwarmOrchestrator(project_id=project_id)
        self.running = False
        self.processed_today = 0
    
    async def start_monitoring(self):
        """Start the real-time monitoring system"""
        self.running = True
        print("🔄 Starting GFMD real-time monitoring...")
        
        while self.running:
            try:
                # Check for new prospects (from database, queue, webhooks, etc.)
                new_prospects = await self.check_for_new_prospects()
                
                if new_prospects:
                    print(f"📥 Found {len(new_prospects)} new prospects")
                    
                    for prospect in new_prospects:
                        await self.process_prospect_immediately(prospect)
                
                # Wait before checking again
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"❌ Monitor error: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def check_for_new_prospects(self):
        """Check various sources for new prospects"""
        # This would connect to:
        # - CRM webhooks
        # - Database change streams
        # - Message queues (RabbitMQ, Redis)
        # - File watchers
        
        # Placeholder - return empty list for now
        return []
    
    async def process_prospect_immediately(self, prospect):
        """Process a prospect immediately when detected"""
        try:
            result = await self.orchestrator.process_new_prospect(prospect)
            self.processed_today += 1
            
            print(f"✅ Processed: {prospect.get('organization_name')}")
            print(f"   Workflow ID: {result.get('workflow_id')}")
            print(f"   Total today: {self.processed_today}")
            
            # Could send notifications, update CRM, etc.
            
        except Exception as e:
            print(f"❌ Processing failed for {prospect.get('organization_name')}: {str(e)}")
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.running = False
        print("⏹️  Stopping GFMD real-time monitoring...")

# Usage:
# monitor = GFMDRealtimeMonitor("gen-lang-client-0673146524")
# await monitor.start_monitoring()
'''
    
    with open('gfmd_realtime_monitor.py', 'w') as f:
        f.write(monitor_code)
    
    print("✅ Created gfmd_realtime_monitor.py")

def create_chatbot_interface():
    """
    Example of conversational chatbot interface
    """
    chatbot_code = '''#!/usr/bin/env python3
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
'''
    
    with open('gfmd_sales_assistant.py', 'w') as f:
        f.write(chatbot_code)
    
    print("✅ Created gfmd_sales_assistant.py")

async def main():
    """
    Main demonstration of operation modes
    """
    demonstrate_operation_modes()
    
    # Show current manual mode
    await manual_processing_example()
    
    # Create example files for other modes
    print("\n🔧 Creating example implementations...")
    create_batch_processor()
    create_realtime_monitor()
    create_chatbot_interface()
    
    print("\n🎯 Summary:")
    print("• Current: Manual/API mode (perfect for CRM integration)")
    print("• Available: Batch, real-time, and chatbot modes")
    print("• All modes use the same core Swarm Agent system")
    print("• Choose based on your business needs")
    
    print("\n💡 Recommended Next Steps:")
    print("1. Integrate with your CRM (Salesforce, HubSpot)")
    print("2. Set up webhook endpoints for real-time processing")
    print("3. Create a sales dashboard to monitor results")

if __name__ == "__main__":
    asyncio.run(main())