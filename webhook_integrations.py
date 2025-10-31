#!/usr/bin/env python3
"""
Webhook and API Integration System for GFMD A2A Swarm Agent
Handles incoming webhooks from CRMs, forms, and other systems
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import httpx

logger = logging.getLogger(__name__)

# Integration Models
class WebhookData(BaseModel):
    source: str = Field(..., description="Source system (salesforce, hubspot, zapier, etc.)")
    event_type: str = Field(..., description="Type of event (new_lead, form_submission, etc.)")
    data: Dict[str, Any] = Field(..., description="The actual data payload")
    timestamp: Optional[str] = Field(default=None, description="Event timestamp")

class ProspectWebhook(BaseModel):
    organization_name: str
    contact_name: str
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = "Healthcare"
    source: Optional[str] = "webhook"
    additional_data: Optional[Dict[str, Any]] = {}

class AutomationTrigger(BaseModel):
    trigger: str = Field(..., description="Type of trigger (daily_automation, manual_run, etc.)")
    source: str = Field(default="api", description="Source of the trigger")
    batch_size: Optional[int] = Field(default=10, description="Number of prospects to process")
    specific_prospects: Optional[List[Dict[str, Any]]] = Field(default=None)

class IntegrationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    workflow_id: Optional[str] = None

app = FastAPI(
    title="GFMD A2A Integration API",
    description="Webhook and API integration endpoints for the A2A multi-agent system",
    version="1.0.0"
)

# Service Configuration
SERVICE_URL = "https://gfmd-a2a-swarm-agent-531787444060.us-central1.run.app"

@app.get("/")
async def integration_root():
    """Integration API root"""
    return {
        "service": "GFMD A2A Integration API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "webhooks": {
                "general": "/webhook",
                "prospects": "/webhook/prospect",
                "salesforce": "/webhook/salesforce",
                "hubspot": "/webhook/hubspot",
                "zapier": "/webhook/zapier"
            },
            "automation": {
                "daily_run": "/api/v1/automation/daily-run",
                "manual_trigger": "/api/v1/automation/trigger",
                "batch_process": "/api/v1/automation/batch"
            },
            "integration": {
                "crm_sync": "/api/v1/integration/crm-sync",
                "status_callback": "/api/v1/integration/status-callback"
            }
        }
    }

@app.post("/webhook", response_model=IntegrationResponse)
async def generic_webhook(webhook_data: WebhookData, background_tasks: BackgroundTasks):
    """Generic webhook endpoint for any system"""
    try:
        logger.info(f"Received webhook from {webhook_data.source}: {webhook_data.event_type}")
        
        # Process webhook based on source and event type
        result = await process_webhook_data(webhook_data, background_tasks)
        
        return IntegrationResponse(
            success=True,
            message=f"Webhook from {webhook_data.source} processed successfully",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/prospect", response_model=IntegrationResponse)
async def prospect_webhook(prospect: ProspectWebhook, background_tasks: BackgroundTasks):
    """Dedicated webhook for prospect data"""
    try:
        logger.info(f"Received prospect webhook: {prospect.organization_name}")
        
        # Convert to standard prospect format
        prospect_data = {
            "organization_name": prospect.organization_name,
            "contact_name": prospect.contact_name,
            "email": prospect.email,
            "phone": prospect.phone,
            "website": prospect.website,
            "industry": prospect.industry,
            "lead_source": prospect.source,
            "additional_data": prospect.additional_data or {}
        }
        
        # Process prospect through A2A system
        workflow_id = await trigger_prospect_processing(prospect_data, background_tasks)
        
        return IntegrationResponse(
            success=True,
            message=f"Prospect {prospect.organization_name} queued for processing",
            workflow_id=workflow_id,
            data={"prospect": prospect_data}
        )
        
    except Exception as e:
        logger.error(f"Error processing prospect webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/salesforce")
async def salesforce_webhook(request: Request, background_tasks: BackgroundTasks):
    """Salesforce-specific webhook handler"""
    try:
        payload = await request.json()
        logger.info("Received Salesforce webhook")
        
        # Extract prospect data from Salesforce format
        prospect_data = parse_salesforce_data(payload)
        
        if prospect_data:
            workflow_id = await trigger_prospect_processing(prospect_data, background_tasks)
            return {"success": True, "workflow_id": workflow_id, "message": "Salesforce lead processed"}
        else:
            return {"success": False, "message": "No valid prospect data found"}
            
    except Exception as e:
        logger.error(f"Error processing Salesforce webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/hubspot")
async def hubspot_webhook(request: Request, background_tasks: BackgroundTasks):
    """HubSpot-specific webhook handler"""
    try:
        payload = await request.json()
        logger.info("Received HubSpot webhook")
        
        # Extract prospect data from HubSpot format
        prospect_data = parse_hubspot_data(payload)
        
        if prospect_data:
            workflow_id = await trigger_prospect_processing(prospect_data, background_tasks)
            return {"success": True, "workflow_id": workflow_id, "message": "HubSpot contact processed"}
        else:
            return {"success": False, "message": "No valid prospect data found"}
            
    except Exception as e:
        logger.error(f"Error processing HubSpot webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/zapier")
async def zapier_webhook(request: Request, background_tasks: BackgroundTasks):
    """Zapier-specific webhook handler"""
    try:
        payload = await request.json()
        logger.info("Received Zapier webhook")
        
        # Zapier usually sends clean, standardized data
        prospect_data = {
            "organization_name": payload.get("company", payload.get("organization_name", "Unknown")),
            "contact_name": f"{payload.get('first_name', '')} {payload.get('last_name', '')}".strip(),
            "email": payload.get("email"),
            "phone": payload.get("phone"),
            "website": payload.get("website"),
            "industry": payload.get("industry", "Healthcare"),
            "lead_source": "zapier",
            "additional_data": payload
        }
        
        workflow_id = await trigger_prospect_processing(prospect_data, background_tasks)
        return {"success": True, "workflow_id": workflow_id, "message": "Zapier data processed"}
        
    except Exception as e:
        logger.error(f"Error processing Zapier webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/automation/daily-run")
async def daily_automation_run(trigger: AutomationTrigger, background_tasks: BackgroundTasks):
    """Daily automation trigger endpoint"""
    try:
        logger.info(f"Daily automation triggered by {trigger.source}")
        
        # This would typically load prospects from your database, Google Sheets, or CRM
        # For now, we'll create a placeholder response
        
        # Trigger the full A2A workflow
        workflow_result = await trigger_daily_workflow(trigger, background_tasks)
        
        return {
            "success": True,
            "message": "Daily automation started successfully",
            "trigger": trigger.trigger,
            "batch_size": trigger.batch_size,
            "workflow_id": workflow_result.get("workflow_id"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in daily automation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/automation/trigger")
async def manual_automation_trigger(trigger: AutomationTrigger, background_tasks: BackgroundTasks):
    """Manual automation trigger"""
    try:
        logger.info(f"Manual trigger: {trigger.trigger}")
        
        if trigger.specific_prospects:
            # Process specific prospects
            results = []
            for prospect_data in trigger.specific_prospects:
                workflow_id = await trigger_prospect_processing(prospect_data, background_tasks)
                results.append({"prospect": prospect_data["organization_name"], "workflow_id": workflow_id})
            
            return {
                "success": True,
                "message": f"Processing {len(trigger.specific_prospects)} specific prospects",
                "results": results
            }
        else:
            # Trigger general automation
            workflow_result = await trigger_daily_workflow(trigger, background_tasks)
            return {
                "success": True,
                "message": "Manual automation triggered",
                "workflow_id": workflow_result.get("workflow_id")
            }
            
    except Exception as e:
        logger.error(f"Error in manual trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/integration/crm-sync")
async def crm_sync_endpoint(request: Request, background_tasks: BackgroundTasks):
    """Sync data back to CRM systems"""
    try:
        payload = await request.json()
        crm_type = payload.get("crm_type", "generic")
        action = payload.get("action", "update")
        data = payload.get("data", {})
        
        logger.info(f"CRM sync request: {crm_type} - {action}")
        
        # Process CRM sync in background
        background_tasks.add_task(process_crm_sync, crm_type, action, data)
        
        return {
            "success": True,
            "message": f"CRM sync queued for {crm_type}",
            "action": action
        }
        
    except Exception as e:
        logger.error(f"Error in CRM sync: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/integration/status-callback")
async def status_callback(request: Request):
    """Receive status callbacks from external systems"""
    try:
        payload = await request.json()
        workflow_id = payload.get("workflow_id")
        status = payload.get("status")
        
        logger.info(f"Status callback: {workflow_id} - {status}")
        
        # Update workflow status
        # This would typically update your database or trigger notifications
        
        return {"success": True, "message": "Status callback processed"}
        
    except Exception as e:
        logger.error(f"Error processing status callback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper Functions

async def process_webhook_data(webhook_data: WebhookData, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Process generic webhook data"""
    
    # Try to extract prospect information from the data
    data = webhook_data.data
    
    # Common field mappings
    prospect_data = {
        "organization_name": (
            data.get("company") or 
            data.get("organization_name") or 
            data.get("account_name") or
            "Unknown Organization"
        ),
        "contact_name": (
            f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or
            data.get("contact_name") or
            data.get("name") or
            "Unknown Contact"
        ),
        "email": data.get("email"),
        "phone": data.get("phone") or data.get("mobile"),
        "website": data.get("website"),
        "industry": data.get("industry", "Healthcare"),
        "lead_source": webhook_data.source,
        "additional_data": data
    }
    
    # Only process if we have minimum required data
    if prospect_data["email"] and prospect_data["organization_name"] != "Unknown Organization":
        workflow_id = await trigger_prospect_processing(prospect_data, background_tasks)
        return {"processed": True, "workflow_id": workflow_id}
    
    return {"processed": False, "reason": "Insufficient prospect data"}

def parse_salesforce_data(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parse Salesforce webhook data"""
    # Salesforce webhook format varies, this is a common structure
    sobject = payload.get("sobject", {})
    
    if not sobject:
        return None
    
    return {
        "organization_name": sobject.get("Company", "Unknown Organization"),
        "contact_name": f"{sobject.get('FirstName', '')} {sobject.get('LastName', '')}".strip(),
        "email": sobject.get("Email"),
        "phone": sobject.get("Phone") or sobject.get("MobilePhone"),
        "website": sobject.get("Website"),
        "industry": sobject.get("Industry", "Healthcare"),
        "lead_source": "salesforce",
        "additional_data": sobject
    }

def parse_hubspot_data(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parse HubSpot webhook data"""
    # HubSpot webhook format
    properties = payload.get("properties", {})
    
    if not properties:
        return None
    
    return {
        "organization_name": properties.get("company", "Unknown Organization"),
        "contact_name": f"{properties.get('firstname', '')} {properties.get('lastname', '')}".strip(),
        "email": properties.get("email"),
        "phone": properties.get("phone") or properties.get("mobilephone"),
        "website": properties.get("website"),
        "industry": properties.get("industry", "Healthcare"),
        "lead_source": "hubspot",
        "additional_data": properties
    }

async def trigger_prospect_processing(prospect_data: Dict[str, Any], background_tasks: BackgroundTasks) -> str:
    """Trigger prospect processing through the A2A system"""
    
    # Generate workflow ID
    workflow_id = f"webhook_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # Add to background processing queue
    background_tasks.add_task(call_a2a_system, "prospect", prospect_data, workflow_id)
    
    return workflow_id

async def trigger_daily_workflow(trigger: AutomationTrigger, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Trigger the daily workflow"""
    
    workflow_id = f"daily_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Add to background processing queue
    background_tasks.add_task(call_a2a_system, "daily_automation", {
        "batch_size": trigger.batch_size,
        "trigger": trigger.trigger
    }, workflow_id)
    
    return {"workflow_id": workflow_id}

async def call_a2a_system(endpoint_type: str, data: Dict[str, Any], workflow_id: str):
    """Call the main A2A system API"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            
            if endpoint_type == "prospect":
                # Call prospect processing endpoint
                response = await client.post(
                    f"{SERVICE_URL}/api/v1/prospect",
                    json=data,
                    headers={"X-Workflow-ID": workflow_id}
                )
            elif endpoint_type == "daily_automation":
                # Call batch processing endpoint
                response = await client.post(
                    f"{SERVICE_URL}/api/v1/prospects/batch",
                    json={"prospects": [], "batch_size": data.get("batch_size", 10)},
                    headers={"X-Workflow-ID": workflow_id}
                )
            
            if response.status_code == 200:
                logger.info(f"A2A system call successful for workflow {workflow_id}")
            else:
                logger.error(f"A2A system call failed: {response.status_code}")
                
    except Exception as e:
        logger.error(f"Error calling A2A system: {str(e)}")

async def process_crm_sync(crm_type: str, action: str, data: Dict[str, Any]):
    """Process CRM synchronization in background"""
    try:
        logger.info(f"Processing CRM sync: {crm_type} - {action}")
        
        # This would implement actual CRM API calls
        # For example, updating Salesforce with campaign results
        # or syncing prospect data back to HubSpot
        
        # Placeholder implementation
        await asyncio.sleep(1)  # Simulate API call
        logger.info(f"CRM sync completed: {crm_type}")
        
    except Exception as e:
        logger.error(f"Error in CRM sync: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8081))
    uvicorn.run(app, host="0.0.0.0", port=port)