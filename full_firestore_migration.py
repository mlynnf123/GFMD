#!/usr/bin/env python3
"""
Full Firestore Migration Script
Migrates all healthcare contacts from CSV to Firestore database with progress tracking
"""

import pandas as pd
import logging
import time
import os
from firestore_service import FirestoreService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main migration function - import all contacts in batches"""
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
        
        # Process in batches of 500 for better performance
        batch_size = 500
        total_imported = 0
        total_skipped = 0
        total_errors = 0
        
        num_batches = (len(df_clean) + batch_size - 1) // batch_size
        logger.info(f"Processing {num_batches} batches of {batch_size} contacts each")
        
        for i in range(0, len(df_clean), batch_size):
            batch_num = i // batch_size + 1
            logger.info(f"Processing batch {batch_num}/{num_batches}...")
            
            # Get batch
            batch_df = df_clean.iloc[i:i + batch_size]
            contacts_list = batch_df.to_dict('records')
            
            # Import batch
            start_time = time.time()
            results = firestore_service.bulk_import_contacts(contacts_list)
            batch_time = time.time() - start_time
            
            # Update totals
            total_imported += results['imported']
            total_skipped += results['skipped']
            total_errors += results['errors']
            
            logger.info(f"Batch {batch_num} completed in {batch_time:.2f}s: "
                       f"imported={results['imported']}, "
                       f"skipped={results['skipped']}, "
                       f"errors={results['errors']}")
            
            # Progress update
            progress = (batch_num / num_batches) * 100
            logger.info(f"Overall progress: {progress:.1f}% "
                       f"(Total: imported={total_imported}, "
                       f"skipped={total_skipped}, errors={total_errors})")
            
            # Small delay to avoid rate limits
            if batch_num < num_batches:
                time.sleep(1)
        
        # Final results
        logger.info("="*50)
        logger.info("MIGRATION COMPLETED!")
        logger.info(f"Total imported: {total_imported} contacts")
        logger.info(f"Total skipped: {total_skipped} contacts (duplicates)")
        logger.info(f"Total errors: {total_errors} contacts")
        
        # Get final count
        from google.cloud import firestore
        client = firestore.Client(project="windy-tiger-471523-m5")
        contacts_ref = client.collection('healthcare_contacts')
        final_count = len(list(contacts_ref.stream()))
        logger.info(f"Final database count: {final_count} contacts")
        
        # Success if we imported most contacts
        success_rate = (total_imported / len(df_clean)) * 100
        logger.info(f"Success rate: {success_rate:.1f}%")
        
        return success_rate > 80  # Consider successful if >80% imported
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nMigration {'SUCCEEDED' if success else 'FAILED'}")
    exit(0 if success else 1)