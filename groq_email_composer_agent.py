#!/usr/bin/env python3
"""
Email Composer Agent for GFMD AI Swarm (Groq-powered)
Creates personalized, human-sounding sales emails
"""

from typing import Dict, Any
from groq_base_agent import GroqBaseAgent, AgentRole
from vector_rag_system import VectorRAGSystem
from email_styling_rules import EmailStyleRules
import json
import re

class GroqEmailComposerAgent(GroqBaseAgent):
    """Agent specialized in composing personalized sales emails"""

    def __init__(self, agent_id: str = "composer_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.EMAIL_COMPOSER,
            temperature=0.85  # Higher temperature for more creative, personalized writing
        )
        # Initialize RAG system for dynamic knowledge retrieval
        try:
            self.rag_system = VectorRAGSystem()
        except Exception as e:
            print(f"Warning: RAG system not available: {e}")
            self.rag_system = None

        # Initialize style rules for post-processing
        self.style_rules = EmailStyleRules()

    def get_system_prompt(self) -> str:
        campaign = getattr(self, '_current_campaign', 'narc_gone')
        return self._get_campaign_system_prompt(campaign)

    def _get_campaign_system_prompt(self, campaign: str = "narc_gone") -> str:
        if campaign == "spectrum":
            from spectrum_ai import SYSTEM
            return SYSTEM
        base_rules = """**CRITICAL RULES - MUST FOLLOW**:

1. **Greeting**: ALWAYS use "Hi [FirstName]," (never "Hello", never "Dear")
2. **Closing**: ALWAYS use "Best," (nothing else)
3. **NO emojis or bullet points** in the email body
4. **NO AI words**: Avoid "leverage", "utilize", "cutting-edge", "state-of-the-art", "innovative solutions", "game-changing", "synergy", "streamline", "optimize", "robust", "seamless"
5. **Keep it SHORT**: 4-5 sentences max
6. **Sound human**: Write like a real person, not a marketing robot
7. **Line formatting**: Keep sentences on single lines, avoid awkward line breaks in middle of sentences
8. Use only verified supplied prospect details. Do not invent research, volumes,
costs, customers, case studies, exact savings, clinical outcomes or regulatory guarantees.
Treat examples as structure only, never facts about this prospect. Do not imply
you noticed or researched anything about the organization.

**CRITICAL FORMATTING RULES**:
- Put a line break (\\n) after "Hi [FirstName],"
- Put line breaks between separate thoughts/sentences
- Each paragraph should be separated by double line breaks (\\n\\n)
- Never put everything in one long paragraph

**RETURN FORMAT** - Must be valid JSON:
{
  "subject": "Natural subject line",
  "body": "Full email body with greeting and closing",
  "personalization_notes": "What was personalized",
  "first_name": "Extracted first name"
}
"""

        if campaign == "centrifuge":
            return f"""You are an Email Composer Agent for GFMD (Global Focus), a B2B sales professional writing to hospital lab managers, clinical lab directors, and lab procurement contacts.

**Your Mission**: Write concise, professional emails about the Silencer Centrifuge.

Personalize with supplied facility/name/role only. Never imply research, sample volume, patient proximity or existing equipment unless explicitly provided as verified facts. Inferred context is hypothetical and must not be stated as fact.

{base_rules}

**About GFMD Silencer Centrifuge**:
- GFMD (Global Focus) is an American small business manufacturing the Silencer centrifuge in Dallas, Texas for over 30 years
- USA built with USA sales and technical support
- Price range: $4,500 - $11,000 per unit
- Very quiet: so quiet GFMD had to manufacture the End-of-Run Light (red while running, green at standby) -- a first in the industry, only necessary on Silencers
- Very reliable: quality parts (mostly metal), large motor, built to last
- Product line: MACH & ELITE (small STAT units), STEALTH (mid-size), TANK (large tabletop), ROVER (floor model)
- Target customers: Hospital labs, clinical labs, university research labs, pharmacies
- Product page: https://gfmd.com/silencer-centrifuges/
- Key differentiators: Quiet operation, durability, USA manufacturing and support, End-of-Run Light
"""

        return f"""You are an Email Composer Agent for GFMD, a B2B sales professional writing to law enforcement Property & Evidence managers.

**Your Mission**: Write concise, professional emails about Narc Gone drug destruction products.

Personalize with supplied agency/name/role only. Never claim research, seizure volume, costs, existing products or specific compliance obligations unless explicitly supplied as verified facts. Inferred context is hypothetical and must not be stated as fact.

{base_rules}

**About GFMD**:
- Manufactures Narc Gone drug destruction products for law enforcement agencies
- Target customers: Property & Evidence managers, police departments, sheriff's offices, federal agencies
- Main value props: Reduces disposal costs, eliminates incineration expenses, secure on-site destruction, DEA compliance
"""

    def get_step_specific_prompt(self, step: int, focus: str, tone: str, previous_subjects: list, campaign: str = "narc_gone") -> str:
        """Generate step-specific instructions for follow-up emails"""
        if campaign == "spectrum":
            from spectrum_campaign import FOCUSES
            if not isinstance(step, int) or isinstance(step, bool) or not 1 <= step <= 8:
                raise ValueError("Invalid Spectrum step")
            return f"Reconstructed Spectrum step {step} of 8: {FOCUSES[step - 1]}. Generate a grounded AI draft for approval."

        if campaign == "centrifuge":
            return self._get_centrifuge_step_prompt(step, focus, tone, previous_subjects)

        step_prompts = {
            1: """**EMAIL TYPE: INITIAL CONTACT (Step 1)**
This is the FIRST email to this prospect. Focus on:
- Identifying a specific pain point they likely have
- Brief introduction to Narc Gone benefits
- Soft call to action for a call
- Keep it short and professional

Example subject: "Drug disposal costs at [Agency Name]"
Example opening: "I noticed [Agency] handles drug evidence and wanted to reach out about..."
""",
            2: """**EMAIL TYPE: VALUE FOLLOW-UP (Step 2)**
This is a FOLLOW-UP to your first email. They haven't responded yet.

CRITICAL: DO NOT repeat the same pitch. Instead:
- Briefly reference your previous email ("Following up on my note last week...")
- Provide NEW value: specific cost savings data or a quick stat
- Different angle than email 1
- Suggest a specific time for call

Example subject: "Quick follow-up - [Agency Name] drug disposal"
Example opening: "I wanted to follow up on my previous email. I was thinking about how [Agency] might benefit from..."
DO NOT say the same things as before. Provide fresh value.
""",
            3: """**EMAIL TYPE: CASE STUDY / SOCIAL PROOF (Step 3)**
This is your THIRD email. Time to use social proof.

CRITICAL: Completely different approach than emails 1 and 2:
- Lead with a success story or case study
- Reference a similar agency (by type or size) that uses Narc Gone
- Make it story-based, not salesy
- Offer a brief demo or consultation

Example subject: "How [Similar Agency] cut disposal costs 40%"
Example opening: "I recently helped [Similar Agency Type] reduce their drug disposal backlog by..."
""",
            4: """**EMAIL TYPE: COMPLIANCE ANGLE (Step 4)**
This is your FOURTH email. Shift to compliance/regulatory angle.

CRITICAL: New angle - focus on compliance:
- Address DEA compliance concerns
- Position yourself as a compliance resource
- Offer to help with regulatory questions
- Don't repeat cost savings pitch

Example subject: "DEA compliance question for [Agency Name]"
Example opening: "I've been helping several agencies navigate DEA requirements for drug destruction..."
""",
            5: """**EMAIL TYPE: BUDGET PLANNING (Step 5)**
This is your FIFTH email. Focus on budget timing.

CRITICAL: Budget-focused approach:
- Reference budget planning season/fiscal year
- Talk about ROI and cost justification
- Offer to help with budget requests
- Don't repeat previous pitches

Example subject: "Budget planning for [Agency Name]"
Example opening: "With budget season coming up, I wanted to share how other agencies have justified..."
""",
            6: """**EMAIL TYPE: FINAL ATTEMPT (Step 6)**
This is your FINAL email in the sequence.

CRITICAL: Graceful close:
- Acknowledge they're busy or may not be interested right now
- Mention this is your last email
- One final, brief value statement
- Leave the door open for future contact
- Be respectful, not pushy

Example subject: "Final note about Narc Gone for [Agency Name]"
Example opening: "I know you're busy, so I'll keep this brief. This will be my last email..."
"""
        }

        base_prompt = step_prompts.get(step, step_prompts[1])

        # Add previous subjects to avoid repetition
        if previous_subjects and step > 1:
            subjects_list = "\n".join([f"  - {s}" for s in previous_subjects[-3:]])
            base_prompt += f"""

**PREVIOUS EMAILS SENT (DO NOT REPEAT THESE APPROACHES)**:
{subjects_list}

Your new email MUST be distinctly different from these. Use a completely new angle, new opening, and new subject line style.
"""

        return base_prompt

    def _get_centrifuge_step_prompt(self, step: int, focus: str, tone: str, previous_subjects: list) -> str:
        """Step-specific prompts for centrifuge hospital lab campaign"""
        step_prompts = {
            1: """**EMAIL TYPE: INITIAL CONTACT (Step 1)**
This is the FIRST email to this lab/hospital prospect. Focus on:
- Identifying a lab pain point (noise levels, centrifuge reliability, sample throughput)
- Brief introduction to the Silencer Centrifuge
- Mention it's the quietest centrifuge available
- Soft call to action for a call

Example subject: "Lab centrifuge noise at [Facility Name]"
Example opening: "I work with hospital labs on improving their centrifuge setup and wanted to reach out..."
""",
            2: """**EMAIL TYPE: VALUE FOLLOW-UP (Step 2)**
This is a FOLLOW-UP (~1 month later). They haven't responded yet.

CRITICAL: DO NOT repeat the same pitch. Instead:
- Briefly reference your previous email
- Provide NEW value: noise reduction data, efficiency improvements, or maintenance savings
- Different angle than email 1
- Suggest a specific time for call

Example subject: "Quick follow-up - [Facility Name] lab equipment"
Example opening: "Following up on my note last month about your lab centrifuge setup..."
""",
            3: """**EMAIL TYPE: CASE STUDY / SOCIAL PROOF (Step 3)**
This is your THIRD email (~2 months in). Use social proof.

CRITICAL: Completely different approach:
- Lead with a success story from a similar hospital or lab
- Reference measurable improvements (noise dB reduction, throughput, reliability)
- Make it story-based, not salesy
- Offer a brief demo or equipment evaluation

Example subject: "How [Similar Hospital] improved lab efficiency"
Example opening: "A hospital lab similar to yours recently switched to our Silencer Centrifuge and saw..."
""",
            4: """**EMAIL TYPE: BUDGET/ROI ANGLE (Step 4)**
This is your FOURTH email (~1 quarter later). Shift to budget justification.

CRITICAL: Budget and ROI focused:
- Reference capital equipment budget cycles
- Talk about ROI: cost per sample, maintenance savings, staff retention
- Offer to help with budget justification or equipment evaluation
- Don't repeat noise pitch verbatim

Example subject: "Budget planning for [Facility Name] lab equipment"
Example opening: "With equipment budgets being planned, I wanted to share how other labs have justified..."
""",
            5: """**EMAIL TYPE: FINAL ATTEMPT (Step 5)**
This is your FINAL email (~2 quarters in).

CRITICAL: Graceful close:
- Acknowledge they're busy or may not be in the market right now
- Mention this is your last email
- One final value statement about lab efficiency or noise reduction
- Leave the door open for when equipment budgets open up

Example subject: "Final note - Silencer Centrifuge for [Facility Name]"
Example opening: "I know lab operations keep you busy, so I'll keep this brief. This will be my last email..."
"""
        }

        base_prompt = step_prompts.get(step, step_prompts[1])

        if previous_subjects and step > 1:
            subjects_list = "\n".join([f"  - {s}" for s in previous_subjects[-3:]])
            base_prompt += f"""

**PREVIOUS EMAILS SENT (DO NOT REPEAT THESE APPROACHES)**:
{subjects_list}

Your new email MUST be distinctly different from these. Use a completely new angle, new opening, and new subject line style.
"""
        return base_prompt

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email composition task"""
        try:
            # Extract data
            prospect_data = task.get("prospect_data", {})
            research_findings = task.get("research_findings", {})
            qualification = task.get("qualification_score", {})

            # CRITICAL: Extract sequence context for follow-up differentiation
            sequence_context = task.get("sequence_context", {})
            campaign = sequence_context.get("campaign", "narc_gone")
            self._current_campaign = campaign
            step = sequence_context.get("step", 1)
            email_type = sequence_context.get("type", "initial")
            focus = sequence_context.get("focus", "pain_point_introduction")
            tone = sequence_context.get("tone", "professional_introduction")
            call_to_action = sequence_context.get("call_to_action", "quick_call")
            is_follow_up = sequence_context.get("is_follow_up", False)
            previous_emails = sequence_context.get("previous_emails", [])
            if campaign == "spectrum":
                from spectrum_ai import generate_spectrum_draft
                return await generate_spectrum_draft(getattr(self, "client", None), prospect_data, step,
                                                     previous_emails, model=getattr(self, "model", "openai/gpt-oss-120b"))

            # Extract previous email subjects for context
            previous_subjects = [e.get("subject", "") for e in previous_emails if e.get("subject")]

            # Extract key info
            contact_name = prospect_data.get("contact_name", "")
            
            # If no contact name, try to extract from email
            if not contact_name or contact_name in ['N/A', '', None]:
                email = prospect_data.get("email", "")
                contact_name = self._extract_name_from_email(email)
            
            company_name = self._clean_company_name(prospect_data.get("company_name", ""))
            location = prospect_data.get("location", "")
            title = prospect_data.get("title", "")

            # Get pain points and talking points
            pain_points = research_findings.get("pain_points", [])
            talking_points = qualification.get("key_talking_points", [])

            # Enrich prospect context for personalization
            enrichment = self._enrich_prospect_context(company_name, location, campaign=campaign)

            # Get RAG context if available
            rag_context = ""
            if self.rag_system:
                try:
                    # Get personalized insights from RAG system
                    agency_type = enrichment["agency_rag_key"]
                    insights = self.rag_system.get_personalized_insights(
                        agency_type=agency_type,
                        pain_points=pain_points[:2],
                        location=location
                    )
                    
                    # Combine relevant context
                    context_parts = []
                    for key, value in insights.items():
                        if value and len(value) > 50:  # Only use substantial context
                            context_parts.append(value[:300])  # Limit length
                    
                    rag_context = " ".join(context_parts)[:800]  # Max 800 chars
                except Exception as e:
                    print(f"RAG context retrieval failed: {e}")
                    rag_context = ""

            # Get step-specific instructions
            step_instructions = self.get_step_specific_prompt(step, focus, tone, previous_subjects, campaign=campaign)

            # Check for similarity rejection context (retry after too-similar email)
            similarity_rejection = sequence_context.get("similarity_rejection")
            rejection_instruction = ""
            if similarity_rejection:
                rejected_subj = similarity_rejection.get("rejected_subject", "")
                rejection_instruction = (
                    f"\n\nIMPORTANT - PREVIOUS ATTEMPT REJECTED: Your last email (subject: \"{rejected_subj}\") "
                    f"was too similar to a previous email in this sequence. You MUST take a completely different "
                    f"approach. Use a different opening, different angle, different subject line style, and "
                    f"different value proposition. Do NOT reuse any phrasing from your rejected attempt."
                )

            # Build composition prompt with sequence awareness
            composition_prompt = {
                "task": "compose_email",
                "sequence_step": step,
                "email_type": email_type,
                "is_follow_up": is_follow_up,
                "prospect": {
                    "contact_name": contact_name,
                    "company_name": company_name,
                    "location": location,
                    "title": title
                },
                "insights": {
                    "pain_points": pain_points[:2],  # Top 2 only
                    "talking_points": talking_points[:2],
                    "qualification_score": qualification.get("total_score", 0)
                },
                "context": {
                    "rag_knowledge": rag_context if rag_context else "Use general GFMD knowledge from system prompt"
                },
                "step_specific_instructions": step_instructions,
                "previous_email_subjects": previous_subjects if previous_subjects else [],
                "instruction": f"""Write a {'FOLLOW-UP' if is_follow_up else 'FIRST CONTACT'} B2B sales email (Step {step} of {enrichment['total_steps']}).

{step_instructions}

Only the explicitly supplied name, organization, location and title are verified
prospect facts. No facility research, sample/evidence volume or specific pain point
has been verified. Do not infer or assert these details.

CRITICAL REQUIREMENTS:
1. This is email #{step} - it MUST be different from previous emails
2. Use the approach specified above for Step {step}
3. NEVER repeat the same pitch, opening, or subject line style as previous emails
4. Reference their organization name: {company_name}
5. Keep it SHORT (4-5 sentences max)
6. Use the context above to write a specific opening - not a generic one
7. Return valid JSON with subject, body, personalization_notes, first_name{rejection_instruction}"""
            }

            # Set campaign context for system prompt selection
            self._current_campaign = campaign

            # Call Groq AI
            result = await self.think(composition_prompt)

            # Parse response
            if "error" in result:
                return self._create_fallback_email(prospect_data, research_findings)

            # If response is wrapped, extract JSON
            if "response" in result and isinstance(result["response"], str):
                try:
                    response_text = result["response"]
                    if "{" in response_text and "}" in response_text:
                        start = response_text.find("{")
                        end = response_text.rfind("}") + 1
                        json_text = response_text[start:end]
                        result = json.loads(json_text)
                except:
                    return self._create_fallback_email(prospect_data, research_findings)

            # Ensure required fields
            if not isinstance(result.get("body"), str) or not result["body"].strip() or not isinstance(result.get("subject"), str) or not result["subject"].strip():
                return self._create_fallback_email(prospect_data, research_findings)
            first_name = self._extract_first_name(contact_name)
            result.setdefault("first_name", first_name)
            result.setdefault("subject", f"Drug disposal discussion - {company_name}")

            # Ensure body has proper greeting/closing
            body = result.get("body", "")
            body = self._ensure_proper_format(body, first_name)

            # Post-process through style rules to strip AI language
            body = self.style_rules.clean_ai_language(body)
            body = self.style_rules.remove_emojis_and_bullets(body)
            body = self.style_rules.apply_professional_tone(body)
            body = body.split("Best,", 1)[0].rstrip() + "\n\nBest,\n\nMeranda Freiner\nsolutions@gfmd.com\n619-341-9058     www.gfmd.com"

            result["body"] = body

            # Create HTML version
            result["html_body"] = self._create_html_version(body, first_name)

            result.setdefault("personalization_notes", f"Personalized for {title} at {company_name}")
            result["success"] = True
            result["ai_generated"] = True
            result["model"] = self.model
            result["recipient_email"] = prospect_data.get("email", "")
            result["company_name"] = company_name

            return result

        except Exception as e:
            return self._create_fallback_email(prospect_data, research_findings, error=str(e))

    def _enrich_prospect_context(self, company_name: str, location: str, campaign: str = "narc_gone") -> Dict[str, str]:
        """Infer org type, region context, and personalization hint from org name and location."""

        if campaign == "centrifuge":
            return self._enrich_centrifuge_context(company_name, location)

        org_upper = (company_name or "").upper()

        # --- Agency type detection ---
        agency_type = "Law Enforcement Agency"
        agency_rag_key = "police"
        if "SHERIFF" in org_upper:
            agency_type = "Sheriff's Office"
            agency_rag_key = "sheriff"
        elif "ISD" in org_upper or "SCHOOL DISTRICT" in org_upper:
            agency_type = "ISD Police"
            agency_rag_key = "school_police"
        elif "UNIVERSITY" in org_upper or "COLLEGE" in org_upper:
            agency_type = "University Police"
            agency_rag_key = "university_police"
        elif "CONSTABLE" in org_upper:
            agency_type = "Constable's Office"
            agency_rag_key = "constable"
        elif any(k in org_upper for k in ["DEA", "CBP", "FEDERAL", "ATF", "FBI", "ICE", "MARSHAL"]):
            agency_type = "Federal Agency"
            agency_rag_key = "federal"
        elif any(k in org_upper for k in ["DPS", "STATE POLICE", "HIGHWAY PATROL", "STATE PATROL"]):
            agency_type = "State Agency"
            agency_rag_key = "state_police"
        elif any(k in org_upper for k in ["POLICE DEPARTMENT", " PD", "POLICE DEPT"]):
            agency_type = "Municipal Police Department"
            agency_rag_key = "police"

        # --- Region detection from state abbreviation ---
        state = ""
        if location:
            parts = [p.strip() for p in location.split(",")]
            if len(parts) >= 2:
                state = parts[-1].strip().upper()[:2]

        border_states = {"TX", "AZ", "NM", "CA"}
        opioid_states = {"OH", "WV", "KY", "PA", "TN", "IN", "NC", "VA", "MD", "NH", "MA"}
        southeast_states = {"FL", "GA", "AL", "MS", "SC", "LA", "AR"}
        midwest_states = {"IL", "MI", "MN", "WI", "MO", "IA", "KS", "NE", "ND", "SD"}

        if state in border_states:
            region_note = f"{state} border region - high seizure volume, cartel corridor trafficking"
        elif state in opioid_states:
            region_note = f"{state} opioid-impact region - fentanyl and opioid evidence surges"
        elif state in southeast_states:
            region_note = f"Southeast region - growing methamphetamine and fentanyl cases"
        elif state in midwest_states:
            region_note = f"Midwest region - increasing drug task-force seizures"
        elif state:
            region_note = f"{state} region"
        else:
            region_note = "Region unknown"

        # --- Personalization hints by agency type ---
        hints = {
            "Sheriff's Office": "manage evidence from multiple jurisdictions, transport makes off-site disposal costly",
            "ISD Police": "handle smaller but frequent seizures from campus incidents, need discreet on-site disposal",
            "University Police": "deal with campus drug seizures that require careful chain-of-custody and discreet disposal",
            "Municipal Police Department": "face drug evidence backlogs and rising incineration costs",
            "Constable's Office": "process seized narcotics across precincts with limited disposal options",
            "Federal Agency": "handle large-volume seizures with strict federal chain-of-custody and DEA audit requirements",
            "State Agency": "coordinate multi-county seizure disposal with complex logistics and regulatory oversight",
            "Law Enforcement Agency": "deal with drug evidence that requires secure, compliant disposal",
        }
        hint = hints.get(agency_type, hints["Law Enforcement Agency"])

        return {
            "agency_type": agency_type,
            "agency_rag_key": agency_rag_key,
            "region_note": region_note,
            "personalization_hint": hint,
            "context_label": "AGENCY CONTEXT",
            "total_steps": 6,
        }

    def _enrich_centrifuge_context(self, company_name: str, location: str) -> Dict[str, str]:
        """Infer facility type, region context, and personalization hint for centrifuge campaign."""
        org_upper = (company_name or "").upper()

        # --- Facility type detection ---
        agency_type = "Healthcare Facility"
        agency_rag_key = "hospital_lab"

        if any(k in org_upper for k in ["HOSPITAL", "MEDICAL CENTER", "HEALTH SYSTEM", "HEALTH CENTER"]):
            agency_type = "Hospital Lab"
            agency_rag_key = "hospital_lab"
        elif any(k in org_upper for k in ["LABORATORY", " LAB", "CLINICAL LAB", "PATHOLOGY", "DIAGNOSTICS"]):
            agency_type = "Clinical Lab"
            agency_rag_key = "clinical_lab"
        elif "PHARMACY" in org_upper:
            agency_type = "Pharmacy"
            agency_rag_key = "pharmacy"
        elif any(k in org_upper for k in ["UNIVERSITY", "COLLEGE"]):
            agency_type = "University Research Lab"
            agency_rag_key = "university_lab"
        elif any(k in org_upper for k in ["VETERINARY", "VET ", "ANIMAL"]):
            agency_type = "Veterinary Lab"
            agency_rag_key = "vet_lab"

        # --- Region detection ---
        state = ""
        if location:
            parts = [p.strip() for p in location.split(",")]
            if len(parts) >= 2:
                state = parts[-1].strip().upper()[:2]

        large_hospital_states = {"TX", "CA", "FL", "NY", "PA", "OH", "IL"}
        research_hub_states = {"MA", "MD", "NC", "MN"}

        if state in large_hospital_states:
            region_note = f"{state} - high-volume hospital market, large lab operations"
        elif state in research_hub_states:
            region_note = f"{state} - major research/academic medical hub"
        elif state:
            region_note = f"{state} region"
        else:
            region_note = "Region unknown"

        # --- Personalization hints by facility type ---
        hints = {
            "Hospital Lab": "run high-volume sample processing with noise-sensitive patient areas nearby, need reliable quiet equipment",
            "Clinical Lab": "process large sample volumes daily, centrifuge reliability and noise affect staff productivity",
            "Pharmacy": "need compact, quiet centrifuge equipment for compounding and testing workflows",
            "University Research Lab": "run varied research protocols requiring precise centrifuge performance in shared lab spaces",
            "Veterinary Lab": "process diverse sample types requiring versatile, reliable centrifuge equipment",
            "Healthcare Facility": "need reliable, quiet lab equipment that fits within existing workflows",
        }
        hint = hints.get(agency_type, hints["Healthcare Facility"])

        return {
            "agency_type": agency_type,
            "agency_rag_key": agency_rag_key,
            "region_note": region_note,
            "personalization_hint": hint,
            "context_label": "FACILITY CONTEXT",
            "total_steps": 5,
        }

    def _extract_first_name(self, full_name: str) -> str:
        """Extract first name from full name"""
        if not full_name or full_name in ['N/A', '', None]:
            return "there"

        # Remove titles
        titles = ['Dr.', 'Dr', 'Mr.', 'Mr', 'Ms.', 'Ms', 'Mrs.', 'Mrs', 'Prof.', 'Prof']
        name_parts = full_name.split()

        for part in name_parts:
            clean_part = part.strip('.,')
            if clean_part not in titles and clean_part:
                return clean_part

        return name_parts[0] if name_parts else "there"

    def _extract_name_from_email(self, email: str) -> str:
        """Extract potential first name from email address"""
        if not email:
            return ""
        
        try:
            # Get the part before @
            username = email.split('@')[0].lower()
            
            # Common patterns: first.last, firstlast, first_last, flast
            parts = username.replace('.', ' ').replace('_', ' ').replace('-', ' ').split()
            
            if parts:
                # Take the first part and capitalize
                first_part = parts[0]
                # Remove numbers and common prefixes
                first_part = ''.join(c for c in first_part if c.isalpha())
                
                # Skip common non-name parts
                skip_words = ['admin', 'info', 'contact', 'support', 'office', 'dept', 'chief', 'director']
                if first_part not in skip_words and len(first_part) > 1:
                    return first_part.capitalize()
        except:
            pass
        
        return ""

    def _clean_company_name(self, company_name: str) -> str:
        """Clean company name - remove (FKA...) and (AKA...) parts"""
        if not company_name:
            return company_name

        # Remove (AKA ...) and (FKA ...) patterns
        pattern = r'\s*\([AF]KA[^)]*\)'
        cleaned = re.sub(pattern, '', company_name).strip()
        return cleaned

    def _ensure_proper_format(self, body: str, first_name: str) -> str:
        """Ensure email has proper greeting and closing"""
        # Check for greeting
        if not body.strip().startswith("Hi "):
            body = f"Hi {first_name},\n\n" + body.lstrip()

        # Check for closing
        if "Best," not in body:
            body = body.rstrip() + "\n\nBest,\n\nMeranda Freiner\nsolutions@gfmd.com\n619-341-9058     www.gfmd.com"

        return body
    
    def _create_html_version(self, text_body: str, first_name: str) -> str:
        """Convert plain text email to HTML with GFMD signature"""
        
        # Split body into content and signature
        if "Best," in text_body:
            parts = text_body.split("Best,", 1)
            content = parts[0].strip()
        else:
            content = text_body.strip()
        
        # First ensure proper line breaks after greeting and between paragraphs
        lines = content.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                # Add the line
                formatted_lines.append(line)
                
                # Add extra spacing after greeting line
                if line.startswith('Hi ') and line.endswith(','):
                    formatted_lines.append('')
                
                # Add spacing between paragraphs (if next line exists and isn't empty)
                elif i < len(lines) - 1 and lines[i + 1].strip():
                    # Check if this is end of a sentence and next line starts a new thought
                    if (line.endswith('.') or line.endswith('?') or line.endswith('!')) and not lines[i + 1].strip().startswith('Our'):
                        formatted_lines.append('')
        
        # Rejoin with line breaks
        content = '\n'.join(formatted_lines)
        
        # Convert line breaks to HTML with proper paragraph spacing
        html_content = content.replace('\n\n', '</p><p>').replace('\n', '<br>\n')
        
        # Wrap in paragraph tags if we have paragraph breaks
        if '</p><p>' in html_content:
            html_content = f'<p>{html_content}</p>'
        
        # Create GFMD HTML signature without icons/logos
        html_signature = """
<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333; margin-top: 20px;">
    <div style="border-top: 1px solid #e0e0e0; padding-top: 15px;">
        <table cellpadding="0" cellspacing="0" border="0" style="width: 100%;">
            <tr>
                <td style="vertical-align: top; width: 80px; padding-right: 15px;">
                    <img src="https://gfmd.com/wp-content/themes/gfmd/assets/images/cropped-gfmd-logo-blue-1024x690.png" alt="GFMD Global Focus" style="width: 60px; height: auto; display: block; max-width: 60px;" />
                </td>
                <td style="vertical-align: top;">
                    <div style="font-weight: bold; font-size: 16px; color: #2c3e9e; margin-bottom: 8px;">
                        Meranda Freiner
                    </div>
                    <div style="font-size: 12px; color: #666; margin-bottom: 8px;">
                        Global Focus Marketing & Distribution
                    </div>
                    <div style="margin-bottom: 4px;">
                        <a href="mailto:solutions@gfmd.com" style="color: #2c3e9e; text-decoration: none; font-size: 13px;">solutions@gfmd.com</a>
                    </div>
                    <div style="margin-bottom: 4px; font-size: 13px; color: #333;">
                        619-341-9058
                    </div>
                    <div style="font-size: 13px;">
                        <a href="https://www.gfmd.com" style="color: #2c3e9e; text-decoration: none;">www.gfmd.com</a>
                    </div>
                </td>
            </tr>
        </table>
    </div>
</div>"""
        
        # Combine into full HTML email
        full_html = f"""
<div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5; color: #333;">
    {html_content}
    
    <div style="margin-top: 60px;">
        Best,
    </div>
    {html_signature}
</div>"""
        
        return full_html

    def _create_fallback_email(
        self,
        prospect_data: Dict[str, Any],
        research_findings: Dict[str, Any],
        error: str = None
    ) -> Dict[str, Any]:
        """Fail closed: an AI failure must never silently produce a canned send."""
        return {"success": False, "ai_generated": False, "actually_sent": False,
                "error": "AI composition failed; no fallback email generated"}


# Test the email composer agent
async def test_email_composer():
    """Test the email composer agent"""
    import os

    print("✉️ Testing Email Composer Agent")
    print("=" * 50)

    if not os.environ.get('GROQ_API_KEY'):
        print("❌ GROQ_API_KEY not set")
        return

    agent = GroqEmailComposerAgent()

    # Simulate full prospect data
    test_prospect = {
        "company_name": "Metro City Police Department",
        "location": "Metro City, TX",
        "facility_type": "Municipal Police Department",
        "title": "Evidence Manager",
        "contact_name": "Detective Lisa Rodriguez",
        "email": "l.rodriguez@metrocitypd.gov"
    }

    test_research = {
        "pain_points": [
            "Evidence destruction backlog",
            "High incineration costs",
            "DEA compliance concerns"
        ]
    }

    test_qualification = {
        "total_score": 90,
        "key_talking_points": [
            "Reduces disposal costs significantly",
            "On-site destruction capability",
            "DEA compliance built-in"
        ]
    }

    print(f"\n📝 Composing email for: {test_prospect['contact_name']}")
    print(f"   Company: {test_prospect['company_name']}")

    result = await agent.execute({
        "prospect_data": test_prospect,
        "research_findings": test_research,
        "qualification_score": test_qualification
    })

    if result.get("success"):
        print(f"\n✅ Email composed!")
        print(f"\n📧 Subject: {result.get('subject')}")
        print(f"\n📄 Body:\n{'-' * 50}")
        print(result.get('body'))
        print(f"{'-' * 50}")
        print(f"\n🧠 Tokens used: {agent.state['total_tokens_used']}")
    else:
        print(f"\n❌ Composition failed")


if __name__ == "__main__":
    import asyncio
    import os
    os.environ['GROQ_API_KEY'] = 'your_groq_api_key_here'
    asyncio.run(test_email_composer())
