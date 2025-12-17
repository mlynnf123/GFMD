#!/usr/bin/env python3
"""
Email Sequence Management API for GFMD Narc Gone Campaign
REST API for managing email sequences, starting campaigns, and monitoring progress
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any
import asyncio
import logging
from datetime import datetime
from email_sequence_orchestrator import EmailSequenceOrchestrator
from sequence_scheduler import SequenceScheduler
from reply_detector import ReplyDetector
import json

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize components
orchestrator = EmailSequenceOrchestrator()
scheduler = SequenceScheduler()
reply_detector = ReplyDetector()

logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "orchestrator": "running",
            "scheduler": "running" if scheduler.running else "stopped",
            "reply_detector": "running"
        }
    })

@app.route('/sequences/start', methods=['POST'])
def start_sequence():
    """Start a new email sequence for a contact"""
    try:
        data = request.get_json()
        
        if not data or 'contact_id' not in data:
            return jsonify({
                "success": False,
                "error": "contact_id required"
            }), 400
        
        contact_id = data['contact_id']
        sequence_name = data.get('sequence_name', 'narcon_law_enforcement')
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            orchestrator.start_sequence(contact_id, sequence_name)
        )
        loop.close()
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/sequences/<contact_id>/pause', methods=['POST'])
def pause_sequence(contact_id: str):
    """Pause email sequence for a contact"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            orchestrator.pause_sequence(contact_id)
        )
        loop.close()
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/sequences/<contact_id>/resume', methods=['POST'])
def resume_sequence(contact_id: str):
    """Resume paused email sequence for a contact"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            orchestrator.resume_sequence(contact_id)
        )
        loop.close()
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/sequences/process', methods=['POST'])
def process_sequences():
    """Manually trigger sequence processing"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            orchestrator.process_sequences()
        )
        loop.close()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/sequences/stats', methods=['GET'])
def get_sequence_stats():
    """Get sequence statistics"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            orchestrator.get_sequence_stats()
        )
        loop.close()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/replies/check', methods=['POST'])
def check_replies():
    """Manually trigger reply checking"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            reply_detector.check_for_replies()
        )
        loop.close()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/replies/handle', methods=['POST'])
def handle_reply():
    """Handle a specific reply"""
    try:
        data = request.get_json()
        
        if not data or 'contact_email' not in data or 'reply_content' not in data:
            return jsonify({
                "success": False,
                "error": "contact_email and reply_content required"
            }), 400
        
        contact_email = data['contact_email']
        reply_content = data['reply_content']
        reply_date = data.get('reply_date')
        
        if reply_date:
            reply_date = datetime.fromisoformat(reply_date)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            orchestrator.handle_reply(contact_email, reply_content, reply_date)
        )
        loop.close()
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/replies/stats', methods=['GET'])
def get_reply_stats():
    """Get reply statistics"""
    try:
        days = request.args.get('days', 7, type=int)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            reply_detector.get_reply_stats(days)
        )
        loop.close()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/scheduler/status', methods=['GET'])
def get_scheduler_status():
    """Get scheduler status"""
    try:
        status = scheduler.get_status()
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/scheduler/run-once', methods=['POST'])
def run_scheduler_once():
    """Run scheduler once for testing"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            scheduler.run_once()
        )
        loop.close()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/sequences/templates', methods=['GET'])
def get_sequence_templates():
    """Get available sequence templates"""
    try:
        from email_sequence_templates import EmailSequenceTemplates
        templates = EmailSequenceTemplates()
        
        sequence_name = request.args.get('sequence', 'narcon_law_enforcement')
        config = templates.get_sequence_config(sequence_name)
        
        return jsonify({
            "success": True,
            "sequence_name": sequence_name,
            "config": config
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/campaigns/bulk-start', methods=['POST'])
def bulk_start_sequences():
    """Start sequences for multiple contacts"""
    try:
        data = request.get_json()
        
        if not data or 'contact_ids' not in data:
            return jsonify({
                "success": False,
                "error": "contact_ids array required"
            }), 400
        
        contact_ids = data['contact_ids']
        sequence_name = data.get('sequence_name', 'narcon_law_enforcement')
        
        results = []
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        for contact_id in contact_ids:
            result = loop.run_until_complete(
                orchestrator.start_sequence(contact_id, sequence_name)
            )
            results.append({
                "contact_id": contact_id,
                "result": result
            })
        
        loop.close()
        
        # Calculate summary
        successful = sum(1 for r in results if r["result"].get("success"))
        failed = len(results) - successful
        
        return jsonify({
            "success": True,
            "total_contacts": len(contact_ids),
            "successful": successful,
            "failed": failed,
            "results": results
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Dashboard endpoints for monitoring
@app.route('/dashboard/overview', methods=['GET'])
def dashboard_overview():
    """Get dashboard overview data"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Get sequence stats
        sequence_stats = loop.run_until_complete(orchestrator.get_sequence_stats())
        
        # Get reply stats
        reply_stats = loop.run_until_complete(reply_detector.get_reply_stats(7))
        
        loop.close()
        
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "sequence_stats": sequence_stats,
            "reply_stats": reply_stats,
            "scheduler_status": scheduler.get_status()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Starting GFMD Email Sequence API")
    print("=" * 50)
    print("Available endpoints:")
    print("  POST /sequences/start - Start sequence for contact")
    print("  POST /sequences/<id>/pause - Pause sequence") 
    print("  POST /sequences/<id>/resume - Resume sequence")
    print("  POST /sequences/process - Process due sequences")
    print("  GET  /sequences/stats - Get sequence statistics")
    print("  POST /replies/check - Check for replies")
    print("  POST /campaigns/bulk-start - Start multiple sequences")
    print("  GET  /dashboard/overview - Dashboard data")
    print("=" * 50)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5001, debug=True)