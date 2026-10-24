# Role-brief evidence requirements

Authored in Kiro. The GoLive Impact Copilot baseline, retrieval upgrade, and
these steering/spec files were prepared outside Kiro and are not claimed as
Kiro work. This spec adds one focused, reviewed improvement to the approved
role-brief PDF export.

1. The approved role-brief PDF (`/api/exports/brief.pdf`, `approved_only=True`)
   SHALL, for each included finding, show the finding's reviewer note when a
   non-empty `review_note` was supplied during review.
2. For each included finding, the PDF SHALL show its supporting source
   quotations, i.e. the validated `quote` text of every citation attached to
   that finding, not only the first two.
3. For each quotation, the PDF SHALL show that quotation's source title and
   page/section locator (`title` and `locator`) alongside the quotation text.
4. Quotation text, source titles, locators, and reviewer notes SHALL be
   rendered as wrapped, escaped PDF text so source content is readable and
   cannot inject reportlab markup. The `chunk_id` SHALL remain visible for
   traceability.
5. Existing approval filtering (`status == 'approved'`), role filtering, source
   attribution, draft (`approved_only=False`) exports, CSV/JSON exports, `.env`,
   the saved runtime database, and all other workflows SHALL be preserved. No
   new findings, automatic approvals, or schema migrations SHALL be added.
6. Draft briefs (`approved_only=False`) SHALL still include unapproved
   findings and SHALL be marked as draft, unchanged from prior behavior.
7. Tests SHALL prove the exported PDF contains an approved finding's reviewer
   note and at least one of its supporting source quotations (with source title
   and locator), while excluding unapproved findings that share the queried
   role. The full test suite SHALL continue to pass.
