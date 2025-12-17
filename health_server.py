#!/usr/bin/env python3
"""
Simple health check server for Railway deployment
Runs alongside the main automation scheduler
"""

import os
import threading
import time
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

# Global status tracking
automation_status = {
    "status": "starting",
    "last_check": None,
    "uptime_start": datetime.now().isoformat()
}

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "automation": automation_status
    }), 200

@app.route('/')
def root():
    """Root endpoint showing service info"""
    return jsonify({
        "service": "GFMD Email Automation",
        "status": automation_status["status"],
        "uptime_start": automation_status["uptime_start"],
        "last_check": automation_status["last_check"],
        "endpoints": {
            "/health": "Health check",
            "/status": "Automation status",
            "/": "This info page"
        }
    })

@app.route('/status')
def status():
    """Detailed status endpoint"""
    return jsonify(automation_status)

def update_status():
    """Background thread to update automation status"""
    while True:
        automation_status["last_check"] = datetime.now().isoformat()
        automation_status["status"] = "running"
        time.sleep(60)  # Update every minute

def start_scheduler():
    """Start the email automation scheduler in background"""
    import subprocess
    import sys
    
    try:
        subprocess.Popen([
            sys.executable, 
            'complete_sequence_automation.py', 
            'schedule'
        ])
        print("✅ Email scheduler started in background")
    except Exception as e:
        print(f"❌ Failed to start scheduler: {e}")

if __name__ == '__main__':
    # Start background status updater
    status_thread = threading.Thread(target=update_status, daemon=True)
    status_thread.start()
    
    # Start the email scheduler
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Get port from environment (Railway sets this)
    port = int(os.environ.get('PORT', 8080))
    
    print(f"🚂 Starting GFMD health server on port {port}")
    print(f"📧 Email automation scheduler starting...")
    
    # Start Flask server
    app.run(host='0.0.0.0', port=port)