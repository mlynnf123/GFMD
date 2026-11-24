# Automatic reply update — November 24, 2026

Railway worker deployment `58c41a2e-720b-4f9c-998a-7628bfa8b320` is SUCCESS.
The live health endpoint identifies `2026-11-24-reply-policy`, Python 3.11.18,
a running scheduler, enabled sending, and successful fresh Gmail identity/inbox,
MongoDB and synthetic AI generation checks. The dashboard deployment is unchanged.

Automatic replies still default to two per contact. Approved individual exceptions
are stored in MongoDB `reply_policies`, keyed by normalized email, with
`enabled: true`, `approved: true` and integer `max_auto_replies` between 2 and 10.
The limit is a total including historical automatic replies. Policy lookup failure
holds responses. Incoming emails and contact uploads cannot grant an exception.
Existing suppression, sender/thread validation and send opt-ins still apply.

The daily suppression scan now removes quoted history for all campaigns before
analyzing a human reply. Genuine newly authored opt-outs still stop outreach.
System bounce processing and Spectrum thread validation are preserved.

Recipient-specific corrections and policy approvals remain private in MongoDB and
the excluded audit folder. False-positive exclusions were archived before repair;
a verified historical sent message supplied missing thread metadata. A newly
received genuine decline remains excluded. No stopped outreach sequence was
restarted, and the repair did not send test or additional campaign messages.

Python 3.11 verification passed 41 offline and 32 real-module integration tests.
New coverage checks per-contact approval, invalid limits and policy read failures,
two additional automatic responses with historical sends preserved, and quoted
history versus a genuine new opt-out in the daily non-Spectrum scan. External
networking was blocked, credentials removed, and Gmail/MongoDB were isolated.

Deployment used the same 26-file allowlist as the restoration release. Only
`ai_auto_reply_system.py` and `email_reply_monitor.py` changed in the worker image.
`recovery/deployed-release-manifest.json` records the new hashes and deployment.
The production inbox monitor retains its two-hour polling interval; a health
check or synthetic draft is not proof that a future recipient reply was delivered
or answered. Confirm real Gmail acceptance and persisted send records when one
arrives. Do not replay old conversations to manufacture that evidence.
