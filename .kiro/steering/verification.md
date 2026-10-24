---
inclusion: always
---

# Development and verification

The developer provides the product requirements and instructions. Kiro implements the prototype, generates and refines code, and assists with testing and documentation. The developer reviews the results and requests revisions.

- Follow the product requirements and evidence constraints.
- Preserve existing user files, environment settings, and saved workspace data.
- Use isolated temporary databases for automated tests.
- After backend changes, run `.venv/bin/python -m pytest tests -q`.
- After frontend changes, run `npm run build`.
- Before committing, run `python3 scripts/check_secrets.py`.
- Fix failures and report actual results.
- Keep API keys in server environment variables.
- Keep fictional demo data separate from public research.
- Record completed Kiro work accurately in KIRO_USAGE.md.
- Claim successful hooks, deployment, or live-model testing only when verified.