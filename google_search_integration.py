#!/usr/bin/env python3
"""
Google Custom Search API Integration
Finds real email addresses for healthcare contacts using web search
"""

import re
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class GoogleSearchEmailFinder:
    """Uses Google Custom Search API to find real email addresses"""
    
    def __init__(self):
        # Load Google Search API credentials
        self.api_key = None
        self.search_engine_id = None
        self.load_search_credentials()
        
    def load_search_credentials(self):
        """Load Google Custom Search API credentials - Compatible with existing OAuth setup"""
        import os
        
        # Use your existing Google Cloud project
        self.project_id = "windy-tiger-471523-m5"
        
        # Try to load from environment variables first
        self.api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        # Try to load from credentials file
        if not self.api_key:
            try:
                with open('google_search_credentials.json', 'r') as f:
                    creds = json.load(f)
                    self.api_key = creds.get('api_key')
                    self.search_engine_id = creds.get('search_engine_id')
            except FileNotFoundError:
                print("⚠️ Google Search credentials not found")
                print(f"💡 For project {self.project_id}:")
                print("   1. Enable Custom Search API in Google Cloud Console")
                print("   2. Create API Key or use service account")
                print("   3. Create Custom Search Engine at https://cse.google.com/")
                print("   4. Add credentials to google_search_credentials.json")
    
    async def search_hospital_contact(self, hospital_name: str, contact_title: str = "Laboratory Director") -> List[Dict[str, Any]]:
        """Search for specific contact at a hospital"""
        
        if not self.api_key:
            print("❌ Google Search API not configured")
            return []
        
        # Search queries to try
        search_queries = [
            f'"{hospital_name}" "{contact_title}" email contact',
            f'site:{self.get_hospital_domain(hospital_name)} {contact_title}',
            f'"{hospital_name}" laboratory director contact information',
            f'"{hospital_name}" lab director email phone'
        ]
        
        contacts = []
        
        try:
            from googleapiclient.discovery import build
            
            service = build("customsearch", "v1", developerKey=self.api_key)
            
            for query in search_queries:
                print(f"🔍 Searching: {query}")
                
                result = service.cse().list(
                    q=query,
                    cx=self.search_engine_id,
                    num=10
                ).execute()
                
                if 'items' in result:
                    for item in result['items']:
                        # Extract emails from search results
                        content = item.get('snippet', '') + item.get('title', '')
                        emails = self.extract_emails_from_text(content)
                        
                        for email_info in emails:
                            if self.is_valid_healthcare_email(email_info['email']):
                                contact = {
                                    "hospital_name": hospital_name,
                                    "contact_name": email_info.get('name', contact_title),
                                    "contact_title": contact_title,
                                    "email": email_info['email'],
                                    "source_url": item.get('link', ''),
                                    "search_snippet": item.get('snippet', ''),
                                    "verified_via": "google_search"
                                }
                                contacts.append(contact)
                
                # Don't overwhelm the API
                await asyncio.sleep(0.1)
                
        except ImportError:
            print("❌ Google API client not installed: pip install google-api-python-client")
        except Exception as e:
            print(f"❌ Search error: {e}")
        
        return contacts
    
    def get_hospital_domain(self, hospital_name: str) -> str:
        """Try to determine hospital's website domain"""
        
        # Common hospital domain patterns
        domain_mappings = {
            "methodist": "houstonmethodist.org",
            "memorial hermann": "memorialhermann.org",
            "baylor": "bswhealth.com",
            "ut southwestern": "utsouthwestern.edu",
            "texas children": "texaschildrens.org",
            "christus": "christushealth.org",
            "adventhealth": "adventhealth.com",
            "mayo clinic": "mayoclinic.org",
            "cleveland clinic": "clevelandclinic.org"
        }
        
        hospital_lower = hospital_name.lower()
        for keyword, domain in domain_mappings.items():
            if keyword in hospital_lower:
                return domain
        
        # Generic healthcare domain guess
        return hospital_name.lower().replace(' ', '').replace('-', '') + ".org"
    
    def extract_emails_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract email addresses and associated names from text"""
        
        results = []
        
        # Enhanced email pattern to catch names
        patterns = [
            r'([A-Z][a-z]+ [A-Z][a-z]+)[\s,]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})[\s,]*([A-Z][a-z]+ [A-Z][a-z]+)',
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:
                        if '@' in match[0]:
                            email, name = match[0], match[1]
                        else:
                            name, email = match[0], match[1]
                    else:
                        email = match[0]
                        name = "Contact"
                else:
                    email = match
                    name = "Contact"
                
                if self.is_valid_healthcare_email(email):
                    results.append({
                        "name": name.strip(),
                        "email": email.lower().strip()
                    })
        
        return results
    
    def is_valid_healthcare_email(self, email: str) -> bool:
        """Check if email is from a valid healthcare domain"""
        
        if not email or "@" not in email:
            return False
        
        # Extract domain
        domain = email.split("@")[-1].lower()
        
        # Healthcare TLDs
        valid_tlds = [".org", ".edu", ".gov", ".com"]
        if not any(domain.endswith(tld) for tld in valid_tlds):
            return False
        
        # Exclude obviously fake domains
        fake_domains = [
            "example.com", "test.com", "fake.com", "gmail.com", 
            "yahoo.com", "hotmail.com", "email.com"
        ]
        
        if domain in fake_domains:
            return False
        
        # Must contain healthcare-related keywords
        healthcare_keywords = [
            "hospital", "health", "medical", "clinic", "center", 
            "care", "medicine", "university", "college", "edu"
        ]
        
        return any(keyword in domain for keyword in healthcare_keywords)
    
    async def enrich_prospect_with_search(self, prospect: Dict[str, Any]) -> Dict[str, Any]:
        """Use Google Search to find more information about a prospect"""
        
        hospital_name = prospect.get('organization_name', '')
        current_email = prospect.get('email', '')
        
        # If we already have a good email, verify it
        if current_email and self.is_valid_healthcare_email(current_email):
            return prospect
        
        # Otherwise, search for real contact
        print(f"🔍 Searching for real contact at {hospital_name}")
        
        contacts = await self.search_hospital_contact(hospital_name)
        
        if contacts:
            # Use the first valid contact found
            best_contact = contacts[0]
            
            # Update prospect with real contact info
            prospect.update({
                "contact_name": best_contact.get('contact_name', prospect.get('contact_name', '')),
                "email": best_contact['email'],
                "search_verified": True,
                "source_url": best_contact.get('source_url', ''),
                "verified": True
            })
            
            print(f"✅ Found real contact: {best_contact['email']}")
        else:
            print(f"⚠️ No verified contact found for {hospital_name}")
            prospect['search_verified'] = False
            prospect['verified'] = False
        
        return prospect

# Setup function for Google Search API
def setup_google_search_api():
    """Setup instructions for Google Custom Search API"""
    
    instructions = """
🔧 GOOGLE CUSTOM SEARCH API SETUP

1. Go to Google Cloud Console (https://console.cloud.google.com)
2. Enable Custom Search API
3. Create API Key:
   - APIs & Services > Credentials > Create Credentials > API Key
4. Create Custom Search Engine:
   - Go to https://cse.google.com/cse/
   - Add sites to search (or select "Search the entire web")
   - Get Search Engine ID

5. Create credentials file:
   Create: google_search_credentials.json
   {
     "api_key": "YOUR_API_KEY_HERE",
     "search_engine_id": "YOUR_SEARCH_ENGINE_ID_HERE"
   }

6. Or set environment variables:
   export GOOGLE_SEARCH_API_KEY="your_key"
   export GOOGLE_SEARCH_ENGINE_ID="your_id"
"""
    
    print(instructions)
    
    # Check if already configured
    import os
    if os.path.exists('google_search_credentials.json'):
        print("✅ google_search_credentials.json found")
    elif os.getenv('GOOGLE_SEARCH_API_KEY'):
        print("✅ Environment variables configured")
    else:
        print("⚠️ Google Search API not configured yet")

if __name__ == "__main__":
    setup_google_search_api()