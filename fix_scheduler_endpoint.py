#!/usr/bin/env python3
"""
Fix Cloud Scheduler by creating a simple trigger endpoint
"""

from flask import Flask, request, jsonify
import asyncio
import sys
sys.path.append('.')
from production_rag_a2a_system import ProductionGFMDSystem

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "GFMD A2A Swarm Agent", 
        "status": "active",
        "endpoints": {
            "daily_trigger": "/daily-automation",
            "health": "/health"
        }
    })

@app.route('/daily-automation', methods=['POST'])
async def daily_automation():
    """Simple endpoint for Cloud Scheduler to trigger daily automation"""
    try:
        print("🚀 Daily automation triggered by Cloud Scheduler")
        
        # Get number of prospects from request body
        data = request.get_json() or {}
        num_prospects = data.get('num_prospects', 50)
        
        print(f"📧 Target: {num_prospects} emails")
        
        # Run the production system
        system = ProductionGFMDSystem()
        results = await system.run_daily_automation(num_prospects)
        
        response = {
            "success": True,
            "message": "Daily automation completed",
            "results": {
                "prospects_processed": results.get("prospects_processed", 0),
                "emails_sent": results.get("emails_sent", 0),
                "memory_enhancements": results.get("memory_enhancements", 0),
                "errors": results.get("errors", [])
            },
            "timestamp": "2025-09-13"
        }
        
        print(f"✅ Automation complete: {results.get('emails_sent', 0)} emails sent")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Automation failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Daily automation failed"
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "GFMD AI Swarm Agent"})

if __name__ == '__main__':
    # For Cloud Run
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)