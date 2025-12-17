#!/usr/bin/env python3
"""
Test RAG-enhanced email composer without full Groq integration
"""

import os
import asyncio
import sys
from typing import Dict, Any

# Load environment variables
try:
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                value = value.strip('"')
                os.environ[key] = value
except FileNotFoundError:
    print("⚠️ .env file not found")

# Import after setting env vars
from vector_rag_system import VectorRAGSystem

def test_rag_enhanced_personalization():
    """Test RAG-enhanced email personalization"""
    
    print("🧠 Testing RAG-Enhanced Email Personalization")
    print("=" * 50)
    
    try:
        # Initialize RAG system
        rag_system = VectorRAGSystem()
        
        # Test prospect data
        prospect_data = {
            "contact_name": "Detective Sarah Martinez",
            "company_name": "Austin Police Department", 
            "location": "Austin, TX",
            "title": "Property & Evidence Manager"
        }
        
        # Test research findings
        research_findings = {
            "pain_points": ["cost", "storage space", "compliance"]
        }
        
        print(f"\n👤 Prospect: {prospect_data['contact_name']}")
        print(f"🏢 Department: {prospect_data['company_name']}")
        print(f"🎯 Pain Points: {', '.join(research_findings['pain_points'])}")
        
        # Get personalized insights from RAG
        print(f"\n🔍 Retrieving RAG insights...")
        
        agency_type = "police"  # Could be enhanced with better detection
        insights = rag_system.get_personalized_insights(
            agency_type=agency_type,
            pain_points=research_findings["pain_points"][:2],
            location=prospect_data["location"]
        )
        
        print(f"\n📊 RAG Insights Retrieved:")
        for key, value in insights.items():
            print(f"  • {key}: {len(value)} characters")
            if value:
                preview = value[:150].replace('\n', ' ')
                print(f"    Preview: {preview}...")
        
        # Combine relevant context for email
        context_parts = []
        for key, value in insights.items():
            if value and len(value) > 50:  # Only use substantial context
                context_parts.append(value[:300])  # Limit length
        
        rag_context = " ".join(context_parts)[:800]  # Max 800 chars
        
        print(f"\n📝 Combined RAG Context ({len(rag_context)} chars):")
        print(f"   {rag_context[:200]}...")
        
        # Show how this would enhance email composition
        print(f"\n✨ Email Enhancement Potential:")
        print(f"  • Dynamic knowledge from {len(insights)} sources")
        print(f"  • Context-aware content for {agency_type} agencies")
        print(f"  • Pain point specific solutions: {research_findings['pain_points'][:2]}")
        print(f"  • Location-specific insights for {prospect_data['location']}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_knowledge_search():
    """Test specific knowledge searches"""
    
    print(f"\n🔎 Testing Knowledge Search Capabilities")
    print("=" * 50)
    
    try:
        rag_system = VectorRAGSystem()
        
        test_queries = [
            ("police department cost savings", "Cost-focused query"),
            ("evidence room storage space problems", "Storage pain point"),
            ("DEA compliance and testing", "Compliance/credibility"),
            ("federal agency drug disposal", "Federal agencies"),
            ("fentanyl officer safety", "Safety concerns")
        ]
        
        for query, description in test_queries:
            print(f"\n📋 {description}")
            print(f"   Query: '{query}'")
            
            results = rag_system.vector_search(query, limit=2)
            print(f"   Results: {len(results)} documents")
            
            for i, result in enumerate(results, 1):
                similarity = result.get("similarity", "N/A")
                content_preview = result.get("content", "")[:80]
                print(f"     {i}. Score: {similarity:.3f} | {content_preview}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Knowledge search test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 GFMD RAG System Test Suite")
    print("=" * 60)
    
    # Test 1: RAG-enhanced personalization
    success1 = test_rag_enhanced_personalization()
    
    # Test 2: Knowledge search capabilities  
    success2 = test_knowledge_search()
    
    print(f"\n🎉 Test Results:")
    print(f"  ✅ RAG Personalization: {'PASSED' if success1 else 'FAILED'}")
    print(f"  ✅ Knowledge Search: {'PASSED' if success2 else 'FAILED'}")
    
    if success1 and success2:
        print(f"\n🎯 RAG system is ready for email composition!")
        print(f"   Next step: Update email composer to use these RAG insights")
    else:
        print(f"\n⚠️ Some tests failed. Check configuration.")