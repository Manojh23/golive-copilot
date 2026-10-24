# Update your existing Mac project

This is the full updated source package. It does not contain your API key or saved
database. The update helper copies code into your existing project and preserves
your local state. Stop the running app with Ctrl+C first.

Extract the ZIP in Downloads. Its folder is `golive-copilot-update`. In Terminal:

```bash
cd ~/Downloads/golive-copilot-update
python3 scripts/apply_update.py --target "$HOME/Downloads/golive-copilot"
```

That previews the files. If the target is your existing project, apply:

```bash
python3 scripts/apply_update.py --target "$HOME/Downloads/golive-copilot" --apply
cd ~/Downloads/golive-copilot
bash scripts/setup.sh
.venv/bin/python -m pytest tests -q
npm run dev
```

Change the target path if your original project lives elsewhere. The script
backs up overwritten files into a timestamped sibling folder. It does not delete
files or replace `.env`, `data/runtime`, `.git`, `.venv`, `node_modules` or your
`KIRO_USAGE.md`. Existing custom files remain. It deliberately replaces changed
code/configuration with this package, with old versions in the backup; inspect
those backups if you made other local code changes after receiving the starter.
The helper does not migrate or reset your database.

Open the ORIGINAL `golive-copilot` folder in Kiro afterward. Your old saved
review is still there; re-run it to generate the new coverage metadata. Source
snapshots remain immutable. Changing a source or requirements still invalidates
approval; content approval still does not resolve a finding.

## What changed

- Kept the Gemini connection timeout/retry fix, backend-only key and model discovery.
- Removed prefix-only retrieval; SQL filters active sources before limiting results.
- Added balanced evidence selection and visible per-source coverage counts.
- Added citation-checked workflow fact candidates for long main documents. Short
  sources keep one generation call; long sources can add one call per main source.
- Added Hypothesis properties, late-evidence/source-isolation regression tests,
  credential-pattern scanning and a tested update helper.
- Added current-format Kiro hooks, an optional disabled public-docs MCP, a retrieval
  spec, verification steering and a submission checklist.
- Kept the existing demo, review/export flow, feedback, hospital aggregates and
  source attribution. No live EHR connection or patient data was added.

## What you must still do

Read `KIRO_NEXT_STEPS.md`. These prepared files were created outside Kiro. Use
Kiro for meaningful implementation and verification, and record only what
actually happens. This package cannot guarantee judging eligibility or replace
the repository URL, working test-build link, public video or submission form.
