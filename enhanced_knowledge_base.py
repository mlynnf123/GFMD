#!/usr/bin/env python3
"""
Enhanced GFMD Knowledge Base with RAG Integration
Stores product information and law enforcement pain points for enhanced email personalization
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

from mongodb_storage import MongoDBStorage

logger = logging.getLogger(__name__)

class GFMDKnowledgeBase:
    """Enhanced knowledge base for GFMD Narc Gone with RAG capabilities"""
    
    def __init__(self):
        """Initialize the knowledge base"""
        self.storage = MongoDBStorage()
        self.collection = self.storage.db.knowledge_base
        
        # Create text index for search
        try:
            self.collection.create_index([
                ("title", "text"),
                ("content", "text"), 
                ("tags", "text")
            ])
        except Exception as e:
            logger.debug(f"Index may already exist: {e}")
    
    def add_document(self, title: str, content: str, doc_type: str, tags: List[str] = None, metadata: Dict = None) -> str:
        """Add a document to the knowledge base"""
        
        # Create unique ID based on content hash
        content_hash = hashlib.md5(content.encode()).hexdigest()
        doc_id = f"{doc_type}_{content_hash[:8]}"
        
        document = {
            "_id": doc_id,
            "title": title,
            "content": content,
            "doc_type": doc_type,
            "tags": tags or [],
            "metadata": metadata or {},
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        try:
            result = self.collection.insert_one(document)
            logger.info(f"Added document: {title}")
            return doc_id
        except Exception as e:
            # Update if document exists
            self.collection.update_one(
                {"_id": doc_id},
                {"$set": {**document, "updated_at": datetime.now()}}
            )
            logger.info(f"Updated document: {title}")
            return doc_id
    
    def search_documents(self, query: str, doc_type: str = None, limit: int = 5) -> List[Dict]:
        """Search for relevant documents"""
        
        # Build search filter
        search_filter = {"$text": {"$search": query}}
        if doc_type:
            search_filter["doc_type"] = doc_type
        
        # Search with text score
        results = list(self.collection.find(
            search_filter,
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit))
        
        return results
    
    def get_pain_point_info(self, pain_point: str) -> List[Dict]:
        """Get information about specific pain points"""
        return self.search_documents(pain_point, doc_type="pain_points", limit=3)
    
    def get_product_info(self, query: str) -> List[Dict]:
        """Get product information"""
        return self.search_documents(query, doc_type="product_info", limit=3)
    
    def get_personalization_data(self, agency_type: str, pain_points: List[str]) -> Dict[str, Any]:
        """Get personalized information for email composition"""
        
        personalization = {
            "product_benefits": [],
            "pain_point_solutions": [],
            "credibility_factors": [],
            "case_studies": []
        }
        
        # Get product benefits
        product_results = self.search_documents("benefits advantages", doc_type="product_info", limit=3)
        for doc in product_results:
            personalization["product_benefits"].append(doc["content"][:200])
        
        # Get pain point solutions
        for pain_point in pain_points:
            solutions = self.search_documents(pain_point, doc_type="pain_points", limit=2)
            for doc in solutions:
                personalization["pain_point_solutions"].append(doc["content"][:200])
        
        # Get credibility factors
        credibility_results = self.search_documents("tested certified DEA approved", doc_type="product_info", limit=2)
        for doc in credibility_results:
            personalization["credibility_factors"].append(doc["content"][:200])
        
        return personalization

def setup_knowledge_base():
    """Setup and populate the knowledge base with GFMD documents"""
    
    kb = GFMDKnowledgeBase()
    
    print("📚 Setting up GFMD Knowledge Base...")
    
    # Load and process the knowledge documents
    knowledge_files = [
        {
            "file": "/Users/merandafreiner/GFMD/GFMD/knowledge_base/gfmd_narc_gone_findings.md",
            "doc_type": "product_info",
            "tags": ["narc_gone", "product_specs", "testing", "compliance"]
        },
        {
            "file": "/Users/merandafreiner/GFMD/GFMD/knowledge_base/law_enforcement_pain_points.md", 
            "doc_type": "pain_points",
            "tags": ["law_enforcement", "challenges", "costs", "compliance"]
        }
    ]
    
    for file_info in knowledge_files:
        try:
            with open(file_info["file"], "r") as f:
                content = f.read()
            
            # Extract title from first line
            lines = content.split('\n')
            title = lines[0].replace('#', '').strip() if lines else "Unknown Document"
            
            # Add to knowledge base
            doc_id = kb.add_document(
                title=title,
                content=content,
                doc_type=file_info["doc_type"],
                tags=file_info["tags"],
                metadata={"source_file": file_info["file"]}
            )
            
            print(f"✅ Added: {title} ({doc_id})")
            
        except Exception as e:
            print(f"❌ Failed to process {file_info['file']}: {e}")
    
    # Add specific product information chunks for better retrieval
    product_chunks = [
        {
            "title": "Narc Gone Cost Benefits",
            "content": "Narc Gone is the most cost-effective drug disposal system available. Eliminates expensive incineration costs (~$1.50 per pound), eliminates travel costs to EPA-approved incinerators (often 100+ miles away), eliminates multi-day trips requiring multiple officers. No equipment purchase required (vs $6,000+ for incinerator units).",
            "tags": ["cost_savings", "benefits", "roi"]
        },
        {
            "title": "Narc Gone DEA Compliance", 
            "content": "Narc Gone is the ONLY chemical destruction product tested and verified by US Government to meet DEA Drug Destruction Standards (79 FR 53520). Created for U.S. Department of Homeland Security under CRADA 22-TST-001. Listed in CBP Laboratory Technology Assessment Catalog. Over 2 years of testing by CBP Laboratory.",
            "tags": ["compliance", "testing", "certification", "credibility"]
        },
        {
            "title": "Law Enforcement Storage Problems",
            "content": "Drug evidence takes up valuable property room space, creates backlog of drugs awaiting disposal, reduces storage space for other evidence. Departments often store drugs for months between disposal events. Narc Gone reclaims property-room space through quick destruction.",
            "tags": ["storage", "evidence_room", "space_management"]
        },
        {
            "title": "Geographic Accessibility Issues",
            "content": "EPA-approved incinerators are often 100+ miles away from small/mid-sized departments. Requires multi-day trips, multiple officers, vehicle costs, time away from community. Many departments cannot share incinerator access due to permit restrictions.",
            "tags": ["accessibility", "travel", "logistics", "small_departments"]
        }
    ]
    
    for chunk in product_chunks:
        doc_id = kb.add_document(
            title=chunk["title"],
            content=chunk["content"], 
            doc_type="product_info",
            tags=chunk["tags"]
        )
        print(f"✅ Added chunk: {chunk['title']} ({doc_id})")
    
    print(f"\n🎉 Knowledge base setup complete!")
    
    # Test the search functionality
    print(f"\n🔍 Testing search functionality:")
    
    test_queries = ["cost savings", "DEA compliance", "storage space"]
    for query in test_queries:
        results = kb.search_documents(query, limit=2)
        print(f"   Query '{query}': {len(results)} results")
    
    return kb

def test_personalization():
    """Test the personalization functionality"""
    
    kb = GFMDKnowledgeBase()
    
    # Test personalization for different agency types
    test_cases = [
        {
            "agency_type": "police",
            "pain_points": ["cost", "storage"]
        },
        {
            "agency_type": "sheriff", 
            "pain_points": ["compliance", "travel"]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🎯 Personalization for {test_case['agency_type']} department:")
        data = kb.get_personalization_data(
            test_case["agency_type"], 
            test_case["pain_points"]
        )
        
        print(f"   Product benefits: {len(data['product_benefits'])} items")
        print(f"   Pain point solutions: {len(data['pain_point_solutions'])} items")
        print(f"   Credibility factors: {len(data['credibility_factors'])} items")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            setup_knowledge_base()
        elif sys.argv[1] == "test":
            test_personalization()
    else:
        print("GFMD Enhanced Knowledge Base")
        print("Usage:")
        print("  python3 enhanced_knowledge_base.py setup  - Setup knowledge base")
        print("  python3 enhanced_knowledge_base.py test   - Test personalization")