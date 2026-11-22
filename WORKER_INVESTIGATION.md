# October 14 send stoppage and worker investigation

Updated November 20, 2026, America/Chicago. Production investigation was read-only apart from accepting Railway's Terms of Service and Acceptable Use Policy with the user's explicit approval. Source recovery and a safeguard were prepared locally. No deployment, email send, scheduler start, production record update, service restart, OAuth renewal, commit, or push was performed.

Subsequent local work: the user requested a Spectrum reconstruction. See `SPECTRUM_RECONSTRUCTION.md` for the implemented eight-step worker, exact knowledge-document recovery, date-matched inferred cadence, and offline verification. The recovered Railway snapshot described below remains unmodified in the private recovery directory. Production and the 25 skipped records remain unchanged.

## What is confirmed

### The last batch emptied the active queue

Gmail contains the worker notification `[GFMD] 26 emails about to send`, dated October 14, 2026, 10:15 a.m. Central. Its body states:

```text
About to process 26 due sequence(s) at 2026-10-14 15:15 (server/UTC).
By campaign: spectrum: 26
By step: spectrum step 8: 26
```

MongoDB records show exactly 26 Spectrum sequence updates in that run:

| Result | Count | Time (Central, October 14) |
| --- | ---: | --- |
| Step 8 sent; sequence completed | 1 | 10:15:23 a.m. |
| Sequence completed while still at step 7; no eighth email added | 25 | 10:15:29–10:22:23 a.m. |

The one send was a verified historical recipient, confirmed separately in Gmail Sent Mail with message ID `[private mailbox identifier]`.

For all 25 other sequences:

- `current_step` is still 7 and `status` became `completed`.
- The email history ends at October 7, 2026; there is no October 14 send entry.
- `next_email_due` remains `2026-10-14T15:15:00` rather than being cleared.
- `reply_received` is false in the inspected sample.
- Each completion occurred approximately 107–114 milliseconds after `processing_started`; the actual send took about 4.3 seconds.

The final 25 therefore took a fast completion/skip path, rather than recording failed Gmail sends or adding an eighth email. This is a behavioral inference from persisted timestamps and histories, not identification of the exact deployed code branch.

All 4,222 sequences across all three campaigns are now completed, suppressed, or replied; none are active. Narc Gone's last recorded successful send was May 11 and Centrifuge's was June 29, so Spectrum was the remaining sending campaign. After its final run, no active work remained.

The Railway source recovered on November 20 contains a no-template completion path. An offline reproduction using that exact snapshot and fake storage produces the same field pattern: `completed`, step 7 unchanged, due date unchanged, no send. This establishes a concrete mechanism, but does not prove which process executed the October 14 updates. A targeted Railway log query for October 14, 9 a.m.–noon Central returned no results.

### The Railway scheduler is running, with an empty queue

Direct Railway access now confirms the correct `solutions@gfmd.com` account and `solutions-dotcom's Projects` workspace:

- Project: `gfmd-email-automation`, ID `8b1cca91-5cbd-4153-9c85-062e43fe2171`.
- Service: `2053dc40-bee9-4268-a096-679fc727e905`, production environment `ee5f06cd-bfc9-4089-96bc-68422cb481da`.
- Active deployment: `4cef359f-b579-4517-9edb-a9ae649948b7`, created April 27, 2026, 4:08 p.m. CDT, via CLI `railway up`.
- Online, one replica, EU West. The health endpoint returned HTTP 200 at November 20, 9:18 a.m. CST, with uptime start `2026-04-27T21:17:29.757961`.
- Runtime logs at 8:41 and 9:00 a.m. CST on November 20 show `Running scheduled sequence processing` followed by `Scheduled run: No emails due`. This is direct scheduler evidence beyond the superficial health endpoint.
- A fresh database read at 9:18 a.m. still found all 4,222 sequences terminal and zero active.

The browser console terminal could not establish its WebSocket connection, so a process-list inspection was not completed. Railway's separate Files browser worked and supplied the source snapshot below.

### Gmail authentication is currently broken

The November 20 runtime logs repeatedly show `invalid_grant: Bad Request` during Gmail OAuth token refresh. At 6:00 a.m. CST, the daily scan logged authentication failure and `Gmail service not initialized`, then misleadingly printed a completed scan with zero checked emails. At 7:43 a.m., automatic reply checking also failed token refresh, then reported no new replies.

**Correction to the earlier assessment:** fresh `daily_email_scan` records with zero counts are not evidence of successful inbox access. The November 20 database snapshot includes a record at 9:08:38 a.m. CST, but its presence does not establish a successful Gmail scan. Its provenance is not confirmed: the recovered Railway scheduler schedules its own scan once daily, whereas persisted scan records also appear hourly.

The OAuth failure is confirmed now. The available evidence does not date its onset to October 14 or establish it as the cause of the 25 early completions. Renewing the token has not been attempted because it could enable scheduled replies/sends.

### There are contacts outside the exhausted Spectrum sequence pool

All 315 Spectrum contacts have sequence records. A separate read found 385 contacts without any sequence whose campaign is legacy/default Narc Gone and whose status is `new`. The recovered worker explicitly sets `PAUSED_CAMPAIGNS = {"narc_gone"}`. Its November 20, 8 a.m. runtime logs confirm that Narc Gone auto-enrollment is skipped and Centrifuge has no available contacts. The automatic enrollment map contains only Narc Gone and Centrifuge; Spectrum is absent. The `campaigns` collection has no configuration documents. No contacts were enrolled, reassigned, or resumed.

## Recovered source and remaining version gap

The user approved the Railway agreements, they were accepted, and project access succeeded. The initial unrelated Railway account was not used as GFMD evidence.

Twenty-seven core source/configuration/knowledge files were downloaded from `/app` through Railway's Files browser. The recovered automation file is dated March 24, 2026; its templates and composer include Centrifuge changes from March. Seven existing source/configuration files differed from GitHub, and two Python utilities plus two Centrifuge knowledge documents were missing locally. Those eleven changed/new files are now reconciled into the working tree. Sixteen other downloaded files matched the GitHub checkout after line-ending normalization.

The exact downloads and their SHA-256 hashes are saved privately under `.git/railway-recovery/4cef359f-b579-4517-9edb-a9ae649948b7/` and `manifest.json`. These hashes identify the local downloaded bytes; Railway did not supply independent source hashes. Pre-recovery local files were backed up to `github-python-before-recovery.zip` in the same recovery area. Gmail token and credential files were neither opened nor downloaded.

**This is not the latest Spectrum worker.** The recovered code has no Spectrum template, composition, enrollment, or automatic-reply support and does not contain the `[GFMD] ... emails about to send` notification. Therefore it cannot by itself explain the successful Spectrum sends and batch notification. Another execution environment or a different loaded revision must account for those behaviors; its location and source remain unverified. Interference between an older Railway worker and a newer worker is a plausible explanation for the mixed October 14 result, not a confirmed historical finding.

The current dashboard upload API can create Spectrum sequences, so a working dashboard alone is insufficient evidence that this Railway worker can process them correctly.

## Local safeguard and verification

`complete_sequence_automation.py` now checks the campaign/sequence configuration and next-step template before acquiring a database lock. Unsupported or mismatched configurations and missing templates return an error with no record changes. Unsupported enrollment no longer falls back to Narc Gone. Scheduled processing errors are reported as failures instead of `No emails due`. No Spectrum content or enrollment schedule was invented.

The recovered migration utility contained an embedded database credential fallback. Its working copy requires the explicit `MONGODB_CONNECTION_STRING` environment variable instead; the exact original is retained only in the private recovery snapshot. Neither migration nor cleanup utility was run.

- Eight offline regression tests pass with fake storage and no application constructor, scheduler, Gmail, Groq, or MongoDB connections: `python -X utf8 -m unittest discover -s tests/offline -v`.
- The exact recovered baseline reproduces the unsupported Spectrum completion; the locally guarded version leaves it active with zero writes. Evidence: `.git/railway-recovery/offline-reproduction.json`.
- Eighteen recovered Python files pass syntax compilation. The unchanged legacy `narcon_knowledge_base.py` has a pre-existing syntax error at line 35 (`class Narc GoneKnowledgeBase`); `setup_mongodb_vector_search.py` references it. This was not repaired as part of the worker safeguard.
- Checks ran on local Python 3.14.7 ARM64. Full backend dependencies and the Python 3.11 production runtime were not exercised.
- The `process` command's legacy dry-run behavior still mutates records; do not run it against production. The recovered alternate `Dockerfile.railway` also contains a pre-existing health-server overwrite that needs review before any future build. The active root Dockerfile matches GitHub.

## Current assessment

The immediate reason no sequences are being sent is the empty active queue. Railway is online and its scheduler is running; enrollment is paused for Narc Gone, exhausted for Centrifuge, and unsupported for Spectrum in the recovered version. Gmail OAuth refresh is independently failing now. The unsupported-template completion bug is reproduced and guarded locally, but the exact October 14 execution history and newer Spectrum worker remain unresolved.

Before production resumption: obtain the newer Spectrum worker source from its actual execution environment, reconcile campaign templates and reply behavior, identify all workers touching the shared database, and verify with isolated services. Review the 25 skipped records individually before any explicit decision to requeue them. Gmail reconnection, production changes, deployment, and email sending remain separate future actions; none were performed here.

## November 20 follow-up: locating the missing worker

The user does not know where the newer Spectrum worker ran. Additional read-only checks found:

- The GFMD Railway project lists only the production environment and its one online service; no second environment was found in that project.
- A fresh MongoDB read at approximately 1:02 p.m. CST found 4,121 `daily_email_scan` records. The latest was at 12:09:00 p.m. CST (`2026-11-20T18:09:00.578Z`). The recent timestamps continue hourly, in addition to records at 6:00:08 and 6:01:13 a.m. CST. The recovered Railway scheduler specifies a single daily scan. This timing discrepancy supports an additional scan caller or different loaded configuration, but does not establish its host, number of processes, successful Gmail access, or identity as the Spectrum sender.
- No `hostname`, `host`, `source`, or `worker_id` fields were found in the scan records queried for those fields. The latest 100 records contain only their ID, type, timestamp, and statistics. Spectrum sequence schemas also lack a worker-origin field.
- All five recovered Next.js dashboard API routes lack external HTTP URLs or Gmail/send API calls. The recovered dashboard is not itself the missing Python sending worker.
- A bounded local lookup found no additional GFMD project/archive among the top-level user, Downloads, Documents, ChatGPT, and Claude Code project locations checked. No GFMD/Spectrum Windows scheduled task or matching Python worker was found. Matching Node processes were Codex browser helpers, not evidence of an outreach worker.
- Desktop Commander's only registered device, `MerandasASUS`, is offline. No remote device could be searched for source.

The repository contains an older Google Cloud Run deployment guide, so the GFMD Google Cloud account was checked. The user completed sign-in for `solutions@gfmd.com`, but Google Cloud then blocked Console access pending 2-step verification. Its notice states enforcement began October 20, 2026; this console restriction does not explain the October 14 stop. Cloud Run services, revisions, logs, and deployed source could not be inspected. The user explicitly chose to **leave the Google Cloud check pending**. No 2-step verification setup, account-security change, API enabling, or Cloud deployment was performed.

New evidence under `.git/railway-recovery/`: `worker-origin-clues.json`, `worker-origin-timing.json`, `railway-origin-environment-check.txt`, and `google-cloud-mfa-required.jpg`. Google Cloud and the other computer remain unverified recovery sources.

## Evidence

Private local evidence under `.git/vercel-recovery/`:

- `worker-investigation-database.json`: October 14 transition groups, sample email history, scan records, contact status/enrollment counts.
- `worker-investigation-transitions.json`: all 26 transition timestamps, completion latencies, and per-campaign completion-step distribution.
- `october14-run-notification.json` and `.jpg`: the original 26-sequence step-eight notification in Gmail.
- `worker-refresh-nov20.json`: fresh queue/scan counts and health response.

Additional private evidence under `.git/railway-recovery/`:

- `manifest.json`, deployment source directory, and pre-recovery ZIP backup.
- `nov20-runtime-logs.txt`: scheduler, enrollment, and OAuth failure logs.
- `oct14-log-query.txt`: empty historical query result.
- `railway-online.jpg`: authenticated service view after approved acceptance of terms.
- `offline-reproduction.json` and `syntax-check.json`: local mechanism reproduction and syntax results.

Existing dashboard-recovery changes on `codex/recover-vercel-dashboard` are preserved. Worker recovery, the local safeguard, and tests are uncommitted; no remote branch or production application was changed.
