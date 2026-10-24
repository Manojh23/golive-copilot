# Design

`backend/retrieval.py` selects main-source evidence separately, avoiding a large
source crowding out the other. Each gets at most 24 chunks: complete small
sources, or first/last anchors plus multiple workflow BM25 queries and spaced
fallback positions. Supporting sources get at most eight additional hits.
The text budget is 65,000 characters, not tokens. Prompt wrapper/fact JSON adds
overhead. This is bounded lexical retrieval, not exhaustive or semantic search.

`rag.retrieve` applies source filtering in SQL before LIMIT. `split_spans` makes
raw text coverage testable without stripping characters; immutable existing
snapshots are not rewritten. `valid_citations` rejects malformed references and
checks normalized, case-insensitive excerpts of 16–650 characters.

For each selected main source whose indexed size exceeds 14 chunks, the engine
uses Gemini structured output to propose at most 30 workflow facts. A fact needs
all supplied citations to validate against that source's selected chunks. The
final finding call sees original selected passages and the candidate fact index.
It does not substitute model summaries for source passages. This may add two
provider calls, latency and cost for two long main documents.

Assessment JSON stores coverage, selected chunk IDs, accepted candidate facts,
discard counts and per-call metadata. No database migration is needed. The UI
shows selection coverage and distinguishes scenario rules from LLM proposals.
Human interpretation review remains necessary, including for correctly quoted
but misinterpreted facts. No guarantee of complete issue detection is made.

Property tests generate Unicode text, chunk sizes/overlaps, quotes, fabricated
quotes and malformed references. Regression tests include >100 retired FTS hits,
a late closure condition, long-document fact rejection and preserving local
files during an update. Existing behavioral tests remain in the suite.

Continuation view: consume assessment.extracted_facts without changing the API.
Use the existing viewSource(source_id) action and details/summary keyboard
behavior. Show original citation quotes so reviewers can assess the fact's
meaning. Do not label extracted facts as clinically verified.
