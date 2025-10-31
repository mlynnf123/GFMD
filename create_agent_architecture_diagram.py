#!/usr/bin/env python3
"""
Create Agent Architecture Diagram for GFMD AI Swarm
Shows how agents work together within the A2A protocol
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_agent_architecture_diagram():
    """Create comprehensive agent architecture diagram"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(8, 11.5, 'GFMD AI Swarm Agent Architecture', 
            ha='center', va='center', fontsize=20, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.8))
    
    # A2A Protocol Layer (Background)
    a2a_box = FancyBboxPatch((0.5, 8.5), 15, 2.5, boxstyle="round,pad=0.1",
                             facecolor='#E6F3FF', edgecolor='#4A90E2', linewidth=2,
                             alpha=0.3)
    ax.add_patch(a2a_box)
    ax.text(8, 10.8, 'Agent-to-Agent (A2A) Communication Protocol', 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#4A90E2')
    ax.text(8, 10.3, 'Enables seamless communication, coordination, and data sharing between all agents',
            ha='center', va='center', fontsize=10, style='italic', color='#4A90E2')
    
    # Define agent positions and colors
    agents = {
        'CoordinatorAgent': {'pos': (8, 9.5), 'color': '#FF6B6B', 'size': (2.5, 0.8)},
        'ResearchAgent': {'pos': (3, 7.5), 'color': '#4ECDC4', 'size': (2.2, 0.7)},
        'QualificationAgent': {'pos': (8, 7.5), 'color': '#45B7D1', 'size': (2.2, 0.7)},
        'EmailComposerAgent': {'pos': (13, 7.5), 'color': '#96CEB4', 'size': (2.2, 0.7)},
    }
    
    # Draw agents
    agent_boxes = {}
    for agent_name, info in agents.items():
        x, y = info['pos']
        w, h = info['size']
        
        # Agent box
        box = FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.1",
                             facecolor=info['color'], edgecolor='darkgray', linewidth=2,
                             alpha=0.8)
        ax.add_patch(box)
        agent_boxes[agent_name] = box
        
        # Agent name
        ax.text(x, y+0.1, agent_name.replace('Agent', '\nAgent'), 
                ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    
    # Draw A2A connections between agents
    connections = [
        ('CoordinatorAgent', 'ResearchAgent'),
        ('CoordinatorAgent', 'QualificationAgent'), 
        ('CoordinatorAgent', 'EmailComposerAgent'),
        ('ResearchAgent', 'QualificationAgent'),
        ('QualificationAgent', 'EmailComposerAgent')
    ]
    
    for agent1, agent2 in connections:
        x1, y1 = agents[agent1]['pos']
        x2, y2 = agents[agent2]['pos']
        
        # Create curved connection
        connectionstyle = "arc3,rad=0.1"
        if agent1 == 'CoordinatorAgent':
            connectionstyle = "arc3,rad=0.2"
        
        arrow = ConnectionPatch((x1, y1-0.4), (x2, y2+0.4), "data", "data",
                               arrowstyle="<->", shrinkA=5, shrinkB=5,
                               connectionstyle=connectionstyle,
                               color='#666', linewidth=2, alpha=0.7)
        ax.add_patch(arrow)
    
    # Memory & Knowledge Base
    memory_box = FancyBboxPatch((1, 5.5), 6, 1.5, boxstyle="round,pad=0.1",
                                facecolor='#F39C12', edgecolor='darkgray', linewidth=2,
                                alpha=0.8)
    ax.add_patch(memory_box)
    ax.text(4, 6.5, 'Memory & Knowledge System', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    ax.text(4, 6, '• GFMD Product Knowledge\n• Industry Insights\n• Successful Approaches\n• Interaction History',
            ha='center', va='center', fontsize=9, color='white')
    
    # Data Sources
    data_box = FancyBboxPatch((9, 5.5), 6, 1.5, boxstyle="round,pad=0.1",
                              facecolor='#8E44AD', edgecolor='darkgray', linewidth=2,
                              alpha=0.8)
    ax.add_patch(data_box)
    ax.text(12, 6.5, 'Data Sources & Integration', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')
    ax.text(12, 6, '• Definitive Healthcare (5,459 contacts)\n• Google Custom Search API\n• Google Sheets Integration\n• Gmail API',
            ha='center', va='center', fontsize=9, color='white')
    
    # Cloud Infrastructure
    cloud_box = FancyBboxPatch((1, 3.5), 14, 1.5, boxstyle="round,pad=0.1",
                               facecolor='#27AE60', edgecolor='darkgray', linewidth=2,
                               alpha=0.8)
    ax.add_patch(cloud_box)
    ax.text(8, 4.5, 'Google Cloud Infrastructure', ha='center', va='center', 
            fontsize=14, fontweight='bold', color='white')
    ax.text(8, 4, 'Vertex AI (Gemini 2.5) • Cloud Run Deployment • Cloud Scheduler • Monitoring & Logging',
            ha='center', va='center', fontsize=11, color='white')
    
    # Workflow arrows
    workflow_arrows = [
        ((4, 5.5), (3, 7)),     # Memory to Research
        ((4, 5.5), (8, 7)),     # Memory to Qualification  
        ((4, 5.5), (13, 7)),    # Memory to Email
        ((12, 5.5), (3, 7)),    # Data to Research
        ((12, 5.5), (13, 7)),   # Data to Email
        ((8, 3.5), (8, 7))      # Cloud to Qualification
    ]
    
    for start, end in workflow_arrows:
        arrow = ConnectionPatch(start, end, "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5,
                               connectionstyle="arc3,rad=0.1",
                               color='#2C3E50', linewidth=1.5, alpha=0.6)
        ax.add_patch(arrow)
    
    # Agent Capabilities
    capabilities = {
        'ResearchAgent': ['• Web research\n• Company analysis\n• Pain point identification\n• Decision maker discovery'],
        'QualificationAgent': ['• Facility fit scoring\n• Pain point analysis\n• Decision maker validation\n• Priority classification'],
        'EmailComposerAgent': ['• AI message crafting\n• Personalization\n• Style enforcement\n• Template-free content'],
        'CoordinatorAgent': ['• Workflow orchestration\n• Agent coordination\n• Task distribution\n• Result aggregation']
    }
    
    y_pos = 2.5
    for i, (agent, caps) in enumerate(capabilities.items()):
        x_pos = 2 + (i * 3.5)
        
        # Capability box
        cap_box = FancyBboxPatch((x_pos-1, y_pos-0.8), 2, 1.6, boxstyle="round,pad=0.1",
                                 facecolor='white', edgecolor=agents[agent]['color'], 
                                 linewidth=2, alpha=0.9)
        ax.add_patch(cap_box)
        
        ax.text(x_pos, y_pos+0.5, agent.replace('Agent', ''), ha='center', va='center', 
                fontsize=10, fontweight='bold', color=agents[agent]['color'])
        ax.text(x_pos, y_pos-0.2, caps[0], ha='center', va='center', 
                fontsize=8, color='#2C3E50')
    
    # Performance Stats
    stats_text = """Production Performance:
• 20/20 emails sent successfully (100% success rate)
• 5,459 verified healthcare contacts loaded
• Memory-enhanced AI processing active
• Google Search API integration ready
• Daily automation configured (9 AM CST)"""
    
    ax.text(8, 0.8, stats_text, ha='center', va='center', fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#ECF0F1', alpha=0.8),
            color='#2C3E50')
    
    plt.tight_layout()
    plt.savefig('agent_architecture_diagram.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    # plt.show()  # Comment out for non-interactive use
    
    print("✅ Agent Architecture Diagram saved as 'agent_architecture_diagram.png'")

if __name__ == "__main__":
    create_agent_architecture_diagram()