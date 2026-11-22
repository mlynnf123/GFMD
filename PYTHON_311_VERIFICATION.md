# Python 3.11 worker verification

November 22 update: see `INTEGRATION_RESTORATION.md` for the subsequent local
Gmail/AI repair and live read-only checks. The current isolated suite passes
41 offline and 28 runtime tests. `PRODUCTION_RESTORATION.md` records the subsequent
authorized Linux deployment and activation. The November 20 report below is historical.

Completed locally November 20, 2026. No deployment, scheduler startup, Gmail connection, real email send, OAuth renewal, or production database operation was performed.

## Results

| Check | Result |
| --- | --- |
| Interpreter | CPython 3.11.18, Windows x64 on the ARM64 development machine |
| Root `requirements.txt` installation | Passed in an isolated environment |
| Dependency consistency | All 87 installed runtime/test packages compatible (`uv pip check`) |
| Dependency/application imports | All 12 checked modules imported, including NumPy, PyMongo, Groq, Google API client, sentence-transformers, the automation worker, and health server |
| Offline regression suite | 41 passed |
| Real-module runtime integration suite | 9 passed |
| Historical cadence replay | All 1,652 adjacent successful-send dates matched |
| Standalone preview | All eight drafts rendered from outside the repository working directory |
| Syntax compilation under actual Python 3.11 | 14 relevant source/test/runner files passed |

The runtime integration suite imports real application modules and constructs the automation worker with injected local adapters. It uses real BSON ObjectIds, the real MongoDB storage methods against a `mongomock` in-memory database, and the real Gmail MIME/threading adapter against a local message recorder. It exercises all eight steps, thread headers, terminal completion, uncertain transport, opt-outs, reply review, and the Flask health route without starting the scheduler.

The validation runner removes relevant service credentials from its own process, uses a temporary working directory without `.env` or OAuth files, and blocks external socket connections and DNS. Windows asyncio's internal loopback socket pair is allowed. Models, Gmail OAuth, production Atlas access, and external AI requests are not used in the integration suite. A separate import smoke check imported sentence-transformers with model/network access disabled; it did not download model weights.

## Issues fixed

1. **Quoted text falsely suppressing positive replies.** A request for pricing could be suppressed because a quoted earlier Spectrum message contained `wrong person`. Spectrum now extracts the newly authored plain-text or HTML reply for suppression analysis, recognizing common Gmail, Outlook, and blockquote boundaries. Full original content remains in the review record.
2. **Suppression before thread validation.** An unsubscribe message with a known Spectrum sender address but an unrelated thread could modify the contact before validation. Spectrum now checks the recorded sender/thread relationship before any suppression or review write. This establishes relevance, not independent sender authentication.
3. **Temporary out-of-office suppression.** A temporary absence is queued for human review instead of being treated as a permanent unsubscribe. An explicit opt-out remains effective even when the message also mentions an absence.

The reply monitor now accepts injected storage/Gmail adapters, allowing Spectrum to reuse its configured adapters and enabling integration checks without starting another OAuth flow. Other campaigns retain their existing reply-processing route. Sending/enrollment defaults remain disabled.

The runtime runner's Windows temporary-directory cleanup was also corrected to leave the directory before cleanup. The failed regression evidence for the first two application issues is retained alongside the final passing results.

## Repeat locally

The interpreter is stored under `.git/python-runtimes/`; the environment is `.git/python311-venv/`. Neither PATH, the Windows Python registration, nor the user's default Python 3.14 installation was changed.

```powershell
.\.git\python311-venv\Scripts\python.exe -X utf8 scripts\verify_worker_runtime.py
.\.git\python311-venv\Scripts\python.exe -X utf8 preview_spectrum.py
```

For a separately prepared Python 3.11 environment, install `tests/runtime/requirements.txt`, then run the same verification script with that interpreter. The runtime test requirements include the root application requirements plus the in-memory MongoDB test dependency.

Private evidence under `.git/python311-validation/` includes:

- `imports.json` and `import-output.txt`.
- `resolved-requirements.txt` with exact installed versions.
- `test-results-before-fixes.txt` and `runtime-before-fixes.json`.
- `test-results.txt` and `runtime-verification.json` for the final 50 passing tests.
- `replay-and-syntax.json` with source hashes and replay/compilation results.
- `offline-preview.txt` with fictional-contact previews.

This validates Python 3.11 execution on Windows. The deployed Linux container image, live Gmail delivery, production database behavior, OAuth validity, and older workers writing to the same database remain unverified by these local tests. The known legacy `narcon_knowledge_base.py` syntax error is outside the active Spectrum import path and was not changed.

## Downloads cleanup

All 27 Railway recovery files in `C:\Users\meran\Downloads` were compared against retained repo recovery snapshots using SHA-256 and matched. Those Downloads copies can be deleted; keep the GFMD project and its `.git` recovery backups. The complete list is `.git/railway-recovery/download-cleanup-list.txt`, with verification in `download-cleanup-inventory.json`. No Downloads files were deleted. The new Python runtime and packages are retained separately for repeatable testing, not among those 27 browser downloads.
