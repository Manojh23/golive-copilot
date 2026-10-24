---
inclusion: always
---

# Verification and provenance

The baseline and retrieval upgrade were prepared outside Kiro. Do not attribute
them to Kiro. Read KIRO_USAGE.md and record only observed Kiro work.

- Preserve .env, data/runtime, source snapshots, review history and existing user files.
- Use isolated temporary databases for automated tests; never reset a user's workspace.
- Run `.venv/bin/python -m pytest tests -q` after backend changes and `npm run build` after frontend changes.
- Run `python3 scripts/check_secrets.py`; in Git also run it with `--staged` before committing.
- Citation checking proves a normalized case-insensitive excerpt match, not entailment.
- Keep long-document selection coverage visible. Absence from selected evidence is not proof of absence from a whole document.
- Fact extraction produces candidates, not verified facts about actual hospital practice.
- No patient records, clinical recommendations or invented integration success.
- Do not claim Kiro hook execution, MCP use, browser checks, live-model evaluation, deployment or novelty without corresponding evidence.
