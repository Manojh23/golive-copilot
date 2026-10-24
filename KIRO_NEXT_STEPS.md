# Do this in the actual Kiro app

Prepared source/configuration is not proof of Kiro use. Keep any genuine earlier
Kiro activity you already recorded; the updater preserves KIRO_USAGE.md.

## 1. Open the original project after the update

Open `~/Downloads/golive-copilot` in Kiro. Use the integrated terminal to run the
setup and tests in UPDATE_EXISTING_PROJECT.md. Do not replace your .env.

## 2. Give Kiro this implementation task

Paste into Kiro chat / its spec workflow:

> Read .kiro/specs/retrieval-upgrade/requirements.md, design.md and tasks.md,
> plus the steering documents. The baseline was prepared outside Kiro; do not
> claim you authored it. Refine the continuation requirement, then implement an
> accessible Extracted workflow facts section on Impact review using
> assessment.extracted_facts. Show each subject, relationship, object, source
> title and exact supporting quote, with a button opening the existing source
> viewer. Make clear that checked quotations do not verify interpretation.
> Hide the section when there are no facts. Preserve existing flows and local
> data. Add an appropriate check for data with/without facts, build the frontend,
> run the backend tests, and explain the results. Update only the tasks you
> actually completed and help me record this session in KIRO_USAGE.md.

This is a meaningful missing reviewer feature, rather than simply adding files
as evidence. Review the result; do not claim features or tests that did not run.
If you complete a different meaningful task, record that task accurately.

## 3. Actually verify the hooks

The included `.kiro/hooks/*.json` definitions use the current v1 format from
Kiro's official docs: https://kiro.dev/docs/hooks/ . One runs isolated backend
tests after an agent saves a backend/test Python file. The other runs an offline
credential-pattern scan after an agent turn. The latter is not a Git commit gate.

Open Agent Hooks, check that both are recognized/enabled, and inspect their
output after relevant Kiro work. If your installed Kiro uses the older format,
ask Kiro through Agent Hooks → create hook to generate equivalent definitions
for that version. Do not leave duplicate active hooks. Match the events and
commands above rather than guessing JSON field names. Running pytest in a normal
terminal does not establish a Kiro hook fired.

Commands the hooks run:

```bash
.venv/bin/python -m pytest tests -q
python3 scripts/check_secrets.py
```

Before committing, also run `python3 scripts/check_secrets.py --staged` in your
Git repository. This inspects the staged bytes, never prints credential values,
and deliberately fails outside Git. The scanner is pattern-based, not a guarantee.

## 4. Optional MCP, only if useful and time permits

`.kiro/settings/mcp.json` has a **disabled** fetch server, matching the official
example at https://kiro.dev/docs/mcp/configuration/ . No MCP use is claimed.
It requires `uvx` (from uv). If available, enable MCP support, set `disabled` to
false, save and confirm the server connects in Kiro. No API credential is needed.
Tools require approval because autoApprove is empty.

Ask Kiro to use that MCP to fetch
https://ai.google.dev/gemini-api/docs/structured-output and compare its JSON
schema guidance against backend/llm.py. Record the actual URL, useful result and
any change you reviewed. Do not send private documents or keys. If you do not use
it, leave disabled and write **MCP not used**. MCP is not required by the app.

## 5. Verify the actual model and unfamiliar-document behavior

```bash
.venv/bin/python scripts/verify_live_llm.py
```

This makes a real API call. You previously demonstrated a successful connectivity
test; repeat after updating if needed. It does not establish medical accuracy.
Use examples/unfamiliar-referral/ for a small independent synthetic test: inspect
the mismatch in v1, then replace with v2 and check whether it disappears, then
try v3 and expect an unresolved question. Do not upload the answer guide.
For the fact panel, use a permitted main source that produces more than 14 chunks;
the default short demo intentionally skips the extra fact-extraction calls.

Record actual results and limitations, including any false positives. The
automated mocked fact test does not replace this live-model check.

## 6. Record actual usage and submit

Use your existing KIRO_USAGE.md. Include date, Kiro surface/version, spec
iterations, actual changed files, real hook output, test results, what PBT checked,
MCP/powers only if used, and remaining limits. Explain what came from this
outside-Kiro starter versus your Kiro implementation.

Read SUBMISSION_CHECKLIST.md. Do not mark planned work complete.
