#!/usr/bin/env python3
"""
Setup Suppression System Database Collections and Indexes
Creates the necessary MongoDB collections and indexes for email suppression management.
"""

import os
from datetime import datetime
from mongodb_storage import MongoDBStorage

def setup_suppression_collections():
    """Set up MongoDB collections and indexes for email suppression"""
    print("🔧 Setting up Email Suppression System")
    print("=" * 50)
    
    try:
        # Initialize MongoDB connection
        storage = MongoDBStorage()
        db = storage.db
        
        print("✅ Connected to MongoDB")
        
        # Create suppression_list collection with indexes
        print("📋 Creating suppression_list collection...")
        
        # Create indexes for suppression_list
        db.suppression_list.create_index("email", unique=True)
        db.suppression_list.create_index("status")
        db.suppression_list.create_index("suppressed_at")
        db.suppression_list.create_index("reason")
        
        print("✅ Suppression list indexes created")
        
        # Create email_replies collection for tracking all replies
        print("📧 Creating email_replies collection...")
        
        db.email_replies.create_index([("sender_email", 1), ("received_at", -1)])
        db.email_replies.create_index("original_message_id")
        db.email_replies.create_index("suppression_triggered")
        db.email_replies.create_index("received_at")
        
        print("✅ Email replies indexes created")
        
        # Create bounce_log collection for detailed bounce tracking
        print("📮 Creating bounce_log collection...")
        
        db.bounce_log.create_index("email")
        db.bounce_log.create_index("bounce_type")
        db.bounce_log.create_index("bounce_date")
        
        print("✅ Bounce log indexes created")
        
        # Update existing contacts collection with suppression fields
        print("👥 Updating contacts collection schema...")
        
        # Add suppression-related indexes to contacts
        db.contacts.create_index("status")  # Already exists, but ensure it's there
        db.contacts.create_index("suppressed_at")
        db.contacts.create_index("suppression_reason")
        
        print("✅ Contacts collection updated")
        
        # Update email_sequences collection
        print("📤 Updating email sequences collection...")
        
        db.email_sequences.create_index("status")  # Already exists
        db.email_sequences.create_index("stopped_at")
        db.email_sequences.create_index("stop_reason")
        
        print("✅ Email sequences collection updated")
        
        # Insert some initial test data to verify setup
        print("🧪 Testing suppression system...")
        
        test_suppression = {
            'email': 'test-suppressed@example.com',
            'suppressed_at': datetime.utcnow(),
            'reason': 'Test suppression for system setup',
            'source': {'type': 'manual_setup'},
            'status': 'active'
        }
        
        # Only insert if it doesn't exist
        existing = db.suppression_list.find_one({'email': 'test-suppressed@example.com'})
        if not existing:
            db.suppression_list.insert_one(test_suppression)
            print("✅ Test suppression record created")
        else:
            print("ℹ️ Test suppression record already exists")
        
        # Show current collection stats
        print("\n📊 Collection Statistics:")
        print(f"  - Suppression List: {db.suppression_list.count_documents({})} records")
        print(f"  - Email Replies: {db.email_replies.count_documents({})} records")
        print(f"  - Bounce Log: {db.bounce_log.count_documents({})} records")
        print(f"  - Total Contacts: {db.contacts.count_documents({})} records")
        print(f"  - Email Sequences: {db.email_sequences.count_documents({})} records")
        
        # Show suppressed contacts
        suppressed_count = db.contacts.count_documents({'status': 'suppressed'})
        active_suppressions = db.suppression_list.count_documents({'status': 'active'})
        print(f"  - Suppressed Contacts: {suppressed_count} contacts")
        print(f"  - Active Suppressions: {active_suppressions} records")
        
        print("\n✅ Email Suppression System setup complete!")
        print("\nNext steps:")
        print("1. Run 'python3 email_reply_monitor.py' to start monitoring")
        print("2. Check logs regularly for suppression activity")
        print("3. Review suppression list monthly for compliance")
        
        storage.close_connection()
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def verify_suppression_system():
    """Verify that the suppression system is working correctly"""
    print("\n🔍 Verifying Suppression System Setup")
    print("=" * 50)
    
    try:
        storage = MongoDBStorage()
        db = storage.db
        
        # Check collections exist
        collections = db.list_collection_names()
        required_collections = ['suppression_list', 'email_replies', 'bounce_log']
        
        for collection in required_collections:
            if collection in collections:
                print(f"✅ {collection} collection exists")
            else:
                print(f"❌ {collection} collection missing")
                return False
        
        # Check indexes
        suppression_indexes = db.suppression_list.index_information()
        required_indexes = ['email_1', 'status_1', 'suppressed_at_1', 'reason_1']
        
        for index in required_indexes:
            if index in suppression_indexes:
                print(f"✅ {index} index exists")
            else:
                print(f"⚠️ {index} index missing")
        
        # Test suppression check function
        from email_reply_monitor import EmailReplyMonitor
        monitor = EmailReplyMonitor()
        
        # Test with the test email
        is_suppressed = monitor.check_suppression_status('test-suppressed@example.com')
        if is_suppressed:
            print("✅ Suppression check function working")
        else:
            print("⚠️ Suppression check function not detecting test record")
        
        print("\n✅ Suppression system verification complete!")
        storage.close_connection()
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 GFMD Email Suppression System Setup")
    print("=" * 60)
    
    # Setup collections and indexes
    setup_success = setup_suppression_collections()
    
    if setup_success:
        # Verify everything is working
        verify_success = verify_suppression_system()
        
        if verify_success:
            print("\n🎉 Email Suppression System is ready!")
            print("Your system will now automatically:")
            print("  ✅ Monitor email replies for unsubscribe keywords")
            print("  ✅ Detect bounced emails and delivery failures")
            print("  ✅ Stop email sequences for suppressed contacts")
            print("  ✅ Maintain compliance with CAN-SPAM regulations")
        else:
            print("\n⚠️ Setup completed but verification had issues")
    else:
        print("\n❌ Setup failed. Please check errors and try again.")

if __name__ == "__main__":
    main()