#!/usr/bin/env python3
"""
Test Firestore connection and basic operations
"""

from firestore_service import FirestoreService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_firestore():
    """Test basic Firestore operations"""
    try:
        # Initialize service
        firestore_service = FirestoreService()
        
        # Test adding a sample contact
        sample_contact = {
            'Business Email': 'test@example.com',
            'Hospital Name': 'Test Hospital',
            'Executive Name': 'John Doe',
            'City': 'Test City',
            'State': 'TS',
            'Office Phone': '555-0123',
            'Title': 'Laboratory Director',
            'Address': '123 Test St'
        }
        
        # Add the contact
        contact_id = firestore_service.add_contact(sample_contact)
        logger.info(f"Added test contact with ID: {contact_id}")
        
        # Get daily stats
        stats = firestore_service.get_daily_stats()
        logger.info(f"Daily stats: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_firestore()
    print(f"Test {'PASSED' if success else 'FAILED'}")