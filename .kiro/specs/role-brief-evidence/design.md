# Design

## Scope

Only the PDF brief renderer in `backend/app.py::export_brief` changes. The data
model already carries everything needed: each citation dict from
`rag.valid_citations`/`rag.evidence_for` has `quote`, `title`, `locator`,
`chunk_id`, `source_id`, `origin`, and `url`. Each finding already has
`review_note`, `owner`, `status`, `citations`, `impact`, and `action`.

No database migration, API route, schema, or Pydantic model change is needed.
CSV and JSON exports are untouched.

## Rendering change

The existing per-finding loop renders `title`, `impact`, `Review action`,
`Owner`, then up to two `Evidence: title / locator / chunk_id` lines. The
evidence lines omit the quotation text entirely and cap citations at two.

New per-finding block, keeping the existing approval/role filter unchanged:

- `title` (Heading2), `impact`, `Review action: ...`, `Owner: ...` as today.
- When `review_note` is non-empty after stripping, render `Reviewer note: ...`.
- When the finding has citations, render a `Supporting source quotations:`
  label, then for every citation (no cap):
  - the quotation text (`quote`), and
  - `Source: <title> / <locator> (chunk <chunk_id>)` as its attribution line.

All text continues to go through the existing `para()` helper, which calls
`xml.sax.saxutils.escape` before `reportlab.platypus.Paragraph`. `Paragraph`
wraps long lines to the frame width, so quotation text up to the 650-character
validation limit stays readable. Escaping prevents source text (`&`, `<`, `>`)
from being interpreted as reportlab markup. No raw concatenation into markup.

## Why this is safe

- Approval and role filtering happen before rendering and are not touched, so
  unapproved findings and other-role findings remain excluded.
- Showing more citations only adds text; it cannot include findings that were
  already filtered out.
- The reviewer note is reviewer-entered text capped at 1600 characters by the
  `Review` Pydantic model, and it is escaped and wrapped like all other text.
- The `chunk_id` is kept so a reviewer can still trace a quotation to its chunk.

## Tests

`tests/test_brief_evidence.py` uses the isolated `TestClient` fixture already
used by `tests/test_workflow.py` (separate `GOLIVE_DB` temp database, no key).

1. Approve only `duplicate_entry` with a distinctive `review_note`; request the
   Nurse approved brief; assert the note, a stored quotation, and the matching
   source title + locator appear in the extracted PDF text, and that an
   unapproved Nurse-role finding (`No path for an unavailable assessment`) does
   not. This proves inclusion of note + quotations and exclusion by approval
   within the same role (not merely by role).
2. Request the draft brief (`approved_only=False`); assert that the unapproved
   Nurse-role finding title now appears and the draft marker is present. This
   proves the approved brief's exclusion is approval-based, not role-based.
3. Approve `duplicate_entry` with no `review_note`; assert the quotation appears
   but no `Reviewer note:` label is rendered, proving the "when supplied" rule.

PDF text is whitespace-collapsed before substring assertions so reportlab line
wrapping does not make extraction differ from the stored strings.
