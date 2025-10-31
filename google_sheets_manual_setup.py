#!/usr/bin/env python3
"""
Manual Google Sheets setup when storage quota is exceeded
This script connects to an existing spreadsheet instead of creating a new one.
"""

import gspread
from google_sheets_integration import GoogleSheetsConfig, GoogleSheetsExporter

class ManualGoogleSheetsExporter(GoogleSheetsExporter):
    """Modified exporter that works with existing spreadsheets"""
    
    def _setup_spreadsheet(self):
        """Connect to existing spreadsheet by URL or ID"""
        try:
            # Try to open by name first
            self.spreadsheet = self.gc.open(self.config.spreadsheet_name)
            print(f"📊 Opened existing spreadsheet: {self.config.spreadsheet_name}")
        except gspread.SpreadsheetNotFound:
            print(f"❌ Spreadsheet '{self.config.spreadsheet_name}' not found or not shared with service account")
            print(f"📧 Service account email: {self.gc.auth.service_account_email}")
            print("\nPlease:")
            print("1. Create a Google Sheet named 'GFMD Swarm Agent Data'")
            print("2. Share it with the service account email above (Editor permissions)")
            print("3. Run this script again")
            raise Exception("Spreadsheet not accessible")
        
        # Setup worksheets with existing spreadsheet
        self._setup_worksheets()

def test_manual_setup():
    """Test the manual Google Sheets setup"""
    try:
        config = GoogleSheetsConfig(spreadsheet_name="GFMD Swarm Agent Data")
        exporter = ManualGoogleSheetsExporter(config)
        
        print(f"✅ Successfully connected to spreadsheet")
        print(f"📊 URL: {exporter.get_spreadsheet_url()}")
        
        # Test a simple export
        test_data = {
            "agent_type": "TestAgent",
            "touchpoint_id": "manual_test_001",
            "channel": "email",
            "recipient": "Test User",
            "organization": "Test Company",
            "content": "Manual test export",
            "status": "sent",
            "tracking_id": "manual_test_123"
        }
        
        exporter.export_agent_output(test_data)
        print("✅ Test export successful!")
        
        return exporter
        
    except Exception as e:
        print(f"❌ Manual setup failed: {e}")
        return None

if __name__ == "__main__":
    print("Manual Google Sheets Setup")
    print("=" * 30)
    test_manual_setup()