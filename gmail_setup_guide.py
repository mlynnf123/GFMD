#!/usr/bin/env python3
"""
Gmail Setup Guide - Two options for automatic email sending
"""

def show_gmail_setup_options():
    """Display Gmail setup options"""
    
    print("📧 Gmail Setup for Automatic Email Sending")
    print("=" * 60)
    
    print("\n🎯 **OPTION 1: Service Account (RECOMMENDED for automation)**")
    print("=" * 50)
    print("✅ Best for: Automated systems, no user interaction needed")
    print("✅ Benefits:")
    print("   • No browser authentication required")
    print("   • Perfect for Cloud Run/scheduled jobs")
    print("   • More secure for production")
    print("   • No token expiration issues")
    
    print("\n📋 Service Account Setup Steps:")
    print("1. Go to Google Cloud Console (console.cloud.google.com)")
    print("2. Select your project (or create one)")
    print("3. Enable Gmail API:")
    print("   → APIs & Services → Library → Search 'Gmail API' → Enable")
    print("4. Create Service Account:")
    print("   → IAM & Admin → Service Accounts → Create Service Account")
    print("   → Name: 'gfmd-email-sender' → Create")
    print("5. Generate Key:")
    print("   → Click your service account → Keys → Add Key → JSON")
    print("   → Download the JSON file")
    print("6. Save JSON as 'gmail_service_account.json' in this directory")
    print("7. Domain-wide Delegation (Gmail requires this):")
    print("   → Service Account Details → Enable G Suite Domain-wide Delegation")
    print("   → Note the Client ID")
    print("8. Admin Console (if you have G Suite/Workspace):")
    print("   → Security → API Controls → Domain-wide Delegation")
    print("   → Add Client ID with scope: https://www.googleapis.com/auth/gmail.send")
    
    print("\n⚠️  Service Account Limitation:")
    print("   Service accounts can only send from G Suite/Workspace domains")
    print("   For personal Gmail, use OAuth (Option 2)")
    
    print("\n🔧 **OPTION 2: OAuth 2.0 (For personal Gmail)**")
    print("=" * 50)
    print("✅ Best for: Personal Gmail accounts, testing")
    print("✅ Works with any Gmail account")
    
    print("\n📋 OAuth Setup Steps:")
    print("1. Go to Google Cloud Console (console.cloud.google.com)")
    print("2. Enable Gmail API (same as above)")
    print("3. Create OAuth 2.0 Credentials:")
    print("   → APIs & Services → Credentials → Create Credentials")
    print("   → OAuth 2.0 Client IDs → Desktop Application")
    print("   → Name: 'GFMD Email Client' → Create")
    print("4. Download JSON file")
    print("5. Save as 'gmail_credentials.json' in this directory")
    print("6. Run: python3 test_gmail_setup.py")
    print("7. Browser will open → Select your Gmail account → Grant permissions")
    
    print("\n" + "=" * 60)
    print("🤔 **Which Should You Choose?**")
    print("=" * 60)
    
    print("\n📊 **For GFMD Business Email** (Recommended):")
    print("→ Use Service Account (Option 1)")
    print("→ Send from your business domain (e.g., sales@gfmd.com)")
    print("→ Perfect for daily automation")
    print("→ No user interaction needed")
    
    print("\n📧 **For Personal Gmail Testing:**")
    print("→ Use OAuth (Option 2)")
    print("→ Send from your personal Gmail")
    print("→ Good for testing the system")
    print("→ Requires browser authentication once")
    
    print("\n🚀 **Quick Start Recommendation:**")
    print("1. Start with OAuth (Option 2) to test the system")
    print("2. Switch to Service Account (Option 1) for production")
    
    return get_user_choice()

def get_user_choice():
    """Get user's setup preference"""
    print("\n" + "=" * 60)
    print("Which setup would you like to use?")
    print("1. Service Account (business email)")
    print("2. OAuth 2.0 (personal Gmail)")
    print("3. Show me both file examples")
    
    return input("\nEnter your choice (1-3): ").strip()

def show_service_account_example():
    """Show service account integration example"""
    
    print("\n🔧 Service Account Integration")
    print("=" * 50)
    
    service_account_code = '''
# Service Account Gmail Integration
from google.oauth2 import service_account
from googleapiclient.discovery import build

class ServiceAccountGmail:
    def __init__(self, service_account_file, delegated_user_email):
        self.service_account_file = service_account_file
        self.delegated_user_email = delegated_user_email
        self.service = self._build_service()
    
    def _build_service(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )
        
        # Delegate to specific user email
        delegated_credentials = credentials.with_subject(self.delegated_user_email)
        
        return build('gmail', 'v1', credentials=delegated_credentials)
    
    def send_email(self, to_email, subject, body):
        # Same sending logic as OAuth version
        pass

# Usage:
gmail = ServiceAccountGmail(
    'gmail_service_account.json', 
    'sales@yourdomain.com'  # The email to send from
)
'''
    
    print("📁 Service Account File Example:")
    print(service_account_code)
    
    print("\n📋 Service Account JSON should look like:")
    print('''{
  "type": "service_account",
  "project_id": "your-project",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",
  "client_email": "gfmd-email-sender@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}''')

def show_oauth_example():
    """Show OAuth integration example"""
    
    print("\n🔧 OAuth 2.0 Integration")
    print("=" * 50)
    
    print("📁 OAuth JSON should look like:")
    print('''{
  "installed": {
    "client_id": "...apps.googleusercontent.com",
    "project_id": "your-project",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "...",
    "redirect_uris": ["http://localhost"]
  }
}''')
    
    print("\n✅ OAuth is already implemented in your system!")
    print("Just need to:")
    print("1. Download OAuth credentials from Google Cloud")
    print("2. Save as 'gmail_credentials.json'")
    print("3. Run 'python3 test_gmail_setup.py'")

def main():
    """Main function"""
    choice = show_gmail_setup_options()
    
    if choice == "1":
        show_service_account_example()
    elif choice == "2":
        show_oauth_example()
    elif choice == "3":
        show_service_account_example()
        show_oauth_example()
    else:
        print("Invalid choice")
    
    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("1. Choose your setup method")
    print("2. Follow the steps above")
    print("3. Your system will automatically start sending emails!")
    print("4. Daily automation will send with your styling rules")

if __name__ == "__main__":
    main()