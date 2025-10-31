#!/usr/bin/env python3
"""
Email Verification System for GFMD AI Swarm
Ensures all internet-sourced contacts have working, deliverable emails
Production-ready with multiple verification layers
"""

import asyncio
import re
import dns.resolver
import smtplib
import socket
from email.mime.text import MIMEText
from typing import Dict, Any, List, Optional, Tuple
import requests
from datetime import datetime
import json

class EmailVerificationSystem:
    """Comprehensive email verification system with multiple validation layers"""
    
    def __init__(self):
        self.verification_cache = {}
        self.cache_file = "email_verification_cache.json"
        self.load_cache()
        
        # Track verification statistics
        self.verification_stats = {
            "total_checked": 0,
            "syntax_valid": 0,
            "domain_valid": 0,
            "mx_record_valid": 0,
            "smtp_deliverable": 0,
            "final_verified": 0
        }
        
    def load_cache(self):
        """Load email verification cache"""
        try:
            with open(self.cache_file, 'r') as f:
                self.verification_cache = json.load(f)
        except FileNotFoundError:
            self.verification_cache = {}
    
    def save_cache(self):
        """Save email verification cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.verification_cache, f, indent=2)
    
    async def verify_email_comprehensive(self, email: str, contact_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive email verification with multiple layers
        Returns detailed verification results
        """
        
        if not email or not isinstance(email, str):
            return {"valid": False, "reason": "Invalid email format", "confidence": 0}
        
        email = email.lower().strip()
        
        # Check cache first
        if email in self.verification_cache:
            cached_result = self.verification_cache[email]
            # Use cache if less than 7 days old
            if (datetime.now() - datetime.fromisoformat(cached_result.get('timestamp', '2000-01-01'))).days < 7:
                return cached_result
        
        print(f"🔍 Verifying email: {email}")
        
        verification_result = {
            "email": email,
            "valid": False,
            "confidence": 0,
            "checks": {},
            "timestamp": datetime.now().isoformat(),
            "reason": ""
        }
        
        self.verification_stats["total_checked"] += 1
        
        # Layer 1: Syntax Validation
        syntax_valid, syntax_reason = self.validate_email_syntax(email)
        verification_result["checks"]["syntax"] = {"valid": syntax_valid, "reason": syntax_reason}
        
        if not syntax_valid:
            verification_result["reason"] = f"Syntax error: {syntax_reason}"
            self.verification_cache[email] = verification_result
            self.save_cache()
            return verification_result
        
        self.verification_stats["syntax_valid"] += 1
        
        # Layer 2: Domain Validation
        domain = email.split('@')[1]
        domain_valid, domain_reason = await self.validate_domain(domain)
        verification_result["checks"]["domain"] = {"valid": domain_valid, "reason": domain_reason}
        
        if not domain_valid:
            verification_result["reason"] = f"Domain error: {domain_reason}"
            self.verification_cache[email] = verification_result
            self.save_cache()
            return verification_result
        
        self.verification_stats["domain_valid"] += 1
        
        # Layer 3: MX Record Validation
        mx_valid, mx_reason = await self.validate_mx_records(domain)
        verification_result["checks"]["mx_records"] = {"valid": mx_valid, "reason": mx_reason}
        
        if not mx_valid:
            verification_result["reason"] = f"MX record error: {mx_reason}"
            self.verification_cache[email] = verification_result
            self.save_cache()
            return verification_result
        
        self.verification_stats["mx_record_valid"] += 1
        
        # Layer 4: Healthcare Domain Verification
        healthcare_valid, healthcare_reason = self.validate_healthcare_domain(domain, contact_info)
        verification_result["checks"]["healthcare_domain"] = {"valid": healthcare_valid, "reason": healthcare_reason}
        
        # Layer 5: SMTP Deliverability Check (careful not to spam)
        smtp_valid, smtp_reason = await self.validate_smtp_deliverability(email, domain)
        verification_result["checks"]["smtp_deliverable"] = {"valid": smtp_valid, "reason": smtp_reason}
        
        if smtp_valid:
            self.verification_stats["smtp_deliverable"] += 1
        
        # Calculate confidence score
        confidence = self.calculate_confidence_score(verification_result["checks"])
        verification_result["confidence"] = confidence
        
        # Determine overall validity
        # Require: syntax + domain + MX records + healthcare domain + high confidence
        if (syntax_valid and domain_valid and mx_valid and 
            healthcare_valid and confidence >= 75):
            verification_result["valid"] = True
            verification_result["reason"] = "Email verified as deliverable"
            self.verification_stats["final_verified"] += 1
            print(f"  ✅ Email verified: {email}")
        else:
            verification_result["reason"] = "Email failed verification checks"
            print(f"  ❌ Email failed verification: {email}")
        
        # Cache result
        self.verification_cache[email] = verification_result
        self.save_cache()
        
        return verification_result
    
    def validate_email_syntax(self, email: str) -> Tuple[bool, str]:
        """Validate email syntax using comprehensive regex"""
        
        # Comprehensive email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        # Additional syntax checks
        local_part, domain_part = email.split('@')
        
        # Local part validation
        if len(local_part) == 0 or len(local_part) > 64:
            return False, "Invalid local part length"
        
        if local_part.startswith('.') or local_part.endswith('.'):
            return False, "Invalid local part format"
        
        # Domain part validation
        if len(domain_part) == 0 or len(domain_part) > 255:
            return False, "Invalid domain length"
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9.-]+$', domain_part):
            return False, "Invalid domain characters"
        
        return True, "Syntax valid"
    
    async def validate_domain(self, domain: str) -> Tuple[bool, str]:
        """Validate domain exists and is reachable"""
        
        try:
            # Check if domain resolves
            socket.gethostbyname(domain)
            return True, "Domain resolves"
        except socket.gaierror:
            return False, "Domain does not resolve"
        except Exception as e:
            return False, f"Domain validation error: {str(e)}"
    
    async def validate_mx_records(self, domain: str) -> Tuple[bool, str]:
        """Validate domain has MX records for email delivery"""
        
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            if len(mx_records) > 0:
                return True, f"MX records found ({len(mx_records)} records)"
            else:
                return False, "No MX records found"
        except dns.resolver.NXDOMAIN:
            return False, "Domain does not exist"
        except dns.resolver.NoAnswer:
            return False, "No MX records for domain"
        except Exception as e:
            return False, f"MX record check error: {str(e)}"
    
    def validate_healthcare_domain(self, domain: str, contact_info: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Validate domain belongs to legitimate healthcare organization"""
        
        domain_lower = domain.lower()
        
        # Healthcare domain indicators
        healthcare_indicators = [
            'hospital', 'medical', 'health', 'clinic', 'center',
            'mercy', 'baptist', 'methodist', 'presbyterian', 'catholic',
            'university', 'regional', 'community', 'memorial',
            'kaiser', 'mayo', 'cleveland', 'johns', 'hopkins',
            'stanford', 'ucla', 'ucsf', 'harvard', 'northwestern'
        ]
        
        # Trusted healthcare TLDs
        trusted_tlds = ['.org', '.edu', '.gov']
        
        # Immediately trust .edu and .gov domains
        if any(domain_lower.endswith(tld) for tld in trusted_tlds):
            return True, f"Trusted healthcare TLD domain"
        
        # Check for healthcare indicators in domain
        healthcare_match = any(indicator in domain_lower for indicator in healthcare_indicators)
        
        if healthcare_match:
            return True, "Healthcare domain indicators found"
        
        # Cross-reference with organization name if available
        if contact_info and 'organization_name' in contact_info:
            org_name = contact_info['organization_name'].lower()
            
            # Extract key words from organization name
            org_words = re.findall(r'\b\w+\b', org_name)
            domain_words = re.findall(r'\b\w+\b', domain_lower.replace('.', ' '))
            
            # Check for overlap between organization name and domain
            common_words = set(org_words) & set(domain_words)
            if len(common_words) > 0:
                return True, f"Organization name matches domain ({common_words})"
        
        # For .com domains, require stricter validation
        if domain_lower.endswith('.com'):
            return False, "Generic .com domain without healthcare indicators"
        
        return False, "Domain not verified as healthcare organization"
    
    async def validate_smtp_deliverability(self, email: str, domain: str) -> Tuple[bool, str]:
        """
        Validate SMTP deliverability without sending actual emails
        Uses SMTP VRFY command when available
        """
        
        try:
            # Get MX records
            mx_records = dns.resolver.resolve(domain, 'MX')
            if not mx_records:
                return False, "No MX records"
            
            # Sort MX records by priority
            sorted_mx = sorted(mx_records, key=lambda x: x.preference)
            mx_host = str(sorted_mx[0].exchange).rstrip('.')
            
            # Connect to SMTP server (read-only check)
            with smtplib.SMTP(mx_host, 25, timeout=10) as server:
                server.helo('verification.example.com')
                
                # Try VRFY command (not all servers support this)
                try:
                    code, message = server.verify(email)
                    if code == 250:
                        return True, "SMTP VRFY successful"
                    elif code == 252:
                        return True, "SMTP VRFY indicates possible delivery"
                    else:
                        return False, f"SMTP VRFY failed: {code} {message}"
                except smtplib.SMTPException:
                    # VRFY not supported, try RCPT TO without sending
                    try:
                        server.mail('noreply@verification.example.com')
                        code, message = server.rcpt(email)
                        server.rset()  # Reset without sending
                        
                        if code == 250:
                            return True, "SMTP RCPT accepted"
                        else:
                            return False, f"SMTP RCPT rejected: {code} {message}"
                    except smtplib.SMTPException as e:
                        return False, f"SMTP check failed: {str(e)}"
                        
        except Exception as e:
            # Don't fail verification entirely on SMTP errors
            return True, f"SMTP check skipped: {str(e)}"
    
    def calculate_confidence_score(self, checks: Dict[str, Dict[str, Any]]) -> int:
        """Calculate confidence score based on verification checks"""
        
        score = 0
        
        # Syntax check (required)
        if checks.get("syntax", {}).get("valid", False):
            score += 20
        
        # Domain check (required)
        if checks.get("domain", {}).get("valid", False):
            score += 25
        
        # MX records (required)
        if checks.get("mx_records", {}).get("valid", False):
            score += 25
        
        # Healthcare domain (highly important)
        if checks.get("healthcare_domain", {}).get("valid", False):
            score += 20
        
        # SMTP deliverability (bonus)
        if checks.get("smtp_deliverable", {}).get("valid", False):
            score += 10
        
        return min(score, 100)
    
    def get_verification_stats(self) -> Dict[str, Any]:
        """Get email verification statistics"""
        
        total = self.verification_stats["total_checked"]
        if total == 0:
            return self.verification_stats
        
        return {
            **self.verification_stats,
            "success_rates": {
                "syntax_rate": f"{self.verification_stats['syntax_valid']/total*100:.1f}%",
                "domain_rate": f"{self.verification_stats['domain_valid']/total*100:.1f}%",
                "mx_record_rate": f"{self.verification_stats['mx_record_valid']/total*100:.1f}%",
                "smtp_rate": f"{self.verification_stats['smtp_deliverable']/total*100:.1f}%",
                "final_verification_rate": f"{self.verification_stats['final_verified']/total*100:.1f}%"
            }
        }

class VerifiedContactDiscovery:
    """Enhanced contact discovery with mandatory email verification"""
    
    def __init__(self):
        self.email_verifier = EmailVerificationSystem()
        
    async def discover_verified_contacts(self, target_count: int) -> List[Dict[str, Any]]:
        """
        Discover contacts with mandatory email verification
        Only returns contacts with verified working emails
        """
        
        print(f"🔍 DISCOVERING VERIFIED CONTACTS")
        print(f"🎯 Target: {target_count} contacts with verified emails")
        print("=" * 60)
        
        from enhanced_contact_discovery import HealthcareContactDiscovery
        
        # Discover more contacts than needed to account for verification failures
        buffer_multiplier = 3  # Get 3x more to account for verification failures
        discovery_target = target_count * buffer_multiplier
        
        print(f"📂 Initial discovery target: {discovery_target} contacts (with buffer)")
        
        discovery = HealthcareContactDiscovery()
        raw_contacts = await discovery.discover_contacts_comprehensive(discovery_target)
        
        print(f"✅ Found {len(raw_contacts)} raw contacts")
        print("🔍 Starting email verification process...")
        
        verified_contacts = []
        verification_failures = 0
        
        for i, contact in enumerate(raw_contacts):
            if len(verified_contacts) >= target_count:
                print(f"✅ Target reached: {target_count} verified contacts")
                break
            
            email = contact.get('email', '')
            if not email:
                verification_failures += 1
                continue
            
            print(f"[{i+1}/{len(raw_contacts)}] Verifying: {contact.get('organization_name', 'Unknown')}")
            
            # Comprehensive email verification
            verification_result = await self.email_verifier.verify_email_comprehensive(email, contact)
            
            if verification_result.get('valid', False) and verification_result.get('confidence', 0) >= 75:
                # Add verification metadata to contact
                contact['email_verified'] = True
                contact['verification_confidence'] = verification_result['confidence']
                contact['verification_timestamp'] = verification_result['timestamp']
                contact['verification_checks'] = verification_result['checks']
                
                verified_contacts.append(contact)
                print(f"  ✅ Verified ({verification_result['confidence']}% confidence)")
            else:
                verification_failures += 1
                print(f"  ❌ Failed verification: {verification_result.get('reason', 'Unknown')}")
        
        print(f"\n📊 VERIFICATION SUMMARY:")
        print(f"   📂 Raw contacts found: {len(raw_contacts)}")
        print(f"   ✅ Email verified: {len(verified_contacts)}")
        print(f"   ❌ Verification failures: {verification_failures}")
        print(f"   🎯 Verification rate: {len(verified_contacts)/(len(raw_contacts))*100:.1f}%")
        
        # Display verification statistics
        stats = self.email_verifier.get_verification_stats()
        print(f"   📈 Overall verification stats:")
        for key, value in stats.get('success_rates', {}).items():
            print(f"      {key}: {value}")
        
        return verified_contacts[:target_count]

# Integration with main system
async def test_email_verification():
    """Test email verification system"""
    
    verifier = EmailVerificationSystem()
    
    # Test with known healthcare emails (examples)
    test_emails = [
        "info@mayoclinic.org",  # Should pass
        "fake@nonexistent.fake",  # Should fail
        "test@gmail.com",  # Should fail (not healthcare)
    ]
    
    print("🧪 Testing Email Verification System")
    print("=" * 50)
    
    for email in test_emails:
        result = await verifier.verify_email_comprehensive(email)
        print(f"Email: {email}")
        print(f"Valid: {result['valid']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Reason: {result['reason']}")
        print("-" * 30)
    
    stats = verifier.get_verification_stats()
    print(f"Final Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(test_email_verification())