"""Create and verify a LOCAL Gmail authorization candidate; never send or deploy."""

import argparse
import contextlib
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.readonly"]
ROOT = Path(__file__).resolve().parents[1]


class PrivateAuthorizationURL:
    def __init__(self, path):
        self.path, self.pending = path, ""

    def write(self, text):
        self.pending += text
        while "\n" in self.pending:
            line, self.pending = self.pending.split("\n", 1)
            if line.startswith("https://accounts.google.com/"):
                self.path.write_text(line, encoding="utf-8")
                sys.__stdout__.write("Google authorization is ready in the private local folder.\n")
                sys.__stdout__.flush()
        return len(text)

    def flush(self):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", type=Path)
    parser.add_argument("--expected-email", default="solutions@gfmd.com")
    args = parser.parse_args()
    private = Path(os.environ["LOCALAPPDATA"]) / "GFMD" / "integration-repair"
    private.mkdir(parents=True, exist_ok=True)
    client_path = args.client or private / "gmail_credentials.json"
    report_path = ROOT / ".git" / "integration-restoration" / "gmail-auth-status.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "success": False, "production_updated": False, "emails_sent": 0}
    try:
        if not client_path.is_file():
            raise ValueError("OAuth client configuration is missing")
        flow = InstalledAppFlow.from_client_secrets_file(str(client_path), SCOPES, autogenerate_code_verifier=True)
        with contextlib.redirect_stdout(PrivateAuthorizationURL(private / "authorization-url.txt")):
            credentials = flow.run_local_server(
                host="localhost", bind_addr="127.0.0.1", port=0, open_browser=False,
                authorization_prompt_message="{url}", timeout_seconds=1200,
                success_message="GFMD local authorization received. No emails were sent. You may close this window.",
                access_type="offline", prompt="consent", login_hint=args.expected_email,
            )
        if not credentials.refresh_token:
            raise ValueError("Google did not return an offline refresh token")
        credentials.refresh(Request())
        service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
        profile = service.users().getProfile(userId="me").execute()
        email = profile.get("emailAddress", "").lower()
        if email != args.expected_email.lower():
            raise ValueError("Authorized mailbox does not match the expected GFMD account")
        messages = service.users().messages().list(userId="me", q="in:inbox", maxResults=5).execute()
        candidate = private / "gmail_token.candidate.json"
        if candidate.exists():
            backup = private / ("gmail_token.candidate." + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + ".json")
            backup.write_bytes(candidate.read_bytes())
        temporary = private / "gmail_token.candidate.tmp"
        temporary.write_text(credentials.to_json(), encoding="utf-8")
        temporary.replace(candidate)
        report.update(success=True, email=email, refresh_verified=True, inbox_read_verified=True,
                      inbox_sample_count=len(messages.get("messages", [])), scopes=SCOPES,
                      candidate_saved_locally=True, checked_at=datetime.now(timezone.utc).isoformat())
        print("Verified local Gmail authorization and inbox read for " + email + ". No emails sent; production unchanged.")
    except Exception as error:
        # Never print Google responses, authorization codes, tokens, or secrets.
        report.update(error_type=type(error).__name__, message="Local Gmail authorization was not completed; production unchanged")
        print(report["message"])
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
