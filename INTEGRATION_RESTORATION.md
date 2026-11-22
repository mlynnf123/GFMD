# Gmail and AI restoration — November 22, 2026

Later November 22: deployment and automatic sending/replies were explicitly
authorized. See `PRODUCTION_RESTORATION.md` for the cloud release record. The
report below describes the earlier local-only verification checkpoint.

Local repair verified; production is unchanged. No emails were sent, no scheduler
was started, and no production records or credentials were modified. Work remains
uncommitted on `codex/recover-vercel-dashboard` alongside the previous recovery.

## Verified live

- Reauthorized the existing GFMD Email Client for `solutions@gfmd.com`, using its
  existing Gmail read/send scopes. A **separate local candidate token** passed a
  real refresh, mailbox identity check and application inbox/reply parsing.
- Parsed ten real inbox messages; none of those ten was classified as a reply.
  This bounded sample does not establish that there is no older reply backlog.
- The newest Sent message remains **October 14, 2026, 10:15:22 AM CDT**
  (`2026-10-14T15:15:22Z`). Gmail acceptance does not prove recipient delivery or
  rule out a subsequent bounce.
- The old `llama-3.3-70b-versatile` returned `NotFoundError` using the existing Groq
  key. Groq's authenticated model list showed `openai/gpt-oss-120b` active. Updated
  the local default and verified real generation of all eight Spectrum steps, a
  pricing reply, and both Narc Gone/Centrifuge outreach and reply agents.
- All model tests used fictional contacts and messages. No real inbox content was
  submitted to Groq. A synthetic instruction-injection message was held for review.

The OAuth client, candidate token and existing Groq key are in the access-restricted
`%LOCALAPPDATA%\GFMD\integration-repair` folder, outside OneDrive and Git. Railway
files and variables were not changed. Do not copy the token to production before
the sending lock is deployed and verified. Reauthorization fixes access but does
not identify the original `invalid_grant` cause or guarantee indefinite validity.

## Local changes

`spectrum_ai.py` uses bounded, tool-free Groq generation with a curated subset of
recovered product facts and the eight inferred topics. Recipients, threading,
subject handling and signatures stay application-owned. Output must pass JSON and
content-shape checks; HTML is escaped. AI failures produce no fallback send.
`preview_spectrum.py` remains a deterministic, fully offline preview.

Spectrum reply handling verifies sender and successful-send thread before writes,
analyzes only new reply text, respects opt-outs and keeps temporary absence for
review. Valid replies stop follow-ups and store one review item per Gmail message.
AI drafts persist idempotently. Spectrum replies are **always review-only**:
restoring the missing historical automatic-reply policy requires a separate choice.

Narc Gone and Centrifuge use the active model too. Removed canned fallback success
on AI failure, reduced instructions encouraging invented prospect research, added
plain-text signatures, and corrected RFC Message-ID threading. Generic replies must
match recorded outreach threads; with sending disabled, their drafts are queued
and follow-ups stop. Repeated queued replies do not regenerate drafts.

Gmail failures now raise errors instead of reporting an empty inbox or logging a
successful zero-check scan. Reporting separates actual sends from review items.
The daily Spectrum scanner verifies threads and strips quoted opt-out wording.

`GFMD_EMAIL_SEND_ENABLED=1` is now required at the Gmail transport boundary for
**all campaigns and replies**, and before sequence processing changes state. It
was not enabled in a real process or remote environment. Spectrum's separate send
and enrollment opt-ins remain disabled; automatic enrollment remains paused. The
25 skipped contacts were not requeued. Never start `health_server.py` to test this.

`GmailIntegration` supports explicit token/client paths or `GMAIL_TOKEN_PATH` and
`GMAIL_CREDENTIALS_PATH`. `scripts/repair_gmail_auth.py` creates a local candidate
only, verifies the mailbox/refresh, and never starts a worker or sends mail.
`GROQ_MODEL` can override the base agent's default. Request compatibility was checked
against the [Groq API reference](https://console.groq.com/docs/api-reference) and
[model documentation](https://console.groq.com/docs/model/openai/gpt-oss-120b).

## Queue and verification

A read-only production check at **10:25 AM CST on November 22** found 4,222 terminal
sequences and **zero active sequences**:

| Campaign | Completed | Replied | Suppressed |
| --- | ---: | ---: | ---: |
| Legacy Narc Gone (campaign absent) | 411 | 40 | 73 |
| Centrifuge | 2,739 | 60 | 584 |
| Spectrum | 231 | 8 | 76 |

Authentication alone will not restart outreach. A campaign and recipient/enrollment
plan must be approved; do not reset completed campaigns.

Python **3.11.18**: **41 offline + 21 real-module integration tests passed** with
external networking blocked, credentials removed, in-memory MongoDB and a local
Gmail MIME recorder. This includes eight-step progression, AI failure, suppression,
threading, quoted history, temporary absence, duplicate draft prevention, ambiguous
sends, sending locked despite authenticated Gmail, a reply during generation, and
failed scans not being logged as successful.

```powershell
.\.git\python311-venv\Scripts\python.exe -X utf8 scripts\verify_worker_runtime.py
```

Evidence: `.git/integration-restoration/gmail-auth-status.json`,
`live-verification.json`, `ai-sample-drafts.md`, and `gmail-local-authorized.jpg`.
Isolated suite results remain under `.git/python311-validation/`.

## Approval steps remaining

1. Review the actual AI drafts and reply behavior. Output checks cannot establish
   every factual claim; the examples need business review before use.
2. Approve deployment **with sending and enrollment disabled**.
3. Once that deployment is verified, approve installing the candidate OAuth token
   in the correct Railway service and verify read-only runtime Gmail/AI operation.
4. Review any older inbox backlog, approve recipients/campaigns and reply policy,
   then separately approve sending activation.

The original missing Spectrum source and other-computer changes remain unrecovered.
Dashboard code/deployment were not changed. The deployed Linux image, production
inbox-processing writes, automatic replies and actual sending remain unverified
and inactive pending approval. Live Gmail and AI checks were separate adapter
checks, not a deployed end-to-end delivery test.
