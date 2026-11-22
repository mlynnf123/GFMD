# Dashboard recovery and operational pulse check

November 22 update: see `INTEGRATION_RESTORATION.md` for the verified separate local
Gmail candidate, real AI generation, current queue check and approval boundaries.
Those were pre-deployment checks. See `PRODUCTION_RESTORATION.md` for the later
authorized deployment, credential repair and activation. Earlier findings below are dated.

Checked November 18, 2026, America/Chicago; Gmail verification completed after the user signed in that evening. Repository branch: `codex/recover-vercel-dashboard`.

November 20 follow-up: see `WORKER_INVESTIGATION.md` for authenticated Railway inspection, recovered March worker source, confirmed current Gmail OAuth failure, the reproduced unsupported-template completion bug, and the local safeguard. Railway access is resolved. The newer Spectrum worker source remains missing, and zero-count mailbox scans must not be interpreted as successful Gmail access.

Subsequent reconstruction: `SPECTRUM_RECONSTRUCTION.md` documents the local eight-step Spectrum worker built from persisted sends and recovered knowledge documents. The original missing source is still unlocated. Sending/enrollment are disabled by default, replies require human review, and no production changes were made.

## Recovery result

The latest listed Vercel production dashboard deployment was recovered into `gfmd-dashboard/`:

- Deployment: `dpl_D2eXbimVDqQvQ8NVhecjgsakpUoK`.
- Created: August 25, 2026, 8:18:31 p.m. CDT; source: CLI.
- Live alias: https://gfmd-dashboard.vercel.app
- Source inspection: https://vercel.com/mlynnf123s-projects/gfmd-dashboard/D2eXbimVDqQvQ8NVhecjgsakpUoK/source
- 39 application/configuration/assets files verified against Vercel's SHA-1 source file identifiers. Identical local text was normalized to LF and verified; differing/missing files and the complete lockfile were retrieved through the authenticated browser's Vercel source responses and hash-verified before writing.
- The working copy contains 16 modified existing application files and five added application files. Eighteen unchanged files retain native checkout line endings; all 39 file contents match the deployment when text line endings are normalized. The saved deployment snapshot preserves the exact hash-verified bytes.
- Generated `next-env.d.ts` and `tsconfig.tsbuildinfo` were excluded from source restoration; Next.js regenerates them locally.
- Added pages/components: `/centrifuge`, `/spectrum`, and shared campaign navigation.
- Restored changes in all five API routes, eight existing components, layout, package manifest, and lockfile. Next.js now resolves to 16.2.4.
- Original GitHub dashboard backup: `.git/vercel-recovery/github-dashboard-before-recovery.zip`.
- Verified deployment snapshot: `.git/vercel-recovery/dpl_D2eXbimVDqQvQ8NVhecjgsakpUoK/`.
- File inventory and verification: `.git/vercel-recovery/manifest.json` and `recovery-verification.json`.

No tracked local application edits existed before restoration. The earlier assessment documents were preserved. No Python code, remote repository, deployment, email, or production record was changed. This restores the newer dashboard; it does not recover the newer Railway worker source, which clearly has behavior/data fields absent from the January GitHub Python snapshot.

## Local verification

| Check | Result |
| --- | --- |
| `npm ci --no-audit --no-fund` | Passed |
| `npm run build` | Passed: Next.js 16.2.4, TypeScript, and all three dashboard pages |
| `npm run lint` | Existing recovered-source failures: 3 errors and 9 warnings |
| Browser navigation | Recovered Narc Gone, Centrifuge, and Spectrum pages render with live database data |
| Dashboard GET APIs | HTTP 200 for all three campaigns |
| Contact-history GET | HTTP 200; latest successful Spectrum send includes Gmail identifiers |
| Active-sequence GET | HTTP 200; no active Spectrum sequences |
| Live frontend | All three campaign pages and contact-history dialogs inspected |

Only read-only browser actions and database/API reads were used for the pulse check. Upload, exclusion edits, scheduler startup, send scripts, deployment, and remote pushes were not executed. Local build and runtime checks used the recovered dashboard without changing its source to fix historical issues, preserving exact source provenance.

## Current campaign state

MongoDB `gfmd_narc_gone.email_sequences` contains 4,222 sequences:

| Campaign | Total | Active | Completed | Replied | Suppressed |
| --- | ---: | ---: | ---: | ---: | ---: |
| Narc Gone | 524 | 0 | 411 | 40 | 73 |
| Silencer Centrifuge | 3,383 | 0 | 2,739 | 60 | 584 |
| Spectrum dx | 315 | 0 | 231 | 8 | 76 |

All sequences are in terminal statuses. There are no currently active sequences to send. A completed sequence is an outreach status, not proof of a sale or of successful delivery of every step. Some Spectrum sequences are marked completed at step 7 of 8 with a remaining due date; the deployed Python source is needed to explain that transition.

The latest inspected persisted mailbox scan ran November 18, 2026, at **8:03:43 p.m. CST** (`2026-11-19T02:03:43.999Z`). It checked two messages and recorded no new bounces, suppressions, or newly replied sequences. The preceding two scan records were one hour apart. This is evidence of recent scanning activity, independent of the dashboard's hardcoded status banner.

## Latest successful-send evidence

The latest email entry across all campaigns with `actually_sent: true` and a stored Gmail message ID is:

- Recipient: a verified historical recipient (identity retained privately).
- Campaign: Spectrum dx, step 8.
- Stored timestamp: **October 14, 2026, `15:15:23.320465`**.
- Subject: `Same-day PCR for UTI, C. auris, CRE & mpox screening`.
- Gmail message ID: `[private mailbox identifier]`.
- Gmail thread ID: `[private mailbox identifier]`.
- `actually_sent: true`; sequence status `completed`; no suppression-list record for this recipient.

The timestamp string omits a timezone. Subsequent direct Gmail verification confirmed this exact message in Sent Mail as **October 14, 2026, at 10:15 a.m. Central (CDT)**, corresponding to 15:15 UTC. Its rendered Gmail message ID is `[private mailbox identifier]`, exactly matching the database record. The current frontend parses the stored offset-free timestamp as browser-local time, so it can display the send five hours later than Gmail on that date. Dates/times in the table below are the stored values, not corrected mailbox-local times.

| Campaign | Latest recorded successful send | Recipient |
| --- | --- | --- |
| Narc Gone | May 11, 2026, 12:06:06 (stored time) | Private historical recipient |
| Silencer Centrifuge | June 29, 2026, 16:15:27 (stored time) | Private historical recipient |
| Spectrum dx | October 14, 2026, 15:15:23 (stored time) | Private historical recipient |

These are successful-send records with Gmail IDs, not inferred from step counters or draft entries. After the user signed into `solutions@gfmd.com`, the latest message was independently verified in Gmail's Sent folder, at the top of the folder, with the matching message ID, recipient, and content. Gmail's actual message subject includes the `Re:` prefix. An all-mail search, including Spam and Trash, after October 13 for this recipient and common mailer-daemon/postmaster/delivery-failure indicators returned `No messages matched your search.` This confirms an actual sent message with no matching failure notice found; it does not constitute a recipient delivery receipt. The earlier per-campaign sends were not individually opened in Gmail during this follow-up.

Mailbox screenshots and message identifiers are retained in the private recovery archive and are not published here.

## What the frontend currently shows

The live Spectrum page's first recent-activity row is a different historical contact (identity retained privately). It shows `Step 7 of 8`, `42 days ago`, and `Customer`. Opening its history shows the latest email as **October 7, 2026**, `15:24:32`, marked `Sent`.

That sequence was last updated on **October 14, 2026**, `15:22:23.446625`, when it became completed. It sorts ahead of the actual October 14 send because `dashboard-data/route.ts` sorts recent sequences by `updated_at`, then displays the last email within each selected sequence. The recent-activity table therefore does not reliably show the newest email sent.

The header's `Last updated` is the browser's most recent data refresh. It is not the last email time, deployment time, or last scheduler run. The server supplies `automationRunning: true` and a new `lastContactAddition` timestamp whenever its database query succeeds. The banner says `Active and processing sequences` even while all three active counts are zero.

## Metrics needing correction

| Campaign | Frontend Total Emails Sent | Email entries marked actually sent | Entries marked not actually sent |
| --- | ---: | ---: | ---: |
| Narc Gone | 2,734 | 2,687 | 48 |
| Silencer Centrifuge | 15,667 | 12,575 | 3,092 |
| Spectrum dx | 1,967 | 1,966 | 1 |

The frontend sums `current_step`; it does not count successful-send records. The Narc Gone history/step totals also differ by one, demonstrating that step totals are not a delivery ledger. A send entry marked actually sent can still subsequently bounce, so even the middle column is not a delivered-email count.

Other observed issues:

- `completed` is displayed as `Customer` without evidence of a sale.
- Spectrum has eight sequences marked `replied`, but its frontend reply count is zero because that KPI counts matching interaction records rather than sequence status.
- The recovered version counts historical `auto_reply` and newer `escalation` interaction types; its comments describe human replies forwarded to Lisa. This is newer than the Python code in GitHub.
- The recovered version intentionally removes open-rate and revenue displays because the former had no functioning tracking and the latter had no order-data source. Earlier assessment findings about those displays describe the old GitHub snapshot.
- The live chart's date labels and scheduled-run display differ from local output because server-local dates are used. Stored send timestamps also lack offsets.
- Embedded database credentials remain in recovered API routes. No credentials were printed in this report, rotated, or changed.
- Lint errors remain in the sequences and suppression-list routes; hook-dependency and unused-import warnings remain in dialogs. These were preserved rather than mixed into source recovery.

## Evidence and remaining limits

Local private evidence is under `.git/vercel-recovery/`:

- `pulse-records.json`: latest email entries, per-campaign successful-send records, send flags, system scan logs.
- `pulse-success-check.json`: latest successful send, contact, suppression lookup, terminal sequence totals, latest Spectrum sequence updates.
- `local-api-verification.json`: recovered API responses and most recent successful contact-history entry.
- Deployment snapshot directory: `live-spectrum-api.json`, `live-spectrum-dashboard.png`, `live-spectrum-history.png`.
- `gmail-verification.json`, `gmail-latest-sent.png`, and `gmail-bounce-search.png`: direct Sent-folder identity/date confirmation and the matching delivery-failure search result.

The authenticated Railway browser session available here did not initially show the named GFMD service; unrelated services were not used as evidence. The successful scan records prove recent database-recorded activity, but this check does not establish the exact running worker revision or complete scheduler health.

The next source-reconciliation boundary is the newer Railway Python worker and any unpushed work on the other computer. Dashboard recovery is complete independently of that remaining backend source gap.
