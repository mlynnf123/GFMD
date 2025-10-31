#!/usr/bin/env python3
"""
Dashboard API for GFMD AI Swarm (Groq-Powered)
Simple Flask API that serves data to the frontend dashboard
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
from simple_storage import SimpleStorage
from groq_coordinator import GroqCoordinator
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js frontend

# Initialize storage
storage = SimpleStorage()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0-groq'
    })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get main dashboard metrics"""
    try:
        stats = storage.get_stats()
        tracking = storage.tracking

        # Calculate metrics
        today = datetime.now().date().isoformat()
        sent_today = sum(
            1 for contact in tracking["contacts"].values()
            for campaign in contact.get("campaigns", [])
            if campaign.get("timestamp", "").startswith(today)
        )

        # This week
        week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
        sent_this_week = sum(
            1 for contact in tracking["contacts"].values()
            for campaign in contact.get("campaigns", [])
            if campaign.get("timestamp", "") >= week_ago
        )

        # Success rate (from recent campaigns)
        recent_campaigns = tracking.get("campaigns", [])[-10:]  # Last 10 campaigns
        total_attempted = sum(c.get("emails_sent", 0) + c.get("emails_failed", 0) for c in recent_campaigns)
        total_sent = sum(c.get("emails_sent", 0) for c in recent_campaigns)
        success_rate = (total_sent / total_attempted * 100) if total_attempted > 0 else 0

        return jsonify({
            'emails_sent_today': sent_today,
            'emails_sent_this_week': sent_this_week,
            'success_rate': round(success_rate, 1),
            'total_contacts': stats['total_contacts'],
            'contacts_ready': stats['never_contacted'],
            'contacts_in_cooldown': stats['contacted'],
            'campaigns_run': len(tracking.get("campaigns", []))
        })

    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    """Get list of campaigns"""
    try:
        campaigns = storage.tracking.get("campaigns", [])
        # Return most recent first
        campaigns_sorted = sorted(
            campaigns,
            key=lambda x: x.get('started_at', ''),
            reverse=True
        )
        return jsonify({'campaigns': campaigns_sorted})

    except Exception as e:
        logger.error(f"Error getting campaigns: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns/run', methods=['POST'])
def run_campaign():
    """Start a new campaign"""
    try:
        data = request.get_json()
        num_prospects = data.get('num_prospects', 10)
        actually_send = data.get('actually_send', False)
        min_score = data.get('min_score', 50)

        # Import and run campaign
        from run_campaign import GFMDCampaignRunner
        runner = GFMDCampaignRunner()

        # Run async campaign
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                runner.run_campaign(
                    num_prospects=num_prospects,
                    min_qualification_score=min_score,
                    actually_send_emails=actually_send
                )
            )
        finally:
            loop.close()

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error running campaign: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get paginated list of contacts"""
    try:
        # Query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))
        search = request.args.get('search', '')
        status_filter = request.args.get('status', 'all')

        # Get all contacts
        all_contacts = storage.get_contacts_for_outreach(limit=10000)

        # Filter by search
        if search:
            search_lower = search.lower()
            all_contacts = [
                c for c in all_contacts
                if search_lower in c.get('contact_name', '').lower()
                or search_lower in c.get('company_name', '').lower()
                or search_lower in c.get('email', '').lower()
            ]

        # Filter by status
        if status_filter == 'never_contacted':
            all_contacts = [
                c for c in all_contacts
                if c['email'] not in storage.tracking['contacts']
            ]
        elif status_filter == 'ready':
            cutoff = datetime.now() - timedelta(days=30)
            all_contacts = [
                c for c in all_contacts
                if c['email'] not in storage.tracking['contacts']
                or datetime.fromisoformat(
                    storage.tracking['contacts'][c['email']].get('last_contacted', '2020-01-01')
                ) < cutoff
            ]

        # Paginate
        total = len(all_contacts)
        start = (page - 1) * per_page
        end = start + per_page
        contacts_page = all_contacts[start:end]

        return jsonify({
            'contacts': contacts_page,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })

    except Exception as e:
        logger.error(f"Error getting contacts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<email>', methods=['GET'])
def get_contact_detail(email):
    """Get details for a specific contact"""
    try:
        contact_tracking = storage.tracking['contacts'].get(email, {})

        # Find contact in CSV
        contacts = storage.get_contacts_for_outreach(limit=10000)
        contact = next((c for c in contacts if c['email'] == email), None)

        if not contact:
            return jsonify({'error': 'Contact not found'}), 404

        # Merge with tracking data
        contact['tracking'] = contact_tracking

        return jsonify(contact)

    except Exception as e:
        logger.error(f"Error getting contact detail: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data for charts"""
    try:
        tracking = storage.tracking

        # Emails over time (last 30 days)
        emails_by_day = {}
        for contact in tracking['contacts'].values():
            for campaign in contact.get('campaigns', []):
                timestamp = campaign.get('timestamp', '')
                if timestamp:
                    day = timestamp[:10]  # YYYY-MM-DD
                    emails_by_day[day] = emails_by_day.get(day, 0) + 1

        # Convert to sorted list
        emails_timeline = [
            {'date': day, 'count': count}
            for day, count in sorted(emails_by_day.items())
        ]

        # Campaign success rates
        campaign_stats = []
        for campaign in tracking.get('campaigns', [])[-30:]:  # Last 30
            campaign_stats.append({
                'campaign_id': campaign.get('campaign_id', ''),
                'date': campaign.get('started_at', '')[:10],
                'sent': campaign.get('emails_sent', 0),
                'failed': campaign.get('emails_failed', 0)
            })

        return jsonify({
            'emails_timeline': emails_timeline,
            'campaign_stats': campaign_stats
        })

    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    return jsonify({
        'groq_api_key': os.environ.get('GROQ_API_KEY', '')[:20] + '...',
        'daily_email_limit': 100,
        'recontact_interval_days': 30,
        'min_qualification_score': 50,
        'sender_name': 'Mark Thompson',
        'sender_email': 'mark@gfmdmedical.com'
    })

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings"""
    # For now, just acknowledge
    # In production, you'd save these to a config file
    data = request.get_json()
    return jsonify({'success': True, 'message': 'Settings updated'})

@app.route('/api/stats', methods=['GET'])
def get_system_stats():
    """Get system statistics"""
    try:
        stats = storage.get_stats()

        # Check system status
        gmail_status = os.path.exists('gmail_token.json')
        groq_status = bool(os.environ.get('GROQ_API_KEY'))
        csv_status = os.path.exists('definitive_healthcare_data.csv')

        return jsonify({
            'system': {
                'gmail_connected': gmail_status,
                'groq_connected': groq_status,
                'contacts_loaded': csv_status,
                'version': '2.0.0-groq'
            },
            'storage': stats
        })

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting GFMD Dashboard API")
    print("=" * 50)
    print("API will be available at: http://localhost:5000")
    print("Endpoints:")
    print("  GET  /api/health")
    print("  GET  /api/metrics")
    print("  GET  /api/campaigns")
    print("  POST /api/campaigns/run")
    print("  GET  /api/contacts")
    print("  GET  /api/contacts/<email>")
    print("  GET  /api/analytics")
    print("  GET  /api/settings")
    print("  POST /api/settings")
    print("  GET  /api/stats")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5000, debug=True)
