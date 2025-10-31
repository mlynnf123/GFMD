#!/usr/bin/env python3
"""
Lead Deduplication System for GFMD
Prevents duplicate leads by tracking all previously generated prospects
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Set
import gspread
from google.oauth2.service_account import Credentials

class LeadDeduplicationSystem:
    """System to prevent duplicate leads"""
    
    def __init__(self, credentials_file: str = "google_sheets_credentials.json"):
        self.credentials_file = credentials_file
        self.local_cache_file = "generated_leads_cache.json"
        self.spreadsheet_name = "GFMD Swarm Agent Data"
        
        # Load existing leads cache
        self.existing_leads = self._load_existing_leads()
        
        # Organization name variations to detect duplicates
        self.organization_patterns = set()
        self._build_organization_patterns()
    
    def _load_existing_leads(self) -> Set[str]:
        """Load existing leads from local cache and Google Sheets"""
        existing = set()
        
        # Load from local cache first
        try:
            if os.path.exists(self.local_cache_file):
                with open(self.local_cache_file, 'r') as f:
                    cache_data = json.load(f)
                    existing.update(cache_data.get('lead_hashes', []))
                print(f"📊 Loaded {len(existing)} leads from local cache")
        except Exception as e:
            print(f"⚠️ Could not load local cache: {e}")
        
        # Load from Google Sheets
        try:
            gc = gspread.service_account(filename=self.credentials_file)
            spreadsheet = gc.open(self.spreadsheet_name)
            prospects_sheet = spreadsheet.worksheet("Prospects")
            
            # Get all existing prospects (skip header row)
            all_values = prospects_sheet.get_all_values()[1:]
            
            for row in all_values:
                if len(row) >= 5:  # Ensure we have enough columns
                    contact_name = row[1]  # Contact Name column
                    contact_email = row[2]  # Contact Email column  
                    company = row[4]       # Company column
                    
                    if contact_name and contact_email and company:
                        lead_hash = self._generate_lead_hash(contact_name, contact_email, company)
                        existing.add(lead_hash)
            
            print(f"📊 Found {len(all_values)} existing prospects in Google Sheets")
            
        except Exception as e:
            print(f"⚠️ Could not load from Google Sheets: {e}")
        
        return existing
    
    def _generate_lead_hash(self, contact_name: str, email: str, organization: str) -> str:
        """Generate unique hash for a lead"""
        # Normalize data
        normalized_name = contact_name.lower().strip()
        normalized_email = email.lower().strip()
        normalized_org = organization.lower().strip()
        
        # Create hash from combination
        combined = f"{normalized_name}|{normalized_email}|{normalized_org}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _build_organization_patterns(self):
        """Build patterns to detect similar organization names"""
        # Load existing organization names to build patterns
        for lead_hash in self.existing_leads:
            # This would need organization data, but we'll build it as we go
            pass
    
    def _normalize_organization_name(self, org_name: str) -> str:
        """Normalize organization name to detect variants"""
        normalized = org_name.lower().strip()
        
        # Remove common suffixes/prefixes that might vary
        replacements = [
            (" laboratory", " lab"),
            (" medical center", " medical"),
            (" hospital", " hosp"),
            (" regional", " reg"),
            (" community", " comm"),
            ("north ", "n "),
            ("south ", "s "),
            ("east ", "e "),
            ("west ", "w "),
            ("central ", "cent "),
        ]
        
        for old, new in replacements:
            normalized = normalized.replace(old, new)
        
        # Remove extra spaces
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def is_duplicate_lead(self, prospect: Dict[str, Any]) -> bool:
        """Check if prospect is a duplicate"""
        contact_name = prospect.get('contact_name', '')
        email = prospect.get('email', '')
        organization = prospect.get('organization_name', '')
        
        if not all([contact_name, email, organization]):
            return False
        
        # Generate hash for this prospect
        lead_hash = self._generate_lead_hash(contact_name, email, organization)
        
        # Check if hash exists
        if lead_hash in self.existing_leads:
            print(f"🔍 Duplicate detected: {contact_name} at {organization}")
            return True
        
        # Check for similar organization names (fuzzy matching)
        normalized_org = self._normalize_organization_name(organization)
        
        # For now, we'll use exact matching after normalization
        # Could be enhanced with fuzzy string matching libraries
        for existing_hash in self.existing_leads:
            # This would need more sophisticated comparison
            # For now, rely on the hash comparison above
            pass
        
        return False
    
    def add_lead(self, prospect: Dict[str, Any]):
        """Add a new lead to the tracking system"""
        contact_name = prospect.get('contact_name', '')
        email = prospect.get('email', '')
        organization = prospect.get('organization_name', '')
        
        if all([contact_name, email, organization]):
            lead_hash = self._generate_lead_hash(contact_name, email, organization)
            self.existing_leads.add(lead_hash)
            
            # Add normalized organization for pattern matching
            normalized_org = self._normalize_organization_name(organization)
            self.organization_patterns.add(normalized_org)
    
    def save_cache(self):
        """Save the current leads cache to file"""
        try:
            cache_data = {
                'last_updated': datetime.now().isoformat(),
                'lead_hashes': list(self.existing_leads),
                'organization_patterns': list(self.organization_patterns)
            }
            
            with open(self.local_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"💾 Saved {len(self.existing_leads)} leads to cache")
            
        except Exception as e:
            print(f"⚠️ Could not save cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get deduplication system statistics"""
        return {
            'total_tracked_leads': len(self.existing_leads),
            'organization_patterns': len(self.organization_patterns),
            'cache_file_exists': os.path.exists(self.local_cache_file),
            'last_cache_update': datetime.now().isoformat()
        }

def generate_unique_leads(num_leads: int, dedup_system: LeadDeduplicationSystem, max_attempts: int = 100):
    """Generate unique leads using the deduplication system"""
    from qualified_lead_generator import generate_qualified_lead
    
    unique_leads = []
    attempts = 0
    duplicates_found = 0
    date_suffix = datetime.now().strftime("%m%d")
    
    print(f"🎯 Generating {num_leads} unique leads (max {max_attempts} attempts)")
    print(f"📊 Currently tracking {len(dedup_system.existing_leads)} existing leads")
    
    while len(unique_leads) < num_leads and attempts < max_attempts:
        # Generate a candidate lead
        candidate = generate_qualified_lead(attempts, date_suffix)
        attempts += 1
        
        # Check if it's a duplicate
        if dedup_system.is_duplicate_lead(candidate):
            duplicates_found += 1
            print(f"⚠️ Skipping duplicate #{duplicates_found}: {candidate['contact_name']} at {candidate['organization_name']}")
            continue
        
        # Add to unique leads and tracking system
        unique_leads.append(candidate)
        dedup_system.add_lead(candidate)
        
        print(f"✅ Added unique lead #{len(unique_leads)}: {candidate['contact_name']} at {candidate['organization_name']}")
    
    # Save updated cache
    dedup_system.save_cache()
    
    print(f"\n📊 Lead Generation Summary:")
    print(f"✅ Unique leads generated: {len(unique_leads)}")
    print(f"⚠️ Duplicates avoided: {duplicates_found}")
    print(f"🔄 Total attempts: {attempts}")
    
    return unique_leads

if __name__ == "__main__":
    # Test the deduplication system
    print("🧪 Testing Lead Deduplication System")
    print("=" * 50)
    
    # Initialize deduplication system
    dedup = LeadDeduplicationSystem()
    
    # Show current stats
    stats = dedup.get_stats()
    print(f"📊 System Stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Generate some test leads
    print(f"\n🎯 Generating 5 test leads...")
    test_leads = generate_unique_leads(5, dedup)
    
    # Show results
    print(f"\n✅ Generated {len(test_leads)} unique leads:")
    for i, lead in enumerate(test_leads, 1):
        print(f"   {i}. {lead['contact_name']} at {lead['organization_name']}")