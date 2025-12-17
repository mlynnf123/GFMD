#!/usr/bin/env python3
"""
Bulk Import Contacts to MongoDB
Import contacts from CSV file and optionally start sequences
"""

import os
import csv
import json
import asyncio
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

class BulkContactImporter:
    """Bulk import contacts from various sources"""
    
    def __init__(self):
        self.storage = MongoDBStorage()
        self.automation = CompleteSequenceAutomation()
    
    def import_from_csv(self, csv_file: str, start_sequences: bool = False) -> dict:
        """Import contacts from CSV file"""
        try:
            imported = 0
            sequences_started = 0
            errors = []
            
            print(f"📂 Reading contacts from {csv_file}...")
            
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                # Detect CSV format
                sample = file.read(1024)
                file.seek(0)
                
                # Try to detect delimiter
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                print(f"📋 CSV columns detected: {list(reader.fieldnames)}")
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Map CSV columns to contact fields
                        contact = self._map_csv_row_to_contact(row)
                        
                        if not contact.get('email'):
                            errors.append(f"Row {row_num}: Missing email")
                            continue
                        
                        if start_sequences:
                            # Add contact and start sequence
                            result = self.automation.add_contact_and_start_sequence(contact)
                            if result.get('success'):
                                imported += 1
                                sequences_started += 1
                                print(f"✅ Row {row_num}: {contact['name']} -> sequence started")
                            else:
                                errors.append(f"Row {row_num}: {result.get('error')}")
                        else:
                            # Just add contact
                            contact_id = self.storage.add_contact(contact)
                            imported += 1
                            print(f"✅ Row {row_num}: {contact['name']} -> {contact_id}")
                            
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
            
            result = {
                'success': True,
                'imported': imported,
                'sequences_started': sequences_started if start_sequences else 0,
                'errors': len(errors),
                'error_details': errors
            }
            
            print(f"\n📊 Import Summary:")
            print(f"   ✅ Imported: {imported} contacts")
            if start_sequences:
                print(f"   📧 Sequences started: {sequences_started}")
            if errors:
                print(f"   ❌ Errors: {len(errors)}")
                for error in errors[:5]:  # Show first 5 errors
                    print(f"      - {error}")
                if len(errors) > 5:
                    print(f"      ... and {len(errors) - 5} more")
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _map_csv_row_to_contact(self, row: dict) -> dict:
        """Map CSV row to contact format - handles various column names"""
        
        # Common column name mappings
        name_fields = ['name', 'contact_name', 'full_name', 'contact', 'person']
        email_fields = ['email', 'email_address', 'contact_email', 'e_mail']
        org_fields = ['organization', 'company', 'department', 'agency', 'org']
        title_fields = ['title', 'position', 'role', 'job_title']
        location_fields = ['location', 'city', 'address', 'state', 'city_state']
        phone_fields = ['phone', 'phone_number', 'telephone', 'contact_phone']
        
        def find_field_value(row, field_list):
            """Find value from row using list of possible field names"""
            for field in field_list:
                for key, value in row.items():
                    if key.lower().strip() == field.lower():
                        return str(value).strip() if value else ''
            return ''
        
        contact = {
            'name': find_field_value(row, name_fields),
            'email': find_field_value(row, email_fields).lower(),
            'organization': find_field_value(row, org_fields),
            'title': find_field_value(row, title_fields),
            'location': find_field_value(row, location_fields),
            'phone': find_field_value(row, phone_fields)
        }
        
        # If no name found, try to create from email
        if not contact['name'] and contact['email']:
            email_parts = contact['email'].split('@')[0]
            contact['name'] = email_parts.replace('.', ' ').replace('_', ' ').title()
        
        return contact
    
    def import_from_json(self, json_file: str, start_sequences: bool = False) -> dict:
        """Import contacts from JSON file"""
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
            
            contacts = data if isinstance(data, list) else data.get('contacts', [])
            
            imported = 0
            sequences_started = 0
            errors = []
            
            for i, contact_data in enumerate(contacts, 1):
                try:
                    if start_sequences:
                        result = self.automation.add_contact_and_start_sequence(contact_data)
                        if result.get('success'):
                            imported += 1
                            sequences_started += 1
                        else:
                            errors.append(f"Contact {i}: {result.get('error')}")
                    else:
                        contact_id = self.storage.add_contact(contact_data)
                        imported += 1
                        
                except Exception as e:
                    errors.append(f"Contact {i}: {str(e)}")
            
            return {
                'success': True,
                'imported': imported,
                'sequences_started': sequences_started if start_sequences else 0,
                'errors': len(errors),
                'error_details': errors
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_sample_csv(self, filename: str = 'sample_contacts.csv'):
        """Create a sample CSV file for reference"""
        sample_data = [
            {
                'name': 'Chief Robert Martinez',
                'email': 'robert.martinez@metropd.gov',
                'organization': 'Metro City Police Department',
                'title': 'Chief of Police',
                'location': 'Metro City, TX',
                'phone': '555-0101'
            },
            {
                'name': 'Sheriff Amanda Thompson',
                'email': 'athompson@rivercounty.gov',
                'organization': 'River County Sheriff Office',
                'title': 'Sheriff',
                'location': 'River County, TX',
                'phone': '555-0102'
            },
            {
                'name': 'Commander Mike Johnson',
                'email': 'mjohnson@statepd.gov',
                'organization': 'State Police Department',
                'title': 'Commander',
                'location': 'Austin, TX',
                'phone': '555-0103'
            }
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=sample_data[0].keys())
            writer.writeheader()
            writer.writerows(sample_data)
        
        print(f"✅ Created sample CSV file: {filename}")
        return filename

def main():
    """Main function for bulk import"""
    import sys
    
    importer = BulkContactImporter()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "csv" and len(sys.argv) > 2:
            csv_file = sys.argv[2]
            start_sequences = len(sys.argv) > 3 and sys.argv[3] == "start"
            
            result = importer.import_from_csv(csv_file, start_sequences)
            print(f"\nFinal result: {result}")
            
        elif command == "json" and len(sys.argv) > 2:
            json_file = sys.argv[2]
            start_sequences = len(sys.argv) > 3 and sys.argv[3] == "start"
            
            result = importer.import_from_json(json_file, start_sequences)
            print(f"Final result: {result}")
            
        elif command == "sample":
            filename = sys.argv[2] if len(sys.argv) > 2 else 'sample_contacts.csv'
            importer.create_sample_csv(filename)
            
        else:
            print("Usage:")
            print("  python3 bulk_import_contacts.py csv <file.csv> [start]")
            print("  python3 bulk_import_contacts.py json <file.json> [start]")
            print("  python3 bulk_import_contacts.py sample [filename.csv]")
            print("")
            print("Options:")
            print("  start - Also start email sequences for imported contacts")
    else:
        print("📋 Bulk Contact Importer")
        print("=" * 40)
        print("Usage:")
        print("  python3 bulk_import_contacts.py csv <file.csv> [start]")
        print("  python3 bulk_import_contacts.py json <file.json> [start]")  
        print("  python3 bulk_import_contacts.py sample [filename.csv]")
        print("")
        print("Examples:")
        print("  python3 bulk_import_contacts.py sample")
        print("  python3 bulk_import_contacts.py csv contacts.csv")
        print("  python3 bulk_import_contacts.py csv contacts.csv start")

if __name__ == "__main__":
    main()