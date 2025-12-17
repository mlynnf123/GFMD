#!/usr/bin/env python3
"""
Enhanced Email Templates for GFMD Narcon Based on Market Research
Uses insights from market research to create more compelling messaging
"""

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class AgencyType(Enum):
    """Types of law enforcement agencies for targeting"""
    POLICE_DEPARTMENT = "police_department"
    SHERIFF_OFFICE = "sheriff_office"
    FEDERAL_AGENCY = "federal_agency"
    STATE_POLICE = "state_police"

@dataclass
class EnhancedEmailTemplate:
    """Enhanced email template with market research insights"""
    id: str
    name: str
    subject_template: str
    body_template: str
    sequence_step: int
    target_agency_types: List[AgencyType]
    pain_points_addressed: List[str]
    value_props_highlighted: List[str]
    wait_days: int = 0

class NarconEmailTemplates:
    """Repository of Narcon-focused email templates based on market research"""
    
    def __init__(self):
        """Initialize enhanced email templates"""
        self.templates = self._load_enhanced_templates()
        
    def _load_enhanced_templates(self) -> Dict[str, EnhancedEmailTemplate]:
        """Load enhanced email templates with market research insights"""
        
        templates = {
            # Initial outreach templates by agency type
            "initial_federal": EnhancedEmailTemplate(
                id="initial_federal",
                name="Initial Outreach - Federal Agencies",
                subject_template="DHS-tested drug destruction for {{organization}}",
                body_template="""I noticed {{organization}} processes significant drug evidence volumes - CBP alone handles 55,000+ pounds monthly.

Our Narc Gone system was created FOR and tested BY DHS under CRADA #22-TST-001. It's the only chemical destruction product tested and verified by the U.S. Government to meet DEA non-retrievable standards.

{{organization}} likely faces the same disposal logistics challenges other federal agencies tell us about. Worth a brief conversation about the DHS-approved solution?""",
                sequence_step=1,
                target_agency_types=[AgencyType.FEDERAL_AGENCY],
                pain_points_addressed=["disposal_logistics", "volume_scale", "compliance"],
                value_props_highlighted=["dhs_partnership", "government_tested", "dea_compliant"]
            ),
            
            "initial_police": EnhancedEmailTemplate(
                id="initial_police",
                name="Initial Outreach - Police Departments", 
                subject_template="Stop driving, start destroying - drug disposal for {{organization}}",
                body_template="""I noticed {{organization}} likely faces the same challenge most departments tell us about: driving hours to dispose of drug evidence.

Our Narc Gone system eliminates those costly trips. 99.99% fentanyl destruction, on-site, DEA-compliant. Created and tested with DHS for law enforcement.

Many departments {{similar_size}} save thousands annually by switching from incineration. Worth a quick conversation about potential savings?""",
                sequence_step=1,
                target_agency_types=[AgencyType.POLICE_DEPARTMENT, AgencyType.SHERIFF_OFFICE],
                pain_points_addressed=["travel_costs", "time_burden", "officer_safety"],
                value_props_highlighted=["cost_savings", "on_site", "fentanyl_tested"]
            ),
            
            "initial_state": EnhancedEmailTemplate(
                id="initial_state",
                name="Initial Outreach - State Police",
                subject_template="Reclaim your evidence room - {{organization}}",
                body_template="""State agencies tell us their biggest challenge is evidence room backlogs from disposal logistics.

Our Narc Gone system processes drugs on-site - no more waiting for incinerator trips or permit restrictions. DHS-tested, 99.99% fentanyl destruction proven by NC State Crime Lab.

{{organization}} could likely reclaim significant evidence storage space. Quick call to discuss?""",
                sequence_step=1,
                target_agency_types=[AgencyType.STATE_POLICE],
                pain_points_addressed=["storage_backlog", "disposal_delays", "space_constraints"],
                value_props_highlighted=["on_site", "lab_proven", "evidence_room_relief"]
            ),
            
            # Follow-up templates with enhanced value props
            "follow_up_cost_focus": EnhancedEmailTemplate(
                id="follow_up_cost_focus",
                name="Follow-up - Cost Savings Focus",
                subject_template="Re: Drug disposal costs at {{organization}}",
                body_template="""Following up on my previous email about drug disposal cost savings.

Most departments spend $1.50/pound plus transportation costs for incineration. Departments {{similar_size}} typically save 40-60% switching to our Narc Gone system.

DHS co-developed this solution specifically for law enforcement needs. The only government-tested chemical destruction system meeting DEA standards.

10-minute call to show you the cost comparison?""",
                sequence_step=2,
                target_agency_types=[AgencyType.POLICE_DEPARTMENT, AgencyType.SHERIFF_OFFICE],
                pain_points_addressed=["disposal_costs", "budget_pressure"],
                value_props_highlighted=["cost_reduction", "dhs_partnership", "dea_compliant"],
                wait_days=3
            ),
            
            "follow_up_safety_focus": EnhancedEmailTemplate(
                id="follow_up_safety_focus", 
                name="Follow-up - Officer Safety Focus",
                subject_template="Re: Officer safety and drug destruction",
                body_template="""Following up on eliminating risky drug transport for {{organization}}.

Transporting seized fentanyl and other drugs puts officers at risk. Our Narc Gone system destroys drugs on-site - 99.99% fentanyl destruction verified by independent lab testing.

No more multi-day trips to incinerators. No more officer exposure during transport. DHS uses this system for the same safety reasons.

Worth 10 minutes to discuss officer safety improvements?""",
                sequence_step=2,
                target_agency_types=[AgencyType.POLICE_DEPARTMENT, AgencyType.FEDERAL_AGENCY],
                pain_points_addressed=["officer_safety", "transport_risk", "fentanyl_exposure"],
                value_props_highlighted=["on_site", "fentanyl_tested", "safety_improvement"],
                wait_days=3
            ),
            
            # Case study template with specific examples
            "case_study_dhs": EnhancedEmailTemplate(
                id="case_study_dhs",
                name="Case Study - DHS Partnership",
                subject_template="How DHS solves drug disposal with Narc Gone",
                body_template="""Since you opened my previous email, thought you'd find this relevant.

DHS partnered with us under CRADA #22-TST-001 to create Narc Gone specifically for federal law enforcement needs. They needed an on-site solution for 55,000+ pounds of monthly seizures.

Key results:
- Eliminated costly incinerator transport
- 99.99% fentanyl destruction (NC State Crime Lab verified)  
- Full DEA compliance without permit restrictions
- Listed in CBP Technology Assessment Catalog

{{organization}} processes similar evidence volumes. Worth discussing how the same DHS-approved solution could work for you?""",
                sequence_step=3,
                target_agency_types=[AgencyType.FEDERAL_AGENCY, AgencyType.STATE_POLICE],
                pain_points_addressed=["scale_challenges", "compliance_burden", "credibility"],
                value_props_highlighted=["dhs_partnership", "scale_proven", "government_approved"],
                wait_days=0
            ),
            
            "case_study_local": EnhancedEmailTemplate(
                id="case_study_local",
                name="Case Study - Local Department Success",
                subject_template="How {{similar_dept}} eliminated disposal trips",
                body_template="""Since you engaged with my previous email, here's a relevant example.

{{similar_dept}} was spending $8,000+ annually on incinerator trips - 6-hour round trips, multiple officers, evidence room backlog growing.

After switching to Narc Gone:
- Eliminated all transport trips (100% on-site destruction)
- Cut disposal costs 45%  
- Reclaimed evidence room space
- Improved officer safety (no more fentanyl transport)

Same DHS-tested system used by federal agencies. {{organization}} likely has similar pain points - worth 10 minutes to discuss?""",
                sequence_step=3,
                target_agency_types=[AgencyType.POLICE_DEPARTMENT, AgencyType.SHERIFF_OFFICE],
                pain_points_addressed=["travel_costs", "evidence_backlog", "officer_safety"],
                value_props_highlighted=["cost_reduction", "space_recovery", "federal_approved"],
                wait_days=0
            ),
            
            # Final breakup email
            "breakup_value_summary": EnhancedEmailTemplate(
                id="breakup_value_summary",
                name="Final Breakup - Value Summary",
                subject_template="Final note about {{organization}} drug disposal",
                body_template="""I'll stop reaching out after this, but wanted to leave you with the key facts:

• Narc Gone is the ONLY chemical destruction system tested and verified by the U.S. Government
• Co-developed with DHS specifically for law enforcement needs
• 99.99% fentanyl destruction (independently verified)
• Eliminates costly incinerator trips and transport risks
• Used by federal agencies processing 55,000+ lbs monthly

If disposal logistics, costs, or officer safety ever become priorities for {{organization}}, we're here to help.

The DHS partnership and government testing speak for themselves.""",
                sequence_step=4,
                target_agency_types=[AgencyType.POLICE_DEPARTMENT, AgencyType.SHERIFF_OFFICE, AgencyType.FEDERAL_AGENCY, AgencyType.STATE_POLICE],
                pain_points_addressed=["credibility_proof", "comprehensive_solution"],
                value_props_highlighted=["government_tested", "dhs_partnership", "comprehensive_benefits"],
                wait_days=7
            ),
            
            # Reorder templates
            "reorder_reminder_federal": EnhancedEmailTemplate(
                id="reorder_reminder_federal",
                name="Reorder Reminder - Federal Agencies",
                subject_template="Narc Gone restock for {{organization}}",
                body_template="""Hi {{firstName}},

Based on {{organization}}'s previous order pattern, you likely need to restock Narc Gone soon.

{{last_quantity}} containers should handle about {{estimated_pounds}} pounds of evidence. Given typical federal seizure volumes, reordering now ensures no processing delays.

Same DHS-approved pricing. Reply to confirm and I'll expedite shipping.""",
                sequence_step=0,
                target_agency_types=[AgencyType.FEDERAL_AGENCY],
                pain_points_addressed=["supply_continuity", "operational_efficiency"],
                value_props_highlighted=["proven_usage", "expedited_service"]
            ),
            
            "reorder_reminder_local": EnhancedEmailTemplate(
                id="reorder_reminder_local", 
                name="Reorder Reminder - Local Agencies",
                subject_template="Narc Gone restock - avoid disposal delays",
                body_template="""Hi {{firstName}},

Your previous order of {{last_quantity}} containers likely needs restocking based on {{organization}}'s usage pattern.

Don't risk evidence room backlog if disposal delays occur. Our standard restock maintains continuous processing capability.

Same pricing as before. Just reply to confirm and we'll ship immediately.""",
                sequence_step=0,
                target_agency_types=[AgencyType.POLICE_DEPARTMENT, AgencyType.SHERIFF_OFFICE],
                pain_points_addressed=["evidence_backlog", "operational_continuity"], 
                value_props_highlighted=["proven_reliability", "immediate_fulfillment"]
            )
        }
        
        return templates
    
    def get_template_for_agency(self, template_base_id: str, agency_type: AgencyType) -> EnhancedEmailTemplate:
        """Get the most appropriate template variation for an agency type"""
        
        # Map agency types to specific template variations
        agency_mappings = {
            "initial_outreach": {
                AgencyType.FEDERAL_AGENCY: "initial_federal",
                AgencyType.POLICE_DEPARTMENT: "initial_police", 
                AgencyType.SHERIFF_OFFICE: "initial_police",
                AgencyType.STATE_POLICE: "initial_state"
            },
            "follow_up": {
                AgencyType.FEDERAL_AGENCY: "follow_up_safety_focus",
                AgencyType.POLICE_DEPARTMENT: "follow_up_cost_focus",
                AgencyType.SHERIFF_OFFICE: "follow_up_cost_focus",
                AgencyType.STATE_POLICE: "follow_up_safety_focus"
            },
            "case_study": {
                AgencyType.FEDERAL_AGENCY: "case_study_dhs",
                AgencyType.POLICE_DEPARTMENT: "case_study_local",
                AgencyType.SHERIFF_OFFICE: "case_study_local", 
                AgencyType.STATE_POLICE: "case_study_dhs"
            },
            "reorder_reminder": {
                AgencyType.FEDERAL_AGENCY: "reorder_reminder_federal",
                AgencyType.POLICE_DEPARTMENT: "reorder_reminder_local",
                AgencyType.SHERIFF_OFFICE: "reorder_reminder_local",
                AgencyType.STATE_POLICE: "reorder_reminder_federal"
            }
        }
        
        # Get specific template ID for this agency type
        if template_base_id in agency_mappings:
            specific_template_id = agency_mappings[template_base_id].get(agency_type)
            if specific_template_id and specific_template_id in self.templates:
                return self.templates[specific_template_id]
        
        # Fallback to breakup email if no specific mapping
        return self.templates.get("breakup_value_summary", list(self.templates.values())[0])
    
    def get_all_templates(self) -> Dict[str, EnhancedEmailTemplate]:
        """Get all available templates"""
        return self.templates
    
    def get_templates_by_agency_type(self, agency_type: AgencyType) -> List[EnhancedEmailTemplate]:
        """Get all templates suitable for a specific agency type"""
        return [template for template in self.templates.values() 
                if agency_type in template.target_agency_types]

# Utility functions for template selection
def determine_agency_type(organization_name: str, title: str = "") -> AgencyType:
    """Determine agency type based on organization name and title"""
    org_lower = organization_name.lower()
    title_lower = title.lower()
    
    # Federal agency indicators
    federal_indicators = ["dhs", "homeland", "border patrol", "cbp", "ice", "dea", "tsa", "fbi", "atf"]
    if any(indicator in org_lower for indicator in federal_indicators):
        return AgencyType.FEDERAL_AGENCY
    
    # Sheriff's office indicators  
    sheriff_indicators = ["sheriff", "county"]
    if any(indicator in org_lower for indicator in sheriff_indicators):
        return AgencyType.SHERIFF_OFFICE
    
    # State police indicators
    state_indicators = ["state police", "highway patrol", "state patrol", "state trooper"]
    if any(indicator in org_lower for indicator in state_indicators):
        return AgencyType.STATE_POLICE
    
    # Default to police department
    return AgencyType.POLICE_DEPARTMENT

def get_pain_point_messaging(agency_type: AgencyType) -> Dict[str, str]:
    """Get pain point messaging tailored to agency type"""
    messaging = {
        AgencyType.FEDERAL_AGENCY: {
            "primary_pain_point": "massive scale disposal logistics",
            "cost_focus": "operational efficiency at scale",
            "safety_focus": "officer safety with high-risk substances",
            "compliance_focus": "strict federal compliance requirements"
        },
        AgencyType.POLICE_DEPARTMENT: {
            "primary_pain_point": "costly disposal trips and evidence backlogs", 
            "cost_focus": "budget relief and cost reduction",
            "safety_focus": "officer safety during transport",
            "compliance_focus": "simple compliance without permits"
        },
        AgencyType.SHERIFF_OFFICE: {
            "primary_pain_point": "rural disposal challenges and travel costs",
            "cost_focus": "eliminating travel expenses", 
            "safety_focus": "reducing transport risks",
            "compliance_focus": "meeting county compliance requirements"
        },
        AgencyType.STATE_POLICE: {
            "primary_pain_point": "statewide coordination and evidence backlogs",
            "cost_focus": "statewide operational efficiency",
            "safety_focus": "officer safety across jurisdictions", 
            "compliance_focus": "state-level compliance standards"
        }
    }
    
    return messaging.get(agency_type, messaging[AgencyType.POLICE_DEPARTMENT])

# Test the enhanced templates
if __name__ == "__main__":
    templates = NarconEmailTemplates()
    
    # Test agency type determination
    test_agencies = [
        ("Austin Police Department", "Evidence Manager"),
        ("Travis County Sheriff's Office", "Property Manager"), 
        ("Department of Homeland Security", "Contracting Officer"),
        ("Texas State Police", "Evidence Supervisor")
    ]
    
    print("🧪 Testing Enhanced Email Templates")
    print("=" * 50)
    
    for org, title in test_agencies:
        agency_type = determine_agency_type(org, title)
        initial_template = templates.get_template_for_agency("initial_outreach", agency_type)
        
        print(f"\n📧 {org} ({title})")
        print(f"   Agency Type: {agency_type.value}")
        print(f"   Template: {initial_template.name}")
        print(f"   Subject: {initial_template.subject_template}")
        print(f"   Pain Points: {', '.join(initial_template.pain_points_addressed)}")
        print(f"   Value Props: {', '.join(initial_template.value_props_highlighted)}")
    
    print(f"\n✅ Total Templates Available: {len(templates.get_all_templates())}")
    print("Ready for integration with email sequence orchestrator!")