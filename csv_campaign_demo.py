#!/usr/bin/env python3
"""
Working Campaign Demo - Uses CSV data directly (bypasses Firestore issues)
"""

import csv
import json
from datetime import datetime
import random
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global storage for contacts (simulating database)
contacts_data = []
campaign_history = []

def load_contacts_from_csv():
    """Load contacts from CSV file"""
    global contacts_data
    contacts_data = []
    
    try:
        with open('definitive_healthcare_data.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader):
                if i >= 100:  # Limit for demo
                    break
                    
                email = row.get('Business Email', '').strip()
                if email and '@' in email:
                    contact = {
                        'contact_id': row.get('Definitive Executive ID', f'demo_{i}'),
                        'contact_name': row.get('Executive Name', 'Unknown'),
                        'email': email,
                        'title': row.get('Title', ''),
                        'company_name': row.get('Hospital Name', ''),
                        'city': row.get('City', ''),
                        'state': row.get('State', ''),
                        'qualification_score': random.randint(6, 10),
                        'last_contacted': None,
                        'email_sent_count': 0
                    }
                    contacts_data.append(contact)
        
        print(f"✅ Loaded {len(contacts_data)} contacts from CSV")
        return True
        
    except FileNotFoundError:
        print("❌ CSV file not found")
        return False
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return False

@app.route('/api/v1/contacts/demo-stats', methods=['GET'])
def demo_contact_stats():
    """Get demo contact statistics"""
    available = [c for c in contacts_data if c['email_sent_count'] == 0]
    
    return jsonify({
        'total_contacts': len(contacts_data),
        'available_contacts': len(available),
        'contacted_today': len([c for c in contacts_data if c['email_sent_count'] > 0]),
        'message': f'Demo database contains {len(contacts_data)} contacts, {len(available)} available for outreach',
        'demo_mode': True
    })

@app.route('/api/v1/automation/demo-campaign', methods=['POST'])
def demo_campaign():
    """Run demo campaign using CSV data"""
    try:
        data = request.get_json()
        num_emails = data.get('num_emails', 5)
        
        # Get available contacts
        available_contacts = [c for c in contacts_data if c['email_sent_count'] == 0]
        
        if not available_contacts:
            return jsonify({
                'success': False,
                'message': 'No contacts available for demo campaign'
            })
        
        # Select contacts for campaign
        selected = available_contacts[:num_emails]
        
        # Simulate sending emails
        emails_sent = 0
        for contact in selected:
            # Simulate 90% success rate
            if random.random() < 0.9:
                contact['email_sent_count'] += 1
                contact['last_contacted'] = datetime.now().isoformat()
                emails_sent += 1
                
                # Log campaign
                campaign_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'contact_name': contact['contact_name'],
                    'email': contact['email'],
                    'company': contact['company_name'],
                    'status': 'sent'
                })
        
        return jsonify({
            'success': True,
            'message': f'✅ Demo campaign completed! Sent {emails_sent} emails',
            'emails_sent': emails_sent,
            'emails_attempted': len(selected),
            'demo_mode': True,
            'results': [
                {
                    'name': c['contact_name'],
                    'email': c['email'][:20] + '...', # Partial email for privacy
                    'company': c['company_name']
                } for c in selected[:emails_sent]
            ]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Demo campaign error: {str(e)}'
        }), 500

@app.route('/api/v1/system/demo-status', methods=['GET'])
def demo_system_status():
    """Demo system status"""
    return jsonify({
        'gmail': True,  # Simulated
        'firestore': False,  # Known issue
        'vertexai': False,  # Known issue  
        'emailsToday': len(campaign_history),
        'dailyLimit': 100,
        'remaining': 100 - len(campaign_history),
        'demo_mode': True,
        'message': 'Demo mode - using CSV data directly'
    })

if __name__ == '__main__':
    print("🚀 GFMD Campaign Demo Server")
    print("=" * 50)
    
    if load_contacts_from_csv():
        print(f"✅ Demo ready with {len(contacts_data)} contacts")
        print("📧 Demo endpoints:")
        print("   POST /api/v1/automation/demo-campaign")
        print("   GET  /api/v1/contacts/demo-stats")  
        print("   GET  /api/v1/system/demo-status")
        print("=" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=8081)
    else:
        print("❌ Failed to load contacts. Check CSV file path.")