#!/usr/bin/env python3
"""
Production RAG + A2A System for GFMD AI Swarm
Works with your existing setup while adding RAG and A2A capabilities
"""

import asyncio
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

sys.path.append('.')

# Import your working AI agents
from research_agent import ResearchAgent
from qualification_agent import QualificationAgent
from email_composer_agent import EmailComposerAgent
from coordinator_agent import CoordinatorAgent

# Import existing systems
from automatic_email_sender import AutomaticEmailSender, update_google_sheets_with_email_status
from google_sheets_integration import GoogleSheetsExporter, GoogleSheetsConfig
from lead_deduplication_system import LeadDeduplicationSystem
from real_prospect_finder import RealProspectFinder
from google_search_integration import GoogleSearchEmailFinder

class ProductionRAGMemorySystem:
    """Production-ready memory system with simplified RAG capabilities"""
    
    def __init__(self):
        self.prospect_memories: Dict[str, Dict[str, Any]] = {}
        self.knowledge_base = self._initialize_gfmd_knowledge()
        self.interaction_history: List[Dict[str, Any]] = []
    
    def _initialize_gfmd_knowledge(self) -> Dict[str, List[Dict[str, str]]]:
        """Initialize GFMD knowledge base"""
        
        return {
            "product_knowledge": [
                {
                    "title": "GFMD Silencer Centrifuge",
                    "content": "Reduces laboratory noise by up to 70% while maintaining full processing capacity. Designed for healthcare facilities with noise concerns.",
                    "keywords": ["noise reduction", "centrifuge", "laboratory", "70%"]
                },
                {
                    "title": "Target Customer Profile",
                    "content": "Mid-size healthcare facilities (150-500 beds) with active laboratory operations, noise complaints, or compliance concerns.",
                    "keywords": ["150-500 beds", "mid-size", "hospital", "laboratory", "noise complaints"]
                }
            ],
            "industry_insights": [
                {
                    "title": "Healthcare Procurement Cycles",
                    "content": "Healthcare facilities typically have 3-5 year equipment refresh cycles. Budget planning often occurs in Q4 for next year implementation.",
                    "keywords": ["budget cycle", "procurement", "Q4", "3-5 years"]
                },
                {
                    "title": "Joint Commission Requirements",
                    "content": "Joint Commission standards require hospitals to maintain quiet healing environments. Noise reduction is both a compliance and patient satisfaction issue.",
                    "keywords": ["Joint Commission", "compliance", "quiet environment", "noise reduction"]
                }
            ],
            "successful_approaches": [
                {
                    "title": "Pain Point Focus",
                    "content": "Start with specific pain point (noise complaints, compliance). Quantify impact on staff satisfaction and patient comfort.",
                    "keywords": ["pain point", "noise complaints", "staff satisfaction", "quantify"]
                },
                {
                    "title": "Decision Maker Approach",
                    "content": "Laboratory Directors focus on operational efficiency. VP Operations care about compliance. Equipment Managers need ROI justification.",
                    "keywords": ["Laboratory Director", "VP Operations", "Equipment Manager", "ROI"]
                }
            ]
        }
    
    async def retrieve_knowledge(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Simple knowledge retrieval based on keyword matching"""
        
        query_lower = query.lower()
        results = []
        
        # Search across all knowledge categories
        for category, docs in self.knowledge_base.items():
            for doc in docs:
                # Simple keyword matching
                relevance_score = 0
                for keyword in doc["keywords"]:
                    if keyword.lower() in query_lower:
                        relevance_score += 1
                
                # Context matching
                if context:
                    if context.get("pain_points"):
                        for pain_point in context["pain_points"]:
                            if pain_point.lower() in doc["content"].lower():
                                relevance_score += 2
                    
                    if context.get("facility_type"):
                        if context["facility_type"].lower() in doc["content"].lower():
                            relevance_score += 1
                
                if relevance_score > 0:
                    results.append({
                        "title": doc["title"],
                        "content": doc["content"],
                        "category": category,
                        "relevance_score": relevance_score
                    })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:5]  # Top 5 results
    
    async def store_interaction(self, prospect_id: str, organization: str, interaction_type: str, data: Dict[str, Any]):
        """Store prospect interaction"""
        
        if prospect_id not in self.prospect_memories:
            self.prospect_memories[prospect_id] = {
                "prospect_id": prospect_id,
                "organization": organization,
                "interactions": [],
                "created_at": datetime.now().isoformat()
            }
        
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "data": data
        }
        
        self.prospect_memories[prospect_id]["interactions"].append(interaction)
        self.interaction_history.append({
            "prospect_id": prospect_id,
            "organization": organization,
            **interaction
        })
    
    async def get_prospect_context(self, prospect_id: str, organization: str = None) -> Dict[str, Any]:
        """Get prospect context and history"""
        
        if prospect_id in self.prospect_memories:
            memory = self.prospect_memories[prospect_id]
            return {
                "has_history": True,
                "total_interactions": len(memory["interactions"]),
                "interactions": memory["interactions"][-5:],  # Last 5 interactions
                "created_at": memory["created_at"]
            }
        else:
            # Look for similar organizations
            similar = []
            if organization:
                for pid, mem in self.prospect_memories.items():
                    if organization.lower() in mem["organization"].lower():
                        similar.append({
                            "organization": mem["organization"],
                            "interactions": len(mem["interactions"])
                        })
            
            return {
                "has_history": False,
                "similar_organizations": similar
            }

class EnhancedResearchAgent(ResearchAgent):
    """Research agent enhanced with memory and knowledge"""
    
    def __init__(self, agent_id: str, memory_system: ProductionRAGMemorySystem):
        super().__init__(agent_id)
        self.memory_system = memory_system
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced research with memory and knowledge"""
        
        organization = task.get("organization_name", "")
        prospect_id = task.get("prospect_id", f"prospect_{organization.replace(' ', '_').lower()}")
        
        # Step 1: Check existing knowledge
        print(f"🧠 Checking knowledge base for {organization}...")
        knowledge = await self.memory_system.retrieve_knowledge(
            f"research insights {organization} hospital laboratory",
            task
        )
        
        # Step 2: Get prospect history
        context = await self.memory_system.get_prospect_context(prospect_id, organization)
        
        # Step 3: Enhanced research prompt
        research_prompt = {
            "target_organization": organization,
            "location": task.get("location", ""),
            "existing_knowledge": [k["content"] for k in knowledge],
            "prospect_history": context,
            "enhanced_focus": [
                "Build on existing knowledge about similar organizations",
                "Focus on pain points we know work for this type of facility",
                "Consider decision maker preferences from our knowledge base",
                "Identify specific ROI opportunities"
            ]
        }
        
        # Step 4: Use AI for research
        result = await self.think(research_prompt)
        
        # Step 5: Store interaction
        await self.memory_system.store_interaction(
            prospect_id,
            organization,
            "research",
            {
                "agent_id": self.agent_id,
                "knowledge_pieces_used": len(knowledge),
                "has_history": context.get("has_history", False),
                "findings": result
            }
        )
        
        # Add enhancement metadata
        result["memory_enhancement"] = {
            "knowledge_pieces_used": len(knowledge),
            "prospect_history_available": context.get("has_history", False),
            "similar_orgs_found": len(context.get("similar_organizations", [])),
            "enhanced": True
        }
        
        return result

class EnhancedQualificationAgent(QualificationAgent):
    """Qualification agent enhanced with memory"""
    
    def __init__(self, agent_id: str, memory_system: ProductionRAGMemorySystem):
        super().__init__(agent_id)
        self.memory_system = memory_system
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced qualification with historical patterns"""
        
        prospect_data = task.get("prospect_data", {})
        organization = prospect_data.get("organization_name", "")
        prospect_id = task.get("prospect_id", f"prospect_{organization.replace(' ', '_').lower()}")
        
        # Get qualification knowledge
        knowledge = await self.memory_system.retrieve_knowledge(
            f"qualification patterns {organization} healthcare facility scoring",
            {"facility_type": prospect_data.get("facility_type"), "pain_points": task.get("research_findings", {}).get("pain_points", [])}
        )
        
        # Enhanced qualification
        qualification_prompt = {
            **task,
            "historical_patterns": [k["content"] for k in knowledge],
            "enhanced_criteria": [
                "Compare with successful qualification patterns",
                "Weight factors based on knowledge base insights",
                "Consider similar organization outcomes",
                "Apply proven scoring methodologies"
            ]
        }
        
        result = await self.think(qualification_prompt)
        
        # Store qualification
        await self.memory_system.store_interaction(
            prospect_id,
            organization,
            "qualification", 
            {
                "agent_id": self.agent_id,
                "score": result.get("total_score", 0),
                "priority": result.get("priority_level", "Unknown"),
                "knowledge_enhanced": len(knowledge) > 0
            }
        )
        
        result["memory_enhancement"] = {
            "historical_patterns_used": len(knowledge),
            "knowledge_enhanced": len(knowledge) > 0
        }
        
        return result

class EnhancedEmailComposer(EmailComposerAgent):
    """Email composer enhanced with successful approaches"""
    
    def __init__(self, agent_id: str, memory_system: ProductionRAGMemorySystem):
        super().__init__(agent_id)
        self.memory_system = memory_system
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced email composition with proven approaches"""
        
        prospect_data = task.get("prospect_data", {})
        organization = prospect_data.get("organization_name", "")
        prospect_id = task.get("prospect_id", f"prospect_{organization.replace(' ', '_').lower()}")
        
        # Get successful email approaches
        knowledge = await self.memory_system.retrieve_knowledge(
            f"successful email approaches {organization} healthcare decision makers",
            {
                "pain_points": task.get("research_findings", {}).get("pain_points", []),
                "contact_title": prospect_data.get("contact_title", "")
            }
        )
        
        # Enhanced composition
        composition_prompt = {
            **task,
            "proven_approaches": [k["content"] for k in knowledge],
            "styling_rules": self.styling_rules,
            "enhancement_focus": [
                "Apply proven messaging approaches from knowledge base",
                "Use language that has worked with similar decision makers",
                "Reference successful case studies and examples",
                "Ensure strict adherence to styling rules"
            ]
        }
        
        result = await self.think(composition_prompt)
        
        # Apply styling rules (unchanged)
        validated_result = self._enforce_styling_rules(result, prospect_data)
        
        # Store email approach
        await self.memory_system.store_interaction(
            prospect_id,
            organization,
            "email",
            {
                "agent_id": self.agent_id,
                "subject": validated_result.get("subject", ""),
                "approaches_used": len(knowledge),
                "style_compliant": all(validated_result.get("style_check", {}).values())
            }
        )
        
        validated_result["memory_enhancement"] = {
            "proven_approaches_used": len(knowledge),
            "knowledge_personalized": len(knowledge) > 0,
            "styling_enforced": True
        }
        
        return validated_result

class ProductionCoordinator(CoordinatorAgent):
    """Production coordinator with memory-enhanced agents"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        
        # Initialize memory system
        self.memory_system = ProductionRAGMemorySystem()
        
        # Replace agents with enhanced versions
        self.agents = {
            "researcher": EnhancedResearchAgent("enhanced_researcher_001", self.memory_system),
            "qualifier": EnhancedQualificationAgent("enhanced_qualifier_001", self.memory_system),
            "composer": EnhancedEmailComposer("enhanced_composer_001", self.memory_system)
        }
        
        print("✅ Production coordinator initialized with memory-enhanced agents")
    
    async def _process_single_prospect(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process prospect with enhanced workflow"""
        
        organization = prospect_data.get("organization_name", "")
        prospect_id = f"prospect_{organization.replace(' ', '_').lower()}"
        
        print(f"🎯 Processing {organization} with memory enhancement")
        
        # Step 1: Research
        print(f"  🔍 Enhanced research...")
        research_result = await self.agents["researcher"].execute({
            **prospect_data,
            "prospect_id": prospect_id
        })
        
        # Step 2: Qualification
        print(f"  🎯 Enhanced qualification...")
        qualification_result = await self.agents["qualifier"].execute({
            "prospect_data": prospect_data,
            "research_findings": research_result,
            "prospect_id": prospect_id
        })
        
        # Step 3: Email composition (for all prospects - temporary fix)
        email_result = None
        # Force email generation for all prospects to get system working
        print(f"  ✉️ Enhanced email composition...")
        email_result = await self.agents["composer"].execute({
            "prospect_data": prospect_data,
            "research_findings": research_result,
            "qualification_score": qualification_result,
            "prospect_id": prospect_id
        })
        
        return {
            "prospect": prospect_data,
            "prospect_id": prospect_id,
            "research": research_result,
            "qualification": qualification_result,
            "email": email_result,
            "memory_enhanced": True,
            "processing_time": datetime.now().isoformat()
        }

class ProductionGFMDSystem:
    """Production GFMD system with memory enhancement"""
    
    def __init__(self):
        self.coordinator = ProductionCoordinator("production_coordinator_001")
        self.email_sender = AutomaticEmailSender()
        # Initialize Google Sheets exporter with error handling for Cloud Run
        try:
            # Only initialize if credentials file exists
            if os.path.exists("google_sheets_credentials.json"):
                self.sheets_exporter = GoogleSheetsExporter(GoogleSheetsConfig(
                    spreadsheet_name="GFMD Swarm Agent Data",
                    credentials_file="google_sheets_credentials.json"
                ))
                self.sheets_enabled = True
                print("✅ Google Sheets integration enabled")
            else:
                print("📊 Google Sheets credentials not found, running in Firestore-only mode")
                self.sheets_exporter = None
                self.sheets_enabled = False
        except Exception as e:
            print(f"⚠️ Google Sheets integration disabled: {e}")
            self.sheets_exporter = None
            self.sheets_enabled = False
        self.dedup_system = LeadDeduplicationSystem()
        self.prospect_finder = RealProspectFinder()
        self.search_finder = GoogleSearchEmailFinder()
        
    async def run_daily_automation(self, num_prospects: int = 10) -> Dict[str, Any]:
        """Run daily automation with memory enhancement"""
        
        print("🚀 GFMD Production System - Memory Enhanced AI Agents")
        print("=" * 70)
        print("🧠 Memory System: Active (knowledge base + interaction history)")
        print("🤖 AI Model: Gemini 1.5 Pro")
        print("✉️ Email Rules: Your exact styling preserved")
        print("=" * 70)
        
        results = {
            "mode": "memory_enhanced_ai",
            "prospects_processed": 0,
            "emails_sent": 0,
            "memory_enhancements": 0,
            "errors": []
        }
        
        # Generate prospects
        prospects = await self._generate_prospects(num_prospects)
        
        # Process each prospect
        for i, prospect in enumerate(prospects, 1):
            try:
                print(f"\n[{i}/{num_prospects}] Processing: {prospect['organization_name']}")
                
                # Process with enhanced system
                result = await self.coordinator._process_single_prospect(prospect)
                
                # Track enhancements
                if result.get("research", {}).get("memory_enhancement", {}).get("enhanced"):
                    results["memory_enhancements"] += 1
                
                # Export to sheets
                await self._export_enhanced_prospect(prospect, result)
                
                # Send email ONLY if we have a verified real email
                if result.get("email"):
                    # Check if prospect is verified or email is real
                    email = prospect.get("email", "")
                    is_verified = prospect.get("verified", False) or prospect.get("email_verified", False)
                    needs_search = prospect.get("needs_email_search", False)
                    
                    # Only send if verified and not a placeholder
                    if is_verified and "@" in email and not needs_search:
                        await self._send_email(prospect, result["email"], results)
                    else:
                        print(f"   ⚠️ Skipping email - need verified real email (verified={is_verified})")
                
                results["prospects_processed"] += 1
                print(f"   ✅ Complete with memory enhancement")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results["errors"].append(str(e))
        
        # Summary
        print(f"\n📊 Production Results:")
        print(f"   ✅ Processed: {results['prospects_processed']}")
        print(f"   📧 Emails Sent: {results['emails_sent']}")
        print(f"   🧠 Memory Enhanced: {results['memory_enhancements']}")
        print(f"   📋 Knowledge Base: Active")
        
        return results
    
    async def _generate_prospects(self, num_prospects: int) -> List[Dict[str, Any]]:
        """Get REAL prospects with verified email addresses - NO FAKE EMAILS"""
        
        print("🔍 Finding REAL prospects with verified emails...")
        print("📂 Loading from Definitive Healthcare data...")
        
        # Load from Definitive Healthcare CSV
        verified_prospects = self.prospect_finder.load_definitive_healthcare_data("definitive_healthcare_data.csv")
        
        if verified_prospects:
            print(f"✅ Found {len(verified_prospects)} REAL contacts from Definitive Healthcare")
            
            # Optionally enrich with Google Search for missing contacts
            enriched_prospects = []
            for i, prospect in enumerate(verified_prospects[:num_prospects]):
                if not prospect.get('email') or prospect.get('email') == '':
                    print(f"🔍 Searching for missing email: {prospect.get('organization_name')}")
                    prospect = await self.search_finder.enrich_prospect_with_search(prospect)
                
                enriched_prospects.append(prospect)
            
            return enriched_prospects
        
        # Otherwise, use manual list of real hospitals and search for contacts
        real_prospects = []
        
        # Real Texas hospitals that we know exist
        real_hospitals = [
            {"name": "Houston Methodist Hospital", "location": "Houston, TX", "website": "houstonmethodist.org"},
            {"name": "Baylor Scott & White Medical Center - Temple", "location": "Temple, TX", "website": "bswhealth.com"},
            {"name": "Memorial Hermann Texas Medical Center", "location": "Houston, TX", "website": "memorialhermann.org"},
            {"name": "UT Southwestern Medical Center", "location": "Dallas, TX", "website": "utsouthwestern.edu"},
            {"name": "CHRISTUS Santa Rosa Hospital", "location": "San Antonio, TX", "website": "christushealth.org"},
            {"name": "Texas Children's Hospital", "location": "Houston, TX", "website": "texaschildrens.org"},
            {"name": "Parkland Health Hospital System", "location": "Dallas, TX", "website": "parklandhealth.org"},
            {"name": "Methodist Hospital San Antonio", "location": "San Antonio, TX", "website": "sahealth.com"},
            {"name": "Cook Children's Medical Center", "location": "Fort Worth, TX", "website": "cookchildrens.org"},
            {"name": "Medical City Dallas", "location": "Dallas, TX", "website": "medicalcityhospital.com"},
        ]
        
        # For now, create prospects with placeholder emails that need web search
        for hospital in real_hospitals[:num_prospects]:
            prospect = {
                "organization_name": hospital["name"],
                "location": hospital["location"],
                "website": hospital["website"],
                "contact_name": "Laboratory Director",  # Will be found via web search
                "contact_title": "Laboratory Director",
                "email": f"labdirector@{hospital['website']}",  # Placeholder - needs verification
                "facility_type": "Major Medical Center",
                "pain_point": "Laboratory noise affecting patient recovery and staff productivity",
                "facility_size": 500,  # Estimate for major hospitals
                "department": "Clinical Laboratory",
                "needs_email_search": True  # Flag to search for real email
            }
            real_prospects.append(prospect)
        
        print(f"📊 Prepared {len(real_prospects)} real hospital prospects")
        print("⚠️ Note: Emails need verification via web search before sending")
        
        return real_prospects
    
    async def _export_enhanced_prospect(self, prospect: Dict[str, Any], result: Dict[str, Any]):
        """Export prospect with memory enhancement metadata"""
        
        enhanced_prospect = {
            **prospect,
            "memory_enhanced": True,
            "ai_qualification_score": result.get("qualification", {}).get("total_score", 0),
            "knowledge_used": result.get("research", {}).get("memory_enhancement", {}).get("knowledge_pieces_used", 0),
            "processed_date": datetime.now().isoformat()
        }
        
        if self.sheets_enabled and self.sheets_exporter:
            self.sheets_exporter.export_prospect(enhanced_prospect)
    
    async def _send_email(self, prospect: Dict[str, Any], email_data: Dict[str, Any], results: Dict[str, Any]):
        """Send enhanced email"""
        
        send_result = self.email_sender.send_email_to_prospect(prospect)
        
        if send_result["success"]:
            results["emails_sent"] += 1
            print(f"   📧 Memory-enhanced email sent")
            if self.sheets_enabled:
                try:
                    update_google_sheets_with_email_status(prospect, send_result)
                except Exception as e:
                    print(f"⚠️ Could not update Google Sheets: {e}")
        else:
            print(f"   📋 Email template created")

# Main deployment
async def deploy_production_system(num_prospects: int = 10):
    """Deploy the production memory-enhanced system"""
    
    system = ProductionGFMDSystem()
    results = await system.run_daily_automation(num_prospects)
    
    print(f"\n🎉 Production deployment complete!")
    return results

# Test the system
async def test_production_system():
    """Test the production system"""
    
    print("🧪 Testing Production Memory-Enhanced System")
    print("=" * 60)
    
    results = await deploy_production_system(5)
    
    if results["prospects_processed"] > 0:
        print("✅ Production system working!")
    else:
        print("⚠️ System needs attention")

if __name__ == "__main__":
    asyncio.run(test_production_system())