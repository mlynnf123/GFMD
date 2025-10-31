#!/usr/bin/env python3
"""
Create single-page portfolio presentation for GFMD AI Swarm Agent
Perfect for portfolio showcase - compact and professional
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def create_portfolio_one_pager():
    """Create single-page portfolio presentation"""
    
    fig, ax = plt.subplots(1, 1, figsize=(8.5, 11))  # Standard letter size
    ax.set_xlim(0, 8.5)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    # Header
    header_box = FancyBboxPatch((0.5, 9.5), 7.5, 1.2, boxstyle="round,pad=0.1",
                                facecolor='#2C3E50', alpha=0.9)
    ax.add_patch(header_box)
    ax.text(4.25, 10.4, 'AI Agent Swarm System', ha='center', va='center', 
            fontsize=20, fontweight='bold', color='white')
    ax.text(4.25, 9.9, 'Automated Healthcare Outreach Platform', ha='center', va='center', 
            fontsize=12, color='white', style='italic')
    
    # Project Overview
    overview_box = FancyBboxPatch((0.5, 8), 7.5, 1.2, boxstyle="round,pad=0.1",
                                  facecolor='#ECF0F1', edgecolor='#BDC3C7', linewidth=1)
    ax.add_patch(overview_box)
    ax.text(4.25, 8.8, 'Project Overview', ha='center', va='center', 
            fontsize=14, fontweight='bold', color='#2C3E50')
    overview_text = """Multi-agent AI system that automates personalized email outreach to healthcare 
decision makers using Google Cloud infrastructure and advanced AI coordination protocols."""
    ax.text(4.25, 8.4, overview_text, ha='center', va='center', 
            fontsize=10, color='#2C3E50', wrap=True)
    
    # Architecture (4 agents in a row)
    ax.text(4.25, 7.5, 'System Architecture', ha='center', va='center', 
            fontsize=14, fontweight='bold', color='#2C3E50')
    
    agents = [
        {'name': 'Coordinator', 'color': '#E74C3C', 'x': 1.5},
        {'name': 'Research', 'color': '#1ABC9C', 'x': 3},
        {'name': 'Qualification', 'color': '#F39C12', 'x': 4.5},
        {'name': 'Email Composer', 'color': '#27AE60', 'x': 6}
    ]
    
    for agent in agents:
        # Agent circle
        circle = plt.Circle((agent['x'], 6.5), 0.3, facecolor=agent['color'], 
                           edgecolor='white', linewidth=2, alpha=0.9)
        ax.add_patch(circle)
        ax.text(agent['x'], 6.5, 'AI', ha='center', va='center', 
                fontsize=8, fontweight='bold', color='white')
        ax.text(agent['x'], 6, agent['name'], ha='center', va='center', 
                fontsize=9, fontweight='bold', color='#2C3E50')
    
    # A2A Protocol arrow
    ax.annotate('', xy=(5.5, 6.5), xytext=(2, 6.5),
                arrowprops=dict(arrowstyle='<->', color='#34495E', lw=2))
    ax.text(3.75, 6.8, 'Agent-to-Agent (A2A) Protocol', ha='center', va='center', 
            fontsize=9, style='italic', color='#34495E')
    
    # Technical Stack
    tech_box = FancyBboxPatch((0.5, 4.5), 3.5, 1.5, boxstyle="round,pad=0.1",
                              facecolor='#3498DB', alpha=0.1, edgecolor='#3498DB')
    ax.add_patch(tech_box)
    ax.text(2.25, 5.7, 'Technology Stack', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='#2C3E50')
    tech_items = ['• Google Cloud Run', '• Vertex AI (Gemini 2.5)', '• A2A Communication', '• Memory Enhancement']
    for i, item in enumerate(tech_items):
        ax.text(0.7, 5.4 - (i*0.2), item, ha='left', va='center', 
                fontsize=9, color='#2C3E50')
    
    # Results
    results_box = FancyBboxPatch((4.5, 4.5), 3.5, 1.5, boxstyle="round,pad=0.1",
                                 facecolor='#27AE60', alpha=0.1, edgecolor='#27AE60')
    ax.add_patch(results_box)
    ax.text(6.25, 5.7, 'Results Achieved', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='#2C3E50')
    results_items = ['• 50+ Daily Emails', '• 100% Success Rate', '• 5,459 Real Contacts', '• Full Automation']
    for i, item in enumerate(results_items):
        ax.text(4.7, 5.4 - (i*0.2), item, ha='left', va='center', 
                fontsize=9, color='#2C3E50')
    
    # Key Features
    features_box = FancyBboxPatch((0.5, 2.5), 7.5, 1.8, boxstyle="round,pad=0.1",
                                  facecolor='#F8F9FA', edgecolor='#BDC3C7', linewidth=1)
    ax.add_patch(features_box)
    ax.text(4.25, 4, 'Key Features & Capabilities', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='#2C3E50')
    
    features = [
        '✓ AI-Crafted Personalized Messages (No Templates)',
        '✓ Real Healthcare Professionals Only (Zero Fake Emails)',
        '✓ Memory-Enhanced Learning System',
        '✓ Enterprise-Grade Google Cloud Infrastructure',
        '✓ Real-time Monitoring & Alerting',
        '✓ Scalable Architecture (50+ to 100+ emails daily)'
    ]
    
    # Two columns of features
    for i, feature in enumerate(features):
        x_pos = 0.7 if i < 3 else 4.2
        y_pos = 3.6 - ((i % 3) * 0.25)
        ax.text(x_pos, y_pos, feature, ha='left', va='center', 
                fontsize=9, color='#2C3E50')
    
    # Business Impact
    impact_box = FancyBboxPatch((0.5, 0.5), 7.5, 1.8, boxstyle="round,pad=0.1",
                                facecolor='#27AE60', alpha=0.9)
    ax.add_patch(impact_box)
    ax.text(4.25, 2, 'Business Impact & Value', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    
    impact_text = """• Automated healthcare decision maker outreach with 100% delivery success
• Cost-efficient pay-per-use cloud infrastructure reducing operational overhead  
• Professional-grade personalization improving engagement rates
• Scalable system ready for business growth and expansion
• Enterprise monitoring ensuring reliability and performance optimization"""
    
    ax.text(4.25, 1.2, impact_text, ha='center', va='center', 
            fontsize=10, color='white')
    
    # Footer
    ax.text(4.25, 0.2, 'Production-Ready • Google Cloud Deployed • 100% Success Rate Verified', 
            ha='center', va='center', fontsize=10, fontweight='bold', 
            color='#7F8C8D', style='italic')
    
    plt.tight_layout()
    plt.savefig('portfolio_one_pager.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    # plt.show()
    
    print("✅ Portfolio One-Pager saved as 'portfolio_one_pager.png'")

if __name__ == "__main__":
    create_portfolio_one_pager()