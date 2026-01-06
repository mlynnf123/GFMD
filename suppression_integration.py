#!/usr/bin/env python3
"""
Suppression Integration for GFMD Email System
Integrates suppression checking into the existing email automation workflow.
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
from mongodb_storage import MongoDBStorage
from email_reply_monitor import EmailReplyMonitor

logger = logging.getLogger(__name__)

class SuppressionManager:
    """Manages email suppression and integrates with existing email workflows"""
    
    def __init__(self):
        """Initialize suppression manager"""
        try:
            self.storage = MongoDBStorage()
            self.reply_monitor = EmailReplyMonitor()
            logger.info("✅ Suppression Manager initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Suppression Manager: {e}")
            raise
    
    def is_suppressed(self, email: str) -> Dict[str, any]:
        """
        Check if an email address is suppressed
        
        Args:
            email: Email address to check
            
        Returns:
            Dict with suppression status and details
        """
        try:
            email = email.lower().strip()
            
            # Check suppression list
            suppression_record = self.storage.db.suppression_list.find_one({
                'email': email,
                'status': 'active'
            })
            
            if suppression_record:
                return {
                    'is_suppressed': True,
                    'reason': suppression_record.get('reason', 'Unknown'),
                    'suppressed_at': suppression_record.get('suppressed_at'),
                    'source': suppression_record.get('source', {})
                }
            
            # Also check contact status
            contact = self.storage.get_contact_by_email(email)
            if contact and contact.get('status') == 'suppressed':
                return {
                    'is_suppressed': True,
                    'reason': contact.get('suppression_reason', 'Contact marked as suppressed'),
                    'suppressed_at': contact.get('suppressed_at'),
                    'source': {'type': 'contact_status'}
                }
            
            return {
                'is_suppressed': False,
                'reason': None,
                'suppressed_at': None,
                'source': None
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking suppression status for {email}: {e}")
            # Return False to avoid blocking legitimate emails on error
            return {
                'is_suppressed': False,
                'reason': None,
                'suppressed_at': None,
                'source': None
            }
    
    def filter_suppressed_contacts(self, contact_list: List[Dict]) -> List[Dict]:
        """
        Filter out suppressed contacts from a list
        
        Args:
            contact_list: List of contact dictionaries
            
        Returns:
            Filtered list with suppressed contacts removed
        """
        filtered_contacts = []
        suppressed_count = 0
        
        for contact in contact_list:
            email = contact.get('email', '').lower()
            if not email:
                continue
                
            suppression_status = self.is_suppressed(email)
            
            if suppression_status['is_suppressed']:
                suppressed_count += 1
                logger.info(f"🚫 Filtered suppressed contact: {email} - {suppression_status['reason']}")
                continue
            
            filtered_contacts.append(contact)
        
        if suppressed_count > 0:
            logger.info(f"📧 Filtered {suppressed_count} suppressed contacts from {len(contact_list)} total")
        
        return filtered_contacts
    
    def pre_send_check(self, email: str, campaign_id: str = None) -> bool:
        """
        Perform pre-send suppression check
        
        Args:
            email: Email address to check
            campaign_id: Optional campaign ID for logging
            
        Returns:
            True if safe to send, False if suppressed
        """
        suppression_status = self.is_suppressed(email)
        
        if suppression_status['is_suppressed']:
            # Log the blocked send attempt
            self.storage.db.email_blocks.insert_one({
                'email': email.lower(),
                'blocked_at': datetime.utcnow(),
                'reason': suppression_status['reason'],
                'campaign_id': campaign_id,
                'suppression_source': suppression_status['source']
            })
            
            logger.warning(f"🚫 Blocked email to suppressed contact: {email} - {suppression_status['reason']}")
            return False
        
        return True
    
    def handle_bounce(self, email: str, bounce_type: str, bounce_details: Dict):
        """
        Handle email bounce by adding to suppression list
        
        Args:
            email: Bounced email address
            bounce_type: Type of bounce (hard/soft/permanent)
            bounce_details: Additional bounce information
        """
        try:
            # Log the bounce
            bounce_record = {
                'email': email.lower(),
                'bounce_date': datetime.utcnow(),
                'bounce_type': bounce_type,
                'details': bounce_details
            }
            
            self.storage.db.bounce_log.insert_one(bounce_record)
            
            # Add to suppression list for hard bounces
            if bounce_type in ['hard', 'permanent', 'invalid']:
                reason = f"Email bounce - {bounce_type}"
                source_data = {
                    'type': 'bounce',
                    'bounce_type': bounce_type,
                    'bounce_details': bounce_details
                }
                
                self.reply_monitor.add_to_suppression_list(email, reason, source_data)
                logger.info(f"📮 Added bounced email to suppression list: {email}")
            
        except Exception as e:
            logger.error(f"❌ Error handling bounce for {email}: {e}")
    
    def manual_suppress(self, email: str, reason: str, admin_user: str = "system"):
        """
        Manually add email to suppression list
        
        Args:
            email: Email to suppress
            reason: Reason for suppression
            admin_user: User who initiated the suppression
        """
        try:
            source_data = {
                'type': 'manual',
                'admin_user': admin_user,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.reply_monitor.add_to_suppression_list(email, reason, source_data)
            logger.info(f"👤 Manual suppression added by {admin_user}: {email} - {reason}")
            
        except Exception as e:
            logger.error(f"❌ Error manually suppressing {email}: {e}")
    
    def unsuppress_contact(self, email: str, admin_user: str = "system"):
        """
        Remove email from suppression list (use carefully!)
        
        Args:
            email: Email to unsuppress
            admin_user: User who initiated the unsuppression
        """
        try:
            # Mark suppression record as inactive
            result = self.storage.db.suppression_list.update_one(
                {'email': email.lower(), 'status': 'active'},
                {
                    '$set': {
                        'status': 'inactive',
                        'unsuppressed_at': datetime.utcnow(),
                        'unsuppressed_by': admin_user
                    }
                }
            )
            
            if result.modified_count > 0:
                # Update contact status
                self.storage.update_contact(email, {
                    'status': 'active',
                    'suppressed_at': None,
                    'suppression_reason': None,
                    'unsuppressed_at': datetime.utcnow(),
                    'unsuppressed_by': admin_user
                })
                
                logger.info(f"✅ Contact unsuppressed by {admin_user}: {email}")
                return True
            else:
                logger.warning(f"⚠️ No active suppression found for {email}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error unsuppressing {email}: {e}")
            return False
    
    def get_suppression_report(self, days: int = 30) -> Dict[str, any]:
        """
        Generate suppression report for the last N days
        
        Args:
            days: Number of days to include in report
            
        Returns:
            Dict with suppression statistics and details
        """
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Recent suppressions
            recent_suppressions = list(self.storage.db.suppression_list.find({
                'suppressed_at': {'$gte': since_date},
                'status': 'active'
            }).sort('suppressed_at', -1))
            
            # Group by reason
            reason_stats = {}
            for suppression in recent_suppressions:
                reason = suppression.get('reason', 'Unknown')
                reason_stats[reason] = reason_stats.get(reason, 0) + 1
            
            # Recent bounces
            recent_bounces = list(self.storage.db.bounce_log.find({
                'bounce_date': {'$gte': since_date}
            }).sort('bounce_date', -1))
            
            # Blocked sends
            blocked_sends = self.storage.db.email_blocks.count_documents({
                'blocked_at': {'$gte': since_date}
            })
            
            # Total active suppressions
            total_suppressions = self.storage.db.suppression_list.count_documents({
                'status': 'active'
            })
            
            report = {
                'period_days': days,
                'period_start': since_date.isoformat(),
                'recent_suppressions': len(recent_suppressions),
                'total_active_suppressions': total_suppressions,
                'recent_bounces': len(recent_bounces),
                'blocked_sends': blocked_sends,
                'suppression_reasons': reason_stats,
                'suppression_details': recent_suppressions[:10],  # Last 10
                'bounce_details': recent_bounces[:10]  # Last 10
            }
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating suppression report: {e}")
            return {}

# Integration helper functions for existing email system

def check_email_before_send(email: str, campaign_id: str = None) -> bool:
    """
    Helper function to check suppression status before sending email
    Use this in your existing email sending functions
    
    Args:
        email: Email address to check
        campaign_id: Optional campaign ID
        
    Returns:
        True if safe to send, False if suppressed
    """
    try:
        suppression_manager = SuppressionManager()
        return suppression_manager.pre_send_check(email, campaign_id)
    except Exception as e:
        logger.error(f"❌ Error in pre-send check: {e}")
        # Return True on error to avoid blocking legitimate emails
        return True

def filter_contact_list(contacts: List[Dict]) -> List[Dict]:
    """
    Helper function to filter suppressed contacts from a list
    
    Args:
        contacts: List of contact dictionaries with 'email' field
        
    Returns:
        Filtered list with suppressed contacts removed
    """
    try:
        suppression_manager = SuppressionManager()
        return suppression_manager.filter_suppressed_contacts(contacts)
    except Exception as e:
        logger.error(f"❌ Error filtering contacts: {e}")
        # Return original list on error
        return contacts

def main():
    """Test suppression integration"""
    print("🔧 Testing GFMD Suppression Integration")
    print("=" * 50)
    
    try:
        manager = SuppressionManager()
        
        # Test suppression check
        test_email = "test@example.com"
        status = manager.is_suppressed(test_email)
        print(f"📧 Test email suppression status: {status}")
        
        # Generate recent report
        report = manager.get_suppression_report(days=7)
        print(f"\n📊 Recent suppression activity:")
        print(f"  - Recent suppressions: {report.get('recent_suppressions', 0)}")
        print(f"  - Total active suppressions: {report.get('total_active_suppressions', 0)}")
        print(f"  - Recent bounces: {report.get('recent_bounces', 0)}")
        print(f"  - Blocked sends: {report.get('blocked_sends', 0)}")
        
        print("\n✅ Suppression integration test complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()