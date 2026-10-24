# Design

## Architecture

React/Vite builds static assets. FastAPI serves those assets and JSON APIs on one local origin. SQLite stores immutable source/chunk records, FTS5 indexing, the current project, review findings, feedback, and an audit trail. The Gemini REST adapter is server-side and optional.

Ingestion -> page-preserving chunks -> BM25 retrieval + active-doc context -> Pydantic structured generation -> excerpt and role checks -> proposed findings -> reviewer action -> approved/draft exports.

Feedback -> keyword rules or optional structured LLM groups -> preserved original reports -> suggested links to earlier findings.

## Provenance

The seeded current/new app guides are synthetic. The Duke study is historical open-access implementation research. The event-log panel is calculated from an attributed, digest-checked public mirror, with artificial alpha/omega boundaries removed. No app identity, causal improvement, or clinical decision is inferred from event-log counts.

## Important implementation decisions

- SQLite FTS5 BM25 avoids a vector-service dependency for the small corpus. This remains valid retrieval-augmented generation; it is not described as embedding search.
- Exact matching of source excerpts filters fabricated citations, but clinical interpretation remains a human task.
- Demo rules are gated to the original current/proposed sources and inventory. Custom documents use live model proposals or retrieval-only inspection.
- Analysis fingerprints include the source catalog and project inputs. Changed inputs invalidate prior review state.
- Approved exports contain only content reviewed by a named owner; no deployment approval is implied.
- The no-auth application is local single-workspace software. Production identity, tenant separation and hospital-data controls are outside this version.

## API

Use the generated FastAPI documentation at `/docs` after starting the server. Key routes: `/api/state`, `/api/project`, `/api/sources`, `/api/analyze`, `/api/ask`, `/api/impacts/{id}`, `/api/feedback`, `/api/feedback/analyze`, `/api/benchmark`, `/api/evaluation`, and `/api/exports/*`.
