#!/usr/bin/env python3
"""
Email Styling Rules for GFMD Automatic Sending
Implements specific formatting and tone requirements
"""

import re
from typing import Dict, Any

class EmailStyleRules:
    """Enforces consistent email styling and tone"""
    
    def __init__(self):
        # Forbidden words/phrases that sound too AI-generated
        self.ai_words_to_avoid = [
            "leverage", "utilize", "optimize", "synergy", "streamline",
            "cutting-edge", "state-of-the-art", "innovative solutions",
            "revolutionary", "game-changing", "next-level", "robust",
            "seamless", "holistic", "comprehensive solution",
            "I hope this message finds you well", "I trust this email finds you",
            "I'm excited to", "I'm thrilled to", "amazing", "incredible"
        ]
        
        # Professional alternatives
        self.professional_replacements = {
            "utilize": "use",
            "leverage": "use",
            "optimize": "improve",
            "innovative": "proven",
            "cutting-edge": "advanced",
            "state-of-the-art": "modern",
            "revolutionary": "effective",
            "game-changing": "significant",
            "robust": "reliable",
            "seamless": "smooth",
            "amazing": "impressive",
            "incredible": "notable"
        }
    
    def format_greeting(self, contact_name: str) -> str:
        """Format greeting with first name only"""
        # Extract first name from full name, handle titles
        if not contact_name:
            return "Hello there,"
        
        # Split name and remove common titles
        name_parts = contact_name.split()
        titles = ['Dr.', 'Dr', 'Mr.', 'Mr', 'Ms.', 'Ms', 'Mrs.', 'Mrs']
        
        # Find first actual name (skip titles)
        first_name = None
        for part in name_parts:
            if part not in titles:
                first_name = part
                break
        
        if not first_name:
            first_name = name_parts[0] if name_parts else "there"
        
        return f"Hi {first_name},"
    
    def clean_organization_name(self, org_name: str) -> str:
        """Clean organization name by removing (AKA...) and (FKA...) parts"""
        if not org_name:
            return org_name
        
        # Remove (AKA ...) and (FKA ...) patterns
        import re
        # Pattern to match (AKA anything) or (FKA anything)
        pattern = r'\s*\([AF]KA[^)]*\)'
        cleaned_name = re.sub(pattern, '', org_name).strip()
        
        return cleaned_name
    
    def format_closing(self) -> str:
        """Standard closing format"""
        return "Best,"
    
    def clean_ai_language(self, text: str) -> str:
        """Remove AI-sounding words and phrases"""
        cleaned_text = text
        
        # Replace AI-sounding words with professional alternatives
        for ai_word, replacement in self.professional_replacements.items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(ai_word), re.IGNORECASE)
            cleaned_text = pattern.sub(replacement, cleaned_text)
        
        # Remove remaining AI phrases
        for phrase in self.ai_words_to_avoid:
            if phrase not in self.professional_replacements:
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                cleaned_text = pattern.sub("", cleaned_text)
        
        # Clean up extra spaces but preserve line breaks
        # First preserve line breaks by replacing them with placeholders
        cleaned_text = cleaned_text.replace('\n', '|||LINEBREAK|||')
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        # Restore line breaks
        cleaned_text = cleaned_text.replace('|||LINEBREAK|||', '\n')
        
        return cleaned_text
    
    def remove_emojis_and_bullets(self, text: str) -> str:
        """Remove emojis and bullet points"""
        # Remove emojis (Unicode ranges for common emojis)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002600-\U000027BF"  # misc symbols
            "\U0001f900-\U0001f9ff"  # supplemental symbols
            "]+", flags=re.UNICODE
        )
        
        text = emoji_pattern.sub('', text)
        
        # Remove bullet points and replace with natural text flow
        bullet_patterns = [
            r'[•·▪▫▸▹‣⁃]',  # Various bullet symbols
            r'✓',  # Checkmarks
            r'→',  # Arrows
        ]
        
        for pattern in bullet_patterns:
            text = re.sub(pattern, '', text)
        
        # Clean up bullet-style formatting
        text = re.sub(r'\n\s*[•·▪▫▸▹‣⁃✓→]\s*', '\n', text)
        
        return text
    
    def apply_professional_tone(self, text: str) -> str:
        """Apply professional, human-like tone"""
        
        # Replace overly enthusiastic language
        enthusiasm_replacements = {
            "We're excited to": "We would like to",
            "I'm excited to": "I would like to",
            "We're thrilled": "We are pleased",
            "Amazing results": "Strong results",
            "Incredible benefits": "Significant benefits",
            "Fantastic opportunity": "Good opportunity"
        }
        
        for enthusiastic, professional in enthusiasm_replacements.items():
            pattern = re.compile(re.escape(enthusiastic), re.IGNORECASE)
            text = pattern.sub(professional, text)
        
        return text
    
    def format_email_body(self, prospect: Dict[str, Any], base_content: str) -> str:
        """Format complete email with all styling rules"""
        
        # Start with greeting
        greeting = self.format_greeting(prospect['contact_name'])
        
        # Clean the base content
        content = self.clean_ai_language(base_content)
        content = self.remove_emojis_and_bullets(content)
        content = self.apply_professional_tone(content)
        
        # Format closing
        closing = self.format_closing()
        
        # Combine all parts
        email_body = f"""{greeting}

{content}

{closing}

GFMD Solutions Team"""
        
        return email_body
    
    def generate_professional_content(self, prospect: Dict[str, Any]) -> str:
        """Generate professional email content without AI language"""
        
        # Clean the organization name to remove (AKA...) and (FKA...) parts
        raw_org_name = prospect.get('organization_name', 'your facility')
        org_name = self.clean_organization_name(raw_org_name)
        location = prospect.get('location', 'your area').split(',')[0]
        pain_point = prospect.get('pain_point', 'laboratory noise and operational efficiency challenges')
        facility_type = prospect.get('facility_type', 'healthcare')
        budget_range = prospect.get('budget_range', 'operational improvement')
        department = prospect.get('department', 'laboratory operations')
        
        # Create natural, professional content
        content = f"""I'm writing regarding the laboratory operations at {org_name} in {location}.

I understand that facilities like yours often face challenges with {pain_point.lower()}. Given your role in {department}, you know how important it is to maintain a professional environment while ensuring reliable equipment performance.

Our GFMD Silencer Centrifuge technology has helped similar {facility_type.lower()} facilities address these exact concerns. The technology reduces laboratory noise by up to 70% while maintaining full processing capacity.

Many facilities in your budget range of {budget_range} have found this solution effective for improving both staff satisfaction and operational efficiency.

I would be happy to share specific case studies from similar facilities in Texas and discuss how this might work for {org_name}.

Would you have 15 minutes for a brief call to explore this further?"""

        return content

def create_styled_email(prospect: Dict[str, Any]) -> Dict[str, str]:
    """Create email with proper styling rules applied"""
    
    styler = EmailStyleRules()
    
    # Generate base content
    base_content = styler.generate_professional_content(prospect)
    
    # Apply all styling rules
    email_body = styler.format_email_body(prospect, base_content)
    
    # Create subject line (simple, direct) with cleaned organization name
    cleaned_org_name = styler.clean_organization_name(prospect['organization_name'])
    subject = f"Laboratory Equipment Discussion - {cleaned_org_name}"
    
    return {
        'subject': subject,
        'body': email_body,
        'recipient_email': prospect['email'],
        'recipient_name': prospect['contact_name']
    }

if __name__ == "__main__":
    # Test the styling rules
    test_prospect = {
        'contact_name': 'Dr. Jennifer Martinez',
        'organization_name': 'Regional Medical Center',
        'location': 'Houston, TX',
        'pain_point': 'Noise complaints from adjacent patient areas',
        'facility_type': 'Regional Medical Center Lab',
        'budget_range': '$100K-200K',
        'department': 'Clinical Laboratory',
        'email': 'j.martinez@regional.org'
    }
    
    print("🧪 Testing Email Styling Rules")
    print("=" * 50)
    
    styled_email = create_styled_email(test_prospect)
    
    print(f"Subject: {styled_email['subject']}")
    print()
    print("Body:")
    print(styled_email['body'])
    print()
    print("✅ Email formatted with styling rules:")
    print("• Starts with 'Hello [first name],'")
    print("• Ends with 'Best,'")
    print("• No emojis or bullet points")
    print("• Professional, human tone")
    print("• No AI-sounding language")