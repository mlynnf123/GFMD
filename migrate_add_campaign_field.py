#!/usr/bin/env python3
"""
One-time migration script: Add campaign field to all existing documents.
Supports multi-campaign infrastructure (Narc Gone + Silencer Centrifuge).

Run once against MongoDB Atlas:
    python3 migrate_add_campaign_field.py
"""

import os
from pymongo import MongoClient

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

MONGODB_URI = os.environ['MONGODB_CONNECTION_STRING']

def migrate():
    client = MongoClient(MONGODB_URI)
    db = client['gfmd_narc_gone']

    print("=" * 60)
    print("GFMD Multi-Campaign Migration")
    print("=" * 60)

    # --- Before counts ---
    contacts_count = db.contacts.count_documents({})
    sequences_count = db.email_sequences.count_documents({})
    interactions_count = db.interactions.count_documents({})

    print(f"\nBefore migration:")
    print(f"  contacts:        {contacts_count}")
    print(f"  email_sequences: {sequences_count}")
    print(f"  interactions:    {interactions_count}")

    # --- Step 1: Add campaign field to all existing docs ---
    print("\nStep 1: Adding campaign='narc_gone' to existing documents...")

    r1 = db.contacts.update_many(
        {"campaign": {"$exists": False}},
        {"$set": {"campaign": "narc_gone"}}
    )
    print(f"  contacts updated: {r1.modified_count}")

    r2 = db.email_sequences.update_many(
        {"campaign": {"$exists": False}},
        {"$set": {"campaign": "narc_gone"}}
    )
    print(f"  email_sequences updated: {r2.modified_count}")

    r3 = db.interactions.update_many(
        {"campaign": {"$exists": False}},
        {"$set": {"campaign": "narc_gone"}}
    )
    print(f"  interactions updated: {r3.modified_count}")

    # --- Step 2: Drop old unique index on contact_id (if it exists) ---
    print("\nStep 2: Updating email_sequences indexes...")

    existing_indexes = list(db.email_sequences.list_indexes())
    dropped = False
    for idx in existing_indexes:
        key_dict = dict(idx["key"])
        # Drop any index that is solely on contact_id
        if key_dict == {"contact_id": 1} and idx.get("unique"):
            print(f"  Dropping old unique index: {idx['name']}")
            db.email_sequences.drop_index(idx["name"])
            dropped = True

    if not dropped:
        print("  No old unique index on contact_id found (may already be migrated)")

    # --- Step 3: Create compound unique index (contact_id, campaign) ---
    print("\nStep 3: Creating compound unique index (contact_id, campaign)...")

    try:
        index_name = db.email_sequences.create_index(
            [("contact_id", 1), ("campaign", 1)],
            unique=True,
            name="contact_id_campaign_unique"
        )
        print(f"  Created index: {index_name}")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("  Index already exists (already migrated)")
        else:
            raise

    # --- After counts ---
    contacts_with_campaign = db.contacts.count_documents({"campaign": {"$exists": True}})
    sequences_with_campaign = db.email_sequences.count_documents({"campaign": {"$exists": True}})
    interactions_with_campaign = db.interactions.count_documents({"campaign": {"$exists": True}})

    print(f"\nAfter migration:")
    print(f"  contacts with campaign field:        {contacts_with_campaign}/{contacts_count}")
    print(f"  email_sequences with campaign field:  {sequences_with_campaign}/{sequences_count}")
    print(f"  interactions with campaign field:      {interactions_with_campaign}/{interactions_count}")

    # --- Verify indexes ---
    print("\nFinal indexes on email_sequences:")
    for idx in db.email_sequences.list_indexes():
        print(f"  {idx['name']}: {dict(idx['key'])} (unique={idx.get('unique', False)})")

    print("\nMigration complete.")
    client.close()


if __name__ == "__main__":
    migrate()
