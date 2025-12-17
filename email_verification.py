#!/usr/bin/env python3
"""
Email Verification System - Ensures only real, verified emails are sent
"""
import re
import dns.resolver
from typing import Dict, Any, Tuple

class EmailVerificationSystem:
    """Verify emails before sending to ensure they're real law enforcement/government addresses"""
    
    def __init__(self):
        # Law enforcement and government domain patterns that are likely legitimate
        self.target_domains = {
            # Federal agencies
            'dea.gov', 'dhs.gov', 'fbi.gov', 'atf.gov', 'ice.gov', 'cbp.gov',
            'usss.gov', 'usms.gov', 'bop.gov', 'uscourts.gov',
            
            # Government domain patterns
            '.gov', '.mil', 'state.gov', 'local.gov', 'county.gov', 'city.gov',
            
            # Police and sheriff departments
            'police.gov', 'sheriff.gov', 'pd.gov', 'so.gov',
            'policedept.gov', 'sheriffsoffice.gov', 'lawenforcement.gov',
            
            # Common law enforcement patterns
            'police.org', 'sheriff.org', 'pd.org', 'so.org',
            'policedept.org', 'sheriffsoffice.org', 'lawenforcement.org',
            
            # State and local government
            '.state.gov', '.co.gov', '.ci.gov', '.city.gov',
            
            # Educational institutions with law enforcement programs
            '.edu'
        }
        
        # Patterns that suggest fake/placeholder emails
        self.fake_patterns = [
            r'example\.com$',
            r'test\.com$',
            r'sample\.com$',
            r'placeholder\.com$',
            r'fake\.com$',
            r'mail\d+@',  # mail1@, mail2@, etc.
            r'noreply@',
            r'donotreply@',
            r'temp@',
            r'temporary@'
        ]
        
        # Generic role-based emails (less preferred but sometimes valid)
        self.generic_roles = [
            'info@', 'admin@', 'webmaster@', 'contact@', 'support@'
        ]
    
    def verify_email(self, email: str, organization_name: str = "") -> Tuple[bool, str]:
        """
        Verify if an email is legitimate for law enforcement/government outreach
        Returns: (is_valid, reason)
        """
        if not email or not isinstance(email, str):
            return False, "Empty or invalid email format"
        
        email = email.strip().lower()
        
        # 1. Basic format check
        if not self._is_valid_email_format(email):
            return False, "Invalid email format"
        
        # 2. Check for fake patterns
        if self._is_fake_email(email):
            return False, "Appears to be fake/placeholder email"
        
        # 3. Check if domain is law enforcement/government-related
        domain = email.split('@')[1] if '@' in email else ""
        if not self._is_target_domain(domain, organization_name):
            return False, "Not a law enforcement or government domain"
        
        # 4. Check for generic role emails (warning but not blocking)
        if self._is_generic_role_email(email):
            return True, "Generic role email - proceed with caution"
        
        # 5. Domain exists check (basic DNS lookup)
        if not self._domain_exists(domain):
            return False, "Domain does not exist"
        
        return True, "Email appears legitimate"
    
    def _is_valid_email_format(self, email: str) -> bool:
        """Check basic email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_fake_email(self, email: str) -> bool:
        """Check if email matches fake/placeholder patterns"""
        for pattern in self.fake_patterns:
            if re.search(pattern, email):
                return True
        return False
    
    def _is_target_domain(self, domain: str, organization_name: str = "") -> bool:
        """Check if domain is law enforcement/government-related"""
        if not domain:
            return False
        
        # Check against known target domains
        for target_domain in self.target_domains:
            if domain == target_domain or domain.endswith(target_domain):
                return True
        
        # Check for law enforcement/government keywords in domain
        target_keywords = [
            'police', 'sheriff', 'law', 'enforcement', 'government', 'gov',
            'dept', 'department', 'city', 'county', 'state', 'federal',
            'pd', 'so', 'da', 'prosecutor', 'court', 'corrections',
            'detention', 'jail', 'prison', 'probation', 'parole',
            'security', 'public', 'safety', 'emergency', 'fire'
        ]
        
        for keyword in target_keywords:
            if keyword in domain:
                return True
        
        # If organization name is provided, check if domain relates to organization
        if organization_name:
            org_words = re.findall(r'\w+', organization_name.lower())
            domain_words = re.findall(r'\w+', domain)
            
            # Check if significant words from organization appear in domain
            matches = sum(1 for word in org_words if len(word) > 3 and word in domain_words)
            if matches >= 1:  # At least one significant word match
                return True
        
        return False
    
    def _is_generic_role_email(self, email: str) -> bool:
        """Check if email is a generic role email"""
        for role in self.generic_roles:
            if email.startswith(role):
                return True
        return False
    
    def _domain_exists(self, domain: str) -> bool:
        """Check if domain exists via DNS lookup"""
        try:
            dns.resolver.resolve(domain, 'MX')
            return True
        except:
            try:
                dns.resolver.resolve(domain, 'A')
                return True
            except:
                return False
    
    def verify_prospect_email(self, prospect: Dict[str, Any]) -> Tuple[bool, str]:
        """Verify a prospect's email with organization context"""
        email = prospect.get('email', '')
        organization = prospect.get('organization_name', '')
        
        return self.verify_email(email, organization)

# Global verification instance
email_verifier = EmailVerificationSystem()

def should_send_email(prospect: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Determine if we should send an email to this prospect
    Returns: (should_send, reason)
    """
    return email_verifier.verify_prospect_email(prospect)

if __name__ == "__main__":
    # Test the verification system
    verifier = EmailVerificationSystem()
    
    test_emails = [
        ("john.smith@police.gov", "City Police Department", True),
        ("fake@example.com", "Test Police Dept", False),
        ("mail2@testpd.com", "Test Police Dept", False),
        ("admin@sheriff.gov", "County Sheriff Office", True),
        ("officer.jones@citypolice.org", "City Police Department", True),
        ("noreply@police.com", "Some Police Dept", False),
        ("evidence@dea.gov", "DEA", True),
        ("manager@property.county.gov", "County Property & Evidence", True)
    ]
    
    print("🔍 Email Verification Tests")
    print("=" * 40)
    
    for email, org, expected in test_emails:
        valid, reason = verifier.verify_email(email, org)
        status = "✅" if valid == expected else "❌"
        print(f"{status} {email} - {reason}")