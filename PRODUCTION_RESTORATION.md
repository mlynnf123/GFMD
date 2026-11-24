# GFMD production restoration — November 22, 2026

The subsequent November 24 worker update is documented in
[REPLY_POLICY_UPDATE.md](REPLY_POLICY_UPDATE.md). Its release manifest and live
verification supersede this dated worker deployment ID and test count.

Deployment and automatic email/reply activation were explicitly approved by the
user. Railway CLI access was restricted to the GFMD workspace and project.

## Dashboard released

Production: https://gfmd-dashboard.vercel.app

Vercel deployment `dpl_EVpRux7BADBddgwT9my2nbydGcgD` is READY, with production
aliases assigned. It contains the recovered source plus six reviewed updates:
confirmed-send totals, last successful send, real worker status, reply review
metrics, completed-versus-customer labels and lint type corrections. Remaining
recovered source matches the Vercel recovery identifiers after line-ending
normalization; generated Next.js files were excluded.

Read-only production API checks passed for all three campaigns. Spectrum now
shows 1,966 confirmed send records and eight repliers instead of step-derived
totals and zero replies. The recorded last send is October 14 at 10:15:23 AM CDT;
the previously verified Gmail acceptance timestamp was one second earlier.
No database records were changed by these dashboard checks.

## Worker released and activated

Railway project: `8b1cca91-5cbd-4153-9c85-062e43fe2171`.
Service: `2053dc40-bee9-4268-a096-679fc727e905`.
Production environment: `ee5f06cd-bfc9-4089-96bc-68422cb481da`.

The 26-file worker release was uploaded through Railway CLI from a clean staging
folder outside OneDrive. Tokens, client secrets, local environments, legacy test
senders, dashboard dependencies and recovery archives were excluded. Source hashes
are recorded under `.git/production-release/worker-manifest.json`.

Initial deployment `1bcf481d-e5e7-4c53-9e9c-b5e6c3c81761` pulled unnecessary GPU
packages. It was superseded by CPU-only release
`d3435c53-c69b-46c0-850b-78d6528bcdd9`, which deployed successfully on Linux,
Python 3.11.18. AI generation and MongoDB reads passed in the deployed container;
the old Gmail token correctly failed while automation and sending stayed disabled.

After that sending lock was verified remotely, the refreshed Gmail token was
installed using standard input to Railway CLI, never a command argument or Git.
The original configuration is backed up in the access-restricted private repair
folder. Token redeployment: `9df337b5-22d7-4ace-b4e6-88ca81ae0c24`.

The token redeployment passed real mailbox identity/inbox, AI generation and
database checks with sending still disabled. Only after that proof, approved
activation settings were applied and the same CPU image was redeployed as
`fbedf128-6a59-4343-b76d-f5d0bd224062`. It is SUCCESS and is the sole active release;
the superseded deployments are REMOVED.

At **12:36 PM CST**, the live endpoint reported a running scheduler subprocess
(no exit code), Gmail identity/inbox reads ready, AI synthetic generation ready,
MongoDB ready, and sending/automation enabled. Startup logs separately confirm
both knowledge-retrieval models loaded, all components initialized with Gmail
connected, and the scheduling loop started. Startup cleanup reset zero stuck
locks and deduplicated zero sequences.

A single approved inbox-processing check was run in the actual production
container through Railway Console. It completed successfully with **zero new
replies**, not an authentication failure. No new emails were sent during these
checks. The dashboard independently returned `automationRunning: true` and
displayed `Running` in the browser.

Automatic inbox checks run every two hours, processing hourly, daily bounce scans
at 12:00 UTC, and weekday contact addition at 14:00 UTC. New Spectrum outreach
retains its reconstructed 15:15–18:00 UTC business-day send window. Older inbox
messages were not bulk-replayed, and a real recipient delivery test was not sent.

The laptop is not required for these running services. Railway and Vercel received
explicit source snapshots rather than GitHub auto-deploys. The subsequent GitHub
sync includes that recovered/restored source, tests, setup guidance and a portable
release manifest. It removes embedded database credential fallbacks from the five
active dashboard routes; Vercel already has the configured connection setting, so
configured runtime behavior is unchanged. Hosting credentials remain in the cloud.

## Behavior and evidence

Every send requires `GFMD_EMAIL_SEND_ENABLED=1`. Spectrum outreach additionally
requires its send opt-in. Approved Spectrum automatic replies require
`GFMD_SPECTRUM_AUTO_REPLY_ENABLED=1`; defaults remain disabled in source images.
Replies still require recorded sender/thread matches, honor opt-outs, exclude
quoted history, retain temporary absence for review, and cap automatic replies at
two per contact. Pending or ambiguous Gmail attempts are held rather than retried.

The health server now checks real Gmail identity/inbox access, MongoDB reads and
synthetic Groq generation before allowing the scheduler to start. Its process
check reports a dead scheduler as unhealthy rather than inventing a heartbeat.
The Railway Dockerfile no longer overwrites the real health server.

Current local validation: 69 Python 3.11 tests passed (41 offline, 28 runtime),
dashboard production build/TypeScript passed, and lint passed with eight existing
warnings and zero errors. Runtime tests used in-memory MongoDB and local Gmail MIME
recorders with external connections blocked.

At 12:29 PM CST, read-only checks found zero active sequences and zero unused,
unsuppressed contacts in both existing Centrifuge and Spectrum pools. Completed,
replied and suppressed records—including the 25 skipped Spectrum contacts—were
not requeued. Automation restoration does not provide a new outreach audience;
new contacts are needed for fresh campaigns. Existing Narc Gone and Spectrum
automatic-enrollment pauses are preserved; explicit new uploads can start sequences.

## Runtime settings and retained evidence

Production now explicitly enables `GFMD_AUTOMATION_ENABLED`,
`GFMD_EMAIL_SEND_ENABLED`, `GFMD_SPECTRUM_SEND_ENABLED`,
`GFMD_SPECTRUM_ENROLLMENT_ENABLED`, and `GFMD_SPECTRUM_AUTO_REPLY_ENABLED`.
`GROQ_MODEL` is `openai/gpt-oss-120b`. Existing credentials remain in Railway's
environment; no token was added to an image or source control. The original
configuration and the candidate token stay in the private local repair folder.

SSH verification was unavailable through this machine's connection, so the
authenticated browser Console was used. The temporary workspace SSH registration
was revoked and its local verification keys removed after that fallback worked.
The approved restricted CLI sign-in remains available for future maintenance.

Non-secret evidence is in `.git/production-release/`: source manifest,
`readiness-before-activation.json`, `health-after-activation.json`, release
verification JSON, `live-inbox-check.jpg` and `dashboard-live-running.jpg`.
The earlier test runner reports remain under `.git/python311-validation/`.

## GitHub source sync

`recovery/deployed-release-manifest.json` records the worker's deployed source
hashes, Vercel source identifiers, cloud project/deployment IDs and verification.
It excludes machine paths, credentials and all mailbox/contact-level audit data.
The runtime dependencies and isolated-test dependency are included so a fresh
checkout can be verified without the original machine's Python environment.

Current source contains no embedded production database password. The old public
Git history still contains the prior value; credential rotation is a separate
remaining security action. This sync does not rotate secrets, replay old messages,
remove exclusions, requeue contacts or redeploy the running services.
