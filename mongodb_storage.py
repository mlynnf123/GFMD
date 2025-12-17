#!/usr/bin/env python3
"""
MongoDB Storage for GFMD Narcon Outreach System
Replaces simple_storage.py with enterprise-grade database storage
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database

logger = logging.getLogger(__name__)

class MongoDBStorage:
    """MongoDB storage for contacts, campaigns, and email tracking"""

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string: MongoDB Atlas connection string
        """
        self.connection_string = connection_string or os.environ.get('MONGODB_CONNECTION_STRING')
        
        if not self.connection_string:
            raise ValueError("MongoDB connection string required. Set MONGODB_CONNECTION_STRING environment variable.")
        
        # Initialize MongoDB client
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client.gfmd_narc_gone
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ MongoDB connection successful")
            
            # Initialize collections
            self._init_collections()
            self._create_indexes()
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise
    
    def _init_collections(self):
        """Initialize MongoDB collections"""
        self.contacts: Collection = self.db.contacts
        self.interactions: Collection = self.db.interactions
        self.campaigns: Collection = self.db.campaigns
        self.sequences: Collection = self.db.sequences
        self.orders: Collection = self.db.orders
        self.email_sequences: Collection = self.db.email_sequences
        
        logger.info("📊 MongoDB collections initialized")
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        try:
            # Contact indexes
            self.contacts.create_index("email", unique=True)
            self.contacts.create_index("organizationType")
            self.contacts.create_index("status")
            self.contacts.create_index("qualificationScore")
            
            # Interaction indexes
            self.interactions.create_index([("contactId", ASCENDING), ("timestamp", DESCENDING)])
            self.interactions.create_index("type")
            self.interactions.create_index("campaignId")
            
            # Campaign indexes
            self.campaigns.create_index("status")
            self.campaigns.create_index("createdAt")
            
            # Email sequence indexes
            self.email_sequences.create_index("contact_id", unique=True)
            self.email_sequences.create_index("status")
            self.email_sequences.create_index("next_email_due")
            self.email_sequences.create_index([("status", ASCENDING), ("next_email_due", ASCENDING)])
            
            logger.info("🔍 Database indexes created")
        except Exception as e:
            logger.warning(f"⚠️ Index creation warning: {e}")
    
    # Contact Management
    def add_contact(self, contact_data: Dict[str, Any]) -> str:
        """Add a new contact to database"""
        try:
            # Add metadata
            contact_data.update({
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow(),
                'status': contact_data.get('status', 'new'),
                'isAttributed': False,
                'campaigns': [],
                'orders': []
            })
            
            result = self.contacts.insert_one(contact_data)
            contact_id = str(result.inserted_id)
            
            logger.info(f"➕ Contact added: {contact_data.get('email')} -> {contact_id}")
            return contact_id
            
        except Exception as e:
            logger.error(f"❌ Failed to add contact: {e}")
            raise
    
    def get_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get contact by email address"""
        try:
            contact = self.contacts.find_one({"email": email.lower()})
            if contact:
                contact['_id'] = str(contact['_id'])
            return contact
        except Exception as e:
            logger.error(f"❌ Failed to get contact: {e}")
            return None
    
    def update_contact(self, email: str, update_data: Dict[str, Any]) -> bool:
        """Update contact information"""
        try:
            update_data['updatedAt'] = datetime.utcnow()
            
            result = self.contacts.update_one(
                {"email": email.lower()},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Contact updated: {email}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to update contact: {e}")
            return False
    
    def get_contacts_for_campaign(self, 
                                 organization_types: List[str] = None,
                                 min_qualification_score: int = 50,
                                 exclude_recent_contact_days: int = 30,
                                 limit: int = 100) -> List[Dict[str, Any]]:
        """Get contacts suitable for outreach campaign"""
        try:
            # Build query
            query = {
                'status': {'$in': ['new', 'active']},
                'qualificationScore': {'$gte': min_qualification_score}
            }
            
            if organization_types:
                query['organizationType'] = {'$in': organization_types}
            
            # Exclude recently contacted
            if exclude_recent_contact_days > 0:
                cutoff_date = datetime.utcnow() - timedelta(days=exclude_recent_contact_days)
                query['lastContactDate'] = {'$lt': cutoff_date}
            
            contacts = list(self.contacts.find(query).limit(limit))
            
            # Convert ObjectId to string
            for contact in contacts:
                contact['_id'] = str(contact['_id'])
            
            logger.info(f"📋 Retrieved {len(contacts)} contacts for campaign")
            return contacts
            
        except Exception as e:
            logger.error(f"❌ Failed to get campaign contacts: {e}")
            return []
    
    # Email Tracking
    def record_email_sent(self, 
                         contact_email: str,
                         subject: str,
                         campaign_id: str,
                         sequence_id: str = None,
                         sequence_step: int = 1,
                         message_id: str = None) -> str:
        """Record an email being sent"""
        try:
            interaction_data = {
                'contactEmail': contact_email.lower(),
                'type': 'email_sent',
                'channel': 'email',
                'campaignId': campaign_id,
                'sequenceId': sequence_id,
                'sequenceStep': sequence_step,
                'subject': subject,
                'messageId': message_id,
                'timestamp': datetime.utcnow(),
                'openedAt': None,
                'clickedLinks': [],
                'repliedAt': None,
                'replyText': None
            }
            
            result = self.interactions.insert_one(interaction_data)
            interaction_id = str(result.inserted_id)
            
            # Update contact's last contact date
            self.update_contact(contact_email, {
                'lastContactDate': datetime.utcnow(),
                'currentSequence': sequence_id,
                'sequenceStep': sequence_step
            })
            
            logger.info(f"📧 Email sent recorded: {contact_email}")
            return interaction_id
            
        except Exception as e:
            logger.error(f"❌ Failed to record email sent: {e}")
            raise
    
    def record_email_opened(self, message_id: str) -> bool:
        """Record an email being opened"""
        try:
            result = self.interactions.update_one(
                {'messageId': message_id, 'type': 'email_sent'},
                {
                    '$set': {'openedAt': datetime.utcnow()},
                    '$inc': {'openCount': 1}
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"👀 Email opened: {message_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to record email open: {e}")
            return False
    
    def record_email_clicked(self, message_id: str, clicked_url: str) -> bool:
        """Record an email link being clicked"""
        try:
            result = self.interactions.update_one(
                {'messageId': message_id, 'type': 'email_sent'},
                {
                    '$push': {'clickedLinks': {
                        'url': clicked_url,
                        'timestamp': datetime.utcnow()
                    }}
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"🔗 Email clicked: {message_id} -> {clicked_url}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to record email click: {e}")
            return False
    
    def record_email_reply(self, message_id: str, reply_text: str) -> bool:
        """Record an email reply"""
        try:
            result = self.interactions.update_one(
                {'messageId': message_id, 'type': 'email_sent'},
                {
                    '$set': {
                        'repliedAt': datetime.utcnow(),
                        'replyText': reply_text
                    }
                }
            )
            
            if result.modified_count > 0:
                # Mark contact as engaged
                contact_email = self.interactions.find_one(
                    {'messageId': message_id}
                )['contactEmail']
                
                self.update_contact(contact_email, {
                    'status': 'engaged',
                    'lastEngagementDate': datetime.utcnow()
                })
                
                logger.info(f"💬 Email reply recorded: {message_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to record email reply: {e}")
            return False
    
    # Campaign Management
    def create_campaign(self, campaign_data: Dict[str, Any]) -> str:
        """Create a new campaign"""
        try:
            campaign_data.update({
                'createdAt': datetime.utcnow(),
                'startDate': datetime.utcnow(),
                'endDate': None,
                'stats': {
                    'totalContacts': 0,
                    'emailsSent': 0,
                    'emailsOpened': 0,
                    'emailsClicked': 0,
                    'emailsReplied': 0,
                    'conversions': 0,
                    'revenue': 0.0
                }
            })
            
            result = self.campaigns.insert_one(campaign_data)
            campaign_id = str(result.inserted_id)
            
            logger.info(f"🚀 Campaign created: {campaign_data.get('name')} -> {campaign_id}")
            return campaign_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create campaign: {e}")
            raise
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign performance statistics"""
        try:
            # Get campaign info
            campaign = self.campaigns.find_one({"_id": campaign_id})
            if not campaign:
                return {}
            
            # Calculate stats from interactions
            stats = {
                'emailsSent': self.interactions.count_documents({
                    'campaignId': campaign_id,
                    'type': 'email_sent'
                }),
                'emailsOpened': self.interactions.count_documents({
                    'campaignId': campaign_id,
                    'type': 'email_sent',
                    'openedAt': {'$exists': True}
                }),
                'emailsClicked': self.interactions.count_documents({
                    'campaignId': campaign_id,
                    'type': 'email_sent',
                    'clickedLinks': {'$exists': True, '$ne': []}
                }),
                'emailsReplied': self.interactions.count_documents({
                    'campaignId': campaign_id,
                    'type': 'email_sent',
                    'repliedAt': {'$exists': True}
                })
            }
            
            # Calculate rates
            if stats['emailsSent'] > 0:
                stats['openRate'] = round(stats['emailsOpened'] / stats['emailsSent'] * 100, 2)
                stats['clickRate'] = round(stats['emailsClicked'] / stats['emailsSent'] * 100, 2)
                stats['replyRate'] = round(stats['emailsReplied'] / stats['emailsSent'] * 100, 2)
            else:
                stats['openRate'] = stats['clickRate'] = stats['replyRate'] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get campaign stats: {e}")
            return {}
    
    # Order Tracking (for recurring Narcon sales)
    def record_order(self, order_data: Dict[str, Any]) -> str:
        """Record a Narcon order for attribution and reorder tracking"""
        try:
            order_data.update({
                'recordedAt': datetime.utcnow(),
                'isRecurring': order_data.get('isRecurring', False)
            })
            
            result = self.orders.insert_one(order_data)
            order_id = str(result.inserted_id)
            
            # Update contact with order info
            if 'contactEmail' in order_data:
                contact = self.get_contact_by_email(order_data['contactEmail'])
                if contact:
                    # Add order to contact
                    order_summary = {
                        'orderId': order_id,
                        'date': order_data.get('orderDate', datetime.utcnow()),
                        'product': order_data.get('product'),
                        'quantity': order_data.get('quantity', 1),
                        'revenue': order_data.get('revenue', 0.0)
                    }
                    
                    self.contacts.update_one(
                        {"email": order_data['contactEmail'].lower()},
                        {
                            '$push': {'orders': order_summary},
                            '$set': {
                                'status': 'customer',
                                'lastOrderDate': order_data.get('orderDate', datetime.utcnow()),
                                'isAttributed': True,
                                'attributionDate': datetime.utcnow(),
                                'updatedAt': datetime.utcnow()
                            }
                        }
                    )
            
            logger.info(f"💰 Order recorded: {order_id}")
            return order_id
            
        except Exception as e:
            logger.error(f"❌ Failed to record order: {e}")
            raise
    
    def get_reorder_candidates(self, days_since_last_order: int = 90) -> List[Dict[str, Any]]:
        """Get customers who may be ready for reorder"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_since_last_order)
            
            pipeline = [
                {
                    '$match': {
                        'status': 'customer',
                        'lastOrderDate': {'$lte': cutoff_date}
                    }
                },
                {
                    '$project': {
                        'email': 1,
                        'firstName': 1,
                        'lastName': 1,
                        'organization': 1,
                        'lastOrderDate': 1,
                        'orders': 1,
                        'daysSinceLastOrder': {
                            '$divide': [
                                {'$subtract': [datetime.utcnow(), '$lastOrderDate']},
                                86400000  # milliseconds in a day
                            ]
                        }
                    }
                }
            ]
            
            candidates = list(self.contacts.aggregate(pipeline))
            
            # Convert ObjectId to string
            for candidate in candidates:
                candidate['_id'] = str(candidate['_id'])
            
            logger.info(f"🔄 Found {len(candidates)} reorder candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"❌ Failed to get reorder candidates: {e}")
            return []
    
    # Email Sequence Helper Methods
    async def find_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Async version of get_contact_by_email for sequence orchestrator"""
        return self.get_contact_by_email(email)
    
    async def get_contact(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get contact by ID"""
        try:
            from bson import ObjectId
            contact = self.contacts.find_one({"_id": ObjectId(contact_id)})
            if contact:
                contact['_id'] = str(contact['_id'])
            return contact
        except Exception as e:
            logger.error(f"❌ Failed to get contact by ID: {e}")
            return None
    
    async def log_interaction(self, contact_id: str, interaction_type: str, data: Dict[str, Any]):
        """Log an interaction for a contact"""
        try:
            interaction_data = {
                'contactId': contact_id,
                'type': interaction_type,
                'timestamp': datetime.utcnow(),
                'data': data
            }
            
            result = self.interactions.insert_one(interaction_data)
            logger.info(f"📝 Interaction logged: {interaction_type} for {contact_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log interaction: {e}")
            raise
    
    def close_connection(self):
        """Close MongoDB connection"""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("🔒 MongoDB connection closed")


# Utility function for easy initialization
def get_mongodb_storage() -> MongoDBStorage:
    """Get MongoDB storage instance with environment configuration"""
    return MongoDBStorage()


if __name__ == "__main__":
    print("🧪 Testing MongoDB Storage")
    print("=" * 50)
    
    # Test connection (requires MONGODB_CONNECTION_STRING environment variable)
    try:
        storage = MongoDBStorage()
        print("✅ MongoDB connection successful")
        
        # Test basic operations
        test_contact = {
            'email': 'test.officer@police.gov',
            'firstName': 'John',
            'lastName': 'Smith',
            'title': 'Property & Evidence Manager',
            'organization': 'City Police Department',
            'organizationType': 'police',
            'location': {
                'city': 'Austin',
                'state': 'TX',
                'zipCode': '78701'
            },
            'qualificationScore': 85
        }
        
        print("\n📝 Testing contact operations...")
        # Add contact
        contact_id = storage.add_contact(test_contact)
        print(f"   Contact added with ID: {contact_id}")
        
        # Get contact
        retrieved_contact = storage.get_contact_by_email('test.officer@police.gov')
        print(f"   Contact retrieved: {retrieved_contact['firstName']} {retrieved_contact['lastName']}")
        
        print("\n📧 Testing email tracking...")
        # Record email sent
        interaction_id = storage.record_email_sent(
            contact_email='test.officer@police.gov',
            subject='Safer Drug Destruction for City Police Department',
            campaign_id='test_campaign_001',
            sequence_id='narc_gone_cold_outreach_v1',
            message_id='test_msg_123'
        )
        print(f"   Email interaction recorded: {interaction_id}")
        
        print("\n📊 Storage system ready for Narcon outreach!")
        
        storage.close_connection()
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        print("\nSetup required:")
        print("1. Create MongoDB Atlas account (free tier)")
        print("2. Set MONGODB_CONNECTION_STRING environment variable")
        print("3. Example: export MONGODB_CONNECTION_STRING='mongodb+srv://user:pass@cluster.mongodb.net/gfmd_narc_gone'")