#!/usr/bin/env python3
"""
Fix contact email_status field to make them available for outreach
"""

from firestore_service import FirestoreService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_contact_status():
    """Update all contacts to have proper email_status"""
    firestore = FirestoreService()
    
    logger.info("Fixing contact email_status fields...")
    
    # Get all contacts (using a large limit)
    try:
        contacts_ref = firestore.contacts_ref
        docs = contacts_ref.limit(10000).stream()
        
        updated_count = 0
        total_count = 0
        
        for doc in docs:
            total_count += 1
            doc_data = doc.to_dict()
            
            # Check if contact has email and needs status update
            if doc_data.get('email') and not doc_data.get('email_status'):
                # Update the contact with email_status = 'pending'
                doc.reference.update({
                    'email_status': 'pending',
                    'last_contacted': None,  # Ensure they're available for outreach
                    'email_sent_count': doc_data.get('email_sent_count', 0)
                })
                updated_count += 1
                
                if updated_count % 100 == 0:
                    logger.info(f"Updated {updated_count} contacts so far...")
        
        logger.info(f"✅ Fix completed!")
        logger.info(f"Total contacts processed: {total_count}")
        logger.info(f"Contacts updated: {updated_count}")
        
        # Test the fix
        logger.info("Testing contact availability...")
        available_contacts = firestore.get_contacts_for_outreach(limit=10)
        logger.info(f"✅ Now {len(available_contacts)} contacts available for outreach!")
        
        # Show sample contact details
        if available_contacts:
            sample = available_contacts[0]
            logger.info(f"Sample contact: {sample.get('contact_name', 'Unknown')} - {sample.get('email', 'No email')}")
            
    except Exception as e:
        logger.error(f"Error fixing contacts: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_contact_status()