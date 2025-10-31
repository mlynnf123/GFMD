#!/usr/bin/env python3
"""
Get Google Custom Search API Key for your existing project
"""

import webbrowser

def get_google_api_key():
    """Guide user through getting API key from their existing Google Cloud project"""
    
    print("🔑 GET GOOGLE CUSTOM SEARCH API KEY")
    print("=" * 50)
    print(f"📁 Project: windy-tiger-471523-m5")
    print(f"🔍 Search Engine ID: 418ed624303f8477f ✅")
    print()
    
    print("📋 STEPS TO GET API KEY:")
    print("-" * 30)
    print("1. Go to Google Cloud Console APIs & Credentials:")
    
    # The direct URL to create API key in their project
    api_url = "https://console.cloud.google.com/apis/credentials?project=windy-tiger-471523-m5"
    print(f"   {api_url}")
    print()
    print("2. Click 'Create Credentials' → 'API Key'")
    print("3. Copy the API Key that appears")
    print("4. Paste it into google_search_credentials.json")
    print()
    
    # Enable the API first
    enable_url = "https://console.cloud.google.com/apis/library/customsearch.googleapis.com?project=windy-tiger-471523-m5"
    print("📡 FIRST: Enable Custom Search API:")
    print(f"   {enable_url}")
    print("   → Click 'Enable' if not already enabled")
    print()
    
    choice = input("🚀 Open these URLs automatically? (y/n): ").lower().strip()
    
    if choice == 'y':
        print("🌐 Opening Google Cloud Console...")
        webbrowser.open(enable_url)
        input("Press Enter after enabling the API...")
        webbrowser.open(api_url)
        print("✅ Now create your API Key and copy it!")
    
    print()
    print("📝 AFTER YOU GET THE API KEY:")
    print("Edit google_search_credentials.json and replace:")
    print('   "api_key": "YOUR_GOOGLE_SEARCH_API_KEY_HERE"')
    print("with:")
    print('   "api_key": "YOUR_ACTUAL_API_KEY"')
    print()
    print("🎉 Then your Google Search integration will be fully active!")

if __name__ == "__main__":
    get_google_api_key()