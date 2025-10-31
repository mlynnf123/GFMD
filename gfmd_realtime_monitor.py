#!/usr/bin/env python3
"""
GFMD Real-time Monitor - Always-running prospect processor
"""

import asyncio
import json
import time
from datetime import datetime
from vertex_ai_swarm_orchestrator import GFMDSwarmOrchestrator

class GFMDRealtimeMonitor:
    def __init__(self, project_id: str):
        self.orchestrator = GFMDSwarmOrchestrator(project_id=project_id)
        self.running = False
        self.processed_today = 0
    
    async def start_monitoring(self):
        """Start the real-time monitoring system"""
        self.running = True
        print("🔄 Starting GFMD real-time monitoring...")
        
        while self.running:
            try:
                # Check for new prospects (from database, queue, webhooks, etc.)
                new_prospects = await self.check_for_new_prospects()
                
                if new_prospects:
                    print(f"📥 Found {len(new_prospects)} new prospects")
                    
                    for prospect in new_prospects:
                        await self.process_prospect_immediately(prospect)
                
                # Wait before checking again
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"❌ Monitor error: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def check_for_new_prospects(self):
        """Check various sources for new prospects"""
        new_prospects = []
        
        try:
            # Source 1: File watcher for CSV/JSON files
            new_prospects.extend(await self._check_file_sources())
            
            # Source 2: Gmail integration for incoming prospect emails
            new_prospects.extend(await self._check_email_sources())
            
            # Source 3: Web form submissions (if configured)
            new_prospects.extend(await self._check_web_forms())
            
            # Source 4: CRM webhook notifications (placeholder)
            new_prospects.extend(await self._check_crm_webhooks())
            
            # Source 5: Database changes (placeholder)
            new_prospects.extend(await self._check_database_changes())
            
            return new_prospects
            
        except Exception as e:
            print(f"⚠️ Error checking prospect sources: {e}")
            return []
    
    async def _check_file_sources(self):
        """Check for new prospect files"""
        prospects = []
        
        try:
            import glob
            import os
            from pathlib import Path
            import json
            
            # Check for new CSV files
            csv_pattern = str(Path(__file__).parent / "incoming_prospects_*.csv")
            for csv_file in glob.glob(csv_pattern):
                # Check if file is new (created in last 24 hours)
                file_age = time.time() - os.path.getctime(csv_file)
                if file_age < 86400:  # 24 hours
                    try:
                        # Load prospects from CSV (implement actual CSV parsing)
                        print(f"📂 Found new prospect file: {csv_file}")
                        # Move file to processed folder after loading
                        processed_dir = Path(__file__).parent / "processed"
                        processed_dir.mkdir(exist_ok=True)
                        os.rename(csv_file, processed_dir / Path(csv_file).name)
                    except Exception as e:
                        print(f"⚠️ Error processing CSV {csv_file}: {e}")
            
            # Check for new JSON files
            json_pattern = str(Path(__file__).parent / "incoming_prospects_*.json")
            for json_file in glob.glob(json_pattern):
                file_age = time.time() - os.path.getctime(json_file)
                if file_age < 86400:
                    try:
                        with open(json_file, 'r') as f:
                            file_prospects = json.load(f)
                        prospects.extend(file_prospects)
                        print(f"📄 Loaded {len(file_prospects)} prospects from {json_file}")
                        
                        # Move to processed folder
                        processed_dir = Path(__file__).parent / "processed"
                        processed_dir.mkdir(exist_ok=True)
                        os.rename(json_file, processed_dir / Path(json_file).name)
                        
                    except Exception as e:
                        print(f"⚠️ Error processing JSON {json_file}: {e}")
            
        except Exception as e:
            print(f"⚠️ File source check failed: {e}")
            
        return prospects
    
    async def _check_email_sources(self):
        """Check Gmail for prospect inquiry emails"""
        prospects = []
        
        try:
            # Check if Gmail integration is available
            gmail_file = Path(__file__).parent / "gmail_integration.py"
            if not gmail_file.exists():
                return prospects
            
            from gmail_integration import GmailIntegration
            
            gmail = GmailIntegration()
            
            # Search for emails with prospect-related keywords
            prospect_keywords = [
                "hospital equipment inquiry",
                "centrifuge request",
                "laboratory equipment",
                "medical equipment quote",
                "silencer centrifuge"
            ]
            
            for keyword in prospect_keywords:
                try:
                    messages = gmail.search_messages(f'subject:({keyword}) newer_than:1d')
                    for msg_id in messages[:5]:  # Process max 5 emails per keyword
                        email_content = gmail.get_message_content(msg_id)
                        
                        # Extract prospect information from email
                        prospect = await self._extract_prospect_from_email(email_content)
                        if prospect:
                            prospects.append(prospect)
                            print(f"📧 Extracted prospect from email: {prospect.get('contact_name', 'Unknown')}")
                            
                except Exception as e:
                    print(f"⚠️ Error processing emails for keyword '{keyword}': {e}")
                    
        except ImportError:
            # Gmail integration not available
            pass
        except Exception as e:
            print(f"⚠️ Email source check failed: {e}")
            
        return prospects
    
    async def _extract_prospect_from_email(self, email_content):
        """Extract prospect information from email content using AI"""
        try:
            # Use the orchestrator's AI to extract prospect data
            extraction_prompt = f"""
            Extract prospect information from this email content and return as JSON:
            
            Email Content:
            {email_content}
            
            Extract these fields if available:
            - contact_name
            - email
            - phone
            - organization_name
            - title
            - location
            - bed_count (estimate if hospital mentioned)
            - lab_type (estimate: full_service, core_lab, specialty, point_of_care)
            - current_equipment (any mentioned equipment)
            - annual_revenue (estimate if hospital size indicated)
            
            Return only valid JSON with extracted fields, or null if no prospect information found.
            """
            
            # This would use the AI model to extract information
            # For now, return a placeholder
            return None
            
        except Exception as e:
            print(f"⚠️ Email extraction failed: {e}")
            return None
    
    async def _check_web_forms(self):
        """Check for web form submissions"""
        prospects = []
        
        try:
            # Check for webhook data files (web forms would post to webhook endpoint)
            webhook_dir = Path(__file__).parent / "webhooks"
            if webhook_dir.exists():
                for webhook_file in webhook_dir.glob("prospect_*.json"):
                    try:
                        with open(webhook_file, 'r') as f:
                            webhook_data = json.load(f)
                        
                        # Convert webhook data to prospect format
                        prospect = self._convert_webhook_to_prospect(webhook_data)
                        if prospect:
                            prospects.append(prospect)
                            print(f"🌐 Processed web form submission: {prospect.get('contact_name', 'Unknown')}")
                        
                        # Move to processed folder
                        processed_dir = webhook_dir / "processed"
                        processed_dir.mkdir(exist_ok=True)
                        webhook_file.rename(processed_dir / webhook_file.name)
                        
                    except Exception as e:
                        print(f"⚠️ Error processing webhook {webhook_file}: {e}")
                        
        except Exception as e:
            print(f"⚠️ Web form check failed: {e}")
            
        return prospects
    
    def _convert_webhook_to_prospect(self, webhook_data):
        """Convert webhook data to prospect format"""
        try:
            # Map common web form fields to prospect fields
            field_mapping = {
                'name': 'contact_name',
                'fullName': 'contact_name',
                'contactName': 'contact_name',
                'email': 'email',
                'emailAddress': 'email',
                'phone': 'phone',
                'phoneNumber': 'phone',
                'company': 'organization_name',
                'organization': 'organization_name',
                'hospitalName': 'organization_name',
                'jobTitle': 'title',
                'position': 'title',
                'city': 'location',
                'location': 'location',
                'beds': 'bed_count',
                'bedCount': 'bed_count',
                'hospitalSize': 'bed_count'
            }
            
            prospect = {}
            for webhook_key, webhook_value in webhook_data.items():
                prospect_key = field_mapping.get(webhook_key, webhook_key)
                prospect[prospect_key] = webhook_value
            
            # Add defaults
            prospect['lead_source'] = 'Web Form'
            prospect['lab_type'] = 'unknown'
            
            return prospect if prospect.get('contact_name') else None
            
        except Exception as e:
            print(f"⚠️ Webhook conversion failed: {e}")
            return None
    
    async def _check_crm_webhooks(self):
        """Check for CRM webhook notifications (placeholder)"""
        # This would connect to Salesforce, HubSpot, etc. webhooks
        return []
    
    async def _check_database_changes(self):
        """Check for database change notifications (placeholder)"""
        # This would connect to database change streams
        return []
    
    async def process_prospect_immediately(self, prospect):
        """Process a prospect immediately when detected"""
        try:
            result = await self.orchestrator.process_new_prospect(prospect)
            self.processed_today += 1
            
            print(f"✅ Processed: {prospect.get('organization_name')}")
            print(f"   Workflow ID: {result.get('workflow_id')}")
            print(f"   Total today: {self.processed_today}")
            
            # Could send notifications, update CRM, etc.
            
        except Exception as e:
            print(f"❌ Processing failed for {prospect.get('organization_name')}: {str(e)}")
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.running = False
        print("⏹️  Stopping GFMD real-time monitoring...")

# Usage:
# monitor = GFMDRealtimeMonitor("gen-lang-client-0673146524")
# await monitor.start_monitoring()
