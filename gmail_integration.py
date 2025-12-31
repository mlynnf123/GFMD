"""
Gmail Integration for GFMD Swarm Agents
Handles OAuth authentication and email sending via Gmail API
"""

import os
import json
import logging
import uuid
import re
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
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly'
    ]
    
    def __init__(self, credentials_file: str = "gmail_credentials.json", tracking_domain: str = None):
        self.credentials_file = credentials_file
        self.token_file = "gmail_token.json"
        self.service = None
        self.tracking_domain = tracking_domain or "gfmd.com"  # Replace with actual tracking domain
        self.tracking_base_url = f"https://{self.tracking_domain}/track"
        
        # In production, create credential files from environment variables
        self._setup_credentials_from_env()
        
        try:
            self._authenticate()
        except Exception as e:
            logger.warning(f"Gmail authentication failed: {e}")
            self.service = None
    
    def _setup_credentials_from_env(self):
        """Setup Gmail credential files from environment variables if they don't exist"""
        try:
            # Create credentials file if it doesn't exist and GMAIL_CREDENTIALS env var is set
            if not os.path.exists(self.credentials_file) and os.environ.get('GMAIL_CREDENTIALS'):
                logger.info("Creating Gmail credentials file from environment variable")
                with open(self.credentials_file, 'w') as f:
                    f.write(os.environ.get('GMAIL_CREDENTIALS'))
            
            # Create token file if it doesn't exist and GMAIL_TOKEN env var is set
            if not os.path.exists(self.token_file) and os.environ.get('GMAIL_TOKEN'):
                logger.info("Creating Gmail token file from environment variable")
                with open(self.token_file, 'w') as f:
                    f.write(os.environ.get('GMAIL_TOKEN'))
                    
        except Exception as e:
            logger.warning(f"Failed to setup credentials from environment: {e}")
    
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
    
    def _generate_tracking_id(self) -> str:
        """Generate unique tracking ID for email"""
        return str(uuid.uuid4())
    
    def _create_tracking_pixel(self, tracking_id: str) -> str:
        """Create invisible tracking pixel HTML for email opens"""
        pixel_url = f"{self.tracking_base_url}/open/{tracking_id}"
        return f'<img src="{pixel_url}" width="1" height="1" style="display:none;" alt="">'
    
    def _add_click_tracking(self, html_content: str, tracking_id: str) -> str:
        """Add click tracking to all URLs in email content"""
        def replace_url(match):
            original_url = match.group(1)
            # Create tracked URL
            tracked_url = f"{self.tracking_base_url}/click/{tracking_id}?url={original_url}"
            return f'href="{tracked_url}"'
        
        # Replace all href attributes
        pattern = r'href="([^"]+)"'
        return re.sub(pattern, replace_url, html_content)
    
    def _enhance_html_with_tracking(self, html_content: str, tracking_id: str) -> str:
        """Add tracking pixel and click tracking to HTML email"""
        # Add click tracking to URLs
        tracked_html = self._add_click_tracking(html_content, tracking_id)
        
        # Add tracking pixel just before closing body tag
        tracking_pixel = self._create_tracking_pixel(tracking_id)
        if '</body>' in tracked_html:
            tracked_html = tracked_html.replace('</body>', f'{tracking_pixel}</body>')
        else:
            tracked_html += tracking_pixel
        
        return tracked_html
    
    def send_email(self, 
                   to_email: str,
                   subject: str, 
                   body: str,
                   from_email: Optional[str] = None,
                   html_body: Optional[str] = None,
                   cc: Optional[List[str]] = None,
                   bcc: Optional[List[str]] = None,
                   enable_tracking: bool = True) -> Dict:
        """
        Send email via Gmail API with optional tracking
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Plain text email body
            from_email: Sender email (optional, uses authenticated account)
            html_body: HTML email body (optional)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            enable_tracking: Enable open/click tracking (default: True)
            
        Returns:
            Dict with success status, message details, and tracking ID
        """
        try:
            # Generate tracking ID if tracking is enabled
            tracking_id = self._generate_tracking_id() if enable_tracking else None
            
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
            
            # Add tracking ID to message headers
            if tracking_id:
                message['X-Tracking-ID'] = tracking_id
            
            # Add plain text part
            text_part = MIMEText(body, 'plain')
            message.attach(text_part)
            
            # Add HTML part with tracking if provided
            if html_body:
                if enable_tracking and tracking_id:
                    enhanced_html = self._enhance_html_with_tracking(html_body, tracking_id)
                    html_part = MIMEText(enhanced_html, 'html')
                else:
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
                'tracking_id': tracking_id,
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
                'subject': subject,
                'tracking_id': tracking_id if 'tracking_id' in locals() else None
            }
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'to': to_email,
                'subject': subject,
                'tracking_id': tracking_id if 'tracking_id' in locals() else None
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
    
    def check_for_replies(self, since_date: str = None, max_results: int = 50) -> List[Dict]:
        """
        Check for email replies to sent messages
        
        Args:
            since_date: Check for replies since this date (YYYY/MM/DD format)
            max_results: Maximum number of replies to return
            
        Returns:
            List of reply data with tracking info
        """
        try:
            # Build query for replies
            query = "in:inbox"
            if since_date:
                query += f" after:{since_date}"
            
            # Get inbox messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            replies = []
            
            for message in messages:
                # Get full message details
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                # Check if this is a reply to our tracked email
                reply_data = self._extract_reply_info(msg)
                if reply_data:
                    replies.append(reply_data)
            
            logger.info(f"Found {len(replies)} replies")
            return replies
            
        except Exception as e:
            logger.error(f"Failed to check for replies: {e}")
            return []
    
    def _extract_reply_info(self, message: Dict) -> Optional[Dict]:
        """Extract reply information from a Gmail message"""
        try:
            payload = message.get('payload', {})
            headers = payload.get('headers', [])
            
            # Extract header information
            reply_data = {
                'message_id': message['id'],
                'thread_id': message.get('threadId'),
                'from': None,
                'to': None,
                'subject': None,
                'date': None,
                'body': None,
                'original_tracking_id': None,
                'in_reply_to': None
            }
            
            # Parse headers
            for header in headers:
                name = header['name'].lower()
                value = header['value']
                
                if name == 'from':
                    reply_data['from'] = value
                elif name == 'to':
                    reply_data['to'] = value
                elif name == 'subject':
                    reply_data['subject'] = value
                elif name == 'date':
                    reply_data['date'] = value
                elif name == 'in-reply-to':
                    reply_data['in_reply_to'] = value
                elif name == 'x-tracking-id':
                    reply_data['original_tracking_id'] = value
            
            # Extract email body
            body_text = self._extract_message_body(payload)
            reply_data['body'] = body_text
            
            # Check if this is actually a reply to our email
            if reply_data['in_reply_to'] or 'Re:' in (reply_data['subject'] or ''):
                # Extract sender email and name for AI processing
                from_field = reply_data.get('from', '')
                if '<' in from_field and '>' in from_field:
                    # Format: "Name <email@domain.com>"
                    name_part = from_field.split('<')[0].strip().strip('"')
                    email_part = from_field.split('<')[1].split('>')[0].strip()
                    reply_data['from_email'] = email_part
                    reply_data['sender_name'] = name_part
                else:
                    # Just email address
                    reply_data['from_email'] = from_field
                    reply_data['sender_name'] = ''
                
                # Clean up the content for AI processing
                reply_data['content'] = body_text or ''
                
                return reply_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract reply info: {e}")
            return None
    
    def _extract_message_body(self, payload: Dict) -> str:
        """Extract text body from Gmail message payload"""
        try:
            # Check if message has parts (multipart)
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
            
            # Check if message body is directly in payload
            elif payload.get('body', {}).get('data'):
                data = payload['body']['data']
                return base64.urlsafe_b64decode(data).decode('utf-8')
            
            return ""
            
        except Exception as e:
            logger.error(f"Failed to extract message body: {e}")
            return ""


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