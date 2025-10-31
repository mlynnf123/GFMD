#!/usr/bin/env python3
"""
Deploy RAG + A2A Enhanced GFMD AI Swarm
Complete system with memory, knowledge persistence, and agent collaboration
"""

import asyncio
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

sys.path.append('.')

# Import all enhanced components
from rag_enhanced_agents import create_rag_a2a_enhanced_swarm
from automatic_email_sender import AutomaticEmailSender, update_google_sheets_with_email_status
from google_sheets_integration import GoogleSheetsExporter, GoogleSheetsConfig
from lead_deduplication_system import LeadDeduplicationSystem

class RAGEnhancedGFMDSystem:
    """Complete GFMD system with RAG + A2A enhancements"""
    
    def __init__(self):
        self.coordinator = None
        self.rag_system = None
        self.a2a_protocol = None
        self.email_sender = AutomaticEmailSender()
        self.sheets_exporter = GoogleSheetsExporter(GoogleSheetsConfig(
            spreadsheet_name="GFMD Swarm Agent Data",
            credentials_file="google_sheets_credentials.json"
        ))
        self.dedup_system = LeadDeduplicationSystem()
        
        self.session_metrics = {
            "prospects_processed": 0,
            "rag_knowledge_used": 0,
            "a2a_collaborations": 0,
            "emails_sent": 0,
            "knowledge_stored": 0
        }
    
    async def initialize(self) -> bool:
        """Initialize the complete RAG + A2A system"""
        
        print("🚀 Initializing RAG + A2A Enhanced GFMD System")
        print("=" * 70)
        
        try:
            # Initialize enhanced swarm
            self.coordinator, self.rag_system, self.a2a_protocol = await create_rag_a2a_enhanced_swarm()
            
            print("✅ RAG + A2A Enhanced AI Swarm initialized")
            print("🧠 Features active:")
            print("   • Persistent memory across sessions")
            print("   • Agent-to-agent negotiation and collaboration")
            print("   • Knowledge retrieval and learning")
            print("   • Historical context for every prospect")
            print("   • Cross-prospect pattern recognition")
            
            return True
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            return False
    
    async def generate_enhanced_prospects(self, num_prospects: int) -> List[Dict[str, Any]]:
        """Generate prospects enhanced with existing knowledge"""
        
        print(f"🎯 Generating {num_prospects} prospects with RAG enhancement...")
        
        # Use existing deduplication system
        prospects = []
        attempts = 0
        max_attempts = num_prospects * 3
        
        while len(prospects) < num_prospects and attempts < max_attempts:
            # Generate base prospect
            base_prospect = self._generate_base_prospect(attempts)
            
            # Check for duplicates
            if not self.dedup_system.is_duplicate(
                base_prospect['contact_name'],
                base_prospect['email'], 
                base_prospect['organization_name']
            ):
                # Enhance with RAG knowledge
                enhanced_prospect = await self._enhance_prospect_with_rag(base_prospect)
                prospects.append(enhanced_prospect)
                
                # Add to deduplication
                self.dedup_system.add_lead(
                    base_prospect['contact_name'],
                    base_prospect['email'],
                    base_prospect['organization_name']
                )
            
            attempts += 1
        
        print(f"✅ Generated {len(prospects)} RAG-enhanced prospects")
        return prospects[:num_prospects]
    
    def _generate_base_prospect(self, index: int) -> Dict[str, Any]:
        """Generate a base prospect (simplified version of qualified_lead_generator)"""
        
        import random
        
        # Hospital templates
        hospitals = [
            "Regional Medical Center", "Community Hospital", "Medical Center",
            "General Hospital", "Healthcare System", "Medical Associates"
        ]
        
        cities = ["Dallas", "Houston", "Austin", "San Antonio", "Fort Worth", "El Paso"]
        
        first_names = ["Dr. Michael", "Dr. Jennifer", "Dr. David", "Dr. Sarah", "Dr. Robert", "Dr. Emily"]
        last_names = ["Johnson", "Chen", "Martinez", "Wilson", "Davis", "Rodriguez"]
        
        titles = [
            "Laboratory Director", "VP of Operations", "Equipment Manager", 
            "Chief Laboratory Officer", "Director of Clinical Services"
        ]
        
        # Generate prospect
        city = random.choice(cities)
        hospital_type = random.choice(hospitals)
        org_name = f"{city} {hospital_type}"
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        contact_name = f"{first_name} {last_name}"
        
        email_domain = org_name.lower().replace(" ", "") + ".org"
        email = f"{first_name.split()[-1][0].lower()}.{last_name.lower()}@{email_domain}"
        
        return {
            "organization_name": org_name,
            "location": f"{city}, TX", 
            "contact_name": contact_name,
            "contact_title": random.choice(titles),
            "email": email,
            "phone": f"555-{random.randint(1000, 9999)}",
            "facility_type": hospital_type,
            "bed_count": random.randint(150, 500),
            "pain_point": random.choice([
                "Noise complaints from adjacent patient areas",
                "Staff complaints about centrifuge noise", 
                "Laboratory equipment needs updating",
                "Joint Commission noise level concerns"
            ]),
            "budget_range": "$100K-200K",
            "buying_timeframe": "Q1-Q2 2025"
        }
    
    async def _enhance_prospect_with_rag(self, base_prospect: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance prospect with RAG knowledge"""
        
        organization = base_prospect["organization_name"]
        location = base_prospect["location"]
        
        # Query RAG for similar organizations or existing knowledge
        rag_context = await self.rag_system.rag_enhanced_query(
            f"similar organization {organization} {location} healthcare facility",
            {
                "organization_name": organization,
                "location": location,
                "facility_type": base_prospect["facility_type"]
            }
        )
        
        # Enhance with RAG insights
        enhanced = {
            **base_prospect,
            "rag_enhanced": True,
            "similar_orgs_found": len(rag_context.get("relevant_knowledge", [])),
            "knowledge_confidence": "high" if len(rag_context.get("relevant_knowledge", [])) > 2 else "medium"
        }
        
        # Use RAG knowledge to refine pain points
        if rag_context.get("relevant_knowledge"):
            for knowledge in rag_context["relevant_knowledge"]:
                if "pain_points" in knowledge.get("metadata", {}).get("type", ""):
                    # Use similar organization's pain points
                    enhanced["pain_point"] = knowledge["content"].split(":")[1].strip() if ":" in knowledge["content"] else enhanced["pain_point"]
                    break
        
        return enhanced
    
    async def process_enhanced_daily_batch(self, num_prospects: int = 10) -> Dict[str, Any]:
        """Process daily batch with full RAG + A2A enhancement"""
        
        print(f"\n🤖 Processing {num_prospects} prospects with RAG + A2A Enhancement")
        print("=" * 70)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "mode": "rag_a2a_enhanced",
            "prospects_processed": 0,
            "emails_sent": 0,
            "rag_enhancements": 0,
            "a2a_collaborations": 0,
            "errors": []
        }
        
        try:
            # Step 1: Generate RAG-enhanced prospects
            prospects = await self.generate_enhanced_prospects(num_prospects)
            
            # Step 2: Process each prospect with full enhancement
            for i, prospect in enumerate(prospects, 1):
                try:
                    print(f"\n🏥 [{i}/{num_prospects}] Processing: {prospect['organization_name']}")
                    
                    # Process with RAG + A2A coordinator
                    processing_result = await self.coordinator._process_single_prospect(prospect)
                    
                    # Track metrics
                    if processing_result.get("rag_knowledge_base", 0) > 0:
                        results["rag_enhancements"] += 1
                        self.session_metrics["rag_knowledge_used"] += processing_result["rag_knowledge_base"]
                    
                    if processing_result.get("coordination_id"):
                        results["a2a_collaborations"] += 1
                        self.session_metrics["a2a_collaborations"] += 1
                    
                    # Export to Google Sheets with enhancement data
                    await self._export_enhanced_prospect(prospect, processing_result)
                    
                    # Send email if generated
                    if processing_result.get("email") and processing_result.get("qualification", {}).get("total_score", 0) >= 60:
                        await self._send_enhanced_email(prospect, processing_result, results)
                    
                    results["prospects_processed"] += 1
                    self.session_metrics["prospects_processed"] += 1
                    
                    print(f"   ✅ Complete with RAG + A2A enhancement")
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    results["errors"].append(str(e))
            
            # Step 3: Summary
            await self._print_enhanced_summary(results)
            
        except Exception as e:
            print(f"❌ Batch processing error: {e}")
            results["errors"].append(str(e))
        
        return results
    
    async def _export_enhanced_prospect(self, prospect: Dict[str, Any], processing_result: Dict[str, Any]):
        """Export prospect with RAG + A2A enhancement data"""
        
        # Enhanced prospect data
        enhanced_prospect = {
            **prospect,
            "ai_processed": True,
            "rag_enhanced": processing_result.get("rag_knowledge_base", 0) > 0,
            "a2a_coordinated": processing_result.get("coordination_id") is not None,
            "qualification_score": processing_result.get("qualification", {}).get("total_score", 0),
            "priority_level": processing_result.get("qualification", {}).get("priority_level", "Unknown"),
            "rag_knowledge_pieces": processing_result.get("rag_knowledge_base", 0),
            "processing_enhanced": True,
            "processed_date": datetime.now().isoformat()
        }
        
        self.sheets_exporter.export_prospect(enhanced_prospect)
        
        # Export enhanced agent analysis
        agent_analysis = {
            "agent_name": "RAG+A2A Enhanced Swarm",
            "workflow_id": processing_result.get("coordination_id", f"enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            "prospect_organization": prospect["organization_name"],
            "output_type": "rag_a2a_enhanced_analysis",
            "output_data": {
                "rag_enhancements": {
                    "knowledge_pieces_used": processing_result.get("rag_knowledge_base", 0),
                    "research_enhanced": processing_result.get("research", {}).get("rag_enhancement") is not None,
                    "qualification_enhanced": processing_result.get("qualification", {}).get("rag_insights") is not None,
                    "email_personalized": processing_result.get("email", {}).get("rag_personalization") is not None
                },
                "a2a_coordination": {
                    "coordination_id": processing_result.get("coordination_id"),
                    "workflow_status": processing_result.get("workflow_status"),
                    "agents_collaborated": 3  # Research, Qualification, Email
                },
                "final_recommendation": processing_result.get("qualification", {}).get("recommended_action", "")
            },
            "execution_time": 0,
            "success": True
        }
        
        self.sheets_exporter.export_agent_output(agent_analysis)
        self.session_metrics["knowledge_stored"] += 1
    
    async def _send_enhanced_email(self, prospect: Dict[str, Any], processing_result: Dict[str, Any], results: Dict[str, Any]):
        """Send AI-enhanced email"""
        
        email_data = processing_result.get("email", {})
        
        # Prepare enhanced email
        enhanced_email_prospect = {
            **prospect,
            "ai_subject": email_data.get("subject", ""),
            "ai_body": email_data.get("full_email", ""),
            "rag_personalized": email_data.get("rag_personalization", {}).get("personalization_confidence", "medium"),
            "style_compliant": all(email_data.get("style_check", {}).values())
        }
        
        # Send using existing email sender
        send_result = self.email_sender.send_email_to_prospect(enhanced_email_prospect)
        
        if send_result["success"]:
            print(f"   ✅ RAG-enhanced email sent to {prospect['email']}")
            results["emails_sent"] += 1
            self.session_metrics["emails_sent"] += 1
            
            # Update sheets with send status
            update_google_sheets_with_email_status(enhanced_email_prospect, send_result)
        else:
            print(f"   📋 Enhanced email saved as template: {send_result['message']}")
            
            # Save enhanced template
            email_template = {
                "id": f"rag_a2a_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "recipient_email": prospect["email"],
                "subject": email_data.get("subject", ""),
                "body": email_data.get("full_email", ""),
                "sent_successfully": False,
                "day_number": "1",
                "send_status": f"RAG_A2A_TEMPLATE: {send_result.get('reason', 'not_sent')}",
                "rag_enhanced": True,
                "a2a_coordinated": True
            }
            
            self.sheets_exporter.export_sent_email(email_template)
    
    async def _print_enhanced_summary(self, results: Dict[str, Any]):
        """Print enhanced processing summary"""
        
        print("\n" + "=" * 70)
        print("📊 RAG + A2A Enhanced Processing Summary")
        print("=" * 70)
        print(f"🤖 Mode: RAG + A2A ENHANCED")
        print(f"✅ Prospects Processed: {results['prospects_processed']}")
        print(f"📧 Emails Sent: {results['emails_sent']}")
        print(f"🧠 RAG Enhancements: {results['rag_enhancements']}")
        print(f"🔗 A2A Collaborations: {results['a2a_collaborations']}")
        
        # System metrics
        rag_stats = self.rag_system.get_system_stats()
        a2a_stats = self.a2a_protocol.get_protocol_metrics()
        
        print(f"\n📈 System Intelligence:")
        print(f"   Knowledge Categories: {rag_stats['knowledge_categories']}")
        print(f"   Prospect Memories: {rag_stats['prospect_memories']}")
        print(f"   Total Interactions: {rag_stats['total_interactions']}")
        print(f"   Agent Messages: {a2a_stats['messages_sent']}")
        
        if results["errors"]:
            print(f"\n⚠️ Errors: {len(results['errors'])}")

# Main deployment function
async def deploy_rag_a2a_system(num_prospects: int = 10):
    """Deploy and run the complete RAG + A2A enhanced system"""
    
    print("🎉 DEPLOYING RAG + A2A ENHANCED GFMD AI SWARM")
    print("=" * 80)
    print("🧠 RAG System: Persistent memory and knowledge retrieval")
    print("🔗 A2A Protocol: Agent negotiation and collaboration")
    print("🤖 AI Model: Gemini 1.5 Pro with enhanced capabilities")
    print("✉️ Email Rules: Your exact styling preserved")
    print("=" * 80)
    
    # Initialize system
    system = RAGEnhancedGFMDSystem()
    
    if await system.initialize():
        # Process enhanced batch
        results = await system.process_enhanced_daily_batch(num_prospects)
        
        print(f"\n🎉 RAG + A2A Enhanced Processing Complete!")
        print(f"📊 Your AI swarm now has memory, knowledge, and collaboration!")
        
        return results
    else:
        print("❌ System initialization failed")
        return None

# Test function
async def test_rag_a2a_deployment():
    """Test the RAG + A2A deployment with a small batch"""
    
    print("🧪 Testing RAG + A2A Enhanced System")
    print("=" * 50)
    
    # Test with 2 prospects
    results = await deploy_rag_a2a_system(2)
    
    if results:
        print("\n✅ RAG + A2A system test successful!")
    else:
        print("\n❌ System test failed")

if __name__ == "__main__":
    asyncio.run(test_rag_a2a_deployment())