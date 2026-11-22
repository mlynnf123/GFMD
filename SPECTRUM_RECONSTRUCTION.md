# Spectrum worker reconstruction

November 22 update: `INTEGRATION_RESTORATION.md` supersedes the deterministic
composition policy with real AI drafts; the standalone preview remains offline.
This describes the pre-deployment checkpoint. `PRODUCTION_RESTORATION.md` records
the subsequent approved deployment and gated automatic replies; human review
remains the default unless the explicit production reply opt-in is enabled.

Implemented locally November 20, 2026, on `codex/recover-vercel-dashboard`. This is a functional reconstruction from persisted history and the recovered Railway code. It is not a recovery of the missing Python source or its original AI prompts.

Python 3.11 follow-up: see `PYTHON_311_VERIFICATION.md`. The current suite passes 50 tests under actual CPython 3.11.18 with dependencies installed. Reply handling now validates the thread before suppression, excludes quoted history, and reviews temporary absences without permanent suppression.

No deployment, scheduler start, email send, OAuth renewal, production record change, commit, or push was performed. Google Cloud investigation remains pending at the user's request.

## Evidence recovered

- Read-only MongoDB export: 315 Spectrum contacts/sequences, 1,967 email-history entries, 1,966 marked actually sent with Gmail identifiers, and one unsent entry. These are recorded sends; only the previously investigated October 14 message was independently matched to Gmail Sent Mail during the earlier pulse check.
- Every step retains its historical template type. The dominant initial subject was `Same-day PCR for UTI, C. auris, CRE & mpox screening`; subsequent sends retained the initial subject for threading.
- Inferred delays using the recovered `BusinessDayCalculator` reproduce the dates of **all 1,652 adjacent successful-send transitions** across the four observed cohorts. This is a date-level match; processing times varied within each batch.
- Three Spectrum-tagged vector records preserve the complete text of two original knowledge documents. Restored without changes to `knowledge_base/gfmd_spectrum_product.md` and `knowledge_base/snf_ltc_pain_points.md`; SHA-256 hashes and source document IDs are recorded privately.
- Their metadata names the original source directory as `/Volumes/SSD/DevProjects/GFMD/GFMD/knowledge_base/`, a Mac/external-drive recovery lead. It does not establish the worker's execution host.
- No Spectrum auto-reply interactions were found, including by recipient address. Eight sequences are marked replied, so missing interactions must not be interpreted as proof there were no incoming replies.

Private evidence is under `.git/spectrum-reconstruction/`: `evidence.json`, `analysis.json`, `knowledge-recovery.json`, `offline-tests.txt`, and `verification.json`. Recipient histories stay out of tracked source and test fixtures.

## Reconstructed sequence

| Step | Stored template type | Reconstructed topic | Inferred business days after prior send |
| --- | --- | --- | ---: |
| 1 | `initial` | Spectrum introduction and test menu | Initial eligible business day |
| 2 | `value_follow_up` | UTI testing and stewardship | 4 |
| 3 | `soft_check_in` | Right contact / wrong contact / not now | 6 |
| 4 | `infection_control_follow_up` | C. auris and CRE colonization screening | 3 |
| 5 | `breadth_follow_up` | Respiratory, mpox, and onychomycosis menu | 5 |
| 6 | `turnaround_value_follow_up` | Turnaround and decision support | 5 |
| 7 | `soft_value_touch` | Offer a menu, pricing, or answer | 5 |
| 8 | `final_attempt` | Respectful final note | 5 |

The reconstructed drafts use the historical subject, topics, one-line reply menu, and `Thanks,` closing. They are sanitized new templates rather than verbatim copies of individual recipient emails. New drafts omit unverified public-health endorsements and stronger clinical-outcome claims found in some historical messages. The exact original knowledge documents remain historical source material, not independent verification of current claims.

Spectrum composition is deterministic and does not call Groq. This avoids inventing unknown historical AI prompts or falling back to Narc Gone/Centrifuge language. Existing campaigns retain their composer paths. The campaign-aware knowledge helper isolates Spectrum tags, and optional knowledge population includes the restored documents; no live population was run.

## Worker behavior

- `spectrum_campaign.py`: pure templates, rendering, UTC timestamp parsing, inferred due dates, and reply-review validation.
- `spectrum_worker.py`: Spectrum processing through the existing storage/Gmail adapters, called by `complete_sequence_automation.py`. Existing dashboard records using `campaign: spectrum` and `sequence_name: spectrum_snf_ltc` are recognized.
- Spectrum sending is disabled unless `GFMD_SPECTRUM_SEND_ENABLED` is explicitly `1`. Explicit worker enrollment separately requires `GFMD_SPECTRUM_ENROLLMENT_ENABLED=1`. Neither flag was configured for production.
- Spectrum remains paused in daily auto-enrollment even if explicit enrollment is enabled; there is no evidence for its original daily enrollment quota. The historical 315-contact cohort is not automatically recreated.
- Due dates use the observed **15:15 UTC** anchor, and an additional daily scheduler tick is registered for that time. This was 10:15 a.m. CDT during the historical sends. It is a fixed UTC reconstruction, not an assertion of an original Central-time/DST policy.
- As a new safety choice, the processing window is business days from 15:15 through before 18:00 UTC. The original cutoff is unknown. The recovered calendar only implements its existing fixed-date holiday exclusions; the original complete holiday policy cannot be inferred from this evidence.
- Terminal, replied, suppressed, not-yet-due, too-recent, malformed, and incomplete-history records are not sent. No terminal sequence is automatically resumed, including the 25 records completed at step 7.
- Spectrum dry runs return previews without sequence writes or Gmail transport. The standalone preview below also avoids service initialization. Legacy non-Spectrum `process` dry runs still have inherited mutation behavior and must not be used against production.
- An atomic processing claim protects each record. Suppression, contact identity, current history, and due time are rechecked after claiming. Actual sends require successful Gmail results containing message and thread IDs; step 8 then completes the sequence and clears its due date.
- Before transport, a pending attempt with a generated RFC `Message-ID` is persisted. Failed/uncertain transport or a post-send database failure leaves a review hold, so this implementation does not blindly retry a possibly accepted message. Operators must reconcile the pending attempt against Gmail before any explicit retry decision. This does not guarantee exactly-once behavior across unreconciled older workers that ignore these fields.
- Gmail threading reads the parent message's RFC `Message-ID`, actual subject, and thread ID instead of using Gmail's internal ID as an RFC header. The adapter follows [Google's threading requirements](https://developers.google.com/workspace/gmail/api/guides/threads). Tests use fake Gmail responses; live end-to-end threading was not exercised.
- No pre-send notification email is generated. The historical notification text is evidence, but its missing notifier implementation was not invented.

## Replies

Spectrum replies require human review. The historical auto-reply policy could not be reconstructed from available interactions. A Spectrum reply must match a recorded contact and successful-send thread before any suppression/review write. Opt-out analysis then uses newly authored text without quoted history. Temporary absences are reviewed; explicit opt-outs still suppress. Incoming text remains untrusted data and is never executed or sent to the AI composer. System-sender bounce processing retains its existing route.

Review items are persisted idempotently in `interactions` with type `spectrum_reply_review`, keyed by the incoming Gmail message ID. An active matching Spectrum sequence is marked replied with no further due date. This is a backend review queue; no dashboard review interface was added. Automatic Spectrum reply sending is blocked, including the direct reply-sending method. A matching sender/thread establishes relevance, not independent sender authentication.

## Offline use and verification

Run these from the repository root:

```powershell
python -X utf8 preview_spectrum.py
python -X utf8 preview_spectrum.py --step 8 --name Alex --organization "Example Care Facility"
python -X utf8 -m unittest discover -s tests/offline -v
```

`preview_spectrum.py` imports no storage, Gmail, Groq, credentials, or scheduler. It defaults to a fictional contact and reserved `.invalid` email address.

The initial 40-test reconstruction suite passed under Python 3.14 with service imports and HTTP blocked. The subsequent actual Python 3.11 run now passes **41 offline tests plus nine real-module integration tests**. Coverage includes all eight steps, completion and duplicate prevention, actual worker/composer/reply routing, disabled defaults, suppression and terminal records, previews, cadence, concurrency, stale records, unavailable Gmail, uncertain transport, post-send database failure, RFC headers, HTML escaping, and knowledge isolation. The implemented cadence again matched all 1,652 historical date transitions, and all eight previews rendered under 3.11. Fourteen relevant Python files compiled under 3.11. Exact dependency versions and runtime details are in `PYTHON_311_VERIFICATION.md` and its private evidence files.

Root backend dependencies installed successfully in the isolated Windows Python 3.11 environment, and all checked dependency/application imports passed. Execution on the actual production Linux image and live services remains unverified. Existing dashboard lint failures and the unchanged legacy `narcon_knowledge_base.py` syntax error are outside this reconstruction.

## Production remains unchanged

The local implementation is reviewable, but production resumption still requires identifying/retiring other writers, reconciling Gmail authentication, and isolated runtime verification. No skipped contact was requeued and no sending/enrollment flag was enabled remotely. The original source can still replace inferred portions if the Mac/external drive or an unverified cloud deployment is recovered later.
