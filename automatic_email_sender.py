#!/usr/bin/env python3
"""
Automatic Email Sender for GFMD Lead Generation
Sends styled emails via Gmail API with safety controls
"""

import sys
import os
import json
from datetime import datetime, date
from typing import Dict, Any, List
sys.path.append('.')

from email_styling_rules import create_styled_email
from email_verification import should_send_email
from gmail_integration import GmailIntegration
from google_sheets_integration import GoogleSheetsExporter, GoogleSheetsConfig

class AutomaticEmailSender:
    """Handles automatic email sending with safety controls"""
    
    def __init__(self):
        self.gmail = None
        self.daily_limit = 100  # Maximum emails per day
        self.sent_today_file = "daily_email_count.json"
        self.error_log_file = "email_errors.json"
        
        # Initialize Gmail integration (revert to working version)
        try:
            self.gmail = GmailIntegration()
            print("✅ Gmail integration initialized")
        except Exception as e:
            print(f"❌ Gmail setup failed: {e}")
            print("📧 Emails will be template-only until Gmail is configured")
            self.gmail = None
    
    def _load_daily_count(self) -> int:
        """Load today's email count"""
        try:
            if os.path.exists(self.sent_today_file):
                with open(self.sent_today_file, 'r') as f:
                    data = json.load(f)
                    today = date.today().isoformat()
                    if data.get('date') == today:
                        return data.get('count', 0)
            return 0
        except Exception:
            return 0
    
    def _save_daily_count(self, count: int):
        """Save today's email count"""
        try:
            data = {
                'date': date.today().isoformat(),
                'count': count,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.sent_today_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save email count: {e}")
    
    def _log_error(self, prospect: Dict[str, Any], error: str):
        """Log email sending errors"""
        try:
            error_entry = {
                'timestamp': datetime.now().isoformat(),
                'prospect_name': prospect.get('contact_name', 'Unknown'),
                'prospect_email': prospect.get('email', 'Unknown'),
                'organization': prospect.get('organization_name', 'Unknown'),
                'error': str(error)
            }
            
            errors = []
            if os.path.exists(self.error_log_file):
                with open(self.error_log_file, 'r') as f:
                    errors = json.load(f)
            
            errors.append(error_entry)
            
            # Keep only last 100 errors
            if len(errors) > 100:
                errors = errors[-100:]
            
            with open(self.error_log_file, 'w') as f:
                json.dump(errors, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Could not log error: {e}")
    
    def can_send_more_emails(self) -> bool:
        """Check if we can send more emails today"""
        sent_today = self._load_daily_count()
        return sent_today < self.daily_limit
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """Get daily email sending statistics"""
        sent_today = self._load_daily_count()
        return {
            'sent_today': sent_today,
            'remaining_today': max(0, self.daily_limit - sent_today),
            'daily_limit': self.daily_limit,
            'gmail_ready': self.gmail is not None
        }
    
    def send_email_to_prospect(self, prospect: Dict[str, Any]) -> Dict[str, Any]:
        """Send styled email to a single prospect"""
        
        # Check daily limit
        if not self.can_send_more_emails():
            return {
                'success': False,
                'reason': 'daily_limit_reached',
                'message': f'Daily limit of {self.daily_limit} emails reached'
            }
        
        # Check Gmail availability
        if not self.gmail:
            return {
                'success': False,
                'reason': 'gmail_not_configured',
                'message': 'Gmail integration not available - email saved as template only'
            }
        
        try:
            # Verify email before sending (NEW RULE ENFORCEMENT)
            should_send, verification_reason = should_send_email(prospect)
            if not should_send:
                return {
                    'success': False,
                    'reason': 'email_verification_failed',
                    'message': f'Email verification failed: {verification_reason}',
                    'verification_details': verification_reason
                }
            
            # Generate styled email with corrected formatting rules
            styled_email = create_styled_email(prospect)
            
            # Send via Gmail
            result = self.gmail.send_email(
                to_email=styled_email['recipient_email'],
                subject=styled_email['subject'],
                body=styled_email['body']
            )
            
            if result.get('success', False):
                # Update daily count
                sent_today = self._load_daily_count()
                self._save_daily_count(sent_today + 1)
                
                print(f"📧 Email sent to {prospect['contact_name']} at {prospect['organization_name']}")
                
                return {
                    'success': True,
                    'message_id': result.get('message_id'),
                    'sent_time': datetime.now().isoformat(),
                    'recipient': styled_email['recipient_email'],
                    'subject': styled_email['subject']
                }
            else:
                error_msg = result.get('error', 'Unknown error')
                self._log_error(prospect, error_msg)
                
                return {
                    'success': False,
                    'reason': 'gmail_send_failed',
                    'message': f'Gmail send failed: {error_msg}'
                }
        
        except Exception as e:
            self._log_error(prospect, str(e))
            
            return {
                'success': False,
                'reason': 'exception',
                'message': f'Error sending email: {str(e)}'
            }
    
    def send_batch_emails(self, prospects: List[Dict[str, Any]], priority_first: bool = True) -> Dict[str, Any]:
        """Send emails to a batch of prospects"""
        
        # Sort by priority if requested
        if priority_first:
            prospects = sorted(prospects, key=lambda x: 
                0 if x.get('priority') == 'High' else 
                1 if x.get('priority') == 'Medium' else 2)
        
        results = {
            'sent_count': 0,
            'failed_count': 0,
            'skipped_count': 0,
            'details': [],
            'daily_stats': self.get_daily_stats()
        }
        
        print(f"📧 Starting batch email send for {len(prospects)} prospects")
        print(f"📊 Daily stats: {results['daily_stats']}")
        
        for i, prospect in enumerate(prospects, 1):
            if not self.can_send_more_emails():
                print(f"⚠️ Daily limit reached after {results['sent_count']} emails")
                results['skipped_count'] = len(prospects) - i + 1
                break
            
            print(f"\n📧 [{i}/{len(prospects)}] Sending to {prospect['contact_name']}...")
            
            send_result = self.send_email_to_prospect(prospect)
            
            prospect_result = {
                'prospect_name': prospect['contact_name'],
                'organization': prospect['organization_name'],
                'email': prospect['email'],
                'priority': prospect.get('priority', 'Unknown'),
                'send_result': send_result
            }
            
            results['details'].append(prospect_result)
            
            if send_result['success']:
                results['sent_count'] += 1
                print(f"   ✅ Sent successfully")
            else:
                results['failed_count'] += 1
                print(f"   ❌ Failed: {send_result['message']}")
        
        # Update final stats
        results['final_daily_stats'] = self.get_daily_stats()
        
        print(f"\n📊 Batch Email Summary:")
        print(f"✅ Sent: {results['sent_count']}")
        print(f"❌ Failed: {results['failed_count']}")
        print(f"⏭️ Skipped: {results['skipped_count']}")
        print(f"📈 Daily total: {results['final_daily_stats']['sent_today']}/{self.daily_limit}")
        
        return results

def update_google_sheets_with_email_status(prospect: Dict[str, Any], send_result: Dict[str, Any]):
    """Update Google Sheets with actual email sending status"""
    try:
        config = GoogleSheetsConfig(
            spreadsheet_name="GFMD Swarm Agent Data",
            credentials_file="google_sheets_credentials.json"
        )
        
        exporter = GoogleSheetsExporter(config)
        
        # Generate styled email for the sheet
        styled_email = create_styled_email(prospect)
        
        # Update email data with actual sending status
        email_data = {
            'id': f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'recipient_email': prospect['email'],
            'subject': styled_email['subject'],
            'body': styled_email['body'],
            'sent_successfully': send_result['success'],
            'day_number': '1',
            'send_status': 'SENT' if send_result['success'] else f"FAILED: {send_result.get('reason', 'unknown')}",
            'message_id': send_result.get('message_id', ''),
            'sent_time': send_result.get('sent_time', '')
        }
        
        exporter.export_sent_email(email_data)
        
    except Exception as e:
        print(f"⚠️ Could not update Google Sheets: {e}")

if __name__ == "__main__":
    # Test the automatic email sender
    print("🧪 Testing Automatic Email Sender")
    print("=" * 50)
    
    sender = AutomaticEmailSender()
    stats = sender.get_daily_stats()
    
    print("📊 Current Status:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test email generation without sending
    test_prospect = {
        'contact_name': 'Jennifer Martinez',
        'organization_name': 'Regional Medical Center',
        'location': 'Houston, TX',
        'pain_point': 'Noise complaints from adjacent patient areas',
        'facility_type': 'Regional Medical Center Lab',
        'budget_range': '$100K-200K',
        'department': 'Clinical Laboratory',
        'email': 'j.martinez@regional.org',
        'priority': 'High'
    }
    
    print(f"\n📧 Generated email preview:")
    styled_email = create_styled_email(test_prospect)
    print(f"Subject: {styled_email['subject']}")
    print(f"To: {styled_email['recipient_email']}")
    print(f"\nBody:\n{styled_email['body']}")
    
    print(f"\n✅ Email sender ready with your styling rules:")
    print(f"• Hello [first name], greeting")
    print(f"• Best, closing")
    print(f"• No emojis or bullets") 
    print(f"• Professional human tone")
    print(f"• Daily limit: {sender.daily_limit} emails")