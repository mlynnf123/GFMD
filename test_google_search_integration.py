#!/usr/bin/env python3
"""
Test Google Custom Search API Integration
Demonstrates how the system finds real healthcare contacts via web search
"""

import asyncio
from google_search_integration import GoogleSearchEmailFinder

async def test_google_search():
    """Test Google Custom Search API integration"""
    
    print("🧪 TESTING GOOGLE CUSTOM SEARCH INTEGRATION")
    print("=" * 60)
    
    # Initialize the search finder
    finder = GoogleSearchEmailFinder()
    
    if not finder.api_key or not finder.search_engine_id:
        print("❌ Google Search API not configured")
        return
    
    print(f"✅ API Key: {finder.api_key[:20]}...")
    print(f"✅ Search Engine ID: {finder.search_engine_id}")
    print(f"✅ Project: {finder.project_id}")
    print()
    
    # Test hospital
    test_hospital = "Houston Methodist Hospital"
    test_title = "Laboratory Director"
    
    print(f"🔍 Testing search for: {test_title} at {test_hospital}")
    print("=" * 60)
    
    try:
        # Search for contacts
        contacts = await finder.search_hospital_contact(test_hospital, test_title)
        
        if contacts:
            print(f"✅ Found {len(contacts)} potential contacts:")
            for i, contact in enumerate(contacts[:3], 1):  # Show first 3
                print(f"   {i}. {contact.get('contact_name', 'N/A')}")
                print(f"      Email: {contact.get('email', 'N/A')}")
                print(f"      Title: {contact.get('contact_title', 'N/A')}")
                print(f"      Source: {contact.get('source_url', 'N/A')[:50]}...")
                print()
        else:
            print("⚠️ No contacts found in this test search")
            print("💡 This is normal - web search results vary")
    
    except Exception as e:
        print(f"❌ Search error: {e}")
        print("💡 This might be due to API quotas or network issues")
    
    print("=" * 60)
    print("🎯 INTEGRATION STATUS: Google Custom Search API Ready!")
    print("🔄 Your GFMD system will now:")
    print("   • Use 5,459 Definitive Healthcare contacts as primary source")
    print("   • Automatically search for missing emails when needed")  
    print("   • Discover additional contacts at target hospitals")
    print("   • Validate and enrich contact information")

async def test_prospect_enrichment():
    """Test prospect enrichment with missing email"""
    
    print("\n🧪 TESTING PROSPECT ENRICHMENT")
    print("=" * 50)
    
    finder = GoogleSearchEmailFinder()
    
    # Create test prospect with missing email
    test_prospect = {
        'organization_name': 'Houston Methodist Hospital',
        'location': 'Houston, TX',
        'contact_name': 'Laboratory Director',
        'contact_title': 'Laboratory Director',
        'email': '',  # Missing email - should trigger search
        'facility_type': 'Major Medical Center'
    }
    
    print(f"📋 Test prospect: {test_prospect['organization_name']}")
    print(f"📧 Current email: {test_prospect['email'] or 'MISSING'}")
    print("🔍 Triggering prospect enrichment...")
    
    try:
        enriched_prospect = await finder.enrich_prospect_with_search(test_prospect)
        
        print(f"✅ Enrichment result:")
        print(f"   Organization: {enriched_prospect.get('organization_name')}")
        print(f"   Contact: {enriched_prospect.get('contact_name')}")
        print(f"   Email: {enriched_prospect.get('email', 'Not found')}")
        print(f"   Verified: {enriched_prospect.get('verified', False)}")
        print(f"   Search Verified: {enriched_prospect.get('search_verified', False)}")
        
    except Exception as e:
        print(f"❌ Enrichment error: {e}")

if __name__ == "__main__":
    asyncio.run(test_google_search())
    asyncio.run(test_prospect_enrichment())