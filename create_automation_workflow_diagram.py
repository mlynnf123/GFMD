#!/usr/bin/env python3
"""
Create Automation Workflow Diagram for GFMD AI Swarm
Shows step-by-step automation process from trigger to email delivery
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle
import numpy as np

def create_automation_workflow_diagram():
    """Create detailed automation workflow diagram"""
    
    fig, ax = plt.subplots(1, 1, figsize=(18, 14))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    # Title
    ax.text(9, 13.5, 'GFMD AI Swarm - Daily Automation Workflow', 
            ha='center', va='center', fontsize=22, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#2C3E50', color='white'))
    
    # Define workflow steps
    steps = [
        {
            'title': '1. TRIGGER',
            'subtitle': 'Daily Schedule',
            'details': ['• Cloud Scheduler fires at 9:00 AM CST', '• Sends POST request to Cloud Run', '• Target: 50+ prospects'],
            'pos': (3, 11.5), 'color': '#E74C3C', 'icon': '⏰'
        },
        {
            'title': '2. LOAD DATA',
            'subtitle': 'Real Contacts',
            'details': ['• Load Definitive Healthcare CSV', '• 5,459 verified healthcare contacts', '• Filter for valid emails only'],
            'pos': (9, 11.5), 'color': '#3498DB', 'icon': '📂'
        },
        {
            'title': '3. ENHANCE CONTACTS',
            'subtitle': 'Google Search',
            'details': ['• Check for missing emails', '• Google Custom Search API', '• Enrich with web-found contacts'],
            'pos': (15, 11.5), 'color': '#9B59B6', 'icon': '🔍'
        },
        {
            'title': '4. AI RESEARCH',
            'subtitle': 'Enhanced Research Agent',
            'details': ['• Company background analysis', '• Pain point identification', '• Decision maker research', '• Industry insights'],
            'pos': (3, 9), 'color': '#1ABC9C', 'icon': '🧠'
        },
        {
            'title': '5. QUALIFICATION',
            'subtitle': 'Smart Scoring Agent',
            'details': ['• Facility fit analysis (40 pts)', '• Pain point relevance (40 pts)', '• Decision maker fit (20 pts)', '• Priority classification'],
            'pos': (9, 9), 'color': '#F39C12', 'icon': '⚖️'
        },
        {
            'title': '6. AI COMPOSITION',
            'subtitle': 'Email Crafting Agent', 
            'details': ['• Personalized message creation', '• No templates - unique content', '• Professional tone & style', '• GFMD value proposition'],
            'pos': (15, 9), 'color': '#27AE60', 'icon': '✍️'
        },
        {
            'title': '7. VALIDATION',
            'subtitle': 'Quality Control',
            'details': ['• Email format validation', '• Healthcare domain verification', '• Style rule enforcement', '• Content quality check'],
            'pos': (3, 6.5), 'color': '#E67E22', 'icon': '✅'
        },
        {
            'title': '8. DELIVERY',
            'subtitle': 'Gmail Integration',
            'details': ['• Gmail API authentication', '• Professional email sending', '• Delivery confirmation', '• Error handling & retry'],
            'pos': (9, 6.5), 'color': '#2ECC71', 'icon': '📧'
        },
        {
            'title': '9. TRACKING',
            'subtitle': 'Data Export',
            'details': ['• Google Sheets integration', '• Prospect data logging', '• Email status tracking', '• Performance metrics'],
            'pos': (15, 6.5), 'color': '#8E44AD', 'icon': '📊'
        }
    ]
    
    # Draw workflow steps
    step_boxes = {}
    for i, step in enumerate(steps):
        x, y = step['pos']
        
        # Main step box
        box = FancyBboxPatch((x-1.3, y-1), 2.6, 2, boxstyle="round,pad=0.1",
                             facecolor=step['color'], edgecolor='darkgray', linewidth=2,
                             alpha=0.9)
        ax.add_patch(box)
        step_boxes[i] = (x, y)
        
        # Step icon
        ax.text(x-0.8, y+0.6, step['icon'], ha='center', va='center', 
                fontsize=20, color='white')
        
        # Step title
        ax.text(x, y+0.6, step['title'], ha='center', va='center', 
                fontsize=11, fontweight='bold', color='white')
        
        # Step subtitle
        ax.text(x, y+0.2, step['subtitle'], ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white', style='italic')
        
        # Step details
        details_text = '\n'.join(step['details'])
        ax.text(x, y-0.4, details_text, ha='center', va='center', 
                fontsize=7, color='white')
    
    # Draw workflow arrows
    workflow_connections = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8)
    ]
    
    for start_idx, end_idx in workflow_connections:
        start_pos = step_boxes[start_idx]
        end_pos = step_boxes[end_idx]
        
        # Calculate arrow positions
        if start_pos[1] == end_pos[1]:  # Same row
            if start_pos[0] < end_pos[0]:  # Left to right
                arrow_start = (start_pos[0] + 1.3, start_pos[1])
                arrow_end = (end_pos[0] - 1.3, end_pos[1])
            else:  # Right to left (shouldn't happen in this flow)
                arrow_start = (start_pos[0] - 1.3, start_pos[1])
                arrow_end = (end_pos[0] + 1.3, end_pos[1])
        else:  # Different rows
            arrow_start = (start_pos[0], start_pos[1] - 1)
            arrow_end = (end_pos[0], end_pos[1] + 1)
        
        arrow = ConnectionPatch(arrow_start, arrow_end, "data", "data",
                               arrowstyle="->", shrinkA=0, shrinkB=0,
                               connectionstyle="arc3,rad=0.1",
                               color='#2C3E50', linewidth=3, alpha=0.8)
        ax.add_patch(arrow)
    
    # Memory & Knowledge Integration (Background process)
    memory_box = FancyBboxPatch((1, 4), 16, 1.5, boxstyle="round,pad=0.1",
                                facecolor='#34495E', edgecolor='darkgray', linewidth=2,
                                alpha=0.2)
    ax.add_patch(memory_box)
    ax.text(9, 4.8, '🧠 MEMORY & KNOWLEDGE ENHANCEMENT (Active Throughout Process)', 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#2C3E50')
    ax.text(9, 4.3, 'Product Knowledge • Industry Insights • Successful Approaches • Interaction History • RAG System',
            ha='center', va='center', fontsize=10, style='italic', color='#2C3E50')
    
    # Performance Metrics Box
    metrics_box = FancyBboxPatch((2, 2), 5.5, 1.8, boxstyle="round,pad=0.1",
                                 facecolor='#ECF0F1', edgecolor='#2C3E50', linewidth=2,
                                 alpha=0.9)
    ax.add_patch(metrics_box)
    ax.text(4.75, 3.4, '📈 PERFORMANCE METRICS', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='#2C3E50')
    
    metrics_text = """Recent Results:
• 20/20 Emails Sent Successfully (100%)
• 5,459 Verified Contacts Available
• Average Processing: 2-3 minutes per prospect
• Memory Enhancement: Active on all prospects
• Google Search Integration: Ready"""
    
    ax.text(4.75, 2.6, metrics_text, ha='center', va='center', 
            fontsize=9, color='#2C3E50')
    
    # System Architecture Box
    arch_box = FancyBboxPatch((8.5, 2), 7, 1.8, boxstyle="round,pad=0.1",
                              facecolor='#ECF0F1', edgecolor='#27AE60', linewidth=2,
                              alpha=0.9)
    ax.add_patch(arch_box)
    ax.text(12, 3.4, '🏗️ CLOUD ARCHITECTURE', ha='center', va='center', 
            fontsize=11, fontweight='bold', color='#27AE60')
    
    arch_text = """Infrastructure:
• Google Cloud Run: Scalable deployment
• Vertex AI: Gemini 2.5 Pro/Flash models
• Cloud Scheduler: Daily 9 AM CST automation
• Google APIs: Sheets, Gmail, Custom Search
• Monitoring: Built-in logging & performance tracking"""
    
    ax.text(12, 2.6, arch_text, ha='center', va='center', 
            fontsize=9, color='#27AE60')
    
    # Status indicators
    status_indicators = [
        ('🟢 PRODUCTION READY', (3, 0.8), '#27AE60'),
        ('🟢 DAILY AUTOMATION ACTIVE', (9, 0.8), '#27AE60'),
        ('🟢 REAL CONTACTS ONLY', (15, 0.8), '#27AE60')
    ]
    
    for status, pos, color in status_indicators:
        ax.text(pos[0], pos[1], status, ha='center', va='center', 
                fontsize=10, fontweight='bold', color=color,
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', 
                         edgecolor=color, linewidth=2))
    
    # Add timing information
    ax.text(9, 0.3, 'Next Scheduled Run: Daily at 9:00 AM CST | Target: 50+ personalized emails to healthcare decision makers',
            ha='center', va='center', fontsize=11, style='italic', color='#2C3E50',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#F8F9FA', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('automation_workflow_diagram.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    # plt.show()  # Comment out for non-interactive use
    
    print("✅ Automation Workflow Diagram saved as 'automation_workflow_diagram.png'")

if __name__ == "__main__":
    create_automation_workflow_diagram()