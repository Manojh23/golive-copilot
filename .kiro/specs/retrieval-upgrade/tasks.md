# Tasks and authorship

The checked items below were implemented outside Kiro in the supplied update.
They must not be described as Kiro-generated work. Unchecked items require a real
Kiro session; update the log with actual results, not planned actions.

- [x] Correct SQL source scoping and remove prefix-only context selection.
- [x] Add bounded balanced selection and coverage metadata.
- [x] Add source-specific structured fact extraction for long main documents.
- [x] Add property tests and regression tests for late evidence and retired versions.
- [x] Add tested credential scanner and non-destructive update helper.
- [x] Prepare current-format Kiro hook definitions and optional disabled MCP configuration.
- [ ] In Kiro, read requirements/design, inspect the prepared code and revise the spec where necessary.
- [ ] In Kiro, implement the extracted workflow facts panel described in requirement 8's continuation section.
- [ ] Verify the panel against an assessment with facts and one without; build the frontend and test the existing app flow.
- [ ] Trigger the backend test hook after an agent edit; inspect the hook output and resolve any failures.
- [ ] Observe the credential hook after an agent turn; run the staged scan before committing in Git.
- [ ] Optional: enable the fetch MCP, consult the public Gemini structured-output documentation, and record an actual useful result. If unused, say unused.
- [ ] Record actual Kiro actions, files, test outputs and limitations in KIRO_USAGE.md.
- [ ] Verify public repository, clean setup, working test build and public video under three minutes before final submission.
