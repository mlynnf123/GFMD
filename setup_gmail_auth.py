#!/usr/bin/env python3
"""
Gmail Authentication Setup
Run this once to authenticate and create gmail_token.json
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 
          'https://www.googleapis.com/auth/gmail.readonly']

def setup_gmail_authentication():
    """Set up Gmail API authentication"""
    print("🔐 Setting up Gmail Authentication...")
    
    creds = None
    
    # Check if token file exists
    if os.path.exists('gmail_token.json'):
        try:
            creds = Credentials.from_authorized_user_file('gmail_token.json', SCOPES)
            print("✅ Found existing token file")
        except Exception as e:
            print(f"⚠️  Existing token invalid: {e}")
    
    # If there are no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("✅ Refreshed expired token")
            except Exception as e:
                print(f"⚠️  Token refresh failed: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists('gmail_credentials.json'):
                print("❌ Gmail credentials file not found!")
                print("📋 Please ensure gmail_credentials.json exists with your OAuth credentials")
                return False
            
            print("🌐 Opening browser for authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'gmail_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            print("✅ Authentication completed")
    
    # Save the credentials for the next run
    with open('gmail_token.json', 'w') as token:
        token.write(creds.to_json())
    print("✅ Token saved to gmail_token.json")
    
    # Test the connection
    try:
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        print(f"✅ Gmail connected successfully!")
        print(f"📧 Email: {profile.get('emailAddress')}")
        print(f"📊 Total messages: {profile.get('messagesTotal', 0)}")
        return True
    except Exception as e:
        print(f"❌ Gmail connection test failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_gmail_authentication()
    
    if success:
        print("\n🎉 Gmail authentication setup complete!")
        print("📧 You can now send emails through the sequence system")
        print("\n🚀 Next steps:")
        print("  1. python3 production_sequence_runner.py stats")
        print("  2. python3 production_sequence_runner.py process")
    else:
        print("\n❌ Authentication failed. Please check your credentials and try again.")