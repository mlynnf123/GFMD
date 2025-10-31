#!/usr/bin/env python3
"""
Daily Scheduler for GFMD AI Swarm Agent
Runs the production system to send 50 emails daily
"""

import asyncio
import json
import sys
from datetime import datetime
from production_system import ProductionGFMDSystem

def log_execution(status, message):
    """Log execution details"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime('%Y-%m-%d'),
        "status": status,
        "message": message
    }
    
    # Write to cron log (create directory if it doesn't exist)
    import os
    os.makedirs("logs", exist_ok=True)
    
    try:
        with open(f"logs/daily_scheduler_{datetime.now().strftime('%Y%m%d')}.log", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        # Fallback to stdout if file logging fails
        print(f"[LOG ERROR] Could not write to file: {e}")
        print(f"[{log_entry['timestamp']}] {status}: {message}")
    
    print(f"[{log_entry['timestamp']}] {status}: {message}")

async def main():
    """Run daily email automation"""
    try:
        log_execution("START", "Starting daily GFMD AI Swarm automation")
        
        # Initialize and run production system
        system = ProductionGFMDSystem()
        results = await system.run_daily_automation()
        
        # Log results
        log_execution("SUCCESS", f"Completed daily automation - {results['successful_emails']}/{results['target_emails']} emails sent")
        
        # Save summary
        with open(f"logs/daily_summary_{datetime.now().strftime('%Y%m%d')}.json", "w") as f:
            json.dump(results, f, indent=2)
        
        return 0
        
    except Exception as e:
        log_execution("ERROR", f"Daily automation failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)