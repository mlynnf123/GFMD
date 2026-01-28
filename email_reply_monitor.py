#!/usr/bin/env python3
"""
Email Reply Monitor and Suppression System
Monitors incoming email replies and automatically handles unsubscribe requests,
bounces, and negative responses by adding contacts to suppression list.
"""

import re
import logging
from datetime import datetime
from typing import List, Dict, Set, Optional
from mongodb_storage import MongoDBStorage
from gmail_integration import GmailIntegration

logger = logging.getLogger(__name__)

class EmailReplyMonitor:
    """Monitor email replies and handle suppression automatically"""
    
    # Comprehensive list of unsubscribe/stop keywords and phrases
    STOP_KEYWORDS = {
        # Direct unsubscribe requests
        'stop', 'unsubscribe', 'remove', 'opt out', 'opt-out', 'optout',
        'take me off', 'remove me', 'delete me', 'no more emails',
        
        # Not interested responses
        'not interested', 'no interest', 'not relevant', 'irrelevant',
        'no thank you', 'no thanks', 'not needed', 'dont need', "don't need",
        'not for us', 'not for me', 'wrong person', 'wrong contact',
        
        # Professional decline responses
        'not in the market', 'not looking', 'not purchasing', 'budget constraints',
        'already have vendor', 'have supplier', 'under contract',
        'policy against', 'cannot purchase', 'not authorized',
        
        # Angry/negative responses  
        'spam', 'junk', 'harassment', 'stop bothering', 'leave me alone',
        'cease contact', 'do not contact', 'dont contact', "don't contact",
        'blocked', 'report spam', 'unsolicited',
        
        # Bounce-related keywords
        'mail not delivered', 'delivery failed', 'failed to deliver', 'undeliverable', 
        'mailbox full', 'user unknown', 'invalid recipient',
        'address not found', 'does not exist', 'bounce', 'returned mail',
        
        # Auto-responders indicating unavailability
        'out of office', 'on vacation', 'no longer with', 'left the company',
        'changed position', 'retired', 'terminated employment'
    }
    
    # Patterns for detecting auto-replies and bounces
    BOUNCE_PATTERNS = [
        r'delivery.*fail',
        r'mail.*delivery.*subsystem',
        r'postmaster',
        r'mailer.*daemon',
        r'delivery.*status.*notification',
        r'undelivered.*mail',
        r'returned.*mail'
    ]
    
    # Patterns for out-of-office auto-replies
    OOO_PATTERNS = [
        r'out.*of.*office',
        r'automatic.*reply',
        r'auto.*reply',
        r'vacation.*reply',
        r'away.*message'
    ]

    def __init__(self):
        """Initialize reply monitor with database and Gmail connections"""
        try:
            self.storage = MongoDBStorage()
            self.gmail = GmailIntegration()
            logger.info("✅ Email Reply Monitor initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Email Reply Monitor: {e}")
            raise

    def analyze_email_content(self, email_content: str, subject: str = "") -> Dict[str, any]:
        """
        Analyze email content for suppression triggers
        
        Args:
            email_content: The email body text
            subject: Email subject line
            
        Returns:
            Dict with analysis results
        """
        content_lower = email_content.lower()
        subject_lower = subject.lower()
        full_text = f"{subject_lower} {content_lower}"
        
        analysis = {
            'should_suppress': False,
            'suppression_reason': None,
            'keywords_found': [],
            'confidence': 0,
            'response_type': 'unknown'
        }
        
        # Check for direct unsubscribe keywords
        found_keywords = []
        for keyword in self.STOP_KEYWORDS:
            if keyword in full_text:
                found_keywords.append(keyword)
        
        if found_keywords:
            analysis['keywords_found'] = found_keywords
            analysis['should_suppress'] = True
            analysis['confidence'] = min(100, len(found_keywords) * 20 + 60)
            
            # Determine response type
            if any(word in ['spam', 'junk', 'harassment'] for word in found_keywords):
                analysis['response_type'] = 'complaint'
                analysis['suppression_reason'] = 'Spam complaint'
            elif any(word in ['stop', 'unsubscribe', 'remove', 'opt out'] for word in found_keywords):
                analysis['response_type'] = 'unsubscribe'
                analysis['suppression_reason'] = 'Unsubscribe request'
            elif any(word in ['not interested', 'no interest'] for word in found_keywords):
                analysis['response_type'] = 'not_interested'
                analysis['suppression_reason'] = 'Not interested'
            else:
                analysis['response_type'] = 'negative'
                analysis['suppression_reason'] = 'Negative response'
        
        # Check for bounce patterns
        for pattern in self.BOUNCE_PATTERNS:
            if re.search(pattern, full_text, re.IGNORECASE):
                analysis['should_suppress'] = True
                analysis['response_type'] = 'bounce'
                analysis['suppression_reason'] = 'Mail delivery failure'
                analysis['confidence'] = 95
                break
        
        # Check for out-of-office (lower priority)
        for pattern in self.OOO_PATTERNS:
            if re.search(pattern, full_text, re.IGNORECASE):
                analysis['response_type'] = 'out_of_office'
                # Don't suppress for OOO unless it mentions permanent status
                if any(word in ['no longer', 'left', 'retired', 'terminated'] for word in found_keywords):
                    analysis['should_suppress'] = True
                    analysis['suppression_reason'] = 'Contact no longer available'
                    analysis['confidence'] = 80
                break
        
        return analysis

    def add_to_suppression_list(self, email: str, reason: str, source_data: Dict = None):
        """
        Add email to suppression list
        
        Args:
            email: Email address to suppress
            reason: Reason for suppression
            source_data: Additional data about the suppression
        """
        try:
            suppression_record = {
                'email': email.lower(),
                'suppressed_at': datetime.utcnow(),
                'reason': reason,
                'source': source_data or {},
                'status': 'active'
            }
            
            # Check if already suppressed
            existing = self.storage.db.suppression_list.find_one({'email': email.lower()})
            if existing:
                logger.info(f"📧 {email} already suppressed")
                return
            
            # Add to suppression list
            self.storage.db.suppression_list.insert_one(suppression_record)
            
            # Mark contact as suppressed in main contacts collection
            self.storage.update_contact(email, {
                'status': 'suppressed',
                'suppressed_at': datetime.utcnow(),
                'suppression_reason': reason
            })
            
            # Stop any active email sequences
            self.storage.db.email_sequences.update_many(
                {'contact_email': email.lower(), 'status': 'active'},
                {'$set': {
                    'status': 'suppressed',
                    'stopped_at': datetime.utcnow(),
                    'stop_reason': reason
                }}
            )
            
            logger.info(f"🚫 Contact suppressed: {email} - {reason}")
            
        except Exception as e:
            logger.error(f"❌ Failed to add {email} to suppression list: {e}")

    def _extract_failed_recipient_from_bounce(self, content: str, subject: str) -> List[str]:
        """
        Extract failed recipient emails from a bounce message

        Args:
            content: Bounce message body
            subject: Bounce message subject

        Returns:
            List of failed recipient emails
        """
        full_text = f"{subject}\n{content}"
        failed_emails = set()

        # Skip patterns - system emails and tracking codes
        skip_patterns = [
            'postmaster', 'mailer-daemon', 'mail-daemon', 'noreply', 'no-reply',
            'solutions@gfmd', 'google.com', 'cafbhqf'  # Gmail tracking codes start with this
        ]

        # Look for emails in angle brackets (most reliable for bounce messages)
        bracket_pattern = r'<([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>'
        matches = re.findall(bracket_pattern, full_text, re.IGNORECASE)
        for match in matches:
            email = match.lower().strip()
            if not any(skip in email for skip in skip_patterns):
                failed_emails.add(email)

        # Additional patterns for bounce messages
        patterns = [
            r'delivery to the following recipient[s]? failed[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'failed recipient[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'the email account.*?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}).*?does not exist',
            r'address rejected[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'original-recipient[:\s]+.*?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'final-recipient[:\s]+.*?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'(?:to|recipient)[:\s]+<?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>?',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                email = match.lower().strip()
                if not any(skip in email for skip in skip_patterns):
                    failed_emails.add(email)

        return list(failed_emails)

    def _is_system_email(self, email: str) -> bool:
        """Check if email is a system/automated email that shouldn't be suppressed"""
        if not email:
            return True
        email_lower = email.lower()
        system_patterns = [
            'postmaster', 'mailer-daemon', 'mail-daemon', 'noreply', 'no-reply',
            'donotreply', 'do-not-reply', 'bounce', 'notifications@', 'alert@',
            'team@', 'hello@', 'news@', 'newsletter@', 'updates@', 'info@mongodb',
            'railway.app', 'vercel.com', 'github.com', 'google.com', 'gfmd.com'
        ]
        return any(pattern in email_lower for pattern in system_patterns)

    def process_gmail_replies(self, days_back: int = 1) -> Dict[str, int]:
        """
        Check Gmail for new replies and process them

        Args:
            days_back: How many days back to check for replies

        Returns:
            Dict with processing stats
        """
        stats = {
            'replies_checked': 0,
            'suppressions_added': 0,
            'bounces_detected': 0,
            'complaints_detected': 0
        }

        try:
            # Get recent emails (replies to our outbound emails)
            query = f'to:me newer_than:{days_back}d'
            emails = self.gmail.get_emails(query=query, max_results=100)

            for email in emails:
                stats['replies_checked'] += 1

                sender_email = email.get('from', '')
                subject = email.get('subject', '')
                content = email.get('body', '')

                # Skip if sender is a system email
                if self._is_system_email(sender_email):
                    # Check if this is a bounce - try to extract failed recipients
                    analysis = self.analyze_email_content(content, subject)

                    if analysis['response_type'] == 'bounce':
                        failed_recipients = self._extract_failed_recipient_from_bounce(content, subject)

                        for failed_recipient in failed_recipients:
                            if failed_recipient and not self._is_system_email(failed_recipient):
                                # Suppress the failed recipient, not the postmaster
                                source_data = {
                                    'email_id': email.get('id'),
                                    'subject': subject,
                                    'received_at': email.get('date'),
                                    'bounce_from': sender_email,
                                    'analysis': analysis
                                }

                                self.add_to_suppression_list(
                                    failed_recipient,
                                    'Email delivery failed - bounce detected',
                                    source_data
                                )

                                stats['suppressions_added'] += 1
                                stats['bounces_detected'] += 1
                                logger.info(f"Bounce detected: {failed_recipient} (from {sender_email})")

                    continue  # Skip further processing for system emails

                # Analyze the email content for human replies
                analysis = self.analyze_email_content(content, subject)

                if analysis['should_suppress']:
                    # Add to suppression list
                    source_data = {
                        'email_id': email.get('id'),
                        'subject': subject,
                        'received_at': email.get('date'),
                        'analysis': analysis
                    }

                    self.add_to_suppression_list(
                        sender_email,
                        analysis['suppression_reason'],
                        source_data
                    )

                    stats['suppressions_added'] += 1

                    if analysis['response_type'] == 'bounce':
                        stats['bounces_detected'] += 1
                    elif analysis['response_type'] == 'complaint':
                        stats['complaints_detected'] += 1

                # Record the reply in interactions
                try:
                    self.storage.record_email_reply(
                        message_id=email.get('references', ''),
                        reply_text=content[:500] if content else ''
                    )
                except Exception as e:
                    logger.warning(f"Failed to record reply: {e}")

            logger.info(f"Processed {stats['replies_checked']} replies, added {stats['suppressions_added']} suppressions")
            return stats

        except Exception as e:
            logger.error(f"Error processing Gmail replies: {e}")
            return stats

    def check_suppression_status(self, email: str) -> bool:
        """
        Check if an email is on the suppression list
        
        Args:
            email: Email address to check
            
        Returns:
            True if email should be suppressed, False otherwise
        """
        try:
            suppressed = self.storage.db.suppression_list.find_one({
                'email': email.lower(),
                'status': 'active'
            })
            return suppressed is not None
        except Exception as e:
            logger.error(f"❌ Error checking suppression status for {email}: {e}")
            return False

    def get_suppression_stats(self) -> Dict[str, int]:
        """Get statistics about suppressed contacts"""
        try:
            stats = {}
            
            # Total suppressed
            stats['total_suppressed'] = self.storage.db.suppression_list.count_documents({
                'status': 'active'
            })
            
            # By reason
            pipeline = [
                {'$match': {'status': 'active'}},
                {'$group': {'_id': '$reason', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}
            ]
            
            reason_stats = list(self.storage.db.suppression_list.aggregate(pipeline))
            for stat in reason_stats:
                reason = stat['_id'].replace(' ', '_').lower()
                stats[f'suppressed_{reason}'] = stat['count']
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting suppression stats: {e}")
            return {}

    def export_suppression_list(self) -> List[Dict]:
        """Export current suppression list for compliance"""
        try:
            suppressed_contacts = list(self.storage.db.suppression_list.find({
                'status': 'active'
            }).sort('suppressed_at', -1))
            
            # Clean up for export
            for contact in suppressed_contacts:
                contact['_id'] = str(contact['_id'])
                
            return suppressed_contacts
            
        except Exception as e:
            logger.error(f"❌ Error exporting suppression list: {e}")
            return []

def main():
    """Main function for testing reply monitor"""
    print("🔍 GFMD Email Reply Monitor")
    print("=" * 50)
    
    try:
        monitor = EmailReplyMonitor()
        
        # Process recent replies
        print("📧 Processing recent email replies...")
        stats = monitor.process_gmail_replies(days_back=1)
        
        print(f"✅ Processing complete:")
        print(f"   - Replies checked: {stats['replies_checked']}")
        print(f"   - New suppressions: {stats['suppressions_added']}")
        print(f"   - Bounces detected: {stats['bounces_detected']}")
        print(f"   - Complaints detected: {stats['complaints_detected']}")
        
        # Show current suppression stats
        print("\n📊 Current Suppression Statistics:")
        suppression_stats = monitor.get_suppression_stats()
        for key, value in suppression_stats.items():
            print(f"   - {key.replace('_', ' ').title()}: {value}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()