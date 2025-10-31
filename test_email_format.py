#!/usr/bin/env python3
"""
Test the fixed email formatting rules
"""
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_styling_rules import create_styled_email

def test_email_formatting():
    """Test the email formatting with the corrected rules"""
    print("🧪 Testing Email Format Rules")
    print("=" * 40)
    
    # Test prospect with problematic hospital name
    test_prospect = {
        'contact_name': 'Dr. John Smith',
        'email': 'john.smith@example.org',
        'organization_name': 'Columbus Regional Hospital (AKA Columbus Regional Health)',
        'title': 'Laboratory Director',
        'location': 'Columbus, OH',
        'pain_point': 'equipment noise issues',
        'facility_type': 'Regional Medical Center',
        'department': 'laboratory operations'
    }
    
    # Generate email with fixed rules
    styled_email = create_styled_email(test_prospect)
    
    print("📧 Generated Email:")
    print("-" * 30)
    print(f"Subject: {styled_email['subject']}")
    print()
    print("Body:")
    print(styled_email['body'])
    print()
    
    # Check if rules are followed
    print("✅ Rule Checks:")
    print(f"   Greeting starts with 'Hi': {'✅' if styled_email['body'].startswith('Hi ') else '❌'}")
    print(f"   Hospital name cleaned: {'✅' if '(AKA' not in styled_email['subject'] and '(AKA' not in styled_email['body'] else '❌'}")
    print(f"   First name used: {'✅' if 'Hi John,' in styled_email['body'] else '❌'}")
    
    return styled_email

if __name__ == "__main__":
    test_email_formatting()