# Requirements

1. WHEN a reviewer opens the application, it SHALL disclose synthetic scenario material, real public research, and model availability.
2. WHEN a reviewer uploads a permitted PDF/TXT/MD document, the system SHALL validate size/type, preserve source locations, compute a content digest, and create an immutable searchable snapshot.
3. WHEN analysis runs, the system SHALL consider active current/proposed sources and exclude retired app guides from active rollout context.
4. WHEN no provider key exists, the system SHALL run only the disclosed fictional scenario rules and SHALL NOT claim LLM generation or apply those rules to an unrelated uploaded app.
5. WHEN live generation is enabled, the backend SHALL retrieve evidence, request structured output, validate role/citation IDs and excerpts, record model metadata, and leave interpretations for human review.
6. WHEN a reviewer approves or resolves a finding, the system SHALL require ownership; resolution/dismissal SHALL require a note. Content approval SHALL NOT count as resolution.
7. WHEN a role brief is exported as approved guidance, only approved, non-stale content SHALL be included. Draft exports SHALL be marked.
8. WHEN source material or requirements change, earlier assessments SHALL be marked stale and approvals SHALL require re-review after recomputation.
9. WHEN staff check-ins are grouped, the system SHALL preserve original reports, provenance, and suggested-not-confirmed links to earlier findings.
10. WHEN public hospital data is shown, only attributed aggregate statistics SHALL be served; artificial mirror boundary events SHALL be excluded and disclosed.
11. The UI SHALL offer editable existing-app inventory, impact review, role briefs, feedback, source inspection, and hospital-data views.
12. The project SHALL include reproducible setup, checks, Kiro steering/specs, and truthful limits on unverified real-provider and browser behavior.
