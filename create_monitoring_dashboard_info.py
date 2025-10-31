#!/usr/bin/env python3
"""
Google Cloud Monitoring Setup for GFMD AI Swarm
Visual monitoring dashboard creation and monitoring guidance
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def create_monitoring_dashboard_diagram():
    """Create Google Cloud monitoring dashboard visualization"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(8, 11.5, 'Google Cloud Monitoring Dashboard for GFMD AI Swarm', 
            ha='center', va='center', fontsize=18, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#4285F4', color='white'))
    
    # Monitoring Sections
    sections = [
        {
            'title': 'Cloud Run Metrics',
            'pos': (4, 9.5), 'size': (3.5, 2),
            'color': '#34A853',
            'metrics': [
                '• Request count & latency',
                '• Memory & CPU usage',
                '• Error rates & status codes',
                '• Container instances',
                '• Billing & cost tracking'
            ]
        },
        {
            'title': 'Agent Performance',
            'pos': (12, 9.5), 'size': (3.5, 2),
            'color': '#EA4335',
            'metrics': [
                '• Email success/failure rates',
                '• Processing time per prospect',
                '• Agent response times',
                '• Memory usage patterns',
                '• API call volumes'
            ]
        },
        {
            'title': 'System Health',
            'pos': (4, 6.5), 'size': (3.5, 2),
            'color': '#FBBC04',
            'metrics': [
                '• Service availability',
                '• Database connections',
                '• External API status',
                '• Error logs & alerts',
                '• Performance bottlenecks'
            ]
        },
        {
            'title': 'Business Metrics',
            'pos': (12, 6.5), 'size': (3.5, 2),
            'color': '#9C27B0',
            'metrics': [
                '• Daily email volume',
                '• Contact processing rate',
                '• Qualification scores',
                '• Success conversion rates',
                '• ROI tracking'
            ]
        }
    ]
    
    # Draw monitoring sections
    for section in sections:
        x, y = section['pos']
        w, h = section['size']
        
        # Section box
        box = FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.1",
                             facecolor=section['color'], edgecolor='darkgray', 
                             linewidth=2, alpha=0.8)
        ax.add_patch(box)
        
        # Section title
        ax.text(x, y+0.6, section['title'], ha='center', va='center', 
                fontsize=12, fontweight='bold', color='white')
        
        # Metrics
        metrics_text = '\n'.join(section['metrics'])
        ax.text(x, y-0.2, metrics_text, ha='center', va='center', 
                fontsize=9, color='white')
    
    # Monitoring Tools
    tools_box = FancyBboxPatch((1, 3.5), 14, 1.5, boxstyle="round,pad=0.1",
                               facecolor='#37474F', edgecolor='darkgray', 
                               linewidth=2, alpha=0.9)
    ax.add_patch(tools_box)
    
    ax.text(8, 4.6, '🛠️ GOOGLE CLOUD MONITORING TOOLS', ha='center', va='center', 
            fontsize=14, fontweight='bold', color='white')
    
    tools_text = """Cloud Monitoring • Cloud Logging • Error Reporting • Cloud Trace • Cloud Profiler • Alerting Policies"""
    ax.text(8, 4, tools_text, ha='center', va='center', 
            fontsize=11, color='white')
    
    # Setup Instructions
    setup_box = FancyBboxPatch((2, 1), 12, 2, boxstyle="round,pad=0.1",
                               facecolor='#F5F5F5', edgecolor='#2196F3', 
                               linewidth=2, alpha=0.9)
    ax.add_patch(setup_box)
    
    ax.text(8, 2.5, '📋 MONITORING SETUP INSTRUCTIONS', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='#2196F3')
    
    setup_text = """1. Go to Google Cloud Console → Monitoring
2. Select project: windy-tiger-471523-m5
3. Create Custom Dashboard: "GFMD AI Swarm Dashboard"
4. Add charts for Cloud Run service: gfmd-a2a-swarm-agent
5. Configure alerts for email failures, high error rates, resource usage
6. Set up notification channels (email, Slack, etc.)"""
    
    ax.text(8, 1.7, setup_text, ha='center', va='center', 
            fontsize=10, color='#37474F')
    
    plt.tight_layout()
    plt.savefig('monitoring_dashboard_diagram.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    # plt.show()  # Comment out for non-interactive use
    
    print("✅ Monitoring Dashboard Diagram saved as 'monitoring_dashboard_diagram.png'")

def print_monitoring_urls():
    """Print direct URLs for Google Cloud monitoring"""
    
    project_id = "windy-tiger-471523-m5"
    service_name = "gfmd-a2a-swarm-agent"
    
    urls = {
        "Cloud Monitoring Dashboard": f"https://console.cloud.google.com/monitoring?project={project_id}",
        "Cloud Run Service Monitoring": f"https://console.cloud.google.com/run/detail/us-central1/{service_name}?project={project_id}",
        "Cloud Logging": f"https://console.cloud.google.com/logs/query?project={project_id}",
        "Error Reporting": f"https://console.cloud.google.com/errors?project={project_id}",
        "Cloud Trace": f"https://console.cloud.google.com/traces?project={project_id}",
        "Alerting Policies": f"https://console.cloud.google.com/monitoring/alerting?project={project_id}",
        "Uptime Checks": f"https://console.cloud.google.com/monitoring/uptime?project={project_id}",
        "Vertex AI Monitoring": f"https://console.cloud.google.com/vertex-ai?project={project_id}"
    }
    
    print("\n🔗 GOOGLE CLOUD MONITORING URLs")
    print("=" * 50)
    
    for name, url in urls.items():
        print(f"📊 {name}:")
        print(f"   {url}")
        print()
    
    print("🎯 KEY METRICS TO MONITOR:")
    print("-" * 30)
    print("• Cloud Run request count (target: 50+ daily)")
    print("• Email success rate (target: 95%+)")
    print("• Average processing time (target: <3 min/prospect)")
    print("• Memory usage (monitor for spikes)")
    print("• API quota usage (Gmail, Sheets, Search)")
    print("• Error rates and logs")
    
    print("\n📧 ALERT RECOMMENDATIONS:")
    print("-" * 30)
    print("• Email failure rate > 10%")
    print("• Processing time > 5 minutes")
    print("• Memory usage > 80%")
    print("• Service downtime > 2 minutes")
    print("• Daily email count < 30")

if __name__ == "__main__":
    create_monitoring_dashboard_diagram()
    print_monitoring_urls()