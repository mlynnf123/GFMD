# GFMD email automation

Python 3.11 outreach and inbox worker, Next.js dashboard, MongoDB Atlas storage,
Groq composition and Gmail OAuth. This repository includes the recovered deployed
sources and the subsequent Spectrum/Gmail/AI restoration.

Start with [AGENTS.md](AGENTS.md) and
[PRODUCTION_RESTORATION.md](PRODUCTION_RESTORATION.md). Historical assessments are
dated; they do not override the current release record.

## Production

- Dashboard: https://gfmd-dashboard.vercel.app
- Worker: https://gfmd-email-automation-production.up.railway.app/health
- Source provenance: `recovery/deployed-release-manifest.json`.
- Credentials belong in Railway/Vercel environment settings, not GitHub source.
  The dashboard requires `MONGODB_CONNECTION_STRING` or `MONGODB_URI`.

Deployment remains explicit: Railway CLI for the worker and Vercel for the
dashboard. Pushing this repository does not itself run an email campaign. Preserve
the linked service/project identities in the release manifest when deploying.
The production worker was explicitly activated on November 22, 2026. Local/Docker
defaults remain disabled. Do not infer that a new checkout is approved to send.

## Safe local verification

Use Python 3.11 and a virtual environment. Install the runtime dependencies from
`requirements.txt` plus `requirements-test.txt`. The Dockerfiles install the
CPU-only PyTorch build used by the deployed worker.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-test.txt
.\.venv\Scripts\python.exe -X utf8 scripts\verify_worker_runtime.py
.\.venv\Scripts\python.exe -X utf8 preview_spectrum.py
```

The verification runner blocks external connections, removes credentials, uses
in-memory MongoDB and records Gmail MIME locally. No real mail is sent.
Do not run all root `test_*.py` scripts: some are legacy live senders. The old
non-Spectrum `process` dry run can still change database sequence state.

For the dashboard, run in `gfmd-dashboard/`:

```powershell
npm ci
npm run build
npm run lint
```

No production credentials are required to build it. Configure your own isolated
database explicitly before exercising routes that upload or exclude contacts.
Root `src/` is a legacy dashboard copy; `gfmd-dashboard/src/` is the active app.

## Operational boundaries

`health_server.py` performs runtime readiness checks before starting the scheduler.
`GFMD_AUTOMATION_ENABLED=1` enables scheduling; every send separately requires
`GFMD_EMAIL_SEND_ENABLED=1`. Spectrum has additional outreach, enrollment and
automatic-reply opt-ins documented in the release report.

Completed, replied and suppressed campaigns are not automatically restarted.
Spectrum and Narc Gone automatic enrollment remain paused. New uploads may
explicitly start a sequence. Incoming email is untrusted data; opt-outs stop
outreach, temporary absence requires review, and ambiguous send attempts must be
reconciled before retrying.

Automatic replies default to two per contact. Explicitly approved, bounded
exceptions are stored in the private MongoDB `reply_policies` collection, keyed
by normalized email, with `enabled: true`, `approved: true` and an integer
`max_auto_replies` from 2 through 10. Historical replies still count; changing a
limit does not erase history, lift an exclusion, or restart a sequence. Policy
read failures hold automatic responses. Never publish recipient policy records.

Recovery archives, OAuth files, private audit/mailbox reports and machine-specific
Python environments are intentionally excluded. The sanitized release manifest
retains source hashes and deployed identities without those local dependencies.

## Historical credential exposure

The public repository previously contained an embedded database password. Current
source now requires configured credentials and documentation uses placeholders.
Old Git history still contains the previous value; it should be rotated in Atlas
and updated in the hosting environments separately. This sync does not rotate it
or rewrite repository history.
