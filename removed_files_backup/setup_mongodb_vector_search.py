#!/usr/bin/env python3
"""
Setup Script for MongoDB Atlas Vector Search
Helps configure vector search index and initialize knowledge base
"""

import os
import json
import logging
from narcon_knowledge_base import NarconKnowledgeBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_vector_search_instructions():
    """Provide instructions for setting up MongoDB Atlas Vector Search"""
    
    instructions = """
🔧 MongoDB Atlas Vector Search Setup Instructions
=================================================

STEP 1: Configure Environment Variables
--------------------------------------
Create a .env file or export these variables:

export MONGODB_CONNECTION_STRING="mongodb+srv://solutions-account:<db_password>@cluster0.hdejtab.mongodb.net/?appName=Cluster0"
export MONGODB_PASSWORD="your_actual_password"
export OPENAI_API_KEY="your_openai_key"  # Optional, for backup embeddings

STEP 2: Create Vector Search Index in MongoDB Atlas
--------------------------------------------------
1. Go to MongoDB Atlas Dashboard (cloud.mongodb.com)
2. Navigate to your Cluster0
3. Click "Search" tab
4. Click "Create Search Index"
5. Choose "JSON Editor"
6. Use database: "narcon_knowledge"
7. Use collection: "knowledge_documents"
8. Use index name: "vector_search_index"
9. Paste this JSON configuration:

{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
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

10. Click "Next" and "Create Search Index"
11. Wait for index to build (usually 1-2 minutes)

STEP 3: Initialize Knowledge Base
---------------------------------
Run this script to populate the knowledge base:

python setup_mongodb_vector_search.py init

STEP 4: Test the System
-----------------------
Run this script to test vector search:

python setup_mongodb_vector_search.py test

TROUBLESHOOTING
---------------
- If connection fails: Check password in connection string
- If vector search fails: Ensure index is built and named correctly
- If embeddings fail: Install sentence-transformers package
- Text search fallback will work even without vector index

For questions: Check MongoDB Atlas documentation on Vector Search
"""
    
    return instructions

def initialize_knowledge_base():
    """Initialize the knowledge base with Narcon data"""
    try:
        print("🏗️ Initializing Narcon Knowledge Base...")
        
        # Check environment variables
        if not os.environ.get('MONGODB_CONNECTION_STRING'):
            print("❌ MONGODB_CONNECTION_STRING environment variable not set")
            return False
        
        if not os.environ.get('MONGODB_PASSWORD'):
            print("❌ MONGODB_PASSWORD environment variable not set") 
            return False
        
        # Initialize knowledge base
        kb = NarconKnowledgeBase()
        
        # Show vector index definition
        print("\n📋 Vector Search Index Definition:")
        index_def = kb.create_vector_search_index()
        if index_def:
            print(json.dumps(index_def, indent=2))
        
        # Initialize with Narcon knowledge
        print("\n📚 Adding Narcon knowledge documents...")
        success = kb.initialize_narcon_knowledge()
        
        if success:
            print("✅ Knowledge base initialized successfully!")
            print("\nNext steps:")
            print("1. Ensure vector search index is created in MongoDB Atlas")
            print("2. Run 'python setup_mongodb_vector_search.py test' to verify")
            return True
        else:
            print("❌ Failed to initialize knowledge base")
            return False
            
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

def test_rag_system():
    """Test the complete RAG system"""
    try:
        print("🧪 Testing RAG System...")
        
        # Initialize knowledge base
        kb = NarconKnowledgeBase()
        
        # Test queries
        test_queries = [
            {
                "query": "DHS partnership government testing",
                "agency_types": ["federal"],
                "description": "Federal agency asking about credibility"
            },
            {
                "query": "fentanyl officer safety police",
                "agency_types": ["police"],
                "description": "Police department asking about safety"
            },
            {
                "query": "cost savings incineration budget",
                "agency_types": ["police", "sheriff"], 
                "description": "Local agency asking about costs"
            },
            {
                "query": "cannabis storage space evidence room",
                "agency_types": ["sheriff"],
                "description": "Sheriff asking about cannabis disposal"
            }
        ]
        
        print("\n🔍 Testing Knowledge Search...")
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n--- Test {i}: {test_case['description']} ---")
            print(f"Query: {test_case['query']}")
            
            results = kb.search_knowledge(
                query=test_case['query'],
                agency_types=test_case['agency_types'],
                limit=2
            )
            
            if results:
                print(f"✅ Found {len(results)} relevant documents:")
                for j, result in enumerate(results, 1):
                    score = result.get('score', 'N/A')
                    print(f"   {j}. {result['title']}")
                    print(f"      Score: {score}, Type: {result['doc_type']}")
                    print(f"      Relevance: {', '.join(result.get('pain_points', []))}")
            else:
                print("❌ No results found")
        
        # Test prospect-specific knowledge retrieval
        print(f"\n🎯 Testing Prospect-Specific Retrieval...")
        test_contact = {
            "organization": "Austin Police Department",
            "title": "Property & Evidence Manager",
            "city": "Austin",
            "state": "TX"
        }
        
        relevant_docs = kb.get_relevant_knowledge_for_prospect(test_contact, "drug disposal costs")
        
        if relevant_docs:
            print(f"✅ Found {len(relevant_docs)} relevant docs for Austin PD:")
            for doc in relevant_docs:
                print(f"   - {doc['title']} ({doc['doc_type']})")
        else:
            print("❌ No relevant docs found for test prospect")
        
        print(f"\n✅ RAG system test completed!")
        return True
        
    except Exception as e:
        print(f"❌ RAG test failed: {e}")
        return False

def test_rag_personalization():
    """Test the RAG-enhanced personalization agent"""
    try:
        print("🤖 Testing RAG-Enhanced Personalization Agent...")
        
        from rag_enhanced_personalization import EnhancedPersonalizationAgent
        import asyncio
        
        async def run_test():
            agent = EnhancedPersonalizationAgent()
            
            test_task = {
                "contact_data": {
                    "firstName": "Sarah",
                    "title": "Property & Evidence Manager", 
                    "organization": "Department of Homeland Security",
                    "city": "Washington",
                    "state": "DC"
                },
                "email_template": {
                    "body": "I noticed {{organization}} processes significant drug evidence volumes. Many agencies tell us disposal logistics are challenging. Our Narc Gone system destroys drugs on-site with government-approved methods. Worth discussing how this could help {{organization}}?"
                }
            }
            
            result = await agent.execute(test_task)
            
            if result.get("success"):
                print(f"✅ RAG Personalization successful!")
                print(f"   Method used: {result.get('method')}")
                print(f"   Knowledge sources: {result.get('knowledge_sources', [])}")
                print(f"\n📧 Personalized Email:")
                print(result["personalized_body"])
                return True
            else:
                print(f"❌ RAG Personalization failed: {result.get('error')}")
                return False
        
        return asyncio.run(run_test())
        
    except Exception as e:
        print(f"❌ RAG personalization test failed: {e}")
        return False

def main():
    """Main setup and test function"""
    import sys
    
    if len(sys.argv) < 2:
        print(setup_vector_search_instructions())
        return
    
    command = sys.argv[1].lower()
    
    if command == "instructions":
        print(setup_vector_search_instructions())
        
    elif command == "init":
        print("🚀 Initializing MongoDB Vector Search for Narcon...")
        success = initialize_knowledge_base()
        if success:
            print("\n✅ Setup complete! Next run: python setup_mongodb_vector_search.py test")
        else:
            print("\n❌ Setup failed. Check error messages above.")
            
    elif command == "test":
        print("🧪 Testing RAG System Components...")
        
        # Test knowledge base
        kb_success = test_rag_system()
        
        # Test personalization
        print("\n" + "="*50)
        personalization_success = test_rag_personalization()
        
        if kb_success and personalization_success:
            print(f"\n🎉 All RAG system tests passed!")
            print("System is ready for production use.")
        else:
            print(f"\n⚠️ Some tests failed. Check configuration and try again.")
            
    else:
        print("❌ Unknown command. Available commands:")
        print("  instructions - Show setup instructions")
        print("  init         - Initialize knowledge base")
        print("  test         - Test RAG system")

if __name__ == "__main__":
    main()