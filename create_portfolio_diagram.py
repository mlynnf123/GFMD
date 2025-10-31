#!/usr/bin/env python3
"""
Create compact portfolio diagram for GFMD AI Swarm Agent
Optimized for portfolio presentation - concise and impactful
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_portfolio_diagram():
    """Create compact portfolio-ready diagram"""
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(6, 7.5, 'AI Agent Swarm for Healthcare Outreach', 
            ha='center', va='center', fontsize=16, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#2C3E50', color='white'))
    
    # System overview box
    overview_box = FancyBboxPatch((0.5, 5.5), 11, 1.5, boxstyle="round,pad=0.1",
                                  facecolor='#ECF0F1', edgecolor='#34495E', linewidth=2)
    ax.add_patch(overview_box)
    ax.text(6, 6.5, 'Multi-Agent AI System', ha='center', va='center', 
            fontsize=14, fontweight='bold', color='#2C3E50')
    ax.text(6, 6, '4 Specialized AI Agents • 5,459 Healthcare Contacts • 100% Success Rate • Google Cloud Infrastructure',
            ha='center', va='center', fontsize=10, color='#2C3E50')
    
    # Agents (compact layout)
    agents = [
        {'name': 'Coordinator\nAgent', 'pos': (2, 4), 'color': '#E74C3C', 'desc': 'Orchestrates workflow'},
        {'name': 'Research\nAgent', 'pos': (4.5, 4), 'color': '#1ABC9C', 'desc': 'Company analysis'},
        {'name': 'Qualification\nAgent', 'pos': (7.5, 4), 'color': '#F39C12', 'desc': 'Prospect scoring'},
        {'name': 'Email\nAgent', 'pos': (10, 4), 'color': '#27AE60', 'desc': 'AI message crafting'}
    ]
    
    # Draw agents
    for agent in agents:
        x, y = agent['pos']
        
        # Agent circle
        circle = plt.Circle((x, y), 0.6, facecolor=agent['color'], 
                           edgecolor='white', linewidth=2, alpha=0.9)
        ax.add_patch(circle)
        
        # Agent name
        ax.text(x, y+0.1, agent['name'], ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white')
        
        # Description
        ax.text(x, y-1, agent['desc'], ha='center', va='center', 
                fontsize=8, color='#2C3E50')
    
    # A2A Protocol arrows
    for i in range(len(agents)-1):
        x1, y1 = agents[i]['pos']
        x2, y2 = agents[i+1]['pos']
        arrow = ConnectionPatch((x1+0.6, y1), (x2-0.6, y2), "data", "data",
                               arrowstyle="->", shrinkA=0, shrinkB=0,
                               color='#34495E', linewidth=2, alpha=0.7)
        ax.add_patch(arrow)
    
    # A2A Protocol label
    ax.text(6, 4.8, 'Agent-to-Agent (A2A) Communication Protocol', 
            ha='center', va='center', fontsize=10, style='italic', color='#34495E')
    
    # Results section
    results_box = FancyBboxPatch((1, 1), 10, 1.5, boxstyle="round,pad=0.1",
                                 facecolor='#27AE60', alpha=0.9)
    ax.add_patch(results_box)
    ax.text(6, 2, 'Production Results', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    ax.text(6, 1.5, '50+ Daily Emails • 100% Delivery Success • Real Healthcare Professionals Only • Fully Automated',
            ha='center', va='center', fontsize=10, color='white')
    
    # Tech stack (compact)
    tech_items = ['Google Cloud Run', 'Vertex AI (Gemini 2.5)', 'A2A Protocol', 'Memory Enhancement']
    for i, tech in enumerate(tech_items):
        x_pos = 1.5 + (i * 2.5)
        ax.text(x_pos, 0.3, tech, ha='center', va='center', 
                fontsize=8, color='#7F8C8D',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='#F8F9FA', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('portfolio_agent_diagram.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    # plt.show()
    
    print("✅ Portfolio Agent Diagram saved as 'portfolio_agent_diagram.png'")

def create_portfolio_summary():
    """Create text summary for portfolio"""
    
    summary = """
# AI Agent Swarm for Healthcare Outreach

## Overview
Multi-agent AI system that automates personalized outreach to healthcare decision makers using Google Cloud infrastructure and advanced AI coordination protocols.

## Key Features
• **4 Specialized AI Agents** working in coordination via Agent-to-Agent (A2A) protocol
• **5,459 Verified Healthcare Contacts** from Definitive Healthcare database
• **100% Email Delivery Success Rate** with real professionals only
• **AI-Crafted Personalized Messages** - no templates, each email unique
• **Full Automation** - runs daily at 9 AM CST via Cloud Scheduler

## Technical Architecture
• **Google Cloud Run** - Scalable serverless deployment
• **Vertex AI** - Gemini 2.5 Pro/Flash models for AI processing
• **Memory Enhancement** - Knowledge base with learning capabilities
• **A2A Protocol** - Seamless agent-to-agent communication
• **Real-time Monitoring** - Complete system visibility and alerting

## Business Impact
• **50+ Daily Emails** to healthcare decision makers
• **Professional Quality** - Clean, personalized messaging
• **Cost Efficient** - Pay-per-use cloud infrastructure
• **Scalable** - Can handle 100+ daily emails with infrastructure scaling
• **Enterprise Ready** - Production deployment with monitoring and alerting

## Results
Successfully deployed production system delivering targeted outreach to laboratory directors, equipment managers, and healthcare decision makers with proven 100% success rate.
"""
    
    with open('portfolio_summary.md', 'w') as f:
        f.write(summary)
    
    print("✅ Portfolio Summary saved as 'portfolio_summary.md'")

if __name__ == "__main__":
    create_portfolio_diagram()
    create_portfolio_summary()