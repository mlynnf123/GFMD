"""Spectrum reconstruction from persisted sends and recovered knowledge documents.

This module has no credentials, model calls, database access, or sending side effects.
The original Python prompts were not recovered. Copy is a sanitized reconstruction;
step types and business-day delays reproduce the recorded August-October sequence.
"""

from datetime import datetime, time, timedelta, timezone
from html import escape
from html.parser import HTMLParser
import re

from business_day_utils import BusinessDayCalculator


CAMPAIGN = "spectrum"
SEQUENCE_NAME = "spectrum_snf_ltc"
SUBJECT = "Same-day PCR for UTI, C. auris, CRE & mpox screening"
SEND_AT_UTC = time(15, 15)
STEP_TYPES = (
    "initial", "value_follow_up", "soft_check_in", "infection_control_follow_up",
    "breadth_follow_up", "turnaround_value_follow_up", "soft_value_touch", "final_attempt",
)
# Inferred with the recovered BusinessDayCalculator; not recovered configuration.
WAIT_BUSINESS_DAYS = (0, 4, 6, 3, 5, 5, 5, 5)
FOCUSES = (
    "test_menu_introduction", "uti_stewardship", "right_contact_check",
    "colonization_screening", "broader_test_menu", "turnaround_value",
    "offer_menu_or_pricing", "respectful_final_note",
)

REPLY_MENU = (
    "Not a fit right now. / We already handle this in-house or through another lab. / "
    "Send me more information. / Send me pricing. / Let's discuss next steps."
)
SIGNATURE = "Meranda Freiner\nsolutions@gfmd.com\n619-341-9058     www.gfmd.com"

# Derived from sent messages, with recipient-specific details removed and clinical
# outcome / public-health endorsement claims omitted from new drafts.
BODY_TEMPLATES = (
    "Orange County's Spectrum dx offers pathogen-specific PCR testing for skilled nursing, "
    "long-term care, and assisted living settings, with same-day results.\n\n"
    "The menu includes UTI PCR, C. auris PCR, CRE screening, mpox PCR, onychomycosis PCR, "
    "and respiratory PCR to support clinical and infection-control workflows.\n\n"
    "Worth a closer look for {company_name}? A one-line reply is all I need:\n{reply_menu}",

    "Following up on UTI testing for the care settings your team supports. Spectrum dx's "
    "same-day, pathogen-specific UTI PCR is intended to support clinician-directed "
    "treatment decisions and antibiotic stewardship.\n\n"
    "Would information or pricing be useful for {company_name}? A one-line reply works:\n"
    "Send me more information. / Send me pricing. / Let's discuss next steps.",

    "I know you're busy at {company_name}. Do you handle lab testing or infection-control "
    "matters, or is there a better person on your team to contact?\n\n"
    "Even a one-line reply helps: right person, wrong person, or not now?",

    "C. auris and CRE colonization screening can support infection-control and "
    "surveillance workflows in long-term care. Spectrum dx offers PCR-based screening "
    "for both.\n\nWould a test menu or more information be useful for {company_name}? "
    "A one-line reply is all I need:\n{reply_menu}",

    "Beyond UTI and colonization screening, Spectrum dx's menu includes respiratory PCR, "
    "mpox PCR, and onychomycosis PCR for nail-related testing. These are offered through "
    "the same Orange County lab.\n\n"
    "Worth a closer look for {company_name}? A one-line reply is all I need:\n{reply_menu}",

    "Waiting on lab results can slow the information available to your team. Spectrum "
    "dx offers same-day, pathogen-specific PCR results to support clinical and "
    "infection-control decisions.\n\n"
    "Would details on UTI PCR or colonization screening be helpful for {company_name}? "
    "A one-line reply works:\n{reply_menu}",

    "I can keep this simple for {company_name}: would a one-page test menu, pricing "
    "details, or an answer to a specific question be helpful?\n\n"
    "A one-line reply is all I need:\n"
    "Not a fit right now. / We already have a lab. / Send the menu. / "
    "Send pricing. / I have a question.",

    "I understand you may already have testing covered in-house or through another lab, "
    "or that this may not be a fit for {company_name}. This will be my final note.\n\n"
    "Spectrum dx offers same-day, pathogen-specific PCR for skilled nursing, long-term "
    "care, and assisted living settings. If useful, a one-line reply works:\n"
    "Info. / Pricing. / Not a fit. / Already covered.",
)


def spectrum_sequence_config():
    """Return a fresh config compatible with EmailSequenceTemplates."""
    cumulative = []
    elapsed = 0
    for days in WAIT_BUSINESS_DAYS:
        elapsed += days
        cumulative.append(elapsed)
    return {
        "name": "Spectrum dx SNF / LTC outreach",
        "description": "Reconstructed eight-step sequence; sending disabled by default",
        "campaign": CAMPAIGN,
        "reconstructed": True,
        "timing_days": cumulative,
        "emails": [
            {
                "step": index + 1, "type": kind, "wait_days": WAIT_BUSINESS_DAYS[index],
                "subject_template": SUBJECT, "focus": FOCUSES[index],
                "tone": "respectful_practical", "call_to_action": "one_line_reply",
                "prompts": {"system_addition": "Use the reconstructed Spectrum draft; never fall back to another campaign."},
            }
            for index, kind in enumerate(STEP_TYPES)
        ],
    }


def utc_datetime(value):
    """Historical offset-free worker timestamps are UTC (confirmed in Gmail)."""
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def next_spectrum_due(sent_at, next_step):
    """Use inferred business-day delays and the observed 15:15 UTC daily anchor."""
    if not 1 <= next_step <= len(STEP_TYPES):
        return None
    sent_at = utc_datetime(sent_at)
    calculator = BusinessDayCalculator()
    due = calculator.add_business_days(sent_at, WAIT_BUSINESS_DAYS[next_step - 1])
    due = due.replace(hour=SEND_AT_UTC.hour, minute=SEND_AT_UTC.minute, second=0, microsecond=0)
    while not calculator.is_business_day(due) or due < sent_at:
        due += timedelta(days=1)
        due = due.replace(hour=SEND_AT_UTC.hour, minute=SEND_AT_UTC.minute, second=0, microsecond=0)
    return due


def render_spectrum_email(prospect, step, previous_emails=()):
    """Build a deterministic draft, without AI or another campaign's fallback."""
    if not isinstance(step, int) or isinstance(step, bool) or not 1 <= step <= 8:
        raise ValueError("Spectrum step must be an integer from 1 to 8")
    name = " ".join(str(prospect.get("contact_name") or prospect.get("name") or "").split())
    first_name = name.split()[0] if name else "there"
    company_name = " ".join(str(prospect.get("organization") or prospect.get("company_name") or "your facility").split())
    text = BODY_TEMPLATES[step - 1].format(company_name=company_name, reply_menu=REPLY_MENU)
    body = f"Hi {first_name},\n\n{text}\n\nThanks,\n\n{SIGNATURE}"
    # Preserve the original thread's subject, ignoring old unsent draft entries.
    subject = next((e["subject"] for e in previous_emails if e.get("actually_sent") is True and e.get("subject")), SUBJECT)
    subject = " ".join(subject.replace("\r", " ").replace("\n", " ").split())
    paragraphs = "".join(f'<p style="font-weight:400">{escape(p).replace(chr(10), "<br>")}</p>' for p in body.split("\n\n"))
    return {
        "success": True, "campaign": CAMPAIGN, "step": step, "subject": subject,
        "body": body, "html_body": f'<div style="font-family:Arial,sans-serif;color:#111;font-weight:400">{paragraphs}</div>',
        "recipient_email": prospect.get("email", ""), "reconstructed": True,
        "template_type": STEP_TYPES[step - 1],
    }


def spectrum_reply_review(reply, sequence):
    """Route an untrusted inbound message for human review; never send a reply.

    Sender and thread matching establish relevance, not sender authentication.
    Incoming content is retained as data. AI drafts use bounded, tool-free prompts
    with human review; content never grants permission to execute or send.
    """
    sender = str(reply.get("from_email") or "").strip().lower()
    sent = [e for e in sequence.get("emails_sent", []) if e.get("actually_sent") is True]
    threads = {e.get("gmail_thread_id") for e in sent if e.get("gmail_thread_id")}
    if sequence.get("campaign") != CAMPAIGN or sender != str(sequence.get("contact_email", "")).lower() or not sender:
        return {"success": False, "error": "Reply does not match a Spectrum contact"}
    if not reply.get("message_id") or not reply.get("thread_id") or reply["thread_id"] not in threads:
        return {"success": False, "error": "Reply does not match a recorded Spectrum thread"}
    return {
        "success": True, "action": "human_review", "campaign": CAMPAIGN,
        "original_message_id": reply["message_id"], "gmail_thread_id": reply["thread_id"],
        "sender_email": sender, "subject": str(reply.get("subject") or ""),
        "original_content": str(reply.get("content") or ""), "status": "pending_review",
        "reason": "AI reply draft requires approval; historical automatic-reply policy was not recovered",
    }


def spectrum_reply_text(content):
    """Extract the new plain-text reply for opt-out analysis, excluding old quotes.

    Full original content is still retained in the human-review item. Ambiguous
    messages remain review-only; this function never grants permission to send.
    """
    text = str(content or "")
    if re.search(r"</?(?:html|body|div|p|br|blockquote|span)(?:\s|>)", text, re.IGNORECASE):
        class ReplyHTML(HTMLParser):
            def __init__(self):
                super().__init__(convert_charrefs=True)
                self.parts = []
                self.quoted = False

            def handle_starttag(self, tag, attrs):
                attributes = dict(attrs)
                classes = (attributes.get("class") or "").lower().split()
                if tag == "blockquote" or any(c in classes for c in ("gmail_quote", "yahoo_quoted")) or (attributes.get("id") or "").lower() == "divrplyfwdmsg":
                    self.quoted = True
                if not self.quoted and tag in {"div", "p", "br"}:
                    self.parts.append("\n")

            def handle_endtag(self, tag):
                if not self.quoted and tag in {"div", "p"}:
                    self.parts.append("\n")

            def handle_data(self, data):
                if not self.quoted:
                    self.parts.append(data)

        parser = ReplyHTML()
        parser.feed(text)
        text = "".join(parser.parts)
    lines = text.replace("\r\n", "\n").splitlines()
    current = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(">"):
            break
        if re.match(r"^-{2,}\s*(?:Original Message|Forwarded message)\s*-*\s*$", stripped, re.IGNORECASE):
            break
        # Gmail sometimes wraps its "On ... wrote:" marker onto several lines.
        if stripped.startswith("On ") and "wrote:" in " ".join(lines[index:index + 3]).lower():
            break
        if re.match(r"^From:\s", stripped, re.IGNORECASE) and any(
            re.match(r"^(?:Sent|Date|To|Subject):\s", following.strip(), re.IGNORECASE)
            for following in lines[index + 1:index + 5]
        ):
            break
        current.append(line)
    return "\n".join(current).strip()
