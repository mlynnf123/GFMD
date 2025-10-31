#!/usr/bin/env python3
"""
GFMD Swarm Agent Data Models - Vertex AI Implementation
Comprehensive data models and schemas for agent communication and system integration.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from enum import Enum
import json
from decimal import Decimal
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic import EmailStr

# ============================
# CORE ENUMS AND CONSTANTS
# ============================

class OrganizationType(str, Enum):
    """Types of healthcare organizations"""
    HOSPITAL = "hospital"
    MEDICAL_CENTER = "medical_center"
    LABORATORY = "laboratory"
    BLOOD_BANK = "blood_bank"
    RESEARCH_INSTITUTION = "research_institution"
    GOVERNMENT_AGENCY = "government_agency"
    MILITARY_BASE = "military_base"
    UNIVERSITY = "university"
    CLINIC = "clinic"

class LabType(str, Enum):
    """Types of laboratory operations"""
    CLINICAL_CHEMISTRY = "clinical_chemistry"
    HEMATOLOGY = "hematology"
    BLOOD_BANK = "blood_bank"
    MICROBIOLOGY = "microbiology"
    PATHOLOGY = "pathology"
    STAT_LAB = "stat_lab"
    MULTI_SPECIALTY = "multi_specialty"
    RESEARCH = "research"
    FORENSIC = "forensic"

class ContactRole(str, Enum):
    """Contact roles and titles"""
    LABORATORY_DIRECTOR = "laboratory_director"
    LABORATORY_MANAGER = "laboratory_manager"
    BIOMEDICAL_ENGINEER = "biomedical_engineer"
    PROCUREMENT_MANAGER = "procurement_manager"
    MATERIALS_MANAGER = "materials_manager"
    DEPARTMENT_HEAD = "department_head"
    PATHOLOGY_DIRECTOR = "pathology_director"
    CLINICAL_MANAGER = "clinical_manager"
    CFO = "cfo"
    VP_OPERATIONS = "vp_operations"
    ADMINISTRATOR = "administrator"

class PriorityLevel(str, Enum):
    """Priority levels for prospects and workflows"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CRITICAL = "critical"

class ProspectStage(str, Enum):
    """Stages in the prospect lifecycle"""
    NEW = "new"
    RESEARCHED = "researched"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    DEMO = "demo"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    NURTURE = "nurture"

class ProductSeries(str, Enum):
    """GFMD product series"""
    MACH = "mach"
    ELITE = "elite"
    STEALTH = "stealth"
    TANK = "tank"
    ROVER = "rover"

# ============================
# ORGANIZATION AND CONTACT MODELS
# ============================

class Address(BaseModel):
    """Address information"""
    street1: str = Field(description="Primary street address")
    street2: Optional[str] = Field(None, description="Secondary address line")
    city: str = Field(description="City name")
    state: str = Field(description="State or province")
    postal_code: str = Field(description="ZIP or postal code")
    country: str = Field(default="USA", description="Country code")

class Contact(BaseModel):
    """Contact person information"""
    contact_id: Optional[str] = Field(None, description="Unique contact identifier")
    first_name: str = Field(description="Contact first name")
    last_name: str = Field(description="Contact last name")
    full_name: Optional[str] = Field(None, description="Complete contact name")
    title: str = Field(description="Job title or role")
    role_category: Optional[ContactRole] = Field(None, description="Categorized role")
    email: Optional[EmailStr] = Field(None, description="Primary email address")
    phone: Optional[str] = Field(None, description="Primary phone number")
    mobile: Optional[str] = Field(None, description="Mobile phone number")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    department: Optional[str] = Field(None, description="Department or division")
    is_primary: bool = Field(default=False, description="Primary contact flag")
    is_decision_maker: bool = Field(default=False, description="Decision maker flag")
    influence_level: Optional[str] = Field(None, description="Level of influence: high, medium, low")
    notes: List[str] = Field(default_factory=list, description="Contact notes")
    last_contacted: Optional[datetime] = Field(None, description="Last contact date")
    preferred_contact_method: Optional[str] = Field(None, description="Preferred communication channel")
    
    @model_validator(mode='before')
    @classmethod
    def set_full_name(cls, values):
        if isinstance(values, dict) and not values.get('full_name'):
            values['full_name'] = f"{values.get('first_name', '')} {values.get('last_name', '')}".strip()
        return values

class Organization(BaseModel):
    """Healthcare organization information"""
    organization_id: Optional[str] = Field(None, description="Unique organization identifier")
    name: str = Field(description="Organization name")
    organization_type: OrganizationType = Field(description="Type of organization")
    parent_organization: Optional[str] = Field(None, description="Parent organization name")
    dba_name: Optional[str] = Field(None, description="Doing business as name")
    website: Optional[str] = Field(None, description="Organization website")
    address: Optional[Address] = Field(None, description="Primary address")
    phone: Optional[str] = Field(None, description="Main phone number")
    fax: Optional[str] = Field(None, description="Fax number")
    
    # Healthcare-specific fields
    bed_count: Optional[int] = Field(None, description="Number of hospital beds")
    annual_admissions: Optional[int] = Field(None, description="Annual patient admissions")
    employee_count: Optional[int] = Field(None, description="Total employees")
    annual_revenue: Optional[str] = Field(None, description="Estimated annual revenue")
    
    # Laboratory information
    lab_types: List[LabType] = Field(default_factory=list, description="Types of laboratory operations")
    test_volume_per_day: Optional[int] = Field(None, description="Daily test volume estimate")
    lab_hours: Optional[str] = Field(None, description="Laboratory operating hours")
    stat_lab: bool = Field(default=False, description="Has stat/emergency laboratory")
    
    # Equipment and vendor information
    current_equipment_vendors: List[str] = Field(default_factory=list, description="Current equipment vendors")
    equipment_age: Optional[str] = Field(None, description="Age of current equipment")
    planned_equipment_refresh: Optional[date] = Field(None, description="Planned equipment refresh date")
    
    # Certification and compliance
    accreditations: List[str] = Field(default_factory=list, description="Laboratory accreditations")
    certifications: List[str] = Field(default_factory=list, description="Organization certifications")
    
    # Financial and procurement
    fiscal_year_end: Optional[date] = Field(None, description="Fiscal year end date")
    budget_cycle: Optional[str] = Field(None, description="Budget planning cycle")
    procurement_process: Optional[str] = Field(None, description="Procurement process description")
    
    contacts: List[Contact] = Field(default_factory=list, description="Associated contacts")
    tags: List[str] = Field(default_factory=list, description="Organization tags")
    notes: List[str] = Field(default_factory=list, description="Organization notes")
    
    created_at: datetime = Field(default_factory=datetime.now, description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

# ============================
# PRODUCT AND PRICING MODELS
# ============================

class ProductSpecification(BaseModel):
    """GFMD product specifications"""
    model: str = Field(description="Product model number")
    series: ProductSeries = Field(description="Product series")
    name: str = Field(description="Product display name")
    category: str = Field(description="Product category")
    
    # Technical specifications
    capacity: Optional[str] = Field(None, description="Capacity specifications")
    speed_rpm: Optional[int] = Field(None, description="Maximum RPM")
    power_hp: Optional[str] = Field(None, description="Motor power (HP)")
    dimensions: Optional[Dict[str, float]] = Field(None, description="Physical dimensions")
    weight: Optional[float] = Field(None, description="Product weight")
    
    # Features
    refrigerated: bool = Field(default=False, description="Refrigeration capability")
    programmable: bool = Field(default=True, description="Programmable controls")
    digital_display: bool = Field(default=True, description="Digital display")
    safety_features: List[str] = Field(default_factory=list, description="Safety features")
    
    # Applications
    applications: List[str] = Field(default_factory=list, description="Intended applications")
    lab_types_suited: List[LabType] = Field(default_factory=list, description="Suitable laboratory types")
    
    # Pricing and availability
    list_price: Optional[Decimal] = Field(None, description="Manufacturer list price")
    dealer_price: Optional[Decimal] = Field(None, description="Dealer pricing")
    lead_time_weeks: Optional[int] = Field(None, description="Lead time in weeks")
    warranty_years: Optional[int] = Field(None, description="Warranty period")
    
    # Documentation
    specification_sheet_url: Optional[str] = Field(None, description="Specification document URL")
    user_manual_url: Optional[str] = Field(None, description="User manual URL")
    
    active: bool = Field(default=True, description="Product active status")

class ProductRecommendation(BaseModel):
    """Product recommendation for a specific prospect"""
    product_model: str = Field(description="Recommended product model")
    recommendation_score: float = Field(ge=0, le=10, description="Recommendation strength (0-10)")
    reasoning: List[str] = Field(description="Reasons for recommendation")
    fit_analysis: Dict[str, str] = Field(description="Fit analysis by category")
    estimated_quantity: Optional[int] = Field(None, description="Estimated quantity needed")
    estimated_value: Optional[Decimal] = Field(None, description="Estimated deal value")
    competitive_advantages: List[str] = Field(default_factory=list, description="Advantages over competition")
    potential_objections: List[str] = Field(default_factory=list, description="Potential customer objections")

# ============================
# PROSPECT AND QUALIFICATION MODELS
# ============================

class QualificationCriteria(BaseModel):
    """Qualification criteria and scoring"""
    bed_count_score: float = Field(ge=0, le=10, description="Bed count scoring")
    lab_type_score: float = Field(ge=0, le=10, description="Laboratory type scoring")
    equipment_age_score: float = Field(ge=0, le=10, description="Equipment age scoring")
    budget_readiness_score: float = Field(ge=0, le=10, description="Budget readiness scoring")
    contact_quality_score: float = Field(ge=0, le=10, description="Contact information quality")
    geographic_score: float = Field(ge=0, le=10, description="Geographic desirability")
    competitive_position_score: float = Field(ge=0, le=10, description="Competitive position")
    
    total_score: float = Field(ge=0, le=10, description="Total qualification score")
    scoring_methodology: str = Field(description="Scoring method used")
    scoring_date: datetime = Field(default_factory=datetime.now, description="When scoring was calculated")

class Prospect(BaseModel):
    """Complete prospect information"""
    prospect_id: str = Field(description="Unique prospect identifier")
    organization: Organization = Field(description="Organization information")
    primary_contact: Optional[Contact] = Field(None, description="Primary contact person")
    
    # Qualification information
    qualification: Optional[QualificationCriteria] = Field(None, description="Qualification scoring")
    priority_level: PriorityLevel = Field(default=PriorityLevel.MEDIUM, description="Prospect priority")
    stage: ProspectStage = Field(default=ProspectStage.NEW, description="Current prospect stage")
    
    # Product recommendations
    product_recommendations: List[ProductRecommendation] = Field(default_factory=list, description="Recommended products")
    estimated_opportunity_value: Optional[Decimal] = Field(None, description="Estimated total opportunity value")
    
    # Sales process information
    lead_source: Optional[str] = Field(None, description="How prospect was acquired")
    assigned_rep: Optional[str] = Field(None, description="Assigned sales representative")
    territory: Optional[str] = Field(None, description="Sales territory")
    
    # Engagement tracking
    first_contact_date: Optional[datetime] = Field(None, description="First contact attempt")
    last_activity_date: Optional[datetime] = Field(None, description="Last activity date")
    next_action: Optional[str] = Field(None, description="Next scheduled action")
    next_action_date: Optional[datetime] = Field(None, description="Next action date")
    
    # Competition and market intelligence
    known_competitors: List[str] = Field(default_factory=list, description="Known competing vendors")
    competitive_situation: Optional[str] = Field(None, description="Competitive landscape analysis")
    decision_timeline: Optional[str] = Field(None, description="Expected decision timeline")
    budget_range: Optional[str] = Field(None, description="Budget range information")
    
    # Internal tracking
    probability: Optional[int] = Field(None, ge=0, le=100, description="Win probability percentage")
    expected_close_date: Optional[date] = Field(None, description="Expected close date")
    tags: List[str] = Field(default_factory=list, description="Prospect tags")
    notes: List[str] = Field(default_factory=list, description="Prospect notes")
    
    created_at: datetime = Field(default_factory=datetime.now, description="Prospect creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="Created by user/agent")

# ============================
# OUTREACH AND COMMUNICATION MODELS
# ============================

class CommunicationChannel(str, Enum):
    """Communication channels"""
    EMAIL = "email"
    PHONE = "phone"
    LINKEDIN = "linkedin"
    DIRECT_MAIL = "direct_mail"
    TEXT_MESSAGE = "text_message"
    VIDEO_CALL = "video_call"
    IN_PERSON = "in_person"

class OutreachTouchpoint(BaseModel):
    """Individual touchpoint in outreach sequence"""
    touchpoint_id: str = Field(description="Unique touchpoint identifier")
    sequence_day: int = Field(description="Day number in sequence")
    channel: CommunicationChannel = Field(description="Communication channel")
    template_name: str = Field(description="Template identifier")
    subject_line: Optional[str] = Field(None, description="Email subject or call topic")
    message_content: Optional[str] = Field(None, description="Generated message content")
    
    # Personalization data
    personalization_tokens: Dict[str, str] = Field(default_factory=dict, description="Personalization tokens")
    dynamic_content: Dict[str, Any] = Field(default_factory=dict, description="Dynamic content elements")
    
    # Execution tracking
    scheduled_date: Optional[datetime] = Field(None, description="Scheduled execution date")
    executed_date: Optional[datetime] = Field(None, description="Actual execution date")
    execution_status: str = Field(default="pending", description="Execution status")
    
    # Response tracking
    response_received: bool = Field(default=False, description="Response received flag")
    response_date: Optional[datetime] = Field(None, description="Response date")
    response_type: Optional[str] = Field(None, description="Type of response")
    response_content: Optional[str] = Field(None, description="Response content")
    
    # Performance metrics
    delivered: Optional[bool] = Field(None, description="Successfully delivered")
    opened: Optional[bool] = Field(None, description="Message opened")
    clicked: Optional[bool] = Field(None, description="Links clicked")
    bounced: Optional[bool] = Field(None, description="Delivery bounced")

class OutreachSequence(BaseModel):
    """Complete outreach sequence"""
    sequence_id: str = Field(description="Unique sequence identifier")
    prospect_id: str = Field(description="Associated prospect ID")
    sequence_type: str = Field(description="Type of sequence")
    sequence_name: str = Field(description="Sequence name")
    
    # Sequence configuration
    persona_type: ContactRole = Field(description="Target persona")
    priority_level: PriorityLevel = Field(description="Sequence priority")
    touchpoints: List[OutreachTouchpoint] = Field(description="Sequence touchpoints")
    
    # Execution tracking
    started_date: Optional[datetime] = Field(None, description="Sequence start date")
    completed_date: Optional[datetime] = Field(None, description="Sequence completion date")
    current_step: int = Field(default=0, description="Current touchpoint index")
    active: bool = Field(default=True, description="Sequence active status")
    paused: bool = Field(default=False, description="Sequence paused status")
    
    # Performance metrics
    total_touchpoints: int = Field(description="Total touchpoints in sequence")
    touchpoints_executed: int = Field(default=0, description="Touchpoints executed")
    total_responses: int = Field(default=0, description="Total responses received")
    positive_responses: int = Field(default=0, description="Positive responses")
    meeting_requests: int = Field(default=0, description="Meeting requests generated")
    
    # Sequence effectiveness
    engagement_score: Optional[float] = Field(None, description="Overall engagement score")
    conversion_probability: Optional[float] = Field(None, description="Conversion probability")
    
    created_at: datetime = Field(default_factory=datetime.now, description="Sequence creation timestamp")
    created_by: Optional[str] = Field(None, description="Created by user/agent")

# ============================
# WORKFLOW AND AGENT MODELS
# ============================

class AgentExecution(BaseModel):
    """Agent execution tracking"""
    agent_id: str = Field(description="Agent identifier")
    agent_type: str = Field(description="Type of agent")
    execution_id: str = Field(description="Unique execution identifier")
    
    # Execution details
    started_at: datetime = Field(description="Execution start time")
    completed_at: Optional[datetime] = Field(None, description="Execution completion time")
    status: str = Field(description="Execution status")
    
    # Input and output
    input_data: Dict[str, Any] = Field(description="Agent input data")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Agent output data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Performance metrics
    execution_time_seconds: Optional[float] = Field(None, description="Execution time in seconds")
    tokens_used: Optional[int] = Field(None, description="Tokens consumed")
    api_calls: Optional[int] = Field(None, description="API calls made")
    
    # Context and handoff
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Execution context")
    handoff_data: Optional[Dict[str, Any]] = Field(None, description="Handoff data for next agent")
    handoff_target: Optional[str] = Field(None, description="Target agent for handoff")

class WorkflowExecution(BaseModel):
    """Complete workflow execution tracking"""
    workflow_id: str = Field(description="Unique workflow identifier")
    workflow_type: str = Field(description="Type of workflow")
    workflow_name: str = Field(description="Workflow name")
    
    # Workflow status
    status: str = Field(description="Workflow status")
    started_at: datetime = Field(description="Workflow start time")
    completed_at: Optional[datetime] = Field(None, description="Workflow completion time")
    
    # Agent executions
    agent_executions: List[AgentExecution] = Field(default_factory=list, description="Agent executions in workflow")
    current_agent: Optional[str] = Field(None, description="Currently executing agent")
    
    # Input data and results
    initial_input: Dict[str, Any] = Field(description="Initial workflow input")
    final_output: Optional[Dict[str, Any]] = Field(None, description="Final workflow output")
    intermediate_results: Dict[str, Any] = Field(default_factory=dict, description="Intermediate results by agent")
    
    # Performance metrics
    total_execution_time: Optional[float] = Field(None, description="Total workflow execution time")
    total_agents_involved: int = Field(default=0, description="Total agents involved")
    handoffs_processed: int = Field(default=0, description="Total handoffs processed")
    success_rate: Optional[float] = Field(None, description="Workflow success rate")
    
    # Error handling
    error_occurred: bool = Field(default=False, description="Error occurred flag")
    error_message: Optional[str] = Field(None, description="Error message")
    error_agent: Optional[str] = Field(None, description="Agent where error occurred")
    recovery_attempted: bool = Field(default=False, description="Recovery attempt made")
    
    created_by: Optional[str] = Field(None, description="Created by user/system")

# ============================
# SYSTEM METRICS AND ANALYTICS MODELS
# ============================

class SystemMetrics(BaseModel):
    """System-wide performance metrics"""
    metric_date: date = Field(default_factory=date.today, description="Metrics date")
    
    # Volume metrics
    total_prospects: int = Field(description="Total prospects in system")
    new_prospects_today: int = Field(description="New prospects added today")
    active_sequences: int = Field(description="Active outreach sequences")
    completed_workflows: int = Field(description="Completed workflows")
    
    # Performance metrics
    average_qualification_score: float = Field(description="Average qualification score")
    qualification_success_rate: float = Field(description="Qualification success rate percentage")
    outreach_response_rate: float = Field(description="Overall outreach response rate")
    meeting_conversion_rate: float = Field(description="Meeting conversion rate")
    
    # Agent performance
    agent_utilization: Dict[str, float] = Field(description="Agent utilization rates")
    average_execution_time: Dict[str, float] = Field(description="Average execution times by agent")
    agent_success_rates: Dict[str, float] = Field(description="Success rates by agent")
    
    # System health
    error_rate: float = Field(description="System error rate")
    uptime_percentage: float = Field(description="System uptime percentage")
    api_response_time: float = Field(description="Average API response time")
    
    created_at: datetime = Field(default_factory=datetime.now, description="Metrics creation timestamp")

# ============================
# INTEGRATION AND CONFIGURATION MODELS
# ============================

class IntegrationConfig(BaseModel):
    """Configuration for external system integrations"""
    integration_name: str = Field(description="Integration name")
    integration_type: str = Field(description="Type of integration")
    
    # Connection details
    endpoint_url: Optional[str] = Field(None, description="API endpoint URL")
    api_key: Optional[str] = Field(None, description="API key")
    credentials: Optional[Dict[str, str]] = Field(None, description="Authentication credentials")
    
    # Configuration settings
    sync_frequency: Optional[str] = Field(None, description="Data sync frequency")
    data_mapping: Optional[Dict[str, str]] = Field(None, description="Field mapping configuration")
    filters: Optional[Dict[str, Any]] = Field(None, description="Data filtering rules")
    
    # Status and monitoring
    active: bool = Field(default=True, description="Integration active status")
    last_sync: Optional[datetime] = Field(None, description="Last sync timestamp")
    sync_status: Optional[str] = Field(None, description="Last sync status")
    error_message: Optional[str] = Field(None, description="Last error message")

class SystemConfiguration(BaseModel):
    """System-wide configuration settings"""
    config_id: str = Field(description="Configuration identifier")
    config_category: str = Field(description="Configuration category")
    
    # Agent settings
    default_model: str = Field(description="Default AI model")
    model_temperature: float = Field(description="Model temperature setting")
    max_tokens: int = Field(description="Maximum tokens per request")
    
    # Workflow settings
    qualification_threshold: float = Field(description="Minimum qualification score")
    auto_advance_sequences: bool = Field(description="Auto advance outreach sequences")
    response_monitoring_interval: int = Field(description="Response monitoring interval in hours")
    
    # Performance settings
    max_concurrent_workflows: int = Field(description="Maximum concurrent workflows")
    rate_limit_per_minute: int = Field(description="API rate limit per minute")
    cache_ttl_hours: int = Field(description="Cache time-to-live in hours")
    
    # Notification settings
    notification_channels: List[str] = Field(description="Notification channels")
    alert_thresholds: Dict[str, float] = Field(description="Alert thresholds")
    
    created_at: datetime = Field(default_factory=datetime.now, description="Configuration creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

# ============================
# UTILITY FUNCTIONS
# ============================

def create_sample_prospect() -> Prospect:
    """Create a sample prospect for testing"""
    address = Address(
        street1="123 Medical Center Dr",
        city="Atlanta",
        state="GA",
        postal_code="30309"
    )
    
    organization = Organization(
        name="St. Mary's Regional Medical Center",
        organization_type=OrganizationType.HOSPITAL,
        address=address,
        phone="404-555-0123",
        bed_count=350,
        lab_types=[LabType.CLINICAL_CHEMISTRY, LabType.HEMATOLOGY],
        test_volume_per_day=1500,
        stat_lab=True
    )
    
    contact = Contact(
        first_name="Dr. Sarah",
        last_name="Johnson",
        title="Laboratory Director",
        role_category=ContactRole.LABORATORY_DIRECTOR,
        email="s.johnson@stmarys.org",
        phone="404-555-0124",
        is_primary=True,
        is_decision_maker=True,
        influence_level="high"
    )
    
    qualification = QualificationCriteria(
        bed_count_score=8.5,
        lab_type_score=9.0,
        equipment_age_score=7.5,
        budget_readiness_score=8.0,
        contact_quality_score=9.5,
        geographic_score=8.0,
        competitive_position_score=7.0,
        total_score=8.2,
        scoring_methodology="GFMD_Standard_V1"
    )
    
    return Prospect(
        prospect_id="prospect_001",
        organization=organization,
        primary_contact=contact,
        qualification=qualification,
        priority_level=PriorityLevel.HIGH,
        stage=ProspectStage.QUALIFIED,
        lead_source="Website Inquiry",
        estimated_opportunity_value=Decimal("125000.00")
    )

def export_schemas() -> Dict[str, Any]:
    """Export all data model schemas for API documentation"""
    schemas = {}
    
    # Core models
    schemas["Organization"] = Organization.schema()
    schemas["Contact"] = Contact.schema()
    schemas["Prospect"] = Prospect.schema()
    schemas["ProductSpecification"] = ProductSpecification.schema()
    schemas["OutreachSequence"] = OutreachSequence.schema()
    schemas["WorkflowExecution"] = WorkflowExecution.schema()
    schemas["SystemMetrics"] = SystemMetrics.schema()
    
    return schemas

if __name__ == "__main__":
    # Demo the data models
    print("🗃️ GFMD Swarm Agent Data Models - Vertex AI Implementation")
    print("=" * 60)
    
    # Create sample prospect
    sample_prospect = create_sample_prospect()
    print(f"Sample Prospect: {sample_prospect.organization.name}")
    print(f"Qualification Score: {sample_prospect.qualification.total_score}")
    print(f"Priority: {sample_prospect.priority_level.value}")
    
    # Export sample as JSON
    prospect_json = sample_prospect.json(indent=2)
    print(f"\nSample JSON Export (first 500 chars):")
    print(prospect_json[:500] + "...")
    
    # Show schema information
    schemas = export_schemas()
    print(f"\nAvailable Schemas: {len(schemas)}")
    for schema_name in schemas.keys():
        print(f"  • {schema_name}")
    
    print(f"\n✅ Data models loaded successfully!")
    print(f"Total model classes: {len([cls for cls in globals().values() if isinstance(cls, type) and issubclass(cls, BaseModel)])}")