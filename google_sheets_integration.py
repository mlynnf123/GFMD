"""
Google Sheets Integration for Agent Output Export
Exports agent outputs, prospects, and sent emails to Google Sheets instead of simulation mode.
"""

import os
import json
import gspread
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class SheetType(Enum):
    AGENT_OUTPUT = "agent_output"
    PROSPECTS = "prospects"
    SENT_EMAILS = "sent_emails"

@dataclass
class GoogleSheetsConfig:
    """Configuration for Google Sheets integration"""
    spreadsheet_name: str = "GFMD Swarm Agent Data"
    credentials_file: Optional[str] = None
    service_account_info: Optional[Dict] = None
    share_with_emails: List[str] = None

class GoogleSheetsExporter:
    """Handles exporting agent data to Google Sheets"""
    
    def __init__(self, config: GoogleSheetsConfig):
        self.config = config
        self.gc = None
        self.spreadsheet = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Sheets client"""
        try:
            if self.config.service_account_info:
                self.gc = gspread.service_account_from_dict(self.config.service_account_info)
            elif self.config.credentials_file and os.path.exists(self.config.credentials_file):
                self.gc = gspread.service_account(filename=self.config.credentials_file)
            else:
                # For Cloud Run, try to use Application Default Credentials
                # This works when service account is properly configured in Cloud Run
                try:
                    import google.auth
                    from google.auth.transport.requests import Request
                    import gspread
                    
                    # Use Application Default Credentials
                    credentials, project = google.auth.default(
                        scopes=['https://www.googleapis.com/auth/spreadsheets', 
                               'https://www.googleapis.com/auth/drive']
                    )
                    self.gc = gspread.authorize(credentials)
                except Exception:
                    # Fallback to default location
                    self.gc = gspread.service_account()
            
            self._setup_spreadsheet()
            print("✅ Google Sheets integration initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Google Sheets: {e}")
            raise
    
    def _setup_spreadsheet(self):
        """Create or open the main spreadsheet with required worksheets"""
        try:
            # Try to open existing spreadsheet
            self.spreadsheet = self.gc.open(self.config.spreadsheet_name)
            print(f"📊 Opened existing spreadsheet: {self.config.spreadsheet_name}")
        except gspread.SpreadsheetNotFound:
            # Create new spreadsheet
            self.spreadsheet = self.gc.create(self.config.spreadsheet_name)
            print(f"📊 Created new spreadsheet: {self.config.spreadsheet_name}")
            
            # Share with specified emails
            if self.config.share_with_emails:
                for email in self.config.share_with_emails:
                    try:
                        self.spreadsheet.share(email, perm_type='user', role='editor')
                        print(f"✅ Shared spreadsheet with {email}")
                    except Exception as e:
                        print(f"⚠️ Could not share with {email}: {e}")
        
        # Setup worksheets
        self._setup_worksheets()
    
    def _setup_worksheets(self):
        """Create and configure all required worksheets"""
        worksheets_config = {
            "Agent Output": self._get_agent_output_headers(),
            "Prospects": self._get_prospects_headers(),
            "Sent Emails": self._get_sent_emails_headers()
        }
        
        for sheet_name, headers in worksheets_config.items():
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
                print(f"📄 Found existing worksheet: {sheet_name}")
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(headers))
                print(f"📄 Created new worksheet: {sheet_name}")
            
            # Set headers if worksheet is empty
            if not worksheet.get('A1'):
                worksheet.update('A1', [headers])
                # Format headers
                worksheet.format('A1:Z1', {
                    'textFormat': {'bold': True},
                    'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                })
                print(f"✅ Set headers for {sheet_name}")
    
    def _get_agent_output_headers(self) -> List[str]:
        """Get column headers for agent output sheet"""
        return [
            "Timestamp", "Agent Type", "Touchpoint ID", "Channel", "Recipient Name", 
            "Organization", "Contact Info", "Content", "Status", "Tracking ID",
            "Execution Time", "Response Received", "Response Type", "Qualification Score",
            "Open Rate", "Click Rate", "Notes", "Error Details"
        ]
    
    def _get_prospects_headers(self) -> List[str]:
        """Get column headers for prospects sheet"""
        return [
            "Timestamp", "Name", "Email", "Phone", "Organization", "Title", 
            "Location", "Industry", "Website", "LinkedIn", "Twitter", 
            "Qualification Score", "Lead Source", "Tags", "Company Size",
            "Revenue", "Technology Stack", "Pain Points", "Notes", "Status"
        ]
    
    def _get_sent_emails_headers(self) -> List[str]:
        """Get column headers for sent emails sheet"""
        return [
            "Timestamp", "Message ID", "From", "To", "Subject", "Body Preview",
            "Full Content", "Campaign", "Touchpoint", "Channel", "Status",
            "Sent Time", "Delivered Time", "Opened Time", "Clicked Time",
            "Reply Time", "Reply Content", "Tracking ID", "Thread ID", "Labels"
        ]
    
    def export_agent_output(self, output_data: Dict[str, Any]):
        """Export agent execution output to Google Sheets"""
        try:
            worksheet = self.spreadsheet.worksheet("Agent Output")
            
            # Prepare row data
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                output_data.get("agent_type", ""),
                output_data.get("touchpoint_id", ""),
                output_data.get("channel", ""),
                output_data.get("recipient", ""),
                output_data.get("organization", ""),
                json.dumps(output_data.get("contact_info", {})),
                output_data.get("content", "")[:500] + "..." if len(output_data.get("content", "")) > 500 else output_data.get("content", ""),
                output_data.get("status", ""),
                output_data.get("tracking_id", ""),
                output_data.get("execution_time", ""),
                output_data.get("response_received", False),
                output_data.get("response_type", ""),
                output_data.get("qualification_score", ""),
                output_data.get("estimated_open_rate", ""),
                output_data.get("estimated_click_rate", ""),
                output_data.get("notes", ""),
                output_data.get("error_details", "")
            ]
            
            worksheet.append_row(row_data)
            print(f"✅ Exported agent output to Google Sheets: {output_data.get('touchpoint_id', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Failed to export agent output: {e}")
            raise
    
    def export_prospect(self, prospect_data: Dict[str, Any]):
        """Export prospect information to Google Sheets"""
        try:
            worksheet = self.spreadsheet.worksheet("Prospects")
            
            # Prepare row data matching exact headers:
            # Date, Contact Name, Contact Email, Phone Number, Company, Title, Location, Industry, Website, LinkedIn
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Date
                prospect_data.get("contact_name", ""),          # Contact Name
                prospect_data.get("email", ""),                  # Contact Email
                prospect_data.get("phone", ""),                  # Phone Number
                prospect_data.get("organization_name", prospect_data.get("company", "")),  # Company
                prospect_data.get("contact_title", prospect_data.get("title", "")),        # Title
                prospect_data.get("location", ""),               # Location
                prospect_data.get("industry", ""),               # Industry
                prospect_data.get("website", ""),                # Website
                prospect_data.get("linkedin", "")                # LinkedIn
            ]
            
            worksheet.append_row(row_data)
            print(f"✅ Exported prospect to Google Sheets: {prospect_data.get('contact_name', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Failed to export prospect: {e}")
            raise
    
    def export_sent_email(self, email_data: Dict[str, Any]):
        """Export sent email information to Google Sheets"""
        try:
            worksheet = self.spreadsheet.worksheet("Sent Emails")
            
            # Prepare row data matching exact headers:
            # Date, ID, Sent Email, Recipient email, Subject, Email, Day Number
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),   # Date
                email_data.get("id", f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),  # ID
                "Yes" if email_data.get("sent_successfully", True) else "No",  # Sent Email (Yes/No)
                email_data.get("recipient_email", email_data.get("to", "")),   # Recipient email
                email_data.get("subject", ""),                                  # Subject
                email_data.get("body", ""),                                     # Email (full body)
                email_data.get("day_number", "1")                              # Day Number
            ]
            
            worksheet.append_row(row_data)
            print(f"✅ Exported sent email to Google Sheets: {email_data.get('subject', 'No Subject')}")
            
        except Exception as e:
            print(f"❌ Failed to export sent email: {e}")
            raise
    
    def get_spreadsheet_url(self) -> str:
        """Get the URL of the spreadsheet for easy access"""
        if self.spreadsheet:
            return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet.id}"
        return ""
    
    def batch_export(self, agent_outputs: List[Dict], prospects: List[Dict], emails: List[Dict]):
        """Export multiple records in batch for better performance"""
        try:
            # Export agent outputs
            if agent_outputs:
                worksheet = self.spreadsheet.worksheet("Agent Output")
                rows_data = []
                for output in agent_outputs:
                    row_data = [
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        output.get("agent_type", ""),
                        output.get("touchpoint_id", ""),
                        output.get("channel", ""),
                        output.get("recipient", ""),
                        output.get("organization", ""),
                        json.dumps(output.get("contact_info", {})),
                        output.get("content", "")[:500] + "..." if len(output.get("content", "")) > 500 else output.get("content", ""),
                        output.get("status", ""),
                        output.get("tracking_id", ""),
                        output.get("execution_time", ""),
                        output.get("response_received", False),
                        output.get("response_type", ""),
                        output.get("qualification_score", ""),
                        output.get("estimated_open_rate", ""),
                        output.get("estimated_click_rate", ""),
                        output.get("notes", ""),
                        output.get("error_details", "")
                    ]
                    rows_data.append(row_data)
                worksheet.append_rows(rows_data)
                print(f"✅ Batch exported {len(agent_outputs)} agent outputs")
            
            # Export prospects
            if prospects:
                worksheet = self.spreadsheet.worksheet("Prospects")
                rows_data = []
                for prospect in prospects:
                    row_data = [
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        prospect.get("name", ""),
                        prospect.get("email", ""),
                        prospect.get("phone", ""),
                        prospect.get("organization", ""),
                        prospect.get("title", ""),
                        prospect.get("location", ""),
                        prospect.get("industry", ""),
                        prospect.get("website", ""),
                        prospect.get("linkedin", ""),
                        prospect.get("twitter", ""),
                        prospect.get("qualification_score", ""),
                        prospect.get("lead_source", ""),
                        json.dumps(prospect.get("tags", [])),
                        prospect.get("company_size", ""),
                        prospect.get("revenue", ""),
                        json.dumps(prospect.get("technology_stack", [])),
                        prospect.get("pain_points", ""),
                        prospect.get("notes", ""),
                        prospect.get("status", "new")
                    ]
                    rows_data.append(row_data)
                worksheet.append_rows(rows_data)
                print(f"✅ Batch exported {len(prospects)} prospects")
            
            # Export emails
            if emails:
                worksheet = self.spreadsheet.worksheet("Sent Emails")
                rows_data = []
                for email in emails:
                    row_data = [
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        email.get("message_id", ""),
                        email.get("from", ""),
                        email.get("to", ""),
                        email.get("subject", ""),
                        email.get("body", "")[:200] + "..." if len(email.get("body", "")) > 200 else email.get("body", ""),
                        email.get("full_content", ""),
                        email.get("campaign", ""),
                        email.get("touchpoint", ""),
                        email.get("channel", "email"),
                        email.get("status", "sent"),
                        email.get("sent_time", ""),
                        email.get("delivered_time", ""),
                        email.get("opened_time", ""),
                        email.get("clicked_time", ""),
                        email.get("reply_time", ""),
                        email.get("reply_content", ""),
                        email.get("tracking_id", ""),
                        email.get("thread_id", ""),
                        json.dumps(email.get("labels", []))
                    ]
                    rows_data.append(row_data)
                worksheet.append_rows(rows_data)
                print(f"✅ Batch exported {len(emails)} sent emails")
                
        except Exception as e:
            print(f"❌ Failed to batch export: {e}")
            raise