#!/usr/bin/env python3
"""
Simple health check server for Railway deployment
Runs alongside the main automation scheduler
"""

import os
import threading
import time
import subprocess
import sys
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

# Global status tracking
automation_status = {
    "status": "starting",
    "last_check": None,
    "uptime_start": datetime.now().isoformat()
}
scheduler_process = None
integration_readiness = {"status": "checking", "ready": False}


def observed_status():
    if scheduler_process is not None:
        code = scheduler_process.poll()
        automation_status["status"] = "running" if code is None else "failed"
        automation_status["exit_code"] = code
    return dict(automation_status)

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    current = observed_status()
    return jsonify({
        "status": "unhealthy" if current["status"] == "failed" else "healthy",
        "timestamp": datetime.now().isoformat(),
        "automation": current,
        "integrations": integration_readiness,
        "sending_enabled": os.environ.get("GFMD_EMAIL_SEND_ENABLED") == "1",
    }), 503 if current["status"] == "failed" else 200

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
    return jsonify(observed_status())


@app.route('/readiness')
def readiness():
    return jsonify(integration_readiness), 200 if integration_readiness.get("ready") else 503

def update_status():
    """Background thread to update automation status"""
    while True:
        automation_status["last_check"] = datetime.now().isoformat()
        observed_status()
        time.sleep(60)  # Update every minute

def start_scheduler():
    """Start the email automation scheduler in background"""
    global scheduler_process
    if os.environ.get("GFMD_AUTOMATION_ENABLED") != "1":
        automation_status["status"] = "disabled"
        print("Automation is disabled for production verification", flush=True)
        return
    if not integration_readiness.get("ready"):
        automation_status["status"] = "blocked"
        print("Automation blocked: integration readiness checks must pass", flush=True)
        return
    try:
        scheduler_process = subprocess.Popen([
            sys.executable, 
            'complete_sequence_automation.py', 
            'schedule'
        ])
        automation_status["status"] = "running"
        print("Email scheduler process started", flush=True)
    except Exception as e:
        automation_status["status"] = "failed"
        print("Failed to start scheduler: " + type(e).__name__, flush=True)


def check_integrations_then_start():
    from production_readiness import check_readiness
    try:
        result = check_readiness()
        integration_readiness.clear()
        integration_readiness.update(result)
        print("PRODUCTION_READINESS " + __import__('json').dumps(result), flush=True)
        start_scheduler()
    except Exception as error:
        integration_readiness.update(status="failed", ready=False, error_type=type(error).__name__)
        automation_status["status"] = "blocked"

if __name__ == '__main__':
    # Start background status updater
    status_thread = threading.Thread(target=update_status, daemon=True)
    status_thread.start()
    
    # Start the email scheduler
    scheduler_thread = threading.Thread(target=check_integrations_then_start, daemon=True)
    scheduler_thread.start()
    
    # Get port from environment (Railway sets this)
    port = int(os.environ.get('PORT', 8080))
    
    print(f"🚂 Starting GFMD health server on port {port}")
    print(f"📧 Email automation scheduler starting...")
    
    # Start Flask server
    app.run(host='0.0.0.0', port=port)
