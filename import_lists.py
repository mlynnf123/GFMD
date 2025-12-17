#!/usr/bin/env python3
"""
Import Your Specific Excel Files
Custom import script for your 3 Excel files
"""

import os
import pandas as pd
from datetime import datetime
from mongodb_storage import MongoDBStorage
from complete_sequence_automation import CompleteSequenceAutomation

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

class YourListImporter:
    """Import your specific Excel contact lists"""
    
    def __init__(self):
        self.storage = MongoDBStorage()
        self.automation = CompleteSequenceAutomation()
    
    def import_all_lists(self, start_sequences: bool = False):
        """Import all three lists"""
        
        files = [
            ('/Users/merandafreiner/Downloads/2024 Attendee list -share.xlsx', '2024_attendees'),
            ('/Users/merandafreiner/Downloads/Attendee List Opt In 2023.xlsx', '2023_opt_in'),
            ('/Users/merandafreiner/Downloads/CAPE 2025 Leads.xlsx', 'cape_2025')
        ]
        
        total_imported = 0
        total_sequences = 0
        
        for file_path, file_type in files:
            print(f"\n{'='*60}")
            print(f"Processing: {os.path.basename(file_path)}")
            print(f"{'='*60}")
            
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                continue
            
            try:
                df = pd.read_excel(file_path, sheet_name=0)
                print(f"📊 File loaded: {len(df)} rows")
                
                imported_count = 0
                sequence_count = 0
                
                for idx, row in df.iterrows():
                    try:
                        contact = self._process_row(row, file_type)
                        
                        if not contact or not contact.get('email'):
                            continue
                        
                        if start_sequences:
                            result = self.automation.add_contact_and_start_sequence(contact)
                            if result.get('success'):
                                imported_count += 1
                                sequence_count += 1
                                if imported_count % 25 == 0:
                                    print(f"   📧 {imported_count} contacts imported with sequences...")
                        else:
                            contact_id = self.storage.add_contact(contact)
                            imported_count += 1
                            if imported_count % 50 == 0:
                                print(f"   📥 {imported_count} contacts imported...")
                    
                    except Exception as e:
                        continue  # Skip problematic rows
                
                print(f"✅ Completed {os.path.basename(file_path)}")
                print(f"   📥 Imported: {imported_count} contacts")
                if start_sequences:
                    print(f"   📧 Sequences started: {sequence_count}")
                
                total_imported += imported_count
                total_sequences += sequence_count
                
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
        
        print(f"\n🎉 FINAL SUMMARY")
        print(f"=" * 40)
        print(f"👥 Total imported: {total_imported} contacts")
        if start_sequences:
            print(f"📧 Total sequences: {total_sequences} started")
        
        return total_imported, total_sequences
    
    def _process_row(self, row, file_type: str) -> dict:
        """Process a single row based on file type"""
        
        if file_type == '2024_attendees':
            # 2024 Attendee list format
            full_name = str(row.get('Full Name', '')).strip() if pd.notna(row.get('Full Name')) else ""
            company = str(row.get('Company Name', '')).strip() if pd.notna(row.get('Company Name')) else ""
            email = str(row.get('Email Address', '')).strip().lower() if pd.notna(row.get('Email Address')) else ""
            
            # Clean up name format "Last, First"
            if ',' in full_name:
                parts = full_name.split(',', 1)
                if len(parts) == 2:
                    full_name = f"{parts[1].strip()} {parts[0].strip()}"
            
            return {
                'name': full_name,
                'email': email,
                'organization': company,
                'source': '2024 Attendees'
            }
        
        elif file_type == '2023_opt_in':
            # 2023 Opt-in list format
            opted_out = str(row.get('Opted-Out', '')).strip().lower()
            if opted_out == 'yes':
                return None  # Skip opted-out contacts
            
            first_name = str(row.get('First Name', '')).strip() if pd.notna(row.get('First Name')) else ""
            last_name = str(row.get('Last Name', '')).strip() if pd.notna(row.get('Last Name')) else ""
            company = str(row.get('Company Name', '')).strip() if pd.notna(row.get('Company Name')) else ""
            email = str(row.get('Email Address', '')).strip().lower() if pd.notna(row.get('Email Address')) else ""
            city = str(row.get('Work City', '')).strip() if pd.notna(row.get('Work City')) else ""
            
            full_name = f"{first_name} {last_name}".strip()
            
            return {
                'name': full_name,
                'email': email,
                'organization': company,
                'location': city,
                'source': '2023 Opt-In Attendees'
            }
        
        elif file_type == 'cape_2025':
            # CAPE 2025 Leads format
            name = str(row.get('Name', '')).strip() if pd.notna(row.get('Name')) else ""
            email = str(row.get('Email', '')).strip().lower() if pd.notna(row.get('Email')) else ""
            department = str(row.get('Department', '')).strip() if pd.notna(row.get('Department')) else ""
            
            return {
                'name': name,
                'email': email,
                'organization': department,
                'source': 'CAPE 2025 Leads'
            }
        
        return None

def main():
    """Main function"""
    import sys
    
    importer = YourListImporter()
    
    start_sequences = len(sys.argv) > 1 and sys.argv[1] == "start"
    
    print("🚀 IMPORTING YOUR EXCEL CONTACT LISTS")
    print("=" * 50)
    if start_sequences:
        print("📧 Will START email sequences for imported contacts")
    else:
        print("📥 Will import contacts only (no sequences)")
    
    total_imported, total_sequences = importer.import_all_lists(start_sequences)
    
    print(f"\n✅ Import complete!")
    print(f"📊 Final stats:")
    print(f"   👥 {total_imported} contacts imported")
    if start_sequences:
        print(f"   📧 {total_sequences} email sequences started")

if __name__ == "__main__":
    main()