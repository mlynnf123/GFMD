#!/usr/bin/env python3
"""
Enhanced Contact Discovery System for GFMD AI Swarm
Combines Definitive Healthcare data with comprehensive internet discovery
Ensures 50 successful emails daily with real, verified contacts
"""

import asyncio
import json
import re
import csv
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
import time

from google_search_integration import GoogleSearchEmailFinder
from real_prospect_finder import RealProspectFinder
from email_verification_system import EmailVerificationSystem
from perplexity_contact_finder import PerplexityContactFinder

class HealthcareContactDiscovery:
    """Comprehensive healthcare contact discovery using multiple sources"""
    
    def __init__(self):
        self.definitive_finder = RealProspectFinder()
        self.google_search = GoogleSearchEmailFinder()
        self.perplexity_finder = PerplexityContactFinder()
        self.email_verifier = EmailVerificationSystem()
        
        # Healthcare organization search terms
        self.healthcare_search_terms = [
            "hospital laboratory director",
            "medical center lab manager", 
            "healthcare facility laboratory",
            "hospital equipment manager",
            "medical laboratory director contact",
            "hospital VP operations",
            "healthcare laboratory services director",
            "medical center clinical laboratory",
            "hospital pathology director",
            "medical laboratory coordinator"
        ]
        
        # Healthcare organization domains to target
        self.healthcare_domains = [
            ".org", ".edu", ".gov", 
            "hospital", "medical", "health", "clinic", "center"
        ]
        
        # Geographic targets for expansion
        self.target_regions = [
            "California hospital laboratory",
            "Texas medical center lab", 
            "Florida healthcare facility",
            "New York hospital laboratory",
            "Illinois medical center",
            "Pennsylvania healthcare",
            "Ohio hospital system",
            "Michigan medical facility",
            "North Carolina healthcare",
            "Georgia hospital laboratory"
        ]

    async def discover_contacts_comprehensive(self, target_count: int = 100) -> List[Dict[str, Any]]:
        """Discover contacts from all sources - 50% Definitive Healthcare, 50% web discovery"""
        
        print(f"🔍 COMPREHENSIVE CONTACT DISCOVERY")
        print(f"🎯 Target: {target_count} verified healthcare contacts")
        print("=" * 60)
        
        # Split target: 50% Definitive Healthcare, 50% web discovery
        definitive_target = target_count // 2
        web_discovery_target = target_count - definitive_target
        
        all_contacts = []
        
        # 1. Load from Definitive Healthcare (verified, high-quality)
        print(f"📂 Loading {definitive_target} contacts from Definitive Healthcare...")
        definitive_contacts = self.get_definitive_healthcare_contacts(definitive_target)
        all_contacts.extend(definitive_contacts)
        print(f"✅ Loaded {len(definitive_contacts)} verified Definitive Healthcare contacts")
        
        # 2. Discover from web sources (fresh, expanded reach) - Use Perplexity + Google Search
        print(f"🌐 Discovering {web_discovery_target} contacts via web search...")
        web_contacts = await self.discover_web_contacts_hybrid(web_discovery_target)
        all_contacts.extend(web_contacts)
        print(f"✅ Discovered {len(web_contacts)} new web-sourced contacts")
        
        # 3. Deduplicate and verify emails (especially for web-sourced contacts)
        print("🔄 Deduplicating and verifying contacts...")
        print("📧 Verifying email addresses for production readiness...")
        verified_contacts = await self.deduplicate_and_verify_emails(all_contacts)
        
        print(f"\n📊 DISCOVERY SUMMARY:")
        print(f"   📂 Definitive Healthcare: {len(definitive_contacts)} contacts")
        print(f"   🌐 Web Discovery: {len(web_contacts)} contacts") 
        print(f"   ✅ Final Verified: {len(verified_contacts)} unique contacts")
        print(f"   🎯 Success Rate: {len(verified_contacts)}/{target_count} ({len(verified_contacts)/target_count*100:.1f}%)")
        
        return verified_contacts

    def get_definitive_healthcare_contacts(self, count: int) -> List[Dict[str, Any]]:
        """Get contacts from Definitive Healthcare database"""
        
        try:
            all_contacts = self.definitive_finder.load_definitive_healthcare_data("definitive_healthcare_data.csv")
            
            # Prioritize by title relevance
            prioritized = self.prioritize_by_title(all_contacts)
            
            # Return top contacts with source tag
            selected = prioritized[:count]
            for contact in selected:
                contact['source'] = 'definitive_healthcare'
                contact['verified'] = True
                contact['priority_score'] = self.calculate_priority_score(contact)
            
            return selected
            
        except Exception as e:
            print(f"❌ Error loading Definitive Healthcare data: {e}")
            return []

    async def discover_web_contacts_hybrid(self, count: int) -> List[Dict[str, Any]]:
        """Discover new contacts via Perplexity API + Google Search hybrid approach"""
        
        web_contacts = []
        
        # Split between Perplexity (70%) and Google Search (30%) for diversity
        perplexity_target = int(count * 0.7)
        google_target = count - perplexity_target
        
        print(f"  🔮 Using Perplexity API for {perplexity_target} contacts...")
        print(f"  🔍 Using Google Search for {google_target} contacts...")
        
        # 1. Use Perplexity API for high-quality contact discovery
        perplexity_contacts = await self.discover_via_perplexity(perplexity_target)
        web_contacts.extend(perplexity_contacts)
        print(f"  ✅ Perplexity found {len(perplexity_contacts)} real contacts")
        
        # 2. Use Google Search as supplementary (only if configured and not returning fake data)
        if google_target > 0 and len(web_contacts) < count:
            remaining_needed = count - len(web_contacts)
            google_contacts = await self.discover_via_google_search(min(google_target, remaining_needed))
            web_contacts.extend(google_contacts)
            print(f"  ✅ Google Search added {len(google_contacts)} contacts")
        
        return web_contacts[:count]

    async def discover_via_perplexity(self, count: int) -> List[Dict[str, Any]]:
        """Use Perplexity API to discover real healthcare contacts"""
        
        perplexity_contacts = []
        
        # Use regional searches for better hospital coverage
        regions = ["California", "Texas", "Florida", "New York", "Illinois"]
        contacts_per_region = max(1, count // len(regions))
        
        for region in regions:
            if len(perplexity_contacts) >= count:
                break
                
            print(f"    🌎 Perplexity searching {region} hospitals...")
            
            try:
                # Check API usage before making requests
                usage = self.perplexity_finder.get_usage_stats()
                if usage['remaining'] <= 0:
                    print(f"    ⚠️ Perplexity daily limit reached ({usage['requests_today']}/{usage['daily_limit']})")
                    break
                
                # Find regional contacts via Perplexity
                regional_contacts = self.perplexity_finder.find_regional_contacts(
                    region=region, 
                    facility_type="hospital", 
                    count=contacts_per_region
                )
                
                for contact in regional_contacts:
                    contact['source'] = 'perplexity_api'
                    contact['discovery_method'] = 'perplexity_regional_search'
                    contact['priority_score'] = self.calculate_priority_score(contact)
                
                perplexity_contacts.extend(regional_contacts)
                print(f"    ✅ Found {len(regional_contacts)} verified contacts in {region}")
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"    ❌ Perplexity error for {region}: {e}")
                continue
        
        return perplexity_contacts[:count]
    
    async def discover_via_google_search(self, count: int) -> List[Dict[str, Any]]:
        """Use Google Search for supplementary contact discovery (with fake data prevention)"""
        
        google_contacts = []
        
        # Only use Google Search if API is properly configured
        if not hasattr(self.google_search, 'api_key') or not self.google_search.api_key:
            print(f"    ⚠️ Google Search API not configured - skipping Google discovery")
            return []
        
        # Use a few targeted healthcare search terms
        healthcare_terms = [
            "laboratory director hospital",
            "medical center lab manager", 
            "healthcare facility laboratory director"
        ]
        
        contacts_per_term = max(1, count // len(healthcare_terms))
        
        for search_term in healthcare_terms:
            if len(google_contacts) >= count:
                break
                
            print(f"    🔍 Google searching: {search_term}")
            
            try:
                search_results = await self.search_healthcare_professionals_verified(search_term, contacts_per_term)
                
                # Filter out any fake/mock data
                real_contacts = self.filter_fake_contacts(search_results)
                
                for contact in real_contacts:
                    contact['source'] = 'google_search'
                    contact['discovery_method'] = 'google_custom_search_verified'
                    contact['priority_score'] = self.calculate_priority_score(contact)
                
                google_contacts.extend(real_contacts)
                print(f"    ✅ Google found {len(real_contacts)} verified contacts")
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"    ❌ Google Search error for '{search_term}': {e}")
                continue
        
        return google_contacts[:count]
    
    def filter_fake_contacts(self, contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out fake/mock contacts that might be generated by search"""
        
        real_contacts = []
        
        for contact in contacts:
            email = contact.get('email', '')
            name = contact.get('contact_name', '')
            
            # Skip contacts with fake/generic patterns
            fake_patterns = [
                # Generic search terms as names
                'laboratory director', 'lab director', 'medical center',
                'hospital laboratory', 'healthcare facility',
                # Test/example emails
                'example.com', 'test.com', 'sample.com',
                # Generic names that are just search terms
                'director', 'manager', 'coordinator'
            ]
            
            is_fake = False
            for pattern in fake_patterns:
                if pattern.lower() in name.lower() or pattern.lower() in email.lower():
                    is_fake = True
                    break
            
            # Only include if it looks like a real person with real email
            if not is_fake and '@' in email and len(name.split()) >= 2:
                real_contacts.append(contact)
            else:
                print(f"    🚫 Filtered fake contact: {name} ({email})")
        
        return real_contacts

    async def search_healthcare_professionals_verified(self, search_term: str, target_count: int) -> List[Dict[str, Any]]:
        """Enhanced Google search that verifies contact authenticity"""
        
        contacts = []
        
        try:
            # Use the existing Google Custom Search but with enhanced verification
            search_results = await self.google_search.search_hospital_contact(
                hospital_name=search_term.replace(" contact", ""),
                contact_title="Laboratory Director"
            )
            
            for result in search_results:
                if len(contacts) >= target_count:
                    break
                    
                contact = {
                    'organization_name': result.get('hospital_name', 'Healthcare Facility'),
                    'contact_name': result.get('contact_name', 'Laboratory Director'),
                    'contact_title': result.get('contact_title', 'Laboratory Director'),
                    'email': result.get('email', ''),
                    'location': self.extract_location_from_search(result),
                    'facility_type': 'Healthcare Facility',
                    'pain_point': 'Laboratory noise affecting patient recovery and staff productivity',
                    'department': 'Clinical Laboratory',
                    'source_url': result.get('source_url', ''),
                    'discovery_method': 'google_custom_search'
                }
                
                # Only add if email looks legitimate
                if self.verify_healthcare_email(contact['email']):
                    contacts.append(contact)
            
        except Exception as e:
            print(f"    ❌ Google Search error: {e}")
        
        return contacts

    async def search_healthcare_professionals(self, search_term: str, target_count: int) -> List[Dict[str, Any]]:
        
        if not self.google_search.api_key:
            print("  ⚠️ Google Search API not configured, using alternative discovery")
            return await self.alternative_contact_discovery(search_term, target_count)
        
        try:
            # Use Google Custom Search to find healthcare professionals
            search_results = await self.google_search.search_hospital_contact(
                hospital_name=search_term.replace(" contact", ""),
                contact_title="Laboratory Director"
            )
            
            for result in search_results:
                if len(contacts) >= target_count:
                    break
                    
                contact = {
                    'organization_name': result.get('hospital_name', 'Healthcare Facility'),
                    'contact_name': result.get('contact_name', 'Laboratory Director'),
                    'contact_title': result.get('contact_title', 'Laboratory Director'),
                    'email': result.get('email', ''),
                    'location': self.extract_location_from_search(result),
                    'facility_type': 'Healthcare Facility',
                    'pain_point': 'Laboratory noise affecting patient recovery and staff productivity',
                    'department': 'Clinical Laboratory',
                    'source_url': result.get('source_url', ''),
                    'discovery_method': 'google_custom_search'
                }
                
                if self.verify_healthcare_email(contact['email']):
                    contacts.append(contact)
            
        except Exception as e:
            print(f"  ❌ Google Search error: {e}")
        
        return contacts

    async def alternative_contact_discovery(self, search_term: str, target_count: int) -> List[Dict[str, Any]]:
        """Alternative contact discovery when Google Search API is unavailable"""
        
        contacts = []
        
        # Use healthcare directory APIs and web scraping as alternatives
        healthcare_directories = [
            "https://www.aha.org/directory",  # American Hospital Association
            "https://www.healthleadersmedia.com",  # Health Leaders Directory
            "https://www.beckershospitalreview.com"  # Becker's Hospital Review
        ]
        
        # For now, create template for real implementation
        # This would integrate with actual healthcare directories
        print(f"  🔄 Alternative discovery for: {search_term}")
        
        # Placeholder for real directory integration
        # Would implement actual API calls to healthcare directories
        
        return contacts

    async def search_by_geographic_regions(self, target_count: int) -> List[Dict[str, Any]]:
        """Search for contacts by geographic regions"""
        
        contacts = []
        contacts_per_region = max(1, target_count // len(self.target_regions))
        
        for region_term in self.target_regions:
            if len(contacts) >= target_count:
                break
                
            print(f"  🌎 Geographic search: {region_term}")
            
            try:
                region_contacts = await self.search_healthcare_professionals(region_term, contacts_per_region)
                contacts.extend(region_contacts)
                await asyncio.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"  ⚠️ Geographic search error: {e}")
                continue
        
        return contacts[:target_count]

    def prioritize_by_title(self, contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize contacts by title relevance"""
        
        # High-priority titles for laboratory equipment sales
        high_priority_titles = [
            'laboratory director', 'lab director', 'director of laboratory',
            'laboratory manager', 'lab manager', 'clinical laboratory director',
            'pathology director', 'laboratory services director'
        ]
        
        medium_priority_titles = [
            'equipment manager', 'facilities manager', 'operations manager',
            'vp operations', 'director operations', 'clinical director'
        ]
        
        def get_title_priority(contact):
            title = contact.get('contact_title', '').lower()
            
            for high_title in high_priority_titles:
                if high_title in title:
                    return 3  # High priority
                    
            for med_title in medium_priority_titles:
                if med_title in title:
                    return 2  # Medium priority
                    
            return 1  # Low priority
        
        return sorted(contacts, key=get_title_priority, reverse=True)

    def verify_healthcare_email(self, email: str) -> bool:
        """Verify email is from legitimate healthcare domain"""
        
        if not email or '@' not in email:
            return False
        
        domain = email.split('@')[1].lower()
        
        # Healthcare domain indicators
        healthcare_indicators = [
            'hospital', 'medical', 'health', 'clinic', 'center',
            'mercy', 'baptist', 'methodist', 'presbyterian', 'catholic',
            'university', 'regional', 'community', 'memorial'
        ]
        
        # Valid TLDs for healthcare
        valid_tlds = ['.org', '.edu', '.gov', '.com']
        
        # Must have valid TLD
        if not any(domain.endswith(tld) for tld in valid_tlds):
            return False
        
        # Must have healthcare indicator OR be .edu/.gov
        if domain.endswith('.edu') or domain.endswith('.gov'):
            return True
            
        return any(indicator in domain for indicator in healthcare_indicators)

    def calculate_priority_score(self, contact: Dict[str, Any]) -> float:
        """Calculate priority score for contact"""
        
        score = 0.0
        
        # Title relevance (40 points max)
        title = contact.get('contact_title', '').lower()
        if 'director' in title and 'lab' in title:
            score += 40
        elif 'director' in title:
            score += 30
        elif 'manager' in title:
            score += 25
        else:
            score += 10
        
        # Email verification (30 points max)
        if contact.get('verified', False):
            score += 30
        elif self.verify_healthcare_email(contact.get('email', '')):
            score += 20
        
        # Source reliability (20 points max)
        if contact.get('source') == 'definitive_healthcare':
            score += 20
        elif contact.get('source') == 'web_discovery':
            score += 15
        
        # Organization type (10 points max)
        org_name = contact.get('organization_name', '').lower()
        if 'medical center' in org_name or 'hospital' in org_name:
            score += 10
        elif 'clinic' in org_name:
            score += 7
        
        return score

    async def deduplicate_and_verify_emails(self, contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates and verify email deliverability - PRODUCTION READY"""
        
        seen_emails = set()
        seen_orgs = set()
        verified_contacts = []
        verification_failures = 0
        
        # Sort by priority score first
        sorted_contacts = sorted(contacts, key=lambda x: x.get('priority_score', 0), reverse=True)
        
        print(f"📧 Verifying {len(sorted_contacts)} contacts for email deliverability...")
        
        for i, contact in enumerate(sorted_contacts):
            email = contact.get('email', '').lower().strip()
            org_key = f"{contact.get('organization_name', '')}.{contact.get('contact_name', '')}".lower()
            
            # Skip if duplicate email or organization+name combination
            if email in seen_emails or org_key in seen_orgs:
                continue
            
            if not email:
                verification_failures += 1
                continue
            
            # For Definitive Healthcare contacts, trust the verification but still log
            if contact.get('source') == 'definitive_healthcare':
                contact['email_verified'] = True
                contact['verification_confidence'] = 95  # High confidence for known good source
                contact['verification_method'] = 'definitive_healthcare_trusted'
                seen_emails.add(email)
                seen_orgs.add(org_key)
                verified_contacts.append(contact)
                continue
            
            # For web-sourced contacts, perform comprehensive verification
            print(f"  [{i+1}/{len(sorted_contacts)}] Verifying: {contact.get('organization_name', 'Unknown')}")
            
            verification_result = await self.email_verifier.verify_email_comprehensive(email, contact)
            
            if verification_result.get('valid', False) and verification_result.get('confidence', 0) >= 75:
                # Add verification metadata
                contact['email_verified'] = True
                contact['verification_confidence'] = verification_result['confidence']
                contact['verification_timestamp'] = verification_result['timestamp']
                contact['verification_method'] = 'comprehensive_verification'
                contact['verification_checks'] = verification_result['checks']
                
                seen_emails.add(email)
                seen_orgs.add(org_key)
                verified_contacts.append(contact)
                print(f"    ✅ Verified ({verification_result['confidence']}% confidence)")
            else:
                verification_failures += 1
                print(f"    ❌ Failed: {verification_result.get('reason', 'Unknown')}")
        
        print(f"📧 Email verification complete:")
        print(f"   ✅ Verified contacts: {len(verified_contacts)}")
        print(f"   ❌ Verification failures: {verification_failures}")
        print(f"   📈 Success rate: {len(verified_contacts)/(len(verified_contacts)+verification_failures)*100:.1f}%")
        
        return verified_contacts

    def extract_location_from_search(self, search_result: Dict[str, Any]) -> str:
        """Extract location from search result"""
        
        # Try to extract location from various fields
        snippet = search_result.get('search_snippet', '')
        url = search_result.get('source_url', '')
        
        # Simple location extraction (would be enhanced with NLP)
        location_patterns = [
            r'([A-Z][a-z]+,?\s+[A-Z]{2})',  # City, ST
            r'([A-Z][a-z]+\s+[A-Z][a-z]+,?\s+[A-Z]{2})'  # City Name, ST
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, snippet)
            if match:
                return match.group(1)
        
        return "Location TBD"


class SuccessTrackedEmailSystem:
    """Enhanced email system that ensures 50 successful emails daily"""
    
    def __init__(self):
        self.success_threshold = 50
        self.daily_success_log = "daily_success_log.json"
        self.contact_discovery = HealthcareContactDiscovery()
        
    async def ensure_daily_success(self, target_date: str = None) -> Dict[str, Any]:
        """Ensure 50 successful emails are sent, monitoring success in real-time"""
        
        if not target_date:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"🎯 ENSURING 50 SUCCESSFUL EMAILS FOR {target_date}")
        print("=" * 60)
        
        # Check current success count for today
        current_success = self.get_daily_success_count(target_date)
        remaining_needed = max(0, self.success_threshold - current_success)
        
        print(f"📊 Current success: {current_success}/50")
        print(f"🎯 Remaining needed: {remaining_needed}")
        
        if remaining_needed == 0:
            print("✅ Daily target already achieved!")
            return {"success": True, "emails_sent": 0, "total_success": current_success}
        
        # Discover more contacts than needed to account for failures
        buffer_multiplier = 1.5  # Get 50% more contacts to ensure success
        contacts_to_discover = int(remaining_needed * buffer_multiplier)
        
        print(f"🔍 Discovering {contacts_to_discover} contacts (with buffer)...")
        contacts = await self.contact_discovery.discover_contacts_comprehensive(contacts_to_discover)
        
        if len(contacts) < remaining_needed:
            print(f"⚠️ Warning: Only found {len(contacts)} contacts, need {remaining_needed}")
        
        # Process contacts until we achieve 50 successful emails
        results = await self.process_contacts_until_success(contacts, remaining_needed, target_date)
        
        return results

    def get_daily_success_count(self, date: str) -> int:
        """Get current successful email count for the date"""
        
        try:
            with open(self.daily_success_log, 'r') as f:
                log_data = json.load(f)
            return log_data.get(date, {}).get('successful_emails', 0)
        except FileNotFoundError:
            return 0

    def record_email_success(self, date: str, email_result: Dict[str, Any]):
        """Record email success/failure"""
        
        try:
            with open(self.daily_success_log, 'r') as f:
                log_data = json.load(f)
        except FileNotFoundError:
            log_data = {}
        
        if date not in log_data:
            log_data[date] = {'successful_emails': 0, 'failed_emails': 0, 'attempts': []}
        
        log_data[date]['attempts'].append({
            'timestamp': datetime.now().isoformat(),
            'contact': email_result.get('contact_name', ''),
            'organization': email_result.get('organization', ''),
            'email': email_result.get('email', ''),
            'success': email_result.get('success', False),
            'error': email_result.get('error', '')
        })
        
        if email_result.get('success', False):
            log_data[date]['successful_emails'] += 1
        else:
            log_data[date]['failed_emails'] += 1
        
        with open(self.daily_success_log, 'w') as f:
            json.dump(log_data, f, indent=2)

    async def process_contacts_until_success(self, contacts: List[Dict[str, Any]], 
                                           target_success: int, date: str) -> Dict[str, Any]:
        """Process contacts until target success is achieved"""
        
        from production_rag_a2a_system import ProductionGFMDSystem
        
        successful_emails = 0
        failed_emails = 0
        processed_contacts = []
        
        # Initialize the production system for processing
        system = ProductionGFMDSystem()
        
        print(f"📧 Processing contacts to achieve {target_success} successful emails...")
        
        for i, contact in enumerate(contacts):
            if successful_emails >= target_success:
                print(f"✅ Target achieved! {successful_emails} successful emails sent")
                break
            
            print(f"[{i+1}/{len(contacts)}] Processing: {contact.get('organization_name', 'Unknown')}")
            
            try:
                # Process single contact through the AI system
                result = await system.coordinator._process_single_prospect(contact)
                
                # Attempt to send email
                if result.get('email') and contact.get('verified', False):
                    email_result = await system._send_email(contact, result['email'], {})
                    
                    if email_result and email_result.get('success', False):
                        successful_emails += 1
                        print(f"  ✅ Email sent successfully ({successful_emails}/{target_success})")
                        
                        # Record success
                        self.record_email_success(date, {
                            'success': True,
                            'contact_name': contact.get('contact_name', ''),
                            'organization': contact.get('organization_name', ''),
                            'email': contact.get('email', '')
                        })
                    else:
                        failed_emails += 1
                        print(f"  ❌ Email failed to send")
                        
                        self.record_email_success(date, {
                            'success': False,
                            'contact_name': contact.get('contact_name', ''),
                            'organization': contact.get('organization_name', ''),
                            'email': contact.get('email', ''),
                            'error': 'Send failure'
                        })
                else:
                    failed_emails += 1
                    print(f"  ⚠️ Contact not ready for email")
                    
                processed_contacts.append(result)
                
            except Exception as e:
                failed_emails += 1
                print(f"  ❌ Processing error: {e}")
                
                self.record_email_success(date, {
                    'success': False,
                    'contact_name': contact.get('contact_name', ''),
                    'organization': contact.get('organization_name', ''),
                    'email': contact.get('email', ''),
                    'error': str(e)
                })
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"   ✅ Successful emails: {successful_emails}")
        print(f"   ❌ Failed emails: {failed_emails}")
        print(f"   📋 Total processed: {len(processed_contacts)}")
        print(f"   🎯 Success rate: {successful_emails/(successful_emails+failed_emails)*100:.1f}%")
        
        return {
            "success": successful_emails >= target_success,
            "successful_emails": successful_emails,
            "failed_emails": failed_emails,
            "total_processed": len(processed_contacts),
            "target_achieved": successful_emails >= target_success
        }


# Integration function for the main production system
async def run_enhanced_daily_automation(num_prospects: int = 50) -> Dict[str, Any]:
    """Run enhanced daily automation with comprehensive contact discovery"""
    
    success_system = SuccessTrackedEmailSystem()
    
    # Ensure 50 successful emails using enhanced contact discovery
    results = await success_system.ensure_daily_success()
    
    return {
        "mode": "enhanced_contact_discovery",
        "prospects_processed": results.get("total_processed", 0),
        "emails_sent": results.get("successful_emails", 0),
        "success_rate": f"{results.get('successful_emails', 0)}/50",
        "target_achieved": results.get("target_achieved", False),
        "discovery_sources": ["definitive_healthcare", "web_discovery"],
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Test the enhanced system
    async def test_enhanced_discovery():
        print("🧪 Testing Enhanced Contact Discovery System")
        
        discovery = HealthcareContactDiscovery()
        contacts = await discovery.discover_contacts_comprehensive(20)
        
        print(f"\n✅ Test complete: {len(contacts)} contacts discovered")
        
        for i, contact in enumerate(contacts[:5], 1):
            print(f"{i}. {contact.get('contact_name', 'Unknown')} at {contact.get('organization_name', 'Unknown')}")
            print(f"   Email: {contact.get('email', 'N/A')}")
            print(f"   Source: {contact.get('source', 'N/A')}")
            print(f"   Priority: {contact.get('priority_score', 0):.1f}")
    
    asyncio.run(test_enhanced_discovery())