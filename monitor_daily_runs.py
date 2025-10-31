#!/usr/bin/env python3
"""
Monitor Daily GFMD Swarm Agent Runs
View logs, summaries, and performance metrics
"""

import os
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path

def show_recent_logs():
    """Show recent log entries"""
    log_dir = Path(__file__).parent / "logs"
    
    print("📋 RECENT LOG ENTRIES")
    print("=" * 50)
    
    # Find most recent log file
    log_files = list(log_dir.glob("daily_scheduler_*.log"))
    if not log_files:
        print("No log files found")
        return
    
    latest_log = max(log_files, key=os.path.getctime)
    print(f"📄 Latest log: {latest_log.name}")
    print()
    
    # Show last 20 lines
    try:
        with open(latest_log, 'r') as f:
            lines = f.readlines()
            for line in lines[-20:]:
                print(line.rstrip())
    except Exception as e:
        print(f"Error reading log: {e}")

def show_execution_summaries():
    """Show recent execution summaries"""
    log_dir = Path(__file__).parent / "logs"
    
    print("\n📊 EXECUTION SUMMARIES")
    print("=" * 50)
    
    # Find summary files from last 7 days
    summary_files = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        summary_file = log_dir / f"daily_summary_{date.strftime('%Y%m%d')}.json"
        if summary_file.exists():
            summary_files.append(summary_file)
    
    if not summary_files:
        print("No execution summaries found")
        return
    
    for summary_file in sorted(summary_files, reverse=True):
        try:
            with open(summary_file, 'r') as f:
                summary = json.load(f)
            
            date = summary_file.stem.split('_')[-1]
            formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
            
            print(f"📅 {formatted_date}")
            print(f"   Duration: {summary.get('duration_minutes', 0):.1f} minutes")
            print(f"   Prospects: {summary.get('total_prospects', 0)}")
            print(f"   Successful: {summary.get('successful', 0)}")
            print(f"   Failed: {summary.get('failed', 0)}")
            print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
            print()
            
        except Exception as e:
            print(f"Error reading summary {summary_file.name}: {e}")

def show_google_sheets_status():
    """Show Google Sheets integration status"""
    print("🔗 GOOGLE SHEETS INTEGRATION")
    print("=" * 50)
    
    try:
        from google_sheets_config import is_google_sheets_enabled, get_google_sheets_config
        from google_sheets_integration import GoogleSheetsExporter
        
        if is_google_sheets_enabled():
            config = get_google_sheets_config()
            exporter = GoogleSheetsExporter(config)
            
            print("✅ Google Sheets integration is ENABLED")
            print(f"📊 Spreadsheet: {config.spreadsheet_name}")
            print(f"🔗 URL: {exporter.get_spreadsheet_url()}")
            print(f"📧 Shared with: {', '.join(config.share_with_emails) if config.share_with_emails else 'None'}")
        else:
            print("❌ Google Sheets integration is NOT enabled")
            print("Run setup guide: python3 google_sheets_config.py")
            
    except Exception as e:
        print(f"Error checking Google Sheets status: {e}")

def show_cron_status():
    """Show cron job status"""
    print("\n⏰ CRON JOB STATUS")
    print("=" * 50)
    
    try:
        import subprocess
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        
        if result.returncode == 0:
            cron_lines = result.stdout.strip().split('\n')
            agent_jobs = [line for line in cron_lines if 'run_daily_agents' in line or 'daily_scheduler' in line]
            
            if agent_jobs:
                print("✅ Cron job is ACTIVE")
                for job in agent_jobs:
                    print(f"   {job}")
                print("\n📅 Next execution: Tomorrow at 9:00 AM CST")
            else:
                print("❌ No GFMD agent cron jobs found")
        else:
            print("❌ Could not check cron status")
            
    except Exception as e:
        print(f"Error checking cron status: {e}")

def show_prospect_sources():
    """Show available prospect sources"""
    print("\n📂 PROSPECT SOURCES")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    
    # Check sample prospects
    sample_file = base_dir / "examples" / "sample_prospects.json"
    if sample_file.exists():
        try:
            with open(sample_file, 'r') as f:
                prospects = json.load(f)
            print(f"✅ Sample prospects: {len(prospects)} available")
        except:
            print("⚠️ Sample prospects file exists but could not be read")
    else:
        print("❌ No sample prospects file found")
    
    # Check prospect queue
    queue_file = base_dir / "prospect_queue.json"
    if queue_file.exists():
        try:
            with open(queue_file, 'r') as f:
                queue = json.load(f)
            print(f"📋 Prospect queue: {len(queue)} prospects waiting")
        except:
            print("⚠️ Prospect queue file exists but could not be read")
    else:
        print("📋 Prospect queue: Empty")
    
    # Check for incoming files
    incoming_files = list(base_dir.glob("incoming_prospects_*.json")) + list(base_dir.glob("incoming_prospects_*.csv"))
    if incoming_files:
        print(f"📥 Incoming files: {len(incoming_files)} files found")
        for f in incoming_files:
            print(f"   - {f.name}")
    else:
        print("📥 Incoming files: None")
    
    # Check processed files
    processed_dir = base_dir / "processed"
    if processed_dir.exists():
        processed_files = list(processed_dir.glob("*"))
        print(f"✅ Processed files: {len(processed_files)} files")
    else:
        print("✅ Processed files: Directory not created yet")

def main():
    """Main monitoring dashboard"""
    print("🔍 GFMD SWARM AGENT MONITORING DASHBOARD")
    print("=" * 60)
    print(f"🕐 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S CST')}")
    
    show_cron_status()
    show_google_sheets_status()
    show_prospect_sources()
    show_execution_summaries()
    show_recent_logs()
    
    print("\n🔧 MANAGEMENT COMMANDS")
    print("=" * 50)
    print("Run now:          python3 daily_scheduler.py --run-now")
    print("View live logs:   tail -f logs/daily_scheduler_$(date +%Y%m%d).log")
    print("Check cron:       crontab -l")
    print("Remove cron:      crontab -l | grep -v run_daily_agents | crontab -")

if __name__ == "__main__":
    main()