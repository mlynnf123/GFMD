#!/usr/bin/env python3
"""
Contact Manager - Simple interface for managing contacts and sequences
"""

import os
import json
from datetime import datetime
from mongodb_storage import MongoDBStorage
from complete_sequence_automation import CompleteSequenceAutomation
from bson import ObjectId

# Load environment variables
def load_env():
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    value = value.strip('"')
                    os.environ[key] = value
    except FileNotFoundError:
        pass

load_env()

class ContactManager:
    """Simple contact management interface"""
    
    def __init__(self):
        self.storage = MongoDBStorage()
        self.automation = CompleteSequenceAutomation()
    
    def get_dashboard_stats(self):
        """Get comprehensive dashboard statistics"""
        try:
            # Contact stats
            total_contacts = self.storage.contacts.count_documents({})
            
            # Sequence stats
            total_sequences = self.storage.db.email_sequences.count_documents({})
            active_sequences = self.storage.db.email_sequences.count_documents({"status": "active"})
            completed_sequences = self.storage.db.email_sequences.count_documents({"status": "completed"})
            replied_sequences = self.storage.db.email_sequences.count_documents({"status": "replied"})
            
            stats = {
                "contacts": total_contacts,
                "sequences": {
                    "total": total_sequences,
                    "active": active_sequences,
                    "completed": completed_sequences,
                    "replied": replied_sequences,
                    "response_rate": round((replied_sequences / total_sequences * 100) if total_sequences > 0 else 0, 2)
                }
            }
            
            print("📊 DASHBOARD STATISTICS")
            print("=" * 50)
            print(f"👥 Total Contacts: {stats['contacts']}")
            print(f"📧 Total Sequences: {stats['sequences']['total']}")
            print(f"   - Active: {stats['sequences']['active']}")
            print(f"   - Completed: {stats['sequences']['completed']}")
            print(f"   - Replied: {stats['sequences']['replied']}")
            print(f"   - Response Rate: {stats['sequences']['response_rate']}%")
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}

def main():
    manager = ContactManager()
    manager.get_dashboard_stats()

if __name__ == "__main__":
    main()