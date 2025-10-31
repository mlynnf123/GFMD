"""
Gmail Integration using Service Account or API Key approach
Alternative method that doesn't require OAuth flow
"""

import os
import base64
import logging
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

logger = logging.getLogger(__name__)

class GmailSMTPIntegration:
    """Gmail integration using SMTP with App Password"""
    
    def __init__(self, email_address: str, app_password: str):
        """
        Initialize with Gmail address and app password
        
        Args:
            email_address: Your Gmail address
            app_password: Gmail app password (not regular password)
        """
        self.email_address = email_address
        self.app_password = app_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def send_email(self,
                   to_email: str,
                   subject: str,
                   body: str,
                   html_body: Optional[str] = None,
                   cc: Optional[List[str]] = None,
                   bcc: Optional[List[str]] = None) -> Dict:
        """Send email using Gmail SMTP"""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = self.email_address
            message['To'] = to_email
            message['Subject'] = subject
            
            if cc:
                message['Cc'] = ', '.join(cc)
            
            # Add text and HTML parts
            text_part = MIMEText(body, 'plain')
            message.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, 'html')
                message.attach(html_part)
            
            # Connect to Gmail SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.app_password)
                
                # Send email
                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)
                
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            
            return {
                'success': True,
                'to': to_email,
                'subject': subject,
                'from': self.email_address
            }
            
        except Exception as e:
            logger.error(f"SMTP email sending failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'to': to_email,
                'subject': subject
            }
    
    def send_gfmd_outreach_email(self,
                                prospect: Dict,
                                email_content: str,
                                subject: str,
                                sender_name: str = "GFMD Sales Team") -> Dict:
        """Send GFMD-specific outreach email"""
        html_content = self._format_email_as_html(
            email_content,
            prospect.get('contact_name', 'Colleague'),
            sender_name
        )
        
        result = self.send_email(
            to_email=prospect['email'],
            subject=subject,
            body=email_content,
            html_body=html_content
        )
        
        result.update({
            'prospect_name': prospect.get('contact_name'),
            'organization': prospect.get('organization_name'),
            'email_type': 'gfmd_outreach'
        })
        
        return result
    
    def _format_email_as_html(self, content: str, contact_name: str, sender_name: str) -> str:
        """Convert plain text email to professional HTML format"""
        html_content = content.replace('\n', '<br>')
        
        html_template = f"""
        <html>
          <head>
            <style>
              body {{ font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; }}
              .header {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
              .content {{ margin: 20px 0; }}
              .signature {{ margin-top: 30px; border-top: 1px solid #eee; padding-top: 15px; }}
              .company {{ color: #3498db; font-weight: bold; }}
            </style>
          </head>
          <body>
            <div class="header">
              <h3>Global Forensic Medical Devices</h3>
            </div>
            <div class="content">
              {html_content}
            </div>
            <div class="signature">
              <p>Best regards,<br>
              <strong>{sender_name}</strong><br>
              <span class="company">Global Forensic Medical Devices (GFMD)</span><br>
              <em>Precision Centrifuge Solutions for Modern Laboratories</em></p>
            </div>
          </body>
        </html>
        """
        
        return html_template


def setup_gmail_app_password():
    """Instructions for setting up Gmail App Password"""
    print("""
    Gmail App Password Setup (Easier Alternative)
    ============================================
    
    1. Go to your Google Account settings:
       https://myaccount.google.com/security
    
    2. Enable 2-Step Verification (if not already enabled)
    
    3. Go to App passwords:
       https://myaccount.google.com/apppasswords
    
    4. Create a new app password:
       - Select "Mail" as the app
       - Select "Other" as the device
       - Name it "GFMD Swarm Agents"
    
    5. Copy the 16-character app password
    
    6. Set environment variables:
       export GMAIL_ADDRESS="your-email@gmail.com"
       export GMAIL_APP_PASSWORD="your-16-char-app-password"
    
    This method is simpler and doesn't require OAuth!
    """)


# Test the integration
if __name__ == "__main__":
    print("🔧 Gmail SMTP Integration Setup")
    print("=" * 40)
    
    # Check for environment variables
    email = os.environ.get('GMAIL_ADDRESS')
    app_password = os.environ.get('GMAIL_APP_PASSWORD')
    
    if not email or not app_password:
        print("❌ Gmail credentials not found!")
        setup_gmail_app_password()
    else:
        try:
            # Test authentication
            gmail = GmailSMTPIntegration(email, app_password)
            print(f"✅ Gmail SMTP ready with: {email}")
            
            # Offer to send test email
            send_test = input("\nSend a test email? (yes/no): ")
            if send_test.lower() in ['yes', 'y']:
                test_email = input("Enter test email address: ")
                
                result = gmail.send_gfmd_outreach_email(
                    prospect={
                        'email': test_email,
                        'contact_name': 'Test User',
                        'organization_name': 'Test Hospital'
                    },
                    email_content="This is a test email from GFMD Swarm Agents using Gmail SMTP.",
                    subject="Test - GFMD Swarm Agents",
                    sender_name="GFMD Test"
                )
                
                if result['success']:
                    print(f"✅ Test email sent to {test_email}")
                else:
                    print(f"❌ Failed: {result['error']}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")