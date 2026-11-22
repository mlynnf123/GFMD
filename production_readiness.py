"""Read-only runtime checks; safe before enabling the scheduler or sending."""
import asyncio
from datetime import datetime, timezone
import json
import os
import platform


def check_readiness():
    checks = {}
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
              "release": os.environ.get("GFMD_RELEASE_ID", "unknown"), "checks": checks,
              "sending_enabled": os.environ.get("GFMD_EMAIL_SEND_ENABLED") == "1",
              "automation_enabled": os.environ.get("GFMD_AUTOMATION_ENABLED") == "1"}
    try:
        from gmail_integration import GmailIntegration
        gmail = GmailIntegration()
        if gmail.service is None:
            raise RuntimeError("Gmail authentication unavailable")
        profile = gmail.service.users().getProfile(userId="me").execute()
        if profile.get("emailAddress", "").lower() != "solutions@gfmd.com":
            raise ValueError("Mailbox identity mismatch")
        gmail.get_emails(max_results=1)
        checks["gmail"] = {"ready": True, "identity_verified": True, "inbox_read_verified": True}
    except Exception as error:
        checks["gmail"] = {"ready": False, "error_type": type(error).__name__}
    client = None
    try:
        from pymongo import MongoClient
        uri = os.environ.get("MONGODB_URI") or os.environ.get("MONGODB_CONNECTION_STRING")
        if not uri:
            raise ValueError("Database configuration missing")
        client = MongoClient(uri, serverSelectionTimeoutMS=15000, connectTimeoutMS=10000)
        client.admin.command("ping")
        active = client.gfmd_narc_gone.email_sequences.count_documents({"status": "active"})
        checks["database"] = {"ready": True, "active_sequences": active}
    except Exception as error:
        checks["database"] = {"ready": False, "error_type": type(error).__name__}
    finally:
        if client:
            client.close()
    ai = None
    try:
        from groq import Groq
        from spectrum_ai import generate_spectrum_draft
        ai = Groq(api_key=os.environ.get("GROQ_API_KEY"), timeout=30, max_retries=0)
        model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
        draft = asyncio.run(generate_spectrum_draft(ai, {"name": "Example", "organization": "Synthetic Care Facility"}, model=model))
        checks["ai"] = {"ready": draft.get("success") is True, "model": model, "synthetic_draft_verified": draft.get("ai_generated") is True}
    except Exception as error:
        checks["ai"] = {"ready": False, "error_type": type(error).__name__}
    finally:
        if ai:
            ai.close()
    report["ready"] = all(check.get("ready") for check in checks.values())
    report["status"] = "ready" if report["ready"] else "failed"
    return report


if __name__ == "__main__":
    result = check_readiness()
    print(json.dumps(result))
    raise SystemExit(0 if result["ready"] else 1)
