#!/usr/bin/env python3
"""
Narc Gone Knowledge Base with MongoDB Vector Search (RAG System)
Stores and retrieves product information, case studies, and competitive intelligence
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from dataclasses import dataclass, asdict

import pymongo
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import openai

logger = logging.getLogger(__name__)

@dataclass
class KnowledgeDocument:
    """Structure for knowledge base documents"""
    id: str
    title: str
    content: str
    doc_type: str  # "product_info", "case_study", "competitor_analysis", "compliance", "pricing"
    tags: List[str]
    agency_types: List[str]  # ["federal", "police", "sheriff", "state"]
    pain_points: List[str]   # ["cost", "safety", "compliance", "logistics"]
    embedding: Optional[List[float]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Narc GoneKnowledgeBase:
    """RAG system for Narc Gone product knowledge using MongoDB Vector Search"""
    
    def __init__(self, connection_string: Optional[str] = None):
        """Initialize the knowledge base with MongoDB Vector Search"""
        
        # MongoDB connection
        self.connection_string = connection_string or os.environ.get('MONGODB_CONNECTION_STRING')
        if not self.connection_string:
            raise ValueError("MongoDB connection string required")
        
        # Replace placeholder with actual password
        if '<db_password>' in self.connection_string:
            password = os.environ.get('MONGODB_PASSWORD')
            if password:
                self.connection_string = self.connection_string.replace('<db_password>', password)
            else:
                raise ValueError("MONGODB_PASSWORD environment variable required")
        
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client.narcon_knowledge
            self.knowledge_collection = self.db.knowledge_documents
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ Connected to MongoDB Atlas for RAG system")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
        
        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Sentence transformer model loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            raise
        
        # Initialize OpenAI for backup embeddings if needed
        self.openai_client = None
        if os.environ.get('OPENAI_API_KEY'):
            try:
                self.openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
                logger.info("✅ OpenAI client initialized for backup embeddings")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI client initialization failed: {e}")
    
    def create_vector_search_index(self):
        """Create vector search index for MongoDB Atlas"""
        try:
            # This needs to be done via MongoDB Atlas UI or MongoDB CLI
            # Providing the index definition for manual creation
            index_definition = {
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": 384,  # all-MiniLM-L6-v2 dimensions
                        "similarity": "cosine"
                    },
                    {
                        "type": "filter",
                        "path": "doc_type"
                    },
                    {
                        "type": "filter", 
                        "path": "agency_types"
                    },
                    {
                        "type": "filter",
                        "path": "pain_points"
                    }
                ]
            }
            
            logger.info("📋 Vector search index definition:")
            logger.info(json.dumps(index_definition, indent=2))
            logger.info("Create this index manually in MongoDB Atlas with name 'vector_search_index'")
            
            return index_definition
            
        except Exception as e:
            logger.error(f"❌ Failed to create vector index: {e}")
            return None
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        try:
            # Use sentence transformer (local, fast)
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {e}")
            return []
    
    def add_knowledge_document(self, doc: KnowledgeDocument) -> str:
        """Add a document to the knowledge base"""
        try:
            # Generate embedding if not provided
            if not doc.embedding:
                combined_text = f"{doc.title} {doc.content}"
                doc.embedding = self._generate_embedding(combined_text)
            
            # Set timestamps
            doc.created_at = datetime.utcnow()
            doc.updated_at = datetime.utcnow()
            
            # Insert into MongoDB
            doc_dict = asdict(doc)
            result = self.knowledge_collection.insert_one(doc_dict)
            
            logger.info(f"✅ Added knowledge document: {doc.title}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to add document: {e}")
            raise
    
    def search_knowledge(self, 
                        query: str,
                        doc_types: Optional[List[str]] = None,
                        agency_types: Optional[List[str]] = None, 
                        pain_points: Optional[List[str]] = None,
                        limit: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge base using vector similarity and filters"""
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            if not query_embedding:
                logger.error("❌ Failed to generate query embedding")
                return []
            
            # Build aggregation pipeline for vector search
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_search_index",
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": limit * 10,
                        "limit": limit
                    }
                }
            ]
            
            # Add filters if specified
            match_filters = {}
            if doc_types:
                match_filters["doc_type"] = {"$in": doc_types}
            if agency_types:
                match_filters["agency_types"] = {"$in": agency_types}
            if pain_points:
                match_filters["pain_points"] = {"$in": pain_points}
            
            if match_filters:
                pipeline.append({"$match": match_filters})
            
            # Add score and project useful fields
            pipeline.extend([
                {
                    "$addFields": {
                        "score": {"$meta": "vectorSearchScore"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "id": 1,
                        "title": 1,
                        "content": 1,
                        "doc_type": 1,
                        "tags": 1,
                        "agency_types": 1,
                        "pain_points": 1,
                        "score": 1
                    }
                }
            ])
            
            # Execute search
            try:
                results = list(self.knowledge_collection.aggregate(pipeline))
                logger.info(f"🔍 Vector search returned {len(results)} results for: {query}")
                return results
                
            except Exception as e:
                # Fallback to simple text search if vector search fails
                logger.warning(f"⚠️ Vector search failed, falling back to text search: {e}")
                return self._fallback_text_search(query, doc_types, agency_types, pain_points, limit)
                
        except Exception as e:
            logger.error(f"❌ Knowledge search failed: {e}")
            return []
    
    def _fallback_text_search(self,
                             query: str,
                             doc_types: Optional[List[str]] = None,
                             agency_types: Optional[List[str]] = None,
                             pain_points: Optional[List[str]] = None,
                             limit: int = 5) -> List[Dict[str, Any]]:
        """Fallback text search when vector search isn't available"""
        try:
            # Build text search query
            search_filter = {
                "$text": {"$search": query}
            }
            
            # Add additional filters
            if doc_types:
                search_filter["doc_type"] = {"$in": doc_types}
            if agency_types:
                search_filter["agency_types"] = {"$in": agency_types}
            if pain_points:
                search_filter["pain_points"] = {"$in": pain_points}
            
            # Execute search with text score
            cursor = self.knowledge_collection.find(
                search_filter,
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit)
            
            results = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                results.append(doc)
            
            logger.info(f"📝 Text search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Fallback text search failed: {e}")
            return []
    
    def get_relevant_knowledge_for_prospect(self, 
                                          contact_data: Dict[str, Any],
                                          query_context: str = "") -> List[Dict[str, Any]]:
        """Get relevant knowledge for a specific prospect"""
        try:
            # Determine agency type
            org_name = contact_data.get("organization", "")
            title = contact_data.get("title", "")
            
            agency_type = self._determine_agency_type(org_name, title)
            pain_points = self._infer_pain_points(contact_data)
            
            # Build search query
            search_query = f"{query_context} {org_name} {title}".strip()
            if not search_query:
                search_query = f"law enforcement drug destruction {agency_type}"
            
            # Search knowledge base
            results = self.search_knowledge(
                query=search_query,
                agency_types=[agency_type],
                pain_points=pain_points,
                limit=3
            )
            
            logger.info(f"📚 Retrieved {len(results)} knowledge docs for {org_name}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to get relevant knowledge: {e}")
            return []
    
    def _determine_agency_type(self, org_name: str, title: str = "") -> str:
        """Determine agency type from organization name and title"""
        org_lower = org_name.lower()
        
        federal_indicators = ["dhs", "homeland", "border patrol", "cbp", "ice", "dea", "tsa", "fbi", "atf"]
        if any(indicator in org_lower for indicator in federal_indicators):
            return "federal"
        
        if "sheriff" in org_lower or "county" in org_lower:
            return "sheriff"
        
        if "state police" in org_lower or "highway patrol" in org_lower:
            return "state"
        
        return "police"
    
    def _infer_pain_points(self, contact_data: Dict[str, Any]) -> List[str]:
        """Infer likely pain points from contact data"""
        pain_points = []
        
        title = contact_data.get("title", "").lower()
        org = contact_data.get("organization", "").lower()
        
        # Property & Evidence managers likely care about logistics and cost
        if "evidence" in title or "property" in title:
            pain_points.extend(["logistics", "cost", "storage"])
        
        # Procurement roles care about compliance and cost
        if "procurement" in title or "purchasing" in title:
            pain_points.extend(["compliance", "cost"])
        
        # Safety roles care about officer safety
        if "safety" in title or "chief" in title:
            pain_points.extend(["safety", "compliance"])
        
        # Federal agencies have scale challenges
        if any(fed in org for fed in ["dhs", "border", "ice", "dea"]):
            pain_points.extend(["scale", "compliance"])
        
        # Default pain points if none identified
        if not pain_points:
            pain_points = ["cost", "logistics"]
        
        return pain_points
    
    def initialize_narcon_knowledge(self):
        """Initialize the knowledge base with Narc Gone product information"""
        try:
            logger.info("🏗️ Initializing Narc Gone knowledge base...")
            
            # Core product documents
            narcon_docs = [
                KnowledgeDocument(
                    id="narcon_mx_overview",
                    title="Narc Gone MX - Multi-Drug Destruction System",
                    content="""Narc Gone MX is the only chemical drug destruction system tested and verified by the U.S. Government to meet DEA non-retrievable standards. Created through CRADA #22-TST-001 with the Department of Homeland Security (DHS).

Key Features:
- Destroys all Schedule I-V controlled substances including fentanyl, heroin, cocaine, methamphetamine, MDMA, prescription medications
- 99.99% fentanyl destruction verified by NC State Crime Lab
- Available in 1.0, 2.5, and 5.0 gallon sizes
- Simple process: add drugs, agitate, add hardener when full
- Renders drugs inert and non-retrievable for safe landfill disposal
- EPA and DEA compliant without permits or special handling
- Used by CBP for processing 55,000+ pounds monthly

DHS Partnership:
- Co-developed under Cooperative Research and Development Agreement
- Listed in CBP Technology Assessment Catalog
- Two years of government testing and verification
- Only system with official U.S. Government testing certification""",
                    doc_type="product_info",
                    tags=["narc_gone", "mx", "multi_drug", "dhs_tested", "fentanyl"],
                    agency_types=["federal", "police", "sheriff", "state"],
                    pain_points=["compliance", "safety", "logistics", "cost"]
                ),
                
                KnowledgeDocument(
                    id="narcon_cx_overview", 
                    title="Narc Gone CX - Cannabis Destruction System",
                    content="""Narc Gone CX is specifically formulated for the destruction of medical and recreational cannabis evidence. Designed to handle the unique challenges of bulk plant material disposal.

Key Features:
- Optimized for all forms of cannabis destruction
- Available in 1.0 and 5.0 gallon sizes
- Reclaims valuable property room space by destroying bulky cannabis evidence
- Same proven chemical process as Narc Gone MX
- EPA and DEA compliant disposal
- Eliminates need for incineration of cannabis evidence

Benefits for Agencies:
- Reduces evidence storage burden
- Eliminates costly cannabis transport to incinerators
- Quick processing of high-volume cannabis seizures
- Safe for landfill disposal after treatment
- No special permits or handling required""",
                    doc_type="product_info",
                    tags=["narc_gone", "cx", "cannabis", "storage", "bulk_disposal"],
                    agency_types=["police", "sheriff", "state"],
                    pain_points=["storage", "logistics", "cost"]
                ),
                
                KnowledgeDocument(
                    id="dhs_partnership_credibility",
                    title="DHS Partnership and Government Credibility",
                    content="""Narc Gone's partnership with the Department of Homeland Security provides unmatched credibility in the law enforcement market.

CRADA #22-TST-001 Details:
- Cooperative Research and Development Agreement with DHS
- Product created specifically FOR federal law enforcement needs
- Two years of rigorous testing by CBP Laboratory of Scientific Services
- Only chemical destruction system with official U.S. Government verification

Government Testing Results:
- Meets DEA non-retrievable standards (verified)
- 99.99% fentanyl destruction (NC State Crime Lab)
- EPA compliant for landfill disposal
- No detectable drug residues after treatment

CBP Usage:
- Processes 55,000+ pounds of seized drugs monthly
- Listed in official CBP Technology Assessment Catalog
- Eliminates costly incinerator transport for federal agencies
- Proven at massive scale operations

Why This Matters:
- Federal agencies prefer government-tested solutions
- Reduces procurement risk and approval time
- Builds immediate trust with law enforcement
- Provides competitive advantage over untested products""",
                    doc_type="credibility",
                    tags=["dhs", "government", "credibility", "cbp", "testing"],
                    agency_types=["federal"],
                    pain_points=["compliance", "credibility", "procurement"]
                ),
                
                KnowledgeDocument(
                    id="cost_savings_analysis",
                    title="Drug Disposal Cost Analysis - Narc Gone vs Incineration",
                    content="""Detailed cost comparison showing significant savings with Narc Gone vs traditional incineration methods.

Typical Incineration Costs:
- $1.50 per pound base disposal fee
- Transportation costs (often 100+ miles to nearest facility)
- Multiple officer time (6-8 hour round trips)
- Vehicle costs and mileage
- Total: $8,000-15,000+ annually for medium departments

Narc Gone Cost Structure:
- Container cost: $200-400 depending on size
- Treats 1,000+ grams of drugs per container
- No transportation required (on-site processing)
- No officer travel time
- Total: 40-60% savings vs incineration

Real Department Example:
Medium police department (100 officers) processing 50 lbs drugs annually:
- Incineration total cost: $12,000/year (fees + transport + labor)
- Narc Gone total cost: $4,800/year
- Annual savings: $7,200 (60% reduction)

Additional Benefits:
- Eliminates evidence backlog from disposal delays
- Reduces officer safety risks during transport
- Reclaims evidence room storage space
- Immediate processing capability""",
                    doc_type="cost_analysis",
                    tags=["cost_savings", "incineration", "comparison", "budget"],
                    agency_types=["police", "sheriff", "state"],
                    pain_points=["cost", "budget", "logistics"]
                ),
                
                KnowledgeDocument(
                    id="officer_safety_fentanyl",
                    title="Officer Safety and Fentanyl Exposure Prevention",
                    content="""Narc Gone eliminates officer safety risks associated with drug transport and handling, particularly with fentanyl.

Fentanyl Safety Concerns:
- 2mg can be lethal dose for officers
- Airborne particles during transport pose exposure risk
- Multiple officer transport requirements increase exposure
- Vehicle contamination risks

Narc Gone Safety Benefits:
- 99.99% fentanyl destruction (NC State Crime Lab verified)
- On-site processing eliminates transport exposure
- Sealed container system minimizes handling
- No airborne particles during treatment process
- Immediate neutralization of dangerous substances

Officer Protection Protocol:
- Standard PPE sufficient for Narc Gone use
- No special hazmat training required
- Eliminates multi-hour transport exposure
- Reduces overall officer contact with substances
- Chemical neutralization makes substances non-retrievable and safe

Department Risk Reduction:
- Lower workers compensation claims
- Reduced liability from transport accidents
- Improved officer confidence in evidence handling
- Compliance with OSHA safety standards
- Protects officers and their families from exposure risks""",
                    doc_type="safety_info",
                    tags=["safety", "fentanyl", "officer_protection", "exposure"],
                    agency_types=["police", "sheriff", "state", "federal"],
                    pain_points=["safety", "liability", "compliance"]
                ),
                
                KnowledgeDocument(
                    id="competitor_rx_destroyer",
                    title="Competitive Analysis - RX Destroyer vs Narc Gone",
                    content="""Detailed comparison between Narc Gone and primary competitor RX Destroyer, highlighting key differentiators.

RX Destroyer Positioning:
- Focuses almost exclusively on healthcare sector
- Targets hospitals, pharmacies, long-term care facilities
- Tagline: "Saving Water, Saving Lives... One prescription at a time"
- Marketing emphasizes pharmaceutical diversion prevention
- No specific law enforcement focus or messaging

Key Competitive Advantages:
- Government Testing: Narc Gone is ONLY system tested and verified by U.S. Government
- Law Enforcement Focus: Purpose-built for evidence disposal vs healthcare waste
- DHS Partnership: Created through official government collaboration
- Scale Proven: CBP processes 55,000+ lbs monthly with Narc Gone
- Federal Credibility: Listed in official government technology catalog

Market Positioning:
- RX Destroyer: Healthcare waste prevention
- Narc Gone: Law enforcement evidence disposal
- Minimal market overlap, clear differentiation
- Law enforcement prefers government-tested solutions
- Federal agencies especially value existing government partnerships

Procurement Advantages:
- Existing government contract relationships
- Reduced vendor approval timeframes
- Built-in credibility with procurement officers
- Lower risk profile for government buyers
- Proven performance at federal agency scale""",
                    doc_type="competitor_analysis",
                    tags=["competitor", "rx_destroyer", "differentiation", "government"],
                    agency_types=["federal", "police", "sheriff", "state"],
                    pain_points=["credibility", "procurement", "compliance"]
                )
            ]
            
            # Add documents to knowledge base
            for doc in narcon_docs:
                doc_id = self.add_knowledge_document(doc)
                logger.info(f"✅ Added: {doc.title}")
            
            logger.info(f"🎯 Successfully initialized {len(narcon_docs)} knowledge documents")
            
            # Create text search index for fallback
            try:
                self.knowledge_collection.create_index([
                    ("title", "text"),
                    ("content", "text"),
                    ("tags", "text")
                ])
                logger.info("✅ Created text search index for fallback")
            except Exception as e:
                logger.warning(f"⚠️ Text index creation failed: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize knowledge base: {e}")
            return False

# Test and utility functions
if __name__ == "__main__":
    import sys
    
    def test_knowledge_base():
        """Test the knowledge base functionality"""
        try:
            # Initialize knowledge base
            kb = Narc GoneKnowledgeBase()
            
            # Initialize with Narc Gone knowledge
            print("🏗️ Initializing Narc Gone knowledge base...")
            success = kb.initialize_narcon_knowledge()
            
            if success:
                print("✅ Knowledge base initialized successfully")
                
                # Test search
                print("\n🔍 Testing knowledge search...")
                test_queries = [
                    ("fentanyl safety for police officers", ["police"]),
                    ("federal agency drug disposal costs", ["federal"]),
                    ("DHS partnership and credibility", ["federal"]),
                    ("cannabis evidence storage problems", ["police", "sheriff"])
                ]
                
                for query, agency_types in test_queries:
                    print(f"\n📝 Query: {query}")
                    results = kb.search_knowledge(query, agency_types=agency_types, limit=2)
                    
                    for i, result in enumerate(results, 1):
                        score = result.get('score', 'N/A')
                        print(f"   {i}. {result['title']} (Score: {score})")
                        print(f"      Type: {result['doc_type']}, Pain Points: {result['pain_points']}")
            else:
                print("❌ Failed to initialize knowledge base")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_knowledge_base()
    elif len(sys.argv) > 1 and sys.argv[1] == "index":
        # Show vector index definition
        kb = Narc GoneKnowledgeBase()
        kb.create_vector_search_index()
    else:
        print("Narc Gone Knowledge Base RAG System")
        print("Usage:")
        print("  python narcon_knowledge_base.py test    # Test the system") 
        print("  python narcon_knowledge_base.py index   # Show vector index definition")
        print()
        print("Environment Variables Required:")
        print("  MONGODB_CONNECTION_STRING - MongoDB Atlas connection string")
        print("  MONGODB_PASSWORD - Database password") 
        print("  OPENAI_API_KEY - OpenAI API key (optional, for backup embeddings)")