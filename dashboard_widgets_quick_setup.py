#!/usr/bin/env python3
"""
Quick Dashboard Widgets Setup for GFMD AI Swarm Agent
Provides copy-paste configurations for Google Cloud Monitoring
"""

def print_widget_configurations():
    """Print widget configurations for easy copy-paste setup"""
    
    print("📊 GFMD AI SWARM AGENT - DASHBOARD WIDGET CONFIGURATIONS")
    print("=" * 80)
    print(f"Dashboard URL: https://console.cloud.google.com/monitoring/dashboards/builder/7b24e670-39ce-4e95-9572-1e1285fb2892?project=windy-tiger-471523-m5")
    print("=" * 80)
    
    widgets = [
        {
            "name": "1. Daily Email Volume (Cloud Run Requests)",
            "type": "Line Chart",
            "config": {
                "Resource Type": "Cloud Run Revision",
                "Metric": "Request count",
                "Filter": "service_name = gfmd-a2a-swarm-agent",
                "Aggregation": "Sum",
                "Alignment": "1 minute"
            }
        },
        {
            "name": "2. Response Time (Request Latency)",
            "type": "Line Chart", 
            "config": {
                "Resource Type": "Cloud Run Revision",
                "Metric": "Request latencies",
                "Filter": "service_name = gfmd-a2a-swarm-agent",
                "Aggregation": "95th percentile",
                "Alignment": "1 minute"
            }
        },
        {
            "name": "3. Memory Usage",
            "type": "Line Chart",
            "config": {
                "Resource Type": "Cloud Run Revision", 
                "Metric": "Container memory utilizations",
                "Filter": "service_name = gfmd-a2a-swarm-agent",
                "Aggregation": "Mean",
                "Alignment": "1 minute"
            }
        },
        {
            "name": "4. CPU Usage",
            "type": "Line Chart",
            "config": {
                "Resource Type": "Cloud Run Revision",
                "Metric": "Container CPU utilizations", 
                "Filter": "service_name = gfmd-a2a-swarm-agent",
                "Aggregation": "Mean",
                "Alignment": "1 minute"
            }
        },
        {
            "name": "5. Error Rate",
            "type": "Line Chart",
            "config": {
                "Resource Type": "Cloud Run Revision",
                "Metric": "Request count",
                "Filter": "service_name = gfmd-a2a-swarm-agent AND response_code_class != '2xx'",
                "Aggregation": "Rate",
                "Alignment": "1 minute"
            }
        },
        {
            "name": "6. Container Instances",
            "type": "Stacked Area Chart",
            "config": {
                "Resource Type": "Cloud Run Revision",
                "Metric": "Container instance count",
                "Filter": "service_name = gfmd-a2a-swarm-agent", 
                "Aggregation": "Mean",
                "Alignment": "1 minute"
            }
        }
    ]
    
    for i, widget in enumerate(widgets, 1):
        print(f"\n🔧 WIDGET {i}: {widget['name']}")
        print("-" * 60)
        print(f"Chart Type: {widget['type']}")
        print("Configuration:")
        for key, value in widget['config'].items():
            print(f"  • {key}: {value}")
        
        if i <= 2:  # Add more details for first two widgets
            print("\n📋 Step-by-step setup:")
            print("  1. Click 'Add Chart' in your dashboard")
            print(f"  2. Select '{widget['type']}'")
            print("  3. Choose 'Metrics Explorer'")
            print("  4. Configure as shown above")
            print("  5. Click 'Apply' then 'Save'")
    
    print("\n" + "="*80)
    print("📧 LOG-BASED METRICS (Custom Business Metrics)")
    print("="*80)
    
    log_metrics = [
        {
            "name": "Email Success Rate",
            "log_filter": '''resource.type="cloud_run_revision"
resource.labels.service_name="gfmd-a2a-swarm-agent"
textPayload=~"Email sent successfully"''',
            "description": "Track successful email deliveries"
        },
        {
            "name": "Email Failure Rate", 
            "log_filter": '''resource.type="cloud_run_revision"
resource.labels.service_name="gfmd-a2a-swarm-agent"
(textPayload=~"Email failed" OR textPayload=~"Error sending")''',
            "description": "Track email delivery failures"
        },
        {
            "name": "Prospect Processing Count",
            "log_filter": '''resource.type="cloud_run_revision"
resource.labels.service_name="gfmd-a2a-swarm-agent"
textPayload=~"Processing.*prospects?"''',
            "description": "Track number of prospects processed"
        },
        {
            "name": "Agent Response Times",
            "log_filter": '''resource.type="cloud_run_revision"
resource.labels.service_name="gfmd-a2a-swarm-agent"
jsonPayload.processing_time''',
            "description": "Track individual agent processing times"
        }
    ]
    
    for metric in log_metrics:
        print(f"\n📊 {metric['name']}")
        print("-" * 40)
        print(f"Purpose: {metric['description']}")
        print("Log Filter:")
        print(metric['log_filter'])
        print("\nSetup: Logging → Logs-based Metrics → Create Metric")
    
    print("\n" + "="*80)
    print("🚨 ALERTING POLICIES")
    print("="*80)
    
    alerts = [
        {
            "name": "High Email Failure Rate",
            "condition": "Email failure rate > 10% for 5 minutes",
            "severity": "Critical",
            "action": "Immediate notification"
        },
        {
            "name": "Service Downtime", 
            "condition": "No requests for 10 minutes during 8 AM - 6 PM CST",
            "severity": "Critical",
            "action": "Immediate notification"
        },
        {
            "name": "High Processing Time",
            "condition": "Request latency > 300 seconds (5 minutes)",
            "severity": "Warning", 
            "action": "Email notification"
        },
        {
            "name": "Low Daily Volume",
            "condition": "Daily email count < 30 by 12:00 PM CST",
            "severity": "Warning",
            "action": "Email notification"
        },
        {
            "name": "High Memory Usage",
            "condition": "Memory utilization > 80% for 10 minutes", 
            "severity": "Warning",
            "action": "Email notification"
        }
    ]
    
    for alert in alerts:
        print(f"\n🔔 {alert['name']}")
        print(f"   Condition: {alert['condition']}")
        print(f"   Severity: {alert['severity']}")
        print(f"   Action: {alert['action']}")
    
    print("\n" + "="*80)
    print("🎯 QUICK SETUP CHECKLIST")
    print("="*80)
    
    checklist = [
        "✅ Add 6 basic Cloud Run metrics widgets",
        "✅ Configure 4 custom log-based metrics", 
        "✅ Set up 5 critical alerting policies",
        "✅ Configure notification channels (email/SMS)",
        "✅ Set dashboard auto-refresh to 1 minute",
        "✅ Share dashboard with team members",
        "✅ Test alerts by triggering conditions",
        "✅ Set up mobile notifications"
    ]
    
    for item in checklist:
        print(item)
    
    print(f"\n🔗 Direct Links:")
    print(f"Dashboard: https://console.cloud.google.com/monitoring/dashboards/builder/7b24e670-39ce-4e95-9572-1e1285fb2892?project=windy-tiger-471523-m5")
    print(f"Alerting: https://console.cloud.google.com/monitoring/alerting?project=windy-tiger-471523-m5")
    print(f"Logs: https://console.cloud.google.com/logs/query?project=windy-tiger-471523-m5")

if __name__ == "__main__":
    print_widget_configurations()