"""
Google Sheets Configuration for GFMD Swarm Agent
"""

import os
from google_sheets_integration import GoogleSheetsConfig

def get_google_sheets_config() -> GoogleSheetsConfig:
    """
    Get Google Sheets configuration from environment variables or return default config
    
    Environment variables:
    - GOOGLE_SHEETS_SPREADSHEET_NAME: Name of the Google Sheets spreadsheet
    - GOOGLE_SHEETS_CREDENTIALS_FILE: Path to service account credentials file
    - GOOGLE_SHEETS_SHARE_EMAILS: Comma-separated list of emails to share the spreadsheet with
    """
    
    # Get configuration from environment variables
    spreadsheet_name = os.getenv('GOOGLE_SHEETS_SPREADSHEET_NAME', 'GFMD Swarm Agent Data')
    credentials_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
    share_emails_str = os.getenv('GOOGLE_SHEETS_SHARE_EMAILS', '')
    
    # Parse share emails
    share_emails = []
    if share_emails_str:
        share_emails = [email.strip() for email in share_emails_str.split(',') if email.strip()]
    
    # Service account info from environment (alternative to file)
    service_account_info = None
    if os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_INFO'):
        import json
        try:
            service_account_info = json.loads(os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_INFO'))
        except json.JSONDecodeError:
            print("⚠️ Invalid GOOGLE_SHEETS_SERVICE_ACCOUNT_INFO format")
    
    return GoogleSheetsConfig(
        spreadsheet_name=spreadsheet_name,
        credentials_file=credentials_file,
        service_account_info=service_account_info,
        share_with_emails=share_emails
    )

def is_google_sheets_enabled() -> bool:
    """Check if Google Sheets integration is enabled"""
    return bool(
        os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE') or 
        os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_INFO') or
        os.path.exists(os.path.expanduser('~/.config/gspread/service_account.json'))
    )

# Example configuration setup
if __name__ == "__main__":
    print("Google Sheets Configuration Setup")
    print("=" * 40)
    
    if is_google_sheets_enabled():
        config = get_google_sheets_config()
        print(f"✅ Google Sheets integration is enabled")
        print(f"📊 Spreadsheet name: {config.spreadsheet_name}")
        print(f"📁 Credentials file: {config.credentials_file or 'Using default location'}")
        print(f"📧 Share with emails: {', '.join(config.share_with_emails) if config.share_with_emails else 'None'}")
    else:
        print("❌ Google Sheets integration is NOT enabled")
        print("\nTo enable Google Sheets integration, you need:")
        print("1. Set up a Google Cloud Project with Sheets API enabled")
        print("2. Create a Service Account and download credentials")
        print("3. Either:")
        print("   - Set GOOGLE_SHEETS_CREDENTIALS_FILE environment variable")
        print("   - Set GOOGLE_SHEETS_SERVICE_ACCOUNT_INFO environment variable")
        print("   - Place credentials at ~/.config/gspread/service_account.json")
        print("\nOptional environment variables:")
        print("- GOOGLE_SHEETS_SPREADSHEET_NAME (default: 'GFMD Swarm Agent Data')")
        print("- GOOGLE_SHEETS_SHARE_EMAILS (comma-separated list)")