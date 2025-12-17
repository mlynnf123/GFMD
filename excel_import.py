#!/usr/bin/env python3
"""
Excel Contact Importer
Import contacts from Excel files and start email sequences
"""

import os
import pandas as pd
import re
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

class ExcelContactImporter:
    """Import contacts from Excel files"""
    
    def __init__(self):
        self.storage = MongoDBStorage()
        self.automation = CompleteSequenceAutomation()
    
    def analyze_excel_file(self, file_path: str):
        """Analyze Excel file structure to understand columns"""
        try:
            print(f"📊 Analyzing Excel file: {file_path}")
            
            # Try to read Excel file
            try:
                # Read first sheet
                df = pd.read_excel(file_path, sheet_name=0)
            except Exception as e:
                print(f"❌ Error reading Excel file: {e}")
                return None
            
            print(f"✅ File read successfully")
            print(f"📋 Shape: {df.shape[0]} rows, {df.shape[1]} columns")
            print(f"📋 Columns found:")
            
            for i, col in enumerate(df.columns):
                print(f"   {i+1:2d}. {col}")
            
            print(f"\n📄 Sample data (first 3 rows):")
            print("-" * 80)
            for idx, row in df.head(3).iterrows():
                print(f"Row {idx + 1}:")
                for col in df.columns:
                    value = str(row[col])[:50]
                    if pd.isna(row[col]):
                        value = "(empty)"
                    print(f"   {col}: {value}")
                print()
            
            # Suggest column mappings
            suggestions = self._suggest_column_mappings(df.columns.tolist())
            print("🤔 Suggested column mappings:")
            for field, suggestion in suggestions.items():
                print(f"   {field}: {suggestion}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error analyzing file: {e}")
            return None
    
    def _suggest_column_mappings(self, columns: list) -> dict:
        """Suggest which columns map to which contact fields"""
        suggestions = {
            'name': None,
            'email': None,
            'organization': None,
            'title': None,
            'location': None,
            'phone': None
        }
        
        # Name field patterns
        name_patterns = ['name', 'full_name', 'contact_name', 'first_name', 'last_name', 'attendee', 'person']
        
        # Email field patterns
        email_patterns = ['email', 'e_mail', 'email_address', 'contact_email', 'mail']
        
        # Organization patterns
        org_patterns = ['organization', 'company', 'department', 'agency', 'employer', 'org', 'business', 'dept']
        
        # Title patterns
        title_patterns = ['title', 'position', 'role', 'job_title', 'rank', 'job']
        
        # Location patterns
        location_patterns = ['location', 'city', 'state', 'address', 'city_state', 'region', 'area']
        
        # Phone patterns
        phone_patterns = ['phone', 'telephone', 'phone_number', 'tel', 'mobile', 'cell']
        
        def find_best_match(patterns, columns):
            for pattern in patterns:
                for col in columns:
                    if pattern.lower() in col.lower():
                        return col
            return None
        
        suggestions['name'] = find_best_match(name_patterns, columns)
        suggestions['email'] = find_best_match(email_patterns, columns)
        suggestions['organization'] = find_best_match(org_patterns, columns)
        suggestions['title'] = find_best_match(title_patterns, columns)
        suggestions['location'] = find_best_match(location_patterns, columns)
        suggestions['phone'] = find_best_match(phone_patterns, columns)
        
        return suggestions
    
    def import_excel_file(self, file_path: str, column_mapping: dict = None, start_sequences: bool = False) -> dict:
        """Import contacts from Excel file with custom column mapping"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=0)
            
            # If no mapping provided, use auto-suggestions
            if not column_mapping:
                column_mapping = self._suggest_column_mappings(df.columns.tolist())
            
            print(f"📥 Importing {len(df)} contacts from {file_path}")
            print(f"📋 Using column mapping: {column_mapping}")
            
            imported = 0
            sequences_started = 0
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    # Extract contact data based on mapping
                    contact = {}
                    
                    # Map columns to contact fields
                    for field, col_name in column_mapping.items():
                        if col_name and col_name in df.columns:
                            value = row[col_name]
                            if pd.notna(value):
                                contact[field] = str(value).strip()
                            else:
                                contact[field] = ""
                        else:
                            contact[field] = ""
                    
                    # Clean and validate email
                    email = contact.get('email', '').lower().strip()
                    if not email or '@' not in email:
                        errors.append(f"Row {idx+1}: Invalid or missing email")
                        continue
                    
                    # Ensure we have a name
                    if not contact.get('name'):
                        # Try to create name from email
                        email_name = email.split('@')[0]
                        contact['name'] = email_name.replace('.', ' ').replace('_', ' ').title()
                    
                    # Clean phone number
                    phone = contact.get('phone', '')
                    if phone:
                        # Remove common phone formatting
                        phone = re.sub(r'[^\d+\-\(\)\s]', '', phone)
                        contact['phone'] = phone
                    
                    # Add metadata
                    contact['source'] = f"Excel import: {os.path.basename(file_path)}"
                    contact['imported_at'] = datetime.now().isoformat()
                    contact['email'] = email  # Ensure email is clean
                    
                    # Import contact
                    if start_sequences:
                        result = self.automation.add_contact_and_start_sequence(contact)
                        if result.get('success'):
                            imported += 1
                            sequences_started += 1
                            print(f"✅ Row {idx+1}: {contact['name']} -> sequence started")
                        else:
                            errors.append(f"Row {idx+1}: {result.get('error')}")
                    else:
                        contact_id = self.storage.add_contact(contact)
                        imported += 1
                        print(f"✅ Row {idx+1}: {contact['name']} -> {contact_id}")
                    
                except Exception as e:
                    errors.append(f"Row {idx+1}: {str(e)}")
                    continue
            
            result = {
                'success': True,
                'file': os.path.basename(file_path),
                'total_rows': len(df),
                'imported': imported,
                'sequences_started': sequences_started if start_sequences else 0,
                'errors': len(errors),
                'error_details': errors
            }
            
            print(f"\n📊 Import Summary for {result['file']}:")
            print(f"   📄 Total rows: {result['total_rows']}")
            print(f"   ✅ Imported: {result['imported']} contacts")
            if start_sequences:
                print(f"   📧 Sequences started: {result['sequences_started']}")
            if errors:
                print(f"   ❌ Errors: {len(errors)}")
                for error in errors[:3]:  # Show first 3 errors
                    print(f"      - {error}")
                if len(errors) > 3:
                    print(f"      ... and {len(errors) - 3} more")
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def import_all_excel_files(self, file_paths: list, start_sequences: bool = False):
        """Import multiple Excel files"""
        total_results = {
            'files_processed': 0,
            'total_imported': 0,
            'total_sequences_started': 0,
            'total_errors': 0,
            'file_results': []
        }
        
        for file_path in file_paths:
            print(f"\n{'='*60}")
            print(f"Processing: {os.path.basename(file_path)}")
            print(f"{'='*60}")
            
            # First analyze the file
            df = self.analyze_excel_file(file_path)
            if df is None:
                continue
            
            # Import with auto-mapping
            result = self.import_excel_file(file_path, start_sequences=start_sequences)
            
            if result.get('success'):
                total_results['files_processed'] += 1
                total_results['total_imported'] += result.get('imported', 0)
                total_results['total_sequences_started'] += result.get('sequences_started', 0)
                total_results['total_errors'] += result.get('errors', 0)
            
            total_results['file_results'].append(result)
        
        print(f"\n🎉 FINAL IMPORT SUMMARY")
        print(f"{'='*50}")
        print(f"📁 Files processed: {total_results['files_processed']}")
        print(f"👥 Total contacts imported: {total_results['total_imported']}")
        if start_sequences:
            print(f"📧 Total sequences started: {total_results['total_sequences_started']}")
        print(f"❌ Total errors: {total_results['total_errors']}")
        
        return total_results

def main():
    """Main function for Excel import"""
    import sys
    
    importer = ExcelContactImporter()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "analyze" and len(sys.argv) > 2:
            # Analyze single file
            file_path = sys.argv[2]
            importer.analyze_excel_file(file_path)
            
        elif command == "import" and len(sys.argv) > 2:
            # Import single file
            file_path = sys.argv[2]
            start_sequences = len(sys.argv) > 3 and sys.argv[3] == "start"
            
            result = importer.import_excel_file(file_path, start_sequences=start_sequences)
            print(f"\nFinal result: {result}")
            
        elif command == "batch":
            # Import multiple files
            file_paths = sys.argv[2:]
            start_sequences = file_paths[-1] == "start"
            if start_sequences:
                file_paths = file_paths[:-1]
            
            importer.import_all_excel_files(file_paths, start_sequences=start_sequences)
            
        else:
            print("Usage:")
            print("  python3 excel_import.py analyze <file.xlsx>")
            print("  python3 excel_import.py import <file.xlsx> [start]")
            print("  python3 excel_import.py batch <file1.xlsx> <file2.xlsx> ... [start]")
    else:
        print("📋 Excel Contact Importer")
        print("=" * 50)
        print("Usage:")
        print("  python3 excel_import.py analyze <file.xlsx>")
        print("  python3 excel_import.py import <file.xlsx> [start]")
        print("  python3 excel_import.py batch <file1.xlsx> <file2.xlsx> ... [start]")
        print("")
        print("Options:")
        print("  start - Also start email sequences for imported contacts")

if __name__ == "__main__":
    main()