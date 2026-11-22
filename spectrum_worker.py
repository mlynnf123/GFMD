"""Spectrum processing with injected existing storage/Gmail adapters.

No startup side effects. Live sending requires an explicit environment opt-in;
uncertain transport results are held for review rather than retried automatically.
"""

import os
from datetime import datetime, timezone
from email.utils import make_msgid
from uuid import uuid4

from business_day_utils import BusinessDayCalculator
from spectrum_campaign import SEND_AT_UTC, SEQUENCE_NAME, next_spectrum_due, render_spectrum_email, utc_datetime


def spectrum_sending_enabled():
    return os.environ.get("GFMD_SPECTRUM_SEND_ENABLED") == "1"


async def process_spectrum_sequence(worker, sequence, send_emails=True, *, now=None):
    if sequence.get("status") != "active" or sequence.get("reply_received"):
        return {"success": True, "action": "skipped", "reason": "terminal_or_replied"}
    if sequence.get("campaign") != "spectrum" or sequence.get("sequence_name", SEQUENCE_NAME) != SEQUENCE_NAME:
        return {"success": False, "error": "Unsupported sequence configuration; sequence unchanged"}
    current_step = sequence.get("current_step", 0)
    if not isinstance(current_step, int) or isinstance(current_step, bool) or not 0 <= current_step < 8:
        return {"success": False, "error": "Invalid Spectrum step; sequence unchanged"}
    step = current_step + 1
    if send_emails and not spectrum_sending_enabled():
        return {"success": False, "action": "disabled", "error": "Spectrum sending is disabled"}
    if send_emails and os.environ.get("GFMD_EMAIL_SEND_ENABLED") != "1":
        return {"success": False, "action": "disabled", "error": "Email sending is disabled pending approval"}
    try:
        now = utc_datetime(now or datetime.now(timezone.utc))
        due = utc_datetime(sequence["next_email_due"]) if sequence.get("next_email_due") else None
        last_sent = utc_datetime(sequence["last_email_sent"]) if sequence.get("last_email_sent") else None
    except (ValueError, TypeError, AttributeError):
        return {"success": False, "error": "Invalid Spectrum timestamp; sequence unchanged"}
    attempt = sequence.get("send_attempt") or {}
    if attempt.get("status") in {"pending", "needs_review"} or (attempt.get("status") == "confirmed" and attempt.get("step") == step):
        return {"success": False, "action": "needs_review", "error": "Resolve the previous send attempt before retrying"}
    history = [e for e in sequence.get("emails_sent", []) if e.get("actually_sent") is True]
    if any(e.get("step") == step for e in history):
        return {"success": False, "action": "needs_review", "error": "Step already has a successful send record"}
    if len(history) != step - 1 or {e.get("step") for e in history} != set(range(1, step)):
        return {"success": False, "action": "needs_review", "error": "Successful-send history has gaps; sequence unchanged"}
    if send_emails:
        if not due or due > now:
            return {"success": True, "action": "skipped", "reason": "not_due"}
        # Reconstruction safety window: observed 15:15 UTC anchor through the
        # recovered worker's 18:00 business-hour boundary. No overnight catch-up.
        start_minute = SEND_AT_UTC.hour * 60 + SEND_AT_UTC.minute
        if not BusinessDayCalculator().is_business_day(now) or not (start_minute <= now.hour * 60 + now.minute < 18 * 60):
            return {"success": True, "action": "skipped", "reason": "outside_send_window"}
        if last_sent and (now - last_sent).total_seconds() < 20 * 3600:
            return {"success": True, "action": "skipped", "reason": "too_recent"}
        if worker.gmail.service is None:
            return {"success": False, "error": "Gmail is unavailable; sequence unchanged"}

    email = str(sequence.get("contact_email") or "").strip().lower()
    contact = worker.storage.get_contact_by_email(email)
    if not contact or str(contact.get("_id")) != str(sequence.get("contact_id")) or contact.get("campaign") != "spectrum":
        return {"success": False, "error": "Spectrum contact identity/campaign mismatch"}
    collection = worker.storage.db.email_sequences

    def suppressed():
        # Always consult persisted suppression state, including before transport.
        return contact.get("status") == "suppressed" or worker.storage.db.suppression_list.find_one({"email": email, "status": "active"})

    if suppressed() and not send_emails:
        return {"success": True, "action": "suppressed", "reason": "contact_or_suppression_list"}
    draft = render_spectrum_email(contact, step, history)
    if not send_emails:
        return {"success": True, "action": "preview", "step": step, "draft": draft, "actually_sent": False}

    identity = {"_id": sequence["_id"]} if "_id" in sequence else {"contact_id": sequence["contact_id"], "campaign": "spectrum"}
    owner = uuid4().hex
    locked = collection.find_one_and_update(
        {**identity, "campaign": "spectrum", "status": "active", "reply_received": {"$ne": True},
         "current_step": step - 1, "processing": {"$ne": True},
         "send_attempt.status": {"$nin": ["pending", "needs_review"]}},
        {"$set": {"processing": True, "processing_owner": owner, "processing_started": now.isoformat()}},
        return_document=True,
    )
    if not locked:
        return {"success": True, "action": "skipped", "reason": "concurrent_processing"}
    owned = {**identity, "processing_owner": owner}
    try:
        # The claimed record, not the earlier queue snapshot, is authoritative.
        history = [e for e in locked.get("emails_sent", []) if e.get("actually_sent") is True]
        claimed_attempt = locked.get("send_attempt") or {}
        if claimed_attempt.get("status") == "confirmed" and claimed_attempt.get("step") == step:
            return {"success": False, "action": "needs_review", "error": "Claimed record already confirms this step"}
        if len(history) != step - 1 or {e.get("step") for e in history} != set(range(1, step)):
            return {"success": False, "action": "needs_review", "error": "Claimed send history changed"}
        if not locked.get("next_email_due") or utc_datetime(locked["next_email_due"]) > now:
            return {"success": True, "action": "skipped", "reason": "claimed_record_not_due"}
        if locked.get("last_email_sent") and (now - utc_datetime(locked["last_email_sent"])).total_seconds() < 20 * 3600:
            return {"success": True, "action": "skipped", "reason": "claimed_record_too_recent"}
        contact = worker.storage.get_contact_by_email(email)
        if not contact or str(contact.get("_id")) != str(sequence["contact_id"]) or contact.get("campaign") != "spectrum":
            return {"success": False, "error": "Contact changed after claiming sequence"}
        if suppressed():
            collection.update_one(owned, {"$set": {
                "status": "suppressed", "next_email_due": None,
                "stop_reason": "Contact or active suppression-list entry", "stopped_at": now.isoformat(),
                "updated_at": now.isoformat(),
            }})
            return {"success": True, "action": "suppressed", "reason": "suppressed_after_claim"}
        draft = await worker.email_composer.execute({"prospect_data": contact, "sequence_context": {
            "campaign": "spectrum", "step": step, "previous_emails": history,
        }})
        if not draft.get("success") or not draft.get("ai_generated"):
            return {"success": False, "action": "human_review", "error": "AI composition failed; sequence unchanged"}
        # Generation can take seconds; a reply, suppression, or approval change
        # during that call must still prevent transport.
        latest = collection.find_one(owned)
        contact = worker.storage.get_contact_by_email(email)
        if (not latest or latest.get("status") != "active" or latest.get("reply_received")
                or latest.get("current_step") != step - 1 or not contact
                or str(contact.get("_id")) != str(sequence["contact_id"])
                or contact.get("campaign") != "spectrum" or suppressed()
                or os.environ.get("GFMD_EMAIL_SEND_ENABLED") != "1" or not spectrum_sending_enabled()):
            return {"success": False, "action": "skipped", "reason": "state_changed_during_generation"}
        threading = {}
        if step > 1:
            parent = next((e for e in reversed(history) if e.get("step") == step - 1), None)
            if not parent or not parent.get("gmail_message_id") or not parent.get("gmail_thread_id"):
                return {"success": False, "error": "Missing Gmail thread history; sequence unchanged"}
            headers = worker.gmail.get_message_thread_headers(parent["gmail_message_id"])
            if not headers.get("success") or headers.get("thread_id") != parent["gmail_thread_id"]:
                return {"success": False, "error": "Could not verify parent Gmail thread; sequence unchanged"}
            threading = {"thread_id": headers["thread_id"], "in_reply_to": headers["rfc_message_id"]}
            draft["subject"] = headers["subject"]

        # Persist intent BEFORE transport. A crash/timeout cannot cause a blind retry.
        attempt = {"step": step, "status": "pending", "started_at": now.isoformat(),
                   "rfc_message_id": make_msgid(domain="gfmd.com")}
        if collection.update_one({**owned, "status": "active", "current_step": step - 1,
                                  "reply_received": {"$ne": True}}, {"$set": {"send_attempt": attempt}}).matched_count != 1:
            return {"success": False, "error": "Lost processing claim before send"}
        result = worker.gmail.send_email(
            to_email=email, subject=draft["subject"], body=draft["body"], html_body=draft["html_body"],
            rfc_message_id=attempt["rfc_message_id"], enable_tracking=False, **threading,
        )
        if not result.get("success") or not result.get("message_id") or not result.get("thread_id"):
            collection.update_one(owned, {"$set": {"send_attempt.status": "needs_review"}})
            return {"success": False, "action": "needs_review", "error": "Gmail send was not confirmed; no automatic retry"}

        record = {
            "step": step, "sent_at": now.isoformat(), "subject": result.get("subject") or draft["subject"],
            "body": draft["body"], "template_type": draft["template_type"], "actually_sent": True,
            "gmail_message_id": result["message_id"], "gmail_thread_id": result["thread_id"],
            "rfc_message_id": attempt["rfc_message_id"], "reconstructed": True,
            "ai_generated": True, "model": draft.get("model"),
        }
        completed = step == 8
        due = next_spectrum_due(now, step + 1)
        update = {
            "current_step": step, "emails_sent": [*locked.get("emails_sent", []), record],
            "last_email_sent": now.isoformat(), "next_email_due": due.isoformat() if due else None,
            "status": "completed" if completed else "active", "updated_at": now.isoformat(),
            "send_attempt": {**attempt, "status": "confirmed", "gmail_message_id": result["message_id"]},
        }
        if completed:
            update["completed_at"] = now.isoformat()
        commit = collection.update_one({**owned, "status": "active", "current_step": step - 1}, {"$set": update})
        if commit.matched_count != 1:
            return {"success": False, "action": "needs_review", "error": "Gmail accepted the message but sequence commit failed; reconcile before retrying"}
        return {"success": True, "action": "completed" if completed else "sent", "step": step,
                "actually_sent": True, "gmail_message_id": result["message_id"]}
    except Exception:
        # A persisted pending attempt survives this failure for manual reconciliation.
        return {"success": False, "action": "needs_review", "error": "Spectrum processing failed; inspect send_attempt before retrying"}
    finally:
        collection.update_one(owned, {"$set": {"processing": False}, "$unset": {"processing_owner": ""}})
