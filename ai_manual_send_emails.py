#!/usr/bin/env python3
"""
AI-Powered Manual Email Sender
Uses Groq AI composer with RAG system for highly personalized emails
"""

import os
import asyncio
from datetime import datetime, timedelta
from mongodb_storage import MongoDBStorage
from gmail_integration import GmailIntegration
from groq_email_composer_agent import GroqEmailComposerAgent
from business_day_utils import BusinessDayCalculator

# Load environment
def load_env():
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    value = value.strip('"')
                    os.environ[key] = value
    except FileNotFoundError:
        pass

load_env()

class AIManualEmailSender:
    def __init__(self):
        self.storage = MongoDBStorage()
        self.gmail = GmailIntegration()
        self.email_composer = GroqEmailComposerAgent(agent_id="manual_sender")
        self.business_day_calc = BusinessDayCalculator()

    def get_new_contacts(self, count=10):
        """Get contacts that haven't been emailed yet"""
        # Get contacts already in sequences
        active_sequences = list(self.storage.db.email_sequences.find(
            {"status": {"$in": ["active", "completed"]}},
            {"contact_id": 1}
        ))
        
        from bson import ObjectId
        active_contact_ids = []
        for seq in active_sequences:
            try:
                if isinstance(seq["contact_id"], str):
                    active_contact_ids.append(ObjectId(seq["contact_id"]))
                else:
                    active_contact_ids.append(seq["contact_id"])
            except:
                pass
        
        # Find contacts without sequences
        query_filter = {"_id": {"$nin": active_contact_ids}} if active_contact_ids else {}
        new_contacts = list(self.storage.db.contacts.find(query_filter).limit(count))
        
        return new_contacts

    def analyze_contact_industry(self, contact):
        """Analyze contact to determine industry and pain points"""
        email = contact.get('email', '').lower()
        company_name = contact.get('company_name', '').lower()
        
        # Determine industry type and specific pain points
        if any(keyword in email + company_name for keyword in ['edu', 'university', 'college', 'school']):
            return {
                'industry': 'Education/Campus Safety',
                'pain_points': ['Campus drug incidents', 'Student safety concerns', 'Limited security budget'],
                'specific_context': 'educational institution'
            }
        elif any(keyword in email + company_name for keyword in ['hospital', 'medical', 'health', 'isd']):
            return {
                'industry': 'Healthcare/School District',
                'pain_points': ['Medical waste disposal regulations', 'Patient medication disposal', 'Compliance requirements'],
                'specific_context': 'healthcare or educational facility'
            }
        elif any(keyword in email + company_name for keyword in ['sheriff', 'police', 'pd', 'county', 'city']):
            return {
                'industry': 'Law Enforcement',
                'pain_points': ['Evidence destruction backlog', 'High incineration costs', 'DEA compliance'],
                'specific_context': 'law enforcement agency'
            }
        elif any(keyword in email + company_name for keyword in ['port', 'authority', 'transportation']):
            return {
                'industry': 'Transportation Authority',
                'pain_points': ['Security drug seizures', 'Limited disposal options', 'Federal compliance'],
                'specific_context': 'transportation authority'
            }
        else:
            return {
                'industry': 'Government/Municipal',
                'pain_points': ['Drug disposal costs', 'Regulatory compliance', 'Budget constraints'],
                'specific_context': 'government agency'
            }

    async def create_ai_personalized_email(self, contact):
        """Use AI composer to create highly personalized email"""
        
        # Analyze contact for industry-specific insights
        industry_analysis = self.analyze_contact_industry(contact)
        
        # Prepare prospect data
        prospect_data = {
            'contact_name': contact.get('contact_name', ''),
            'email': contact.get('email', ''),
            'company_name': contact.get('company_name', ''),
            'location': contact.get('location', ''),
            'title': contact.get('title', 'Decision Maker'),
            'facility_type': industry_analysis['specific_context']
        }
        
        # Research findings based on industry
        research_findings = {
            'pain_points': industry_analysis['pain_points'],
            'industry_type': industry_analysis['industry']
        }
        
        # Qualification data
        qualification_score = {
            'total_score': 85,
            'key_talking_points': [
                f"Specialized solution for {industry_analysis['industry'].lower()}",
                "Reduces disposal costs by 30-60%",
                "Ensures full regulatory compliance"
            ]
        }
        
        try:
            # Generate email using AI composer with RAG
            result = await self.email_composer.execute({
                'prospect_data': prospect_data,
                'research_findings': research_findings,
                'qualification_score': qualification_score
            })
            
            if result.get('success') and 'Fallback template' not in result.get('personalization_notes', ''):
                return result
            else:
                print(f"⚠️ AI generation failed, using enhanced fallback for {contact.get('email')}")
                return self.create_enhanced_fallback_email(contact, industry_analysis)
                
        except Exception as e:
            print(f"❌ AI composer error for {contact.get('email')}: {e}")
            return self.create_enhanced_fallback_email(contact, industry_analysis)

    def create_enhanced_fallback_email(self, contact, industry_analysis):
        """Create an enhanced fallback email with industry personalization"""
        email = contact.get('email', '')
        company_name = contact.get('company_name', 'your organization')
        contact_name = contact.get('contact_name', '')
        
        # Extract first name
        first_name = "there"
        if contact_name:
            name_parts = contact_name.split()
            for part in name_parts:
                clean_part = part.strip('.,')
                if clean_part and clean_part not in ['Dr.', 'Dr', 'Mr.', 'Mr', 'Ms.', 'Ms', 'Mrs.', 'Mrs']:
                    first_name = clean_part
                    break
        
        # Industry-specific subject and content
        if industry_analysis['industry'] == 'Education/Campus Safety':
            subject = f"Campus drug disposal solution for {company_name}"
            pain_point = "managing drug incidents and contraband disposal on campus"
        elif industry_analysis['industry'] == 'Healthcare/School District':
            subject = f"Medical waste compliance for {company_name}"
            pain_point = "managing pharmaceutical and medical waste disposal regulations"
        elif industry_analysis['industry'] == 'Transportation Authority':
            subject = f"Security seizure disposal for {company_name}"
            pain_point = "disposing of drug seizures and contraband from security operations"
        else:
            subject = f"Drug disposal costs at {company_name}"
            pain_point = "managing drug evidence disposal costs and compliance requirements"
        
        body = f"""Hi {first_name},

I understand that {pain_point} can be a significant challenge for {industry_analysis['industry'].lower()} organizations like {company_name}. Our Narc Gone system is specifically designed to help {industry_analysis['specific_context']}s destroy illicit substances and medications on-site, reducing disposal costs and ensuring full regulatory compliance.

Would you be open to a brief call to discuss how our system could help {company_name}?

Best,

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com"""

        # Create HTML version with proper formatting and logo
        html_body = self.create_html_email(body, first_name)
        
        return {
            'success': True,
            'subject': subject,
            'body': body,
            'html_body': html_body,
            'first_name': first_name,
            'personalization_notes': f"Industry-personalized for {industry_analysis['industry']} - {company_name}",
            'recipient_email': email,
            'company_name': company_name
        }

    def create_html_email(self, text_body, first_name):
        """Create HTML version with proper GFMD signature and logo"""
        
        # Split body into content and signature
        if "Best," in text_body:
            parts = text_body.split("Best,", 1)
            content = parts[0].strip()
        else:
            content = text_body.strip()
        
        # Convert line breaks to HTML
        html_content = content.replace('\n\n', '</p><p>').replace('\n', '<br>\n')
        html_content = f'<p>{html_content}</p>'
        
        # GFMD HTML signature with logo
        html_signature = """
<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333; margin-top: 20px;">
    <div style="border-top: 1px solid #e0e0e0; padding-top: 15px;">
        <table cellpadding="0" cellspacing="0" border="0" style="width: 100%;">
            <tr>
                <td style="vertical-align: top; width: 80px; padding-right: 15px;">
                    <img src="https://gfmd.com/wp-content/themes/gfmd/assets/images/cropped-gfmd-logo-blue-1024x690.png" alt="GFMD Global Focus" style="width: 60px; height: auto; display: block; max-width: 60px;" />
                </td>
                <td style="vertical-align: top;">
                    <div style="font-weight: bold; font-size: 16px; color: #2c3e9e; margin-bottom: 8px;">
                        Meranda Freiner
                    </div>
                    <div style="font-size: 12px; color: #666; margin-bottom: 8px;">
                        Global Focus Marketing & Distribution
                    </div>
                    <div style="margin-bottom: 4px;">
                        <a href="mailto:solutions@gfmd.com" style="color: #2c3e9e; text-decoration: none; font-size: 13px;">solutions@gfmd.com</a>
                    </div>
                    <div style="margin-bottom: 4px; font-size: 13px; color: #333;">
                        619-341-9058
                    </div>
                    <div style="font-size: 13px;">
                        <a href="https://www.gfmd.com" style="color: #2c3e9e; text-decoration: none;">www.gfmd.com</a>
                    </div>
                </td>
            </tr>
        </table>
    </div>
</div>"""
        
        # Combine into full HTML email
        full_html = f"""
<div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5; color: #333;">
    {html_content}
    
    <div style="margin-top: 20px;">
        Best,
    </div>
    {html_signature}
</div>"""
        
        return full_html

    async def send_ai_emails_to_new_contacts(self, count=10, actually_send=True):
        """Send AI-personalized emails to new contacts"""
        print(f"\n🤖 AI Email Sender - Generating {count} personalized emails...")
        print("=" * 60)
        
        # Get new contacts
        new_contacts = self.get_new_contacts(count)
        
        if not new_contacts:
            print("❌ No new contacts available")
            return {"success": False, "message": "No new contacts available"}
        
        print(f"✅ Found {len(new_contacts)} new contacts")
        
        sent_count = 0
        results = []
        
        for i, contact in enumerate(new_contacts):
            try:
                print(f"\n📨 Processing {i+1}/{len(new_contacts)}: {contact.get('email', 'unknown')}")
                
                # Generate AI-personalized email
                email_data = await self.create_ai_personalized_email(contact)
                
                if not email_data.get('success'):
                    print(f"❌ Failed to generate email: {email_data.get('error', 'Unknown error')}")
                    continue
                
                print(f"📝 Generated: {email_data['subject']}")
                print(f"🎯 Personalization: {email_data['personalization_notes']}")
                
                if actually_send:
                    # Send email via Gmail with HTML
                    send_result = self.gmail.send_email(
                        to_email=email_data['recipient_email'],
                        subject=email_data['subject'],
                        body=email_data['body'],
                        html_body=email_data.get('html_body')
                    )
                    
                    if send_result.get('success'):
                        print(f"✅ Email sent successfully")
                        sent_count += 1
                        
                        # Create sequence record
                        contact_id = str(contact['_id'])
                        next_email_due = self.business_day_calc.add_business_days(datetime.now(), 3)
                        
                        sequence_data = {
                            "contact_id": contact_id,
                            "sequence_name": "narc_gone_law_enforcement",
                            "current_step": 1,
                            "status": "active",
                            "created_at": datetime.now().isoformat(),
                            "updated_at": datetime.now().isoformat(),
                            "next_email_due": next_email_due.isoformat(),
                            "last_email_sent": datetime.now().isoformat(),
                            "reply_received": False,
                            "reply_date": None,
                            "emails_sent": [{
                                "step": 1,
                                "sent_at": datetime.now().isoformat(),
                                "subject": email_data['subject'],
                                "template_type": "initial",
                                "actually_sent": True
                            }]
                        }
                        
                        self.storage.db.email_sequences.insert_one(sequence_data)
                        
                        results.append({
                            "contact_email": email_data['recipient_email'],
                            "subject": email_data['subject'],
                            "personalization": email_data['personalization_notes'],
                            "success": True
                        })
                    else:
                        print(f"❌ Failed to send: {send_result.get('error')}")
                        results.append({
                            "contact_email": email_data['recipient_email'],
                            "success": False,
                            "error": send_result.get('error')
                        })
                else:
                    print(f"📧 DRY RUN - Would send: {email_data['subject']}")
                    results.append({
                        "contact_email": email_data['recipient_email'],
                        "subject": email_data['subject'],
                        "personalization": email_data['personalization_notes'],
                        "dry_run": True
                    })
                    
            except Exception as e:
                print(f"❌ Error processing contact: {e}")
                results.append({
                    "contact_email": contact.get('email', 'unknown'),
                    "success": False,
                    "error": str(e)
                })
        
        print(f"\n📊 Final Summary:")
        print(f"   🎯 AI-Personalized emails sent: {sent_count}")
        print(f"   📈 Success rate: {(sent_count/len(results)*100):.1f}%" if results else "0%")
        
        return {
            "success": True,
            "sent": sent_count,
            "processed": len(results),
            "details": results
        }

async def main():
    """Send 10 AI-personalized emails"""
    sender = AIManualEmailSender()
    
    print("🤖 AI-Powered Email Sender")
    print("🎯 Using Groq AI + RAG for industry-specific personalization")
    print("=" * 70)
    
    # Send personalized emails
    result = await sender.send_ai_emails_to_new_contacts(count=10, actually_send=True)
    
    if result.get('success'):
        print(f"\n✅ Mission accomplished!")
        print(f"📧 Personalized emails sent: {result.get('sent', 0)}")
        print(f"🎨 Each email uniquely crafted for recipient's industry & context")
    else:
        print(f"\n❌ Process failed: {result.get('message')}")

if __name__ == "__main__":
    asyncio.run(main())