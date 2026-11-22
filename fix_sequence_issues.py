#!/usr/bin/env python3
"""
Fix Existing Sequence Issues in Database
Addresses:
1. Sequences stuck at final step (should be completed)
2. Active sequences for suppressed contacts (should be stopped)
3. General cleanup of invalid states
"""

import os
from datetime import datetime
from mongodb_storage import MongoDBStorage
from email_sequence_templates import EmailSequenceTemplates

# Load environment variables
def load_env():
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    value = value.strip('"').strip("'")
                    os.environ[key] = value
    except FileNotFoundError:
        pass

load_env()

def fix_sequence_issues():
    """Fix all sequence issues in the database"""

    print("=" * 70)
    print("FIXING SEQUENCE ISSUES IN DATABASE")
    print("=" * 70)

    storage = MongoDBStorage()
    templates = EmailSequenceTemplates()

    # Determine max step for the sequence
    max_step = 0
    step = 1
    while templates.get_email_template('narc_gone_law_enforcement', step):
        max_step = step
        step += 1

    print(f"\nSequence has {max_step} total steps\n")

    # Fix 1: Mark sequences at final step as completed
    print("Fix 1: Marking sequences at final step as completed...")
    print("-" * 70)

    stuck_sequences = storage.db.email_sequences.find({
        'status': 'active',
        'current_step': {'$gte': max_step}
    })

    stuck_count = 0
    for seq in stuck_sequences:
        result = storage.db.email_sequences.update_one(
            {'_id': seq['_id']},
            {'$set': {
                'status': 'completed',
                'completed_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'completion_reason': 'Fixed: Was stuck at final step'
            }}
        )
        if result.modified_count > 0:
            stuck_count += 1
            print(f"  ✓ Completed: {seq.get('contact_email')} (was at step {seq.get('current_step')})")

    print(f"\nFixed {stuck_count} stuck sequences")

    # Fix 2: Stop active sequences for suppressed contacts
    print("\nFix 2: Stopping active sequences for suppressed contacts...")
    print("-" * 70)

    # Get all suppressed emails
    suppressed_contacts = list(storage.db.suppression_list.find({
        'status': 'active'
    }))

    suppressed_emails = [s['email'] for s in suppressed_contacts]
    print(f"Found {len(suppressed_emails)} suppressed contacts")

    # Find active sequences for these contacts
    active_suppressed = storage.db.email_sequences.find({
        'contact_email': {'$in': suppressed_emails},
        'status': 'active'
    })

    suppressed_count = 0
    for seq in active_suppressed:
        # Get suppression reason
        supp_record = storage.db.suppression_list.find_one({
            'email': seq.get('contact_email')
        })

        reason = supp_record.get('reason', 'On suppression list') if supp_record else 'On suppression list'

        result = storage.db.email_sequences.update_one(
            {'_id': seq['_id']},
            {'$set': {
                'status': 'suppressed',
                'stopped_at': datetime.now().isoformat(),
                'stop_reason': reason,
                'updated_at': datetime.now().isoformat()
            }}
        )

        if result.modified_count > 0:
            suppressed_count += 1
            print(f"  ✓ Stopped: {seq.get('contact_email')} (reason: {reason})")

    print(f"\nStopped {suppressed_count} active sequences for suppressed contacts")

    # Fix 3: Ensure contacts marked as suppressed have status updated
    print("\nFix 3: Updating contact status for suppressed emails...")
    print("-" * 70)

    contact_update_count = 0
    for supp in suppressed_contacts:
        result = storage.contacts.update_one(
            {'email': supp['email']},
            {'$set': {
                'status': 'suppressed',
                'suppressed_at': supp.get('suppressed_at'),
                'suppression_reason': supp.get('reason'),
                'updatedAt': datetime.now()
            }}
        )

        if result.modified_count > 0:
            contact_update_count += 1

    print(f"Updated {contact_update_count} contact records")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✓ Marked {stuck_count} stuck sequences as completed")
    print(f"✓ Stopped {suppressed_count} sequences for suppressed contacts")
    print(f"✓ Updated {contact_update_count} contact records")

    # Show current state
    print("\nCurrent sequence status counts:")
    total = storage.db.email_sequences.count_documents({})
    active = storage.db.email_sequences.count_documents({'status': 'active'})
    completed = storage.db.email_sequences.count_documents({'status': 'completed'})
    replied = storage.db.email_sequences.count_documents({'status': 'replied'})
    suppressed = storage.db.email_sequences.count_documents({'status': 'suppressed'})

    print(f"  Total: {total}")
    print(f"  Active: {active}")
    print(f"  Completed: {completed}")
    print(f"  Replied: {replied}")
    print(f"  Suppressed: {suppressed}")

    storage.close_connection()

    print("\n✅ Database cleanup complete!")

if __name__ == "__main__":
    fix_sequence_issues()
