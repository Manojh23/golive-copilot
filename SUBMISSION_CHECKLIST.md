# Final submission checklist

Based on the Hackachusetts rules supplied by the user. Check the organizer's
submission page for the actual deadline and final form fields. This is a working
checklist, not a representation that these actions are already complete.

## Required materials to finish

- [ ] Meaningful actual Kiro development, honestly documented in KIRO_USAGE.md.
- [ ] Track: Healthcare & Biotech.
- [ ] All team members added (maximum four), with an authorized representative.
- [ ] Public GitHub URL containing source, assets, setup/testing instructions and
  the root `.kiro/` directory. Do not ignore `.kiro/`.
- [ ] Working website, functioning demo or downloadable test-build link, freely
  accessible to judges during judging. A local-only localhost URL is not a
  judge-accessible link. A repository with documented setup is useful; make the
  test-build access explicit on the form and verify it from another machine.
- [ ] Public video URL, duration less than 3:00, showing the functioning app.
- [ ] English text description, accurate Kiro write-up and testing instructions.
- [ ] Review third-party permissions/attribution; no unauthorized logos or music.
- [ ] Verify every link, submit, and preserve the submitted version. Do not alter
  the submission after the submission period without organizer permission.

The supplied rules require sufficient Kiro use at the judges' discretion and
request a write-up discussing features including but not limited to specs,
hooks, steering, MCP, PBT and powers. They do not separately say every listed
feature must be used. Avoid claiming a disabled MCP or prepared hook was used.

## Repository checks

```bash
git status --short
git check-ignore .kiro/specs/retrieval-upgrade/requirements.md
git ls-files .kiro
git ls-files .env
```

`git check-ignore` should print nothing and exit 1 for a tracked-intended Kiro
file. `git ls-files .kiro` should list the specs, steering and hooks after adding
them. `git ls-files .env` should be empty. Check for other secret-bearing files
as well. Keep .env.example; exclude virtual environments, node_modules, runtime
databases, raw data downloads and caches. Run the staged credential scan before
committing. If a real key was previously exposed, removal alone does not revoke it.

Fresh setup in a separate directory:

```bash
bash scripts/setup.sh
.venv/bin/python -m pytest tests -q
python3 scripts/check_secrets.py
npm run dev
```

Without .env credentials, judges can run the disclosed eight-check fictional demo,
review citations/owners, export an approved brief and group synthetic feedback.
Live findings for custom apps require their own permitted provider configuration;
do not give out your provider key. Keep the existing unauthed API local. If you
choose to host publicly, provide isolation, restricted demo behavior and appropriate
access controls first. No public deployment is included or claimed in this ZIP.

## Accurate product description starting point

GoLive Impact Copilot helps a healthcare rollout reviewer compare proposed-app
documentation with a hospital's supplied current workflow. It drafts role-specific
changes, gaps and vendor questions with source excerpts, supports accountable
human review and export, and links post-launch staff reports to earlier concerns.
It combines bounded BM25 retrieval, structured Gemini output and excerpt checking.
Its demonstration rollout is fictional; attributed public research and historical
hospital aggregates are separately labeled. It does not certify integration,
approve clinical deployment or demonstrate measured hospital benefit.

## Three-minute video plan (target 2:45)

- 0:00–0:20: reviewer, proposed rollout and document-comparison problem.
- 0:20–1:35: app running; finding; both sources; owner/content approval; brief.
- 1:35–2:00: unfamiliar-document example and honest coverage/uncertainty limits.
- 2:00–2:35: actual Kiro spec iteration, implementation and hook/test output.
- 2:35–2:45: prototype limits and next validation step.

Do not imply all tests measure Gemini accuracy. The eight planted checks test
the scenario rules; property tests check citation/chunking contracts; mocked API
tests check control flow and validation. Real utility still needs reviewer study.
