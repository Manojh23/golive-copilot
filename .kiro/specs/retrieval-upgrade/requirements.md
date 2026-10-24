# Retrieval upgrade requirements

Prepared outside Kiro. These requirements describe implemented baseline changes
and a concrete continuation task; they are not evidence of Kiro authorship.

1. When active workflow and proposed-app sources are selected, retrieval shall exclude retired versions before ranking limits apply.
2. A relevant passage after chunk 14 shall be eligible for selection. Selection shall search all indexed positions, stay within a bounded context, and disclose selected/total counts for each main source.
3. For a main source longer than 14 chunks, the live path shall extract source-specific subject/relationship/object candidates with exact citations before finding generation. It shall discard a fact if any supporting excerpt fails validation.
4. Findings and facts shall remain proposals requiring interpretation review. Unknown evidence shall not become a product-failure claim.
5. Chunk spans shall cover every character of the original text, preserve ordering, terminate and respect maximum chunk size. Invalid size/overlap shall fail immediately.
6. Citation validation shall reject invented identifiers, modified quotes and malformed values. Whitespace and case normalization shall remain explicit.
7. Existing demo checks, review ownership, stale approvals, exports, feedback and backend-only credentials shall continue working.
8. The update tool shall preserve .env, saved runtime data, Git history and KIRO_USAGE.md, make backups of overwritten files, and delete no existing files.

## Meaningful Kiro continuation

Add an accessible, collapsible **Extracted workflow facts** view on Impact review:
show subject, relationship, object, source title and a source-opening button for
each fact; explain excerpt checking versus interpretation. Hide when no facts
were extracted. No new patient data or automatic approvals. Preserve all current
flows. Implement and verify this task in an actual Kiro session, then document it.
