# GoLive Impact Copilot

A local, end-to-end healthcare software rollout prototype. Review a proposed app against an existing workflow, create source-linked findings and role briefs, assign reviewers, and connect post-launch staff feedback to anticipated issues. See [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) before submitting.

## Run on your Mac in Kiro

Requirements: Python 3.11+ and Node.js 22.12+ (Node 24 was used for verification). Open this entire folder in Kiro, including `.kiro/`.

```bash
bash scripts/setup.sh
npm run dev
```

Open **http://localhost:8000**. The same FastAPI server serves both the backend and built React frontend. The workspace persists in `data/runtime/workspace.sqlite3`.

After frontend changes, run `npm run build` and restart the backend. During frontend development you may run `npm run frontend` in a second terminal; its `/api` proxy points to the backend on port 8000.

### Windows PowerShell

```powershell
py -3 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.lock.txt
npm ci
npm run build
Copy-Item .env.example .env
.venv\Scripts\python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

## Live RAG and LLM setup

The app starts without a provider key. That mode is explicitly labeled: deterministic rules evaluate the fictional scenario, SQLite FTS5 BM25 retrieves evidence, and keyword rules group staff reports. **It does not pretend to call an LLM.**

To enable live generation, set `GEMINI_API_KEY` in `.env` and restart. Credentials stay on the backend. Never commit `.env` or enter credentials into the frontend. When enabled, selected source excerpts and user input are sent to Google's Gemini API; use public or otherwise permitted non-patient material.

`GEMINI_MODEL` is optional. When blank, the backend queries the models endpoint and selects an available Flash text-generation model. If your key does not support model discovery, set a supported text model explicitly.

```bash
.venv/bin/python scripts/list_models.py
.venv/bin/python scripts/verify_live_llm.py
```

The optional smoke test makes a real provider request and may incur cost. The initial development environment has no API credential. The user subsequently demonstrated a successful live connectivity/schema smoke test on their Mac. The updated long-document fact path still needs live semantic evaluation; mocked tests do not establish its accuracy.

### RAG implementation

1. Accept PDF, UTF-8 text, or Markdown sources (5 MB, 80 PDF pages, 240,000 extracted characters maximum).
2. Preserve PDF pages and text-section locations; create immutable SHA-256-identified source snapshots.
3. Split text into overlapping chunks and index them with SQLite FTS5.
4. Retrieve using BM25 with SQL source filtering before result limits. Read short active documents in full; select up to 24 chunks per long main source using workflow queries, first/last anchors and spaced positions. Add up to eight supporting chunks within a 65,000-character text budget. Show selected/total coverage; this is not exhaustive review. Retired main-source versions are excluded.
5. For each main source longer than 14 indexed chunks, first extract structured subject/relationship/object candidates and reject facts with invalid citations. Then call Gemini for findings using original selected passages plus that fact index. Short dossiers keep one call. Store per-call metadata; extra calls increase latency and cost. Use Pydantic-derived JSON schemas, an evidence-only instruction, allowed roles and source IDs.
6. Reject fabricated chunk IDs, nonmatching quoted excerpts, unsupported role names, and public-research-only claims about the local rollout.
7. Save model ID, prompt version, usage metadata, source fingerprint, and review actions.

Excerpt validation checks traceability, not factual entailment or clinical correctness. All generated findings remain human-review proposals. RAG is lexical in this implementation; there is no claim of semantic vector search, model training, or autonomous clinical decision-making.

## Main demo

1. On Overview, click **Run impact review**. Without a key this runs the disclosed synthetic scenario rules.
2. Inspect the eight deliberately planted gaps. Open evidence links to read the exact source snapshots.
3. Review one finding, assign an owner, and mark its content approved. Approval does not mean the issue is resolved.
4. Open **Role briefs**, select Nurse, and export an approved PDF. Only approved items are included. Draft export is clearly marked.
5. Open **Feedback loop**, load 20 labeled synthetic check-ins, and group reports. With a configured provider, enable Live LLM first to use model-based grouping.
6. Follow a suggested link from a report group to an earlier finding. Reports and suggested relationships remain unverified.
7. Open workspace settings. Set `training_recorded` to `true` or assign `alert_owner`, save, and re-run. Prior approvals become stale when inputs change.
8. In **Evidence library**, ask about nurse responsibilities, training, or lactate. Without a key this returns excerpts; with Live LLM it generates a cited answer.
9. Open **Hospital dataset** to inspect independently computed historical hospital aggregates and their provenance.

To try a custom rollout, upload a proposed-app guide and optionally replace the current-workflow description. Replacing the proposed guide disables all demo-specific rule findings; live LLM generation is required to propose findings for the new app. A general medical paper alone is insufficient to describe local practice.

## Real data and demo boundaries

**Real hospital research:** attributed excerpts from Sandhu et al., *Integrating a Machine Learning System Into Clinical Workflows: Qualitative Study*, JMIR 2020;22(11):e22421, DOI 10.2196/22421, PMCID PMC7714645. Identity and open-access permission were checked against the Europe PMC XML. This is historical Duke implementation research, not a validation of EarlyWatch.

**Real historical workflow data:** Felix Mannhardt, *Sepsis Cases — Event Log* (2016), DOI 10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460. The original 4TU host returned HTTP 503 during retrieval. A disclosed Git-LFS mirror was used and digest-checked. Its artificial alpha/omega start/end markers are excluded. Bundled aggregates contain **1,050 cases, 15,214 events, and 16 activity types**. The bundled app does not include or serve patient-level records.

**Synthetic:** Northstar Demo Hospital, CareRecord, LabBridge, TeamInbox, FollowTrack, EarlyWatch, local requirements, all planted rollout problems, and the 20 demonstration staff check-ins. These are fictional evaluation fixtures. No fictional product is represented as FDA-authorized or used at a real hospital.

Observed pathway counts do not show which apps were installed, whether an event was unnecessary, or whether an app would improve clinical outcomes. No alerts-per-shift estimate or time saving is invented from documentation.

Regenerate public aggregates and attributed excerpts with `python scripts/fetch_public_data.py`. This requires network access. Only aggregates are redistributed; consult the original data terms. `data/hospital_benchmark.json` records the source, mirror, excluded markers, digest, and limitations.

## Verification

```bash
npm run build
.venv/bin/python -m pytest tests -q
```

The suite includes Hypothesis-generated chunk coverage and citation validation properties, plus late-evidence selection, active-source ranking, fact-validation and safe-update regressions. The automated tests also cover the API journey, citation rejection, stale approvals, role exports, upload validation, feedback grouping, custom-app isolation, changed requirements, public-data integrity, and mocked Gemini transport/schema behavior. `data/evaluation_cases.json` is an independent manifest of the original eight planted gaps and important negative cases. The app's benchmark is disclosed as a rule-engine scenario check, not a live LLM accuracy result.

See `VERIFICATION.md` for the actual initial results and limits. Real provider accuracy, real vendor APIs, Docker execution, real clinical workflow utility, and production deployment are not inferred from unit tests.

## Kiro and hackathon submission

`.kiro/specs/golive-impact/` contains the original requirements, architecture and task plan. `.kiro/specs/retrieval-upgrade/` documents this update and a meaningful continuation task. `.kiro/hooks/` contains test and credential-check definitions for the current Kiro v1 format; `.kiro/settings/mcp.json` configures a public-docs fetch server. See `KIRO_USAGE.md` for the actual hook/MCP outcomes observed in Kiro. `.kiro/steering/` preserves the product and evidence constraints.

The starter was prepared outside Kiro. Merely including these files does not establish material Kiro usage. Open the folder in Kiro, have it run/review the project, complete meaningful work, and record what it actually did. Keep `.kiro/` tracked. Check the hackathon's supplied requirements for public source, a working/testable build, and a public video under three minutes.

## Access and deployment scope

This is a **local single-workspace prototype**, not a production hospital system. It has no multi-user authentication or patient-data controls. Keep it local; do not publish its API directly to the internet or upload patient records.

A Dockerfile is included as an optional local packaging path (not executed during initial verification):

```bash
docker build -t golive-copilot .
docker run --rm -p 127.0.0.1:8000:8000 --env-file .env -v golive-data:/app/data/runtime golive-copilot
```

The app exports PDF, CSV, and JSON review material. No direct Whatfix, uPerform, EHR, or clinical-device integration is implemented or claimed. Hospital reviewers must approve guidance and validation before use.

## Structure

- `backend/`: FastAPI, SQLite persistence, ingestion/retrieval, rule checks, provider adapter, exports.
- `frontend/`: React interface and responsive styling.
- `data/`: synthetic benchmark manifest, attributed research excerpts, public aggregate data.
- `scripts/`: setup, public-data preparation, provider discovery and smoke test.
- `tests/`: behavioral tests with temporary isolated databases.
- `.kiro/`: requirements, design, tasks, and steering for continued work in Kiro.
