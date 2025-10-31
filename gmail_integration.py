"""
Gmail Integration for GFMD Swarm Agents
Handles OAuth authentication and email sending via Gmail API
"""

import os
import json
import logging
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

# Gmail API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class GmailIntegration:
    """Gmail API integration for sending emails via GFMD agents"""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self, credentials_file: str = "gmail_credentials.json"):
        self.credentials_file = credentials_file
        self.token_file = "gmail_token.json"
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API using OAuth 2.0"""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
                logger.info("Loaded existing OAuth token")
            except Exception as e:
                logger.error(f"Failed to load token file: {e}")
                creds = None
        
        # If no valid credentials, try to refresh or fail gracefully
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("Attempting to refresh expired token...")
                    creds.refresh(Request())
                    logger.info("Token refreshed successfully")
                    
                    # Save refreshed token
                    with open(self.token_file, 'w') as token:
                        token.write(creds.to_json())
                        
                except Exception as e:
                    logger.error(f"Token refresh failed: {e}")
                    raise Exception(f"OAuth token refresh failed in production environment: {e}")
            else:
                # In production, we can't run interactive OAuth flow
                raise Exception(
                    "No valid OAuth token found. In Cloud Run production environment, "
                    "interactive OAuth authentication is not possible. Please ensure "
                    "a valid gmail_token.json file is included in the deployment."
                )
        
        # Build Gmail service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail API authentication successful")
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {e}")
            raise Exception(f"Gmail service initialization failed: {e}")
    
    def send_email(self, 
                   to_email: str,
                   subject: str, 
                   body: str,
                   from_email: Optional[str] = None,
                   html_body: Optional[str] = None,
                   cc: Optional[List[str]] = None,
                   bcc: Optional[List[str]] = None) -> Dict:
        """
        Send email via Gmail API
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Plain text email body
            from_email: Sender email (optional, uses authenticated account)
            html_body: HTML email body (optional)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            
        Returns:
            Dict with success status and message details
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['To'] = to_email
            message['Subject'] = subject
            
            if from_email:
                message['From'] = from_email
            
            if cc:
                message['Cc'] = ', '.join(cc)
            
            if bcc:
                message['Bcc'] = ', '.join(bcc)
            
            # Add plain text part
            text_part = MIMEText(body, 'plain')
            message.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                message.attach(html_part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send email
            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"Email sent successfully. Message ID: {result['id']}")
            
            return {
                'success': True,
                'message_id': result['id'],
                'to': to_email,
                'subject': subject,
                'sent_at': result.get('internalDate')
            }
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'to': to_email,
                'subject': subject
            }
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
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
        """
        Send GFMD-specific outreach email with proper formatting
        
        Args:
            prospect: Prospect information dictionary
            email_content: Generated email content from agents
            subject: Email subject line
            sender_name: Name to appear as sender
            
        Returns:
            Dict with sending result
        """
        # Create professional HTML version
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
        
        # Add prospect context to result
        result.update({
            'prospect_name': prospect.get('contact_name'),
            'organization': prospect.get('organization_name'),
            'email_type': 'gfmd_outreach'
        })
        
        return result
    
    def _format_email_as_html(self, content: str, contact_name: str, sender_name: str) -> str:
        """Convert plain text email to professional HTML format"""
        # Replace line breaks with HTML breaks
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
    
    def get_sent_emails(self, query: str = "from:me", max_results: int = 10) -> List[Dict]:
        """
        Get list of sent emails for tracking purposes
        
        Args:
            query: Gmail search query
            max_results: Maximum number of emails to return
            
        Returns:
            List of email metadata
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            email_list = []
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id']
                ).execute()
                
                headers = msg['payload'].get('headers', [])
                email_data = {'id': message['id']}
                
                for header in headers:
                    if header['name'] in ['To', 'Subject', 'Date']:
                        email_data[header['name'].lower()] = header['value']
                
                email_list.append(email_data)
            
            return email_list
            
        except Exception as e:
            logger.error(f"Failed to retrieve emails: {e}")
            return []


def setup_gmail_integration() -> Dict:
    """
    Setup guide for Gmail integration
    
    Returns:
        Dict with setup instructions
    """
    setup_instructions = {
        "steps": [
            "1. Go to Google Cloud Console (console.cloud.google.com)",
            "2. Enable Gmail API for your project",
            "3. Create OAuth 2.0 credentials (Desktop application)",
            "4. Download credentials JSON file",
            "5. Save as 'gmail_credentials.json' in this directory",
            "6. Run the integration - it will open browser for authentication"
        ],
        "required_files": [
            "gmail_credentials.json - OAuth 2.0 client credentials",
            "gmail_token.json - Access token (auto-generated)"
        ],
        "scopes_needed": [
            "https://www.googleapis.com/auth/gmail.send"
        ]
    }
    
    return setup_instructions


# Test the integration
if __name__ == "__main__":
    print("🔧 Gmail Integration Test")
    print("=" * 40)
    
    # Show setup instructions if credentials not found
    if not os.path.exists("gmail_credentials.json"):
        print("❌ Gmail credentials not found!")
        print("\n📋 Setup Instructions:")
        instructions = setup_gmail_integration()
        for step in instructions["steps"]:
            print(f"   {step}")
        print(f"\n📁 Required files:")
        for file in instructions["required_files"]:
            print(f"   {file}")
    else:
        try:
            # Test authentication
            gmail = GmailIntegration()
            print("✅ Gmail authentication successful!")
            
            # Test with sample prospect (won't actually send without confirmation)
            sample_prospect = {
                'email': 'test@example.com',
                'contact_name': 'Dr. Test',
                'organization_name': 'Test Hospital'
            }
            
            print("\n📧 Gmail integration ready for GFMD agents!")
            print("   Use gmail.send_gfmd_outreach_email() to send emails")
            
        except Exception as e:
            print(f"❌ Gmail setup error: {e}")
            print("\n🔧 Check your credentials file and try again")