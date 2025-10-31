#!/usr/bin/env python3
"""
Simple Firestore Migration Script - Import just the first 100 contacts for testing
"""

import pandas as pd
import logging
from firestore_service import FirestoreService
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main migration function - import first 100 contacts"""
    try:
        # Set environment variable for authentication
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/merandafreiner/gfmd_swarm_agent/google_sheets_credentials.json'
        
        # Initialize Firestore service
        logger.info("Initializing Firestore service...")
        firestore_service = FirestoreService()
        
        # Load CSV data
        csv_file = "definitive_healthcare_data.csv"
        
        if not os.path.exists(csv_file):
            logger.error(f"CSV file not found: {csv_file}")
            return False
        
        logger.info(f"Loading data from {csv_file}...")
        df = pd.read_csv(csv_file)
        
        # Clean and prepare data
        logger.info(f"Loaded {len(df)} records from CSV")
        
        # Remove rows with empty emails
        df_clean = df.dropna(subset=['Business Email'])
        df_clean = df_clean[df_clean['Business Email'].str.strip() != '']
        
        logger.info(f"After cleaning: {len(df_clean)} valid records")
        
        # Take only first 100 for testing
        df_sample = df_clean.head(100)
        logger.info(f"Importing sample of {len(df_sample)} contacts")
        
        # Convert DataFrame to list of dictionaries
        contacts_list = df_sample.to_dict('records')
        
        # Bulk import to Firestore
        logger.info("Starting bulk import to Firestore...")
        results = firestore_service.bulk_import_contacts(contacts_list)
        
        # Print results
        logger.info("Migration completed!")
        logger.info(f"Imported: {results['imported']} contacts")
        logger.info(f"Skipped: {results['skipped']} contacts (duplicates or invalid)")
        logger.info(f"Errors: {results['errors']} contacts")
        
        # Simple count instead of complex stats
        from google.cloud import firestore
        client = firestore.Client(project="windy-tiger-471523-m5")
        contacts_ref = client.collection('healthcare_contacts')
        total_count = len(list(contacts_ref.stream()))
        logger.info(f"Total contacts in database: {total_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)