#!/usr/bin/env python3
"""
Create HTML Email Signature with GFMD Logo
"""

import os
import base64
from email.mime.image import MIMEImage

def create_gfmd_html_signature():
    """Create HTML signature with embedded GFMD logo"""
    
    # For now, create signature with logo URL (will need to host logo or embed as base64)
    html_signature = """
<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
    <br>
    <table cellpadding="0" cellspacing="0" border="0">
        <tr>
            <td style="vertical-align: top; padding-right: 15px;">
                <img src="data:image/png;base64,{logo_base64}" alt="GFMD Logo" style="width: 80px; height: auto; display: block;">
            </td>
            <td style="vertical-align: top; border-left: 2px solid #2c3e9e; padding-left: 15px;">
                <div style="font-weight: bold; font-size: 16px; color: #2c3e9e; margin-bottom: 5px;">
                    Meranda Freiner
                </div>
                <div style="margin-bottom: 3px;">
                    <a href="mailto:solutions@gfmd.com" style="color: #2c3e9e; text-decoration: none;">solutions@gfmd.com</a>
                </div>
                <div style="margin-bottom: 3px;">
                    📞 619-341-9058
                </div>
                <div>
                    🌐 <a href="https://www.gfmd.com" style="color: #2c3e9e; text-decoration: none;">www.gfmd.com</a>
                </div>
            </td>
        </tr>
    </table>
</div>
"""
    
    return html_signature

def create_simple_signature_without_logo():
    """Create clean HTML signature without logo for now"""
    html_signature = """
<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333; margin-top: 20px;">
    <div style="border-top: 1px solid #e0e0e0; padding-top: 15px;">
        <div style="font-weight: bold; font-size: 16px; color: #2c3e9e; margin-bottom: 8px;">
            Meranda Freiner
        </div>
        <div style="margin-bottom: 5px;">
            <span style="color: #666;">Email:</span> 
            <a href="mailto:solutions@gfmd.com" style="color: #2c3e9e; text-decoration: none;">solutions@gfmd.com</a>
        </div>
        <div style="margin-bottom: 5px;">
            <span style="color: #666;">Phone:</span> 
            <span style="color: #333;">619-341-9058</span>
        </div>
        <div>
            <span style="color: #666;">Web:</span> 
            <a href="https://www.gfmd.com" style="color: #2c3e9e; text-decoration: none;">www.gfmd.com</a>
        </div>
    </div>
</div>
"""
    
    return html_signature

# Create both versions
def get_text_signature():
    """Get plain text signature"""
    return """

Meranda Freiner
solutions@gfmd.com
619-341-9058     www.gfmd.com"""

def get_html_signature():
    """Get HTML signature"""
    return create_simple_signature_without_logo()

if __name__ == "__main__":
    print("📧 GFMD Email Signatures")
    print("=" * 50)
    
    print("\n📝 Text Signature:")
    print(get_text_signature())
    
    print("\n🌐 HTML Signature:")
    print(get_html_signature())