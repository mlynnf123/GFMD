#!/usr/bin/env python3
"""
RAG-Enhanced Personalization Agent for GFMD Narc Gone
Uses MongoDB Vector Search to retrieve relevant knowledge for dynamic personalization
"""

from typing import Dict, Any, List
from groq_base_agent import GroqBaseAgent, AgentRole
from narcon_knowledge_base import Narc GoneKnowledgeBase
import json
import logging

logger = logging.getLogger(__name__)

class RAGEnhancedPersonalizationAgent(GroqBaseAgent):
    """Personalization agent enhanced with RAG knowledge retrieval"""

    def __init__(self, agent_id: str = "rag_personalizer_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.EMAIL_COMPOSER,
            temperature=0.7  # Moderate temperature for natural writing
        )
        
        # Initialize knowledge base
        try:
            self.knowledge_base = Narc GoneKnowledgeBase()
            logger.info("✅ RAG knowledge base initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize knowledge base: {e}")
            self.knowledge_base = None

    def get_system_prompt(self) -> str:
        return """You are an expert B2G (Business-to-Government) copywriter specializing in writing cold outreach emails to law enforcement and government officials. Your tone is professional, direct, and respectful.

**Your Goal:** Personalize the provided email template using the relevant knowledge retrieved from the knowledge base.

**Key Principles:**
1. Use the retrieved knowledge to add specific, relevant details
2. Reference credible sources (DHS partnership, government testing, lab results)
3. Mention specific pain points and solutions relevant to the prospect's agency type
4. Keep the email concise and under 120 words
5. Do not change the core message of the template, only enhance it with personalization

**Retrieved Knowledge Context:**
Use the provided knowledge documents to enhance personalization with:
- Specific product benefits relevant to their agency type
- Credible third-party validation (DHS, lab results, government testing)
- Relevant case studies or examples
- Cost savings data specific to their situation
- Safety information relevant to their role

**Instructions:**
1. Read the email template and identify personalization opportunities
2. Use the retrieved knowledge to insert specific, relevant details
3. Reference the prospect's organization and title naturally
4. Highlight the most relevant value propositions based on their agency type and role
5. Return ONLY the final, personalized email body as a single block of text
6. Do not include subject line, greeting, or sign-off

**Output Format:**
A single block of text representing the final email body."""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute RAG-enhanced personalization"""
        try:
            # Extract data
            contact_data = task.get("contact_data", {})
            email_template = task.get("email_template", {})
            
            # Get relevant knowledge from RAG system
            relevant_knowledge = []
            if self.knowledge_base:
                try:
                    # Create search context from contact and template
                    search_context = self._build_search_context(contact_data, email_template)
                    
                    relevant_knowledge = self.knowledge_base.get_relevant_knowledge_for_prospect(
                        contact_data=contact_data,
                        query_context=search_context
                    )
                    
                    logger.info(f"📚 Retrieved {len(relevant_knowledge)} knowledge documents")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Knowledge retrieval failed: {e}")
            
            # Build enhanced prompt with retrieved knowledge
            full_prompt = self._build_enhanced_prompt(contact_data, email_template, relevant_knowledge)
            
            # Call Groq AI
            result = await self.think({"prompt": full_prompt})
            
            # Ensure we have a valid response
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"]
                }
            
            # Extract the personalized email body
            personalized_body = result.get("response", "")
            
            if personalized_body:
                return {
                    "success": True,
                    "personalized_body": personalized_body.strip(),
                    "knowledge_used": len(relevant_knowledge),
                    "knowledge_sources": [doc.get("title", "") for doc in relevant_knowledge],
                    "tokens_used": result.get("tokens_used", 0)
                }
            else:
                return {
                    "success": False,
                    "error": "No personalized content generated",
                    "raw_response": result
                }

        except Exception as e:
            logger.error(f"❌ RAG personalization failed: {e}")
            return {
                "success": False,
                "error": f"RAG personalization task failed: {str(e)}"
            }
    
    def _build_search_context(self, contact_data: Dict[str, Any], email_template: Dict[str, Any]) -> str:
        """Build search context for knowledge retrieval"""
        context_parts = []
        
        # Add role-specific context
        title = contact_data.get("title", "").lower()
        if "evidence" in title or "property" in title:
            context_parts.append("evidence disposal logistics storage")
        elif "procurement" in title or "purchasing" in title:
            context_parts.append("cost savings compliance procurement")
        elif "chief" in title or "sheriff" in title:
            context_parts.append("budget officer safety department leadership")
        elif "safety" in title:
            context_parts.append("officer safety fentanyl exposure")
        
        # Add organization-specific context
        org_name = contact_data.get("organization", "").lower()
        if "federal" in org_name or any(fed in org_name for fed in ["dhs", "cbp", "ice", "dea"]):
            context_parts.append("federal agency scale government")
        elif "sheriff" in org_name:
            context_parts.append("sheriff county rural")
        elif "state" in org_name:
            context_parts.append("state police highway patrol")
        else:
            context_parts.append("police department municipal")
        
        # Add template-specific context
        template_body = email_template.get("body", "").lower()
        if "cost" in template_body or "savings" in template_body:
            context_parts.append("cost analysis savings budget")
        if "safety" in template_body or "fentanyl" in template_body:
            context_parts.append("officer safety fentanyl exposure")
        if "dhs" in template_body or "government" in template_body:
            context_parts.append("dhs partnership government credibility")
        
        return " ".join(context_parts)
    
    def _build_enhanced_prompt(self, 
                              contact_data: Dict[str, Any], 
                              email_template: Dict[str, Any], 
                              knowledge_docs: List[Dict[str, Any]]) -> str:
        """Build the enhanced prompt with RAG knowledge"""
        
        # Format contact info
        contact_info = {
            "firstName": contact_data.get("firstName", contact_data.get("first_name", "")),
            "title": contact_data.get("title", ""),
            "organization": contact_data.get("organization", contact_data.get("company_name", "")),
            "location": {
                "city": contact_data.get("city", ""),
                "state": contact_data.get("state", "")
            }
        }
        
        # Format knowledge documents
        knowledge_context = ""
        if knowledge_docs:
            knowledge_context = "\n**Retrieved Knowledge for Personalization:**\n\n"
            for i, doc in enumerate(knowledge_docs, 1):
                knowledge_context += f"**Knowledge Document {i}: {doc.get('title', 'Unknown')}**\n"
                knowledge_context += f"Type: {doc.get('doc_type', 'unknown')}\n"
                knowledge_context += f"Content: {doc.get('content', '')[:500]}...\n"
                knowledge_context += f"Relevant for: {', '.join(doc.get('agency_types', []))}\n"
                knowledge_context += f"Addresses: {', '.join(doc.get('pain_points', []))}\n\n"
        
        # Build full prompt
        full_prompt = f"""**Contact to Email:**

```json
{json.dumps(contact_info, indent=2)}
```

**Email Template to Personalize:**

```
{email_template.get('body', '')}
```

{knowledge_context}

{self.get_system_prompt()}

**Personalization Instructions:**
Based on the retrieved knowledge documents above, enhance the email template with:
1. Specific facts and benefits relevant to {contact_info['organization']}
2. Credible references from the knowledge base (DHS partnership, lab results, etc.)
3. Pain point solutions specific to their {contact_info['title']} role
4. Relevant cost savings or safety data from the knowledge documents
5. Government credibility and testing results where appropriate

Return only the enhanced email body."""
        
        return full_prompt

# Wrapper class to maintain compatibility with existing orchestrator
class EnhancedPersonalizationAgent:
    """Wrapper to provide enhanced personalization with RAG fallback"""
    
    def __init__(self):
        """Initialize with both RAG and standard agents"""
        try:
            self.rag_agent = RAGEnhancedPersonalizationAgent()
            logger.info("✅ RAG-enhanced personalization agent ready")
        except Exception as e:
            logger.error(f"❌ RAG agent initialization failed: {e}")
            self.rag_agent = None
        
        # Fallback to standard agent if RAG fails
        try:
            from groq_personalization_agent import GroqPersonalizationAgent
            self.standard_agent = GroqPersonalizationAgent()
            logger.info("✅ Standard personalization agent ready as fallback")
        except Exception as e:
            logger.error(f"❌ Standard agent initialization failed: {e}")
            self.standard_agent = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute personalization with RAG enhancement and fallback"""
        # Try RAG-enhanced personalization first
        if self.rag_agent:
            try:
                result = await self.rag_agent.execute(task)
                if result.get("success"):
                    result["method"] = "rag_enhanced"
                    logger.info("✅ RAG-enhanced personalization successful")
                    return result
                else:
                    logger.warning("⚠️ RAG personalization failed, falling back to standard")
            except Exception as e:
                logger.warning(f"⚠️ RAG personalization error: {e}, falling back to standard")
        
        # Fallback to standard personalization
        if self.standard_agent:
            try:
                result = await self.standard_agent.execute(task)
                result["method"] = "standard_fallback"
                logger.info("✅ Standard personalization used as fallback")
                return result
            except Exception as e:
                logger.error(f"❌ Standard personalization also failed: {e}")
        
        return {
            "success": False,
            "error": "Both RAG and standard personalization failed",
            "method": "none"
        }

# Test function
if __name__ == "__main__":
    import asyncio
    
    async def test_rag_personalization():
        """Test the RAG-enhanced personalization"""
        agent = EnhancedPersonalizationAgent()
        
        # Test data
        test_task = {
            "contact_data": {
                "firstName": "Sarah",
                "title": "Property & Evidence Manager", 
                "organization": "Austin Police Department",
                "city": "Austin",
                "state": "TX"
            },
            "email_template": {
                "body": "I noticed {{organization}} processes significant drug evidence volumes. Many departments tell us incineration costs are straining budgets. Our Narc Gone system destroys drugs on-site for 30% less than traditional methods. Worth a brief conversation about potential savings?"
            }
        }
        
        print("🧪 Testing RAG-Enhanced Personalization...")
        result = await agent.execute(test_task)
        
        print("Result:")
        print(json.dumps(result, indent=2))
        
        if result.get("success"):
            print(f"\n📧 Personalized Email ({result.get('method')}):")
            print(result["personalized_body"])
            print(f"\n📚 Knowledge Sources Used: {result.get('knowledge_sources', [])}")
    
    # Run test
    asyncio.run(test_rag_personalization())