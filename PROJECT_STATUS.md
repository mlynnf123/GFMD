# GFMD project assessment

Recorded November 18, 2026, America/Chicago. This is a point-in-time assessment, not a live status feed.

**Follow-up:** The newer Vercel dashboard has since been recovered locally on `codex/recover-vercel-dashboard`. See `RECOVERY_AND_PULSE_CHECK.md` for hash verification, live database/frontend observations, and the latest recorded successful email. The findings below describe the earlier January GitHub snapshot and have not all been re-applied to the recovered source.

## Repository and deployment history

- Repository: https://github.com/mlynnf123/GFMD
- Local branch: `main`, tracking `origin/main`.
- Latest GitHub commit verified against remote HEAD: `f008dcbca5c0aacfea5bce940118d1c215b2823e`.
- Commit author and committer: Meranda Freiner.
- Author/commit timestamp: January 29, 2026, 1:19:21 a.m. CST.
- Subject: `Remove subtext from Total Emails Sent KPI`.
- The checkout has 27 commits, beginning October 31, 2025. Only the remote `main` branch was present.
- Recent January work addressed CSV uploading, reply-rate statistics, bounce detection, suppression, and automatic replies.

### Newer deployed dashboard source exists

The connected Vercel account has project `gfmd-dashboard`.

- Latest listed production deployment: `dpl_D2eXbimVDqQvQ8NVhecjgsakpUoK`.
- Created August 25, 2026, 8:18:31 p.m. CDT.
- Platform state: `READY`; source: `cli`; no Git SHA supplied in the returned deployment metadata.
- Alias: https://gfmd-dashboard.vercel.app
- Inspection: https://vercel.com/mlynnf123s-projects/gfmd-dashboard/D2eXbimVDqQvQ8NVhecjgsakpUoK
- Vercel Authentication protection is enabled for `all_except_custom_domains`; password protection is disabled.

The complete returned deployment file inventory includes five application files absent from this checkout:

```text
src/components/centrifuge-dashboard.tsx
src/components/nav-header.tsx
src/components/spectrum-dashboard.tsx
src/app/centrifuge/page.tsx
src/app/spectrum/page.tsx
```

These paths are relative to the deployed dashboard source root; Vercel prefixes that root with another `src/` in its file inventory. The navigation source labels the three areas `Narc Gone`, `Silencer Centrifuge`, and `Spectrum dx`. Retrieved component excerpts request campaign-specific dashboard data for `centrifuge` and `spectrum`. Their complete functionality was not verified.

The deployed `package.json` specifies Next.js `^16.2.4`; GitHub specifies `16.0.10`. After normalizing local CRLF line endings to LF, comparison of local SHA-1 content hashes with deployment file UIDs found differences in 16 existing dashboard files: the package manifest/lockfile, app layout, five API route files, and eight components. Nineteen existing files matched. Generated `tsconfig.tsbuildinfo` also exists in the deployment and was absent locally before assessment.

This confirms that GitHub is missing newer dashboard work. It does not establish which other changes remain only on another computer, or what Python source is deployed to Railway. Some Vercel source-content responses were truncated; no complete deployment-source recovery or merge was performed.

## What the application does

The GitHub version is an outreach and monitoring system for GFMD's Narc Gone products, targeting law enforcement property and evidence contacts. Despite the historical "AI swarm" name, the active entry point is a scheduled Python service using specialized email-composition and reply agents.

```text
CSV / contact import
        |
        v
MongoDB contacts + email_sequences
        |
        v
Python scheduler -> Groq composition + knowledge retrieval -> Gmail
        ^                                                    |
        |                                                    v
Sequence / suppression updates <- reply and bounce processing

Next.js browser UI <-> Next.js API routes <-> the same MongoDB database
```

The dashboard accesses MongoDB directly through server-side API routes. Its main data path does not request data from the Railway health service.

### Code map

| Location | Role |
| --- | --- |
| `health_server.py` | Flask endpoints and launch of the scheduler subprocess |
| `complete_sequence_automation.py` | Enrollment, due-sequence processing, scheduling, daily scans |
| `email_sequence_templates.py` | Six-step Narc Gone sequence definitions |
| `groq_email_composer_agent.py`, `groq_base_agent.py` | Groq composition; default model `llama-3.3-70b-versatile` |
| `gmail_integration.py` | OAuth, Gmail sends, inbox reads, message parsing |
| `ai_auto_reply_system.py` | Reply filtering, AI responses, two-response cap per address |
| `email_reply_monitor.py`, `suppression_integration.py` | Bounce/opt-out analysis and suppression records |
| `mongodb_storage.py` | Database operations and index creation |
| `vector_rag_system.py` | Sentence-transformer embeddings and knowledge retrieval |
| `knowledge_base/` | Two checked-in knowledge Markdown files |
| `gfmd_documents/` | Contains only a README in this checkout |
| `gfmd-dashboard/` | Runnable Next.js/React/TypeScript/Tailwind/Recharts app |
| root `src/` | Older duplicate UI source, outside the runnable dashboard project |
| `removed_files_backup/` | 35 legacy files |

Relevant MongoDB collections include `contacts`, `email_sequences`, `interactions`, `suppression_list`, `orders`, `campaigns`, `system_logs`, `knowledge_vectors`, and `document_embeddings`.

### Dashboard workflow in GitHub

- Poll statistics every 30 seconds.
- Display active sequences, reply rate, total sent, bounce and suppression counts, charts, and recent contacts.
- Open sequence and per-contact email-history dialogs.
- Import CSV contacts with duplicate handling and optional immediate sequence enrollment.
- Add or deactivate suppression records; adding suppression also stops matching active sequences.

## Scheduling as implemented in GitHub

The scheduler uses process-local clock times with comments assuming a UTC server and fixed CST offsets:

| Job | Configured schedule |
| --- | --- |
| Process due sequences | Every hour, plus 15:00, 19:00, 23:00 |
| Enroll contacts | Monday-Friday at 14:00; 10 contacts per run |
| AI reply check | Every two hours |
| Bounce/reply/suppression scan | Daily at 12:00; scans the previous seven days |

The intended fixed-CST equivalents are 9 a.m./1 p.m./5 p.m. processing, 8 a.m. enrollment, and 6 a.m. scanning. The implementation has no explicit America/Chicago timezone or daylight-saving handling. Actual Railway process timezone was not inspected.

Templates store `wait_days` as 0, 2, 4, 6, 8, 10, but processing adds each next value to the time of the preceding send. This produces successive nominal waits of 2, 4, 6, 8, and 10 business days, rather than a uniform two-day interval. An isolated step-two probe confirmed the next wait is four business days.

The business-day helper excludes weekends and four fixed holiday dates. Floating holidays are listed but not calculated. The send path does not enforce a business-hours check when selecting and sending due emails; the helper is used to schedule a later due date.

## Verification performed on this computer

| Check | Result |
| --- | --- |
| Remote `main` vs local HEAD | Match at `f008dcb` |
| `npm ci --no-audit --no-fund` | Passed; 406 packages installed |
| `npm run build` in `gfmd-dashboard/` | Passed compilation, TypeScript, and production build |
| `npm run lint` | Failed: 3 errors, 8 warnings |
| AST syntax scan of 32 root Python files | 31 parsed; `narcon_knowledge_base.py:35` has invalid class syntax |
| Isolated sequence-method probe with fake clients | Confirmed dry-run state update and increasing follow-up interval |
| Railway `/health` HTTP GET | HTTP 200; reports healthy/running |
| Vercel deployment metadata and file inventory | Confirmed newer CLI deployment and source divergence |

The offline probe extracted the method definition without importing application modules and used fake storage, composer, and Gmail objects. It sent no messages and made no database requests. With sending disabled, it still recorded one sequence update, advanced the step, returned action `sent`, and recorded `actually_sent: false`.

No live MongoDB query, Gmail authentication, AI generation, real email send, browser flow, or full backend startup was performed. The integration scripts named `test_*.py` were inspected rather than executed because some perform real sends or reply processing. No deployment or Git commit/push was performed.

## Findings requiring attention

1. **Source reconciliation:** the GitHub checkout cannot reproduce the latest deployed dashboard. Preserve the newer deployment and reconcile it with the other computer before preparing a replacement release.
2. **Exposed database credentials:** credential-bearing MongoDB fallback URIs are committed in all five dashboard API routes and the old root API route. A Railway setup document also includes credentials. Their validity was not tested and values are intentionally omitted here. Replace hardcoded fallbacks with environment configuration and rotate the exposed credentials; removing current text alone does not remove Git history.
3. **Dry run changes records:** `process` without `send` advances sequence state and contributes to the dashboard's step-based sent total. Missing Gmail service also follows that state-update path.
4. **Suppression is incomplete in the main send flow:** the due-send method does not perform a final suppression/reply check; automatic enrollment excludes only active/completed sequence records, allowing suppressed/replied contacts to be selected and their state replaced. The separately implemented suppression pre-send helper is not called by this main path.
5. **Timing differs from intent:** increasing wait intervals, timezone assumptions, partial holiday support, and lack of a send-time business-hours guard need reconciliation.
6. **Metrics need verification:** sent totals sum `current_step`; reply rate counts senders with recorded AI responses rather than all incoming replies; daily reply queries use Date boundaries although auto-reply timestamps are ISO strings. The API marks every successful DB response `automationRunning: true` and sets last-contact-addition to the current time. It also maps a completed outreach sequence to `Customer` without an order check.
7. **Health is superficial:** Flask's status thread unconditionally sets `running`, without checking scheduler subprocess health. HTTP 200 proves endpoint availability, not recent mail processing. The response's reported uptime began April 27, 2026, but that is application-reported, not an independent process audit.
8. **Incoming-reply scope:** reply detection accepts inbox messages with an In-Reply-To header or `Re:` subject without verifying they match a tracked campaign. Unknown senders can reach AI response generation, and message-ID deduplication is only in memory. The two-response cap is persisted through successful response records.
9. **Local quality/setup gaps:** lint failures, one broken knowledge-base module referenced by the vector setup script, no configured automated test runner/CI, and production/local Python version differences remain.
10. **Stale and conflicting guidance:** docs cite 20 enrollments/day, old contact counts, Next.js 14, older Google Cloud deployments, and an absent `run_campaign.py`. Those statements do not prove current operation. `Dockerfile.railway` also overwrites the real health server with an invalid one-line Python script; which Dockerfile Railway actually uses remains unverified.

The dashboard source has no application-level authentication checks in its API handlers. Vercel project-level protection is currently configured as described above; its coverage should be accounted for before exposing another deployment or custom domain.

## Local setup state and working process

The Git repository is connected and dashboard dependencies/build output are installed locally. This assessment adds only `AGENTS.md` and this report to tracked-source candidates; application code is unchanged.

This machine has Node 24.22.1, npm 11.19.1, and Python 3.14.7 ARM64. The production Dockerfile uses Python 3.11. Railway CLI and Docker were not found on PATH. No local Python virtual environment or backend dependency installation was created during assessment.

No root `.env`, Gmail credentials/token JSON files, or dashboard `.env.local` exist locally. The relevant MongoDB, Groq, and Gmail environment variables were absent from this process. Because committed dashboard fallbacks exist, missing environment configuration does not guarantee production isolation.

For local dashboard work, use `gfmd-dashboard/` and configure an explicitly isolated MongoDB connection before starting the browser app. For backend runtime setup, align with the container's Python version and supply credentials securely, then verify against isolated services. Starting the health server or scheduler is an operational action capable of sending mail.

The first continuation task is to reconcile the newer Vercel source and any unpushed work from the other computer, then establish a single reproducible source baseline. The Railway worker's deployed version and recent successful job activity still require authenticated Railway inspection. Existing documentation's historical contact counts and send volumes were not verified against live data.
