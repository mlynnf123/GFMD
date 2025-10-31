"""
Gmail OAuth Integration for Cloud Run
Uses OAuth credentials stored as environment variables
"""

import os
import json
import base64
import logging
from typing import Dict, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GmailOAuthCloudRun:
    """Gmail OAuth integration that works in Cloud Run using environment variables"""
    
    def __init__(self):
        self.service = None
        self._initialize_from_env()
    
    def _initialize_from_env(self):
        """Initialize Gmail service from environment variables"""
        try:
            # Check for OAuth credentials in environment variables
            gmail_oauth_json = os.environ.get('GMAIL_OAUTH_CREDENTIALS')
            
            if not gmail_oauth_json:
                logger.warning("GMAIL_OAUTH_CREDENTIALS environment variable not found")
                return
            
            # Decode base64 if needed
            try:
                if gmail_oauth_json.startswith('eyJ'):  # Base64 encoded JSON starts with 'eyJ'
                    gmail_oauth_json = base64.b64decode(gmail_oauth_json).decode('utf-8')
            except:
                pass  # If decode fails, assume it's already JSON
            
            # Parse credentials
            cred_data = json.loads(gmail_oauth_json)
            
            # Create credentials object
            creds = Credentials(
                token=cred_data.get('token'),
                refresh_token=cred_data.get('refresh_token'),
                token_uri=cred_data.get('token_uri'),
                client_id=cred_data.get('client_id'),
                client_secret=cred_data.get('client_secret'),
                scopes=cred_data.get('scopes', ['https://www.googleapis.com/auth/gmail.send'])
            )
            
            # Refresh token if needed
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    logger.info("OAuth token refreshed successfully")
                else:
                    logger.error("OAuth credentials are invalid and cannot be refreshed")
                    return
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("✅ Gmail OAuth service initialized successfully for Cloud Run")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gmail OAuth from environment: {e}")
            self.service = None
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   html_body: Optional[str] = None, **kwargs) -> Dict:
        """Send email via Gmail API"""
        if not self.service:
            return {
                'success': False,
                'error': 'Gmail service not initialized',
                'to': to_email,
                'subject': subject
            }
        
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['To'] = to_email
            message['Subject'] = subject
            
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
            
            logger.info(f"Email sent successfully to {to_email}. Message ID: {result['id']}")
            
            return {
                'success': True,
                'message_id': result['id'],
                'to': to_email,
                'subject': subject,
                'method': 'OAuth'
            }
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return {
                'success': False,
                'error': f"Gmail API error: {str(e)}",
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
    
    def is_ready(self) -> bool:
        """Check if Gmail service is ready"""
        return self.service is not None
    
    def get_status(self) -> Dict:
        """Get current status"""
        return {
            'ready': self.is_ready(),
            'method': 'OAuth' if self.is_ready() else None,
            'details': f"Gmail {'ready' if self.is_ready() else 'not configured'} via OAuth"
        }


def encode_oauth_for_cloudrun(token_file_path: str) -> str:
    """Helper function to encode OAuth credentials for Cloud Run environment variable"""
    try:
        with open(token_file_path, 'r') as f:
            token_data = f.read()
        
        # Base64 encode the JSON string
        encoded = base64.b64encode(token_data.encode('utf-8')).decode('utf-8')
        
        print(f"Encoded OAuth credentials for Cloud Run:")
        print(f"Set this as GMAIL_OAUTH_CREDENTIALS environment variable:")
        print(f"\nGMAIL_OAUTH_CREDENTIALS='{encoded}'")
        
        return encoded
        
    except Exception as e:
        print(f"Error encoding OAuth credentials: {e}")
        return ""


# Test the integration
if __name__ == "__main__":
    print("🔧 Testing Gmail OAuth Cloud Run Integration")
    print("=" * 50)
    
    # First, show how to encode the token for Cloud Run
    if os.path.exists('gmail_token.json'):
        print("📁 Found gmail_token.json - encoding for Cloud Run...")
        encode_oauth_for_cloudrun('gmail_token.json')
        print("\n" + "="*50)
    
    # Test the integration
    gmail = GmailOAuthCloudRun()
    status = gmail.get_status()
    
    print(f"Status: {status['details']}")
    print(f"Ready: {status['ready']}")
    
    if gmail.is_ready():
        print("\n✅ Gmail OAuth is ready for Cloud Run!")
    else:
        print("\n❌ Gmail OAuth needs configuration")
        print("Run this script locally to get the encoded credentials,")
        print("then set GMAIL_OAUTH_CREDENTIALS environment variable in Cloud Run")