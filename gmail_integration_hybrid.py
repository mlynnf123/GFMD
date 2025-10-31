"""
Gmail Integration Hybrid - Tries multiple authentication methods
Supports OAuth, Service Account, and SMTP for maximum compatibility
"""

import os
import json
import logging
from typing import Dict, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

logger = logging.getLogger(__name__)


class GmailHybridIntegration:
    """Hybrid Gmail integration that works in both local and Cloud Run environments"""
    
    def __init__(self):
        self.gmail_client = None
        self.method = None
        self._initialize_gmail()
    
    def _initialize_gmail(self):
        """Try multiple Gmail authentication methods in order"""
        
        # Method 1: Try OAuth from environment variables (best for Cloud Run with existing OAuth)
        if os.environ.get('GMAIL_OAUTH_CREDENTIALS'):
            try:
                from gmail_oauth_cloudrun import GmailOAuthCloudRun
                self.gmail_client = GmailOAuthCloudRun()
                if self.gmail_client.is_ready():
                    self.method = "OAuth-CloudRun"
                    logger.info("✅ Gmail initialized with OAuth from environment")
                    return
            except Exception as e:
                logger.warning(f"OAuth CloudRun initialization failed: {e}")
        
        # Method 2: Try SMTP with environment variables
        gmail_address = os.environ.get('GMAIL_ADDRESS')
        gmail_app_password = os.environ.get('GMAIL_APP_PASSWORD')
        
        if gmail_address and gmail_app_password:
            try:
                from gmail_integration_service_account import GmailSMTPIntegration
                self.gmail_client = GmailSMTPIntegration(gmail_address, gmail_app_password)
                self.method = "SMTP"
                logger.info(f"✅ Gmail initialized with SMTP for {gmail_address}")
                return
            except Exception as e:
                logger.warning(f"SMTP initialization failed: {e}")
        
        # Method 3: Try local OAuth (best for local development)
        try:
            from gmail_integration import GmailIntegration
            self.gmail_client = GmailIntegration()
            self.method = "OAuth-Local"
            logger.info("✅ Gmail initialized with local OAuth")
            return
        except Exception as e:
            logger.warning(f"Local OAuth initialization failed: {e}")
        
        # Method 4: Try service account with domain delegation (for Google Workspace)
        try:
            self._init_service_account_gmail()
            return
        except Exception as e:
            logger.warning(f"Service account initialization failed: {e}")
        
        # No method worked
        logger.error("❌ No Gmail authentication method succeeded")
        self.gmail_client = None
        self.method = None
    
    def _init_service_account_gmail(self):
        """Initialize Gmail with service account (requires domain-wide delegation)"""
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        # Try to find service account credentials
        cred_paths = [
            '/app/credentials/service-account.json',
            'service-account.json',
            os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '')
        ]
        
        creds = None
        for path in cred_paths:
            if path and os.path.exists(path):
                creds = service_account.Credentials.from_service_account_file(
                    path,
                    scopes=['https://www.googleapis.com/auth/gmail.send']
                )
                # For domain-wide delegation, you'd need to impersonate a user:
                # creds = creds.with_subject('user@yourdomain.com')
                break
        
        if not creds:
            raise Exception("No service account credentials found")
        
        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)
        
        # Create a wrapper to match our interface
        self.gmail_client = ServiceAccountGmailWrapper(service)
        self.method = "ServiceAccount"
        logger.info("✅ Gmail initialized with Service Account")
    
    def send_email(self, to_email: str, subject: str, body: str, **kwargs) -> Dict:
        """Send email using the initialized method"""
        if not self.gmail_client:
            return {
                'success': False,
                'error': 'Gmail not initialized - no authentication method available',
                'method': 'none'
            }
        
        try:
            if self.method == "SMTP":
                result = self.gmail_client.send_email(to_email, subject, body, **kwargs)
            elif self.method == "OAuth":
                result = self.gmail_client.send_email(to_email, subject, body, **kwargs)
            elif self.method == "ServiceAccount":
                result = self.gmail_client.send_email(to_email, subject, body, **kwargs)
            else:
                result = {'success': False, 'error': 'Unknown method'}
            
            result['method'] = self.method
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': self.method,
                'to': to_email,
                'subject': subject
            }
    
    def is_ready(self) -> bool:
        """Check if Gmail is ready to send"""
        return self.gmail_client is not None
    
    def get_status(self) -> Dict:
        """Get current Gmail integration status"""
        return {
            'ready': self.is_ready(),
            'method': self.method,
            'details': f"Gmail {'ready' if self.is_ready() else 'not configured'} via {self.method or 'no method'}"
        }


class ServiceAccountGmailWrapper:
    """Wrapper for service account Gmail to match our interface"""
    
    def __init__(self, service):
        self.service = service
    
    def send_email(self, to_email: str, subject: str, body: str, **kwargs) -> Dict:
        """Send email via service account"""
        try:
            message = MIMEText(body)
            message['To'] = to_email
            message['Subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                'success': True,
                'message_id': result['id'],
                'to': to_email,
                'subject': subject
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'to': to_email,
                'subject': subject
            }


# Test the hybrid integration
if __name__ == "__main__":
    print("🔧 Testing Gmail Hybrid Integration")
    print("=" * 40)
    
    gmail = GmailHybridIntegration()
    status = gmail.get_status()
    
    print(f"Status: {status['details']}")
    print(f"Ready: {status['ready']}")
    print(f"Method: {status['method']}")
    
    if gmail.is_ready():
        print("\n✅ Gmail is ready to send emails!")
    else:
        print("\n❌ Gmail needs configuration:")
        print("\nOption 1 - SMTP with App Password (Recommended for Cloud Run):")
        print("  export GMAIL_ADDRESS='your-email@gmail.com'")
        print("  export GMAIL_APP_PASSWORD='your-16-char-app-password'")
        print("\nOption 2 - OAuth (For local development):")
        print("  Place gmail_credentials.json in current directory")
        print("  Run this script to authenticate")