# Tasks

Authored in Kiro. Status reflects actual Kiro work.

- [x] Read existing code (app.py export_brief, engine.py, rag.py, store.py,
      seed.py) and .kiro steering/spec files; confirm the citation/finding data
      model already carries quote, title, locator, review_note.
- [x] Create this spec (requirements, design, tasks) under
      `.kiro/specs/role-brief-evidence`.
- [x] Modify `backend/app.py::export_brief` to render the reviewer note when
      supplied, all supporting source quotations, and each quotation's source
      title + locator + chunk_id, keeping text escaped and wrapped.
- [x] Add `tests/test_brief_evidence.py` proving the approved PDF includes the
      approved finding's note and quotations and excludes unapproved findings.
- [x] Run `.venv/bin/python -m pytest tests -q`; confirm all tests pass
      (baseline 34 plus 3 new = 37 passed).
- [x] Observe whether the configured `.kiro/hooks` actually fire; report only
      observed executions. (See KIRO_USAGE.md: no automatic hook execution was
      observed; the credential scanner and test suite were run manually.)
- [x] Append actual changes, commands, results, and limitations to
      `KIRO_USAGE.md`. Do not attribute the starter or retrieval upgrade to Kiro.
