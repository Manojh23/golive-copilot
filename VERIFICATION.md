# Submission update verification — 24 October 2026

- Fresh dependency installation from requirements.lock.txt succeeded in a separate virtual environment. All 34 tests also passed from an extracted copy of the final package.
- 34 tests passed, including the existing review/export/feedback API journey and Gemini retry recovery.
- Hypothesis generated Unicode text, chunk sizes/overlaps and citation variations to check text coverage, termination and rejection of invented evidence.
- Regression checks cover a relevant passage after chunk 14, active-source filtering despite more than 100 retired hits, citation rejection during long-document fact extraction, and update backups/preservation of local state.
- Vite production build passed. FastAPI TestClient serves the built entrypoint; no browser visual check is claimed for the new disclosure.
- Offline configured credential-pattern scan passed. This is not a comprehensive security audit.
- The Gemini timeout/retry fix remains included. User supplied a successful live connectivity/schema result from their Mac; this environment has no provider key. The updated fact pipeline was tested with mocked model output, not a live clinical accuracy evaluation.
- Kiro hook definitions follow the current official v1 schema. Their commands were run directly; no actual Kiro hook firing or MCP execution was performed here. The optional MCP is disabled.
- The update helper was tested with temporary fake local state; it keeps .env, runtime data, KIRO_USAGE.md and extra files while backing up overwritten code.
- No GitHub publishing, hosted demo, video recording or final submission was performed.

A Starlette TestClient deprecation warning about the installed httpx transport remains non-failing.

---

The original verification record follows, for historical context.

# Initial verification

Date: 24 October 2026.

## Completed

- Corrected an empty backend dependency lock file discovered during user setup; verified the populated lock by installing all packages and importing the backend dependencies in a fresh virtual environment. Setup now falls back to requirements.txt if the lock is empty.
- Installed frontend and backend dependencies in isolated local environments.
- Built the React frontend successfully with Vite.
- Ran 18 behavioral tests successfully, covering ingestion, BM25 retrieval, citation rejection, the review/export/feedback journey, stale approvals, custom-app isolation, input validation, changed requirements, public-data integrity, and mocked Gemini transport.
- Retrieved an attributed historical hospital event-log mirror and verified SHA-256 `20f844ab39f96045daff8470448c1d3fb47dfebf3a9fd5dc21bb80995d2cb6bb`.
- Excluded 2,100 artificial alpha/omega trace markers. Computed 1,050 cases, 15,214 recorded events, and 16 activity types.
- Retrieved the correct Duke study by DOI, checked its title/PMCID and open-access reuse notice, and bundled attributed excerpts.
- FastAPI TestClient exercised the JSON backend and built frontend entrypoint on the same application. Temporary test databases do not affect the user's saved workspace.

## Verification limits

- **Live model:** no provider key was available. Transport/schema and output-validation behavior were tested with a mock. Actual Gemini access, quota, latency, cost and generated-answer accuracy still need the provided live smoke test and reviewer evaluation.
- **Browser:** the managed preview runner could not start the Python virtual environment in its isolated `/site` filesystem. Two attempts failed before serving the app. No browser end-to-end or visual verification is claimed. Verify the local UI in Kiro on your Mac.
- **Container:** Dockerfile included but not executed.
- **Clinical/vendor integration:** none performed or claimed. FHIR-related scenario checks compare fictional declared requirements, not a live EHR exchange.
- **Clinical benefit and adoption:** not measured. The planted-case score is a rule-engine regression scenario, not live LLM accuracy or a real hospital outcome.
- **Deployment:** delivered as a local single-workspace project. No publicly hosted hospital service or multi-user authentication is included.

One dependency emitted a Starlette TestClient deprecation warning recommending httpx2. The current installed httpx test transport passed; that warning is not represented as a failed test.
