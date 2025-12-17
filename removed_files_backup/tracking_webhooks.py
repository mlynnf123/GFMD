#!/usr/bin/env python3
"""
Email Tracking Webhooks for GFMD Narcon System
Handles open tracking, click tracking, and analytics
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, redirect, make_response, jsonify
from mongodb_storage import MongoDBStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize MongoDB storage
try:
    storage = MongoDBStorage()
    logger.info("✅ Tracking webhooks connected to MongoDB")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    storage = None

# 1x1 transparent pixel for tracking opens
TRACKING_PIXEL = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff'
    b'\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00'
    b'\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00\x3b'
)

@app.route('/track/open/<tracking_id>')
def track_email_open(tracking_id):
    """Handle email open tracking via invisible pixel"""
    try:
        # Log the open event
        logger.info(f"📧 Email opened - Tracking ID: {tracking_id}")
        
        # Store in MongoDB if available
        if storage:
            storage.record_email_opened(tracking_id)
        
        # Get request information for analytics
        user_agent = request.headers.get('User-Agent', 'Unknown')
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        logger.info(f"   User-Agent: {user_agent}")
        logger.info(f"   IP: {ip_address}")
        
        # Return 1x1 transparent pixel
        response = make_response(TRACKING_PIXEL)
        response.headers['Content-Type'] = 'image/gif'
        response.headers['Content-Length'] = str(len(TRACKING_PIXEL))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error tracking email open: {e}")
        # Still return pixel even on error
        response = make_response(TRACKING_PIXEL)
        response.headers['Content-Type'] = 'image/gif'
        return response

@app.route('/track/click/<tracking_id>')
def track_email_click(tracking_id):
    """Handle email click tracking and redirect to original URL"""
    try:
        # Get the original URL from query parameters
        original_url = request.args.get('url')
        
        if not original_url:
            logger.error(f"❌ No URL provided for click tracking: {tracking_id}")
            return "Invalid tracking link", 400
        
        # Log the click event
        logger.info(f"🔗 Email link clicked - Tracking ID: {tracking_id}")
        logger.info(f"   Original URL: {original_url}")
        
        # Store in MongoDB if available
        if storage:
            storage.record_email_clicked(tracking_id, original_url)
        
        # Get request information for analytics
        user_agent = request.headers.get('User-Agent', 'Unknown')
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        logger.info(f"   User-Agent: {user_agent}")
        logger.info(f"   IP: {ip_address}")
        
        # Redirect to original URL
        return redirect(original_url, code=302)
        
    except Exception as e:
        logger.error(f"❌ Error tracking email click: {e}")
        # Try to redirect anyway if we have the URL
        original_url = request.args.get('url')
        if original_url:
            return redirect(original_url, code=302)
        return "Tracking error", 500

@app.route('/track/stats/<tracking_id>')
def get_tracking_stats(tracking_id):
    """Get tracking statistics for a specific email"""
    try:
        if not storage:
            return jsonify({"error": "Database not available"}), 503
        
        # This would require additional MongoDB queries to get stats
        # For now, return a simple response
        stats = {
            "tracking_id": tracking_id,
            "message": "Stats endpoint - implementation depends on specific MongoDB queries needed"
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"❌ Error getting tracking stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/track/health')
def health_check():
    """Health check endpoint for tracking service"""
    try:
        status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "mongodb_connected": storage is not None
        }
        
        if storage:
            # Test MongoDB connection
            storage.client.admin.command('ping')
            status["mongodb_status"] = "connected"
        else:
            status["mongodb_status"] = "disconnected"
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/track/webhook/reply', methods=['POST'])
def handle_reply_webhook():
    """Handle incoming reply webhooks (if using a service that supports them)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        logger.info(f"💬 Reply webhook received: {data}")
        
        # Extract reply information
        tracking_id = data.get('tracking_id')
        reply_text = data.get('reply_text', '')
        sender_email = data.get('from_email', '')
        
        if tracking_id and storage:
            storage.record_email_reply(tracking_id, reply_text)
            logger.info(f"   Reply recorded for tracking ID: {tracking_id}")
        
        return jsonify({"status": "success", "message": "Reply processed"})
        
    except Exception as e:
        logger.error(f"❌ Error processing reply webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Tracking endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal tracking error"}), 500

if __name__ == "__main__":
    print("🔍 GFMD Email Tracking Server")
    print("=" * 40)
    
    # Check MongoDB connection
    if storage:
        print("✅ MongoDB connected - tracking enabled")
    else:
        print("❌ MongoDB not available - limited tracking")
        print("   Set MONGODB_CONNECTION_STRING environment variable")
    
    print("\n📊 Tracking endpoints:")
    print("   /track/open/<tracking_id>    - Email open tracking")
    print("   /track/click/<tracking_id>   - Email click tracking") 
    print("   /track/stats/<tracking_id>   - Tracking statistics")
    print("   /track/health                - Health check")
    print("   /track/webhook/reply         - Reply webhook")
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"\n🚀 Starting tracking server on {host}:{port}")
    print("📝 Note: For production, use a proper WSGI server like gunicorn")
    
    # Run development server
    app.run(host=host, port=port, debug=True)