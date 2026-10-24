Kiro development workflow
Project: GoLive Impact Copilot
Date: 24 October 2026
Tool: Kiro IDE, using agent chat and repository-based specs and steering.

This record describes Kiro's implementation and verification work on the existing GoLive prototype.
Spec-driven implementation
Kiro created requirements, design, and tasks in .kiro/specs/role-brief-evidence/, then implemented the specified PDF improvement in backend/app.py.

Approved role briefs now include the reviewer's note when supplied, all supporting quotations, and each quotation's source title, page or section locator, and chunk ID. Kiro reused the existing escaping and text-wrapping helper and preserved role filtering, approval filtering, stale-review checks, and the other exports. No database migration was needed.

The specs made the acceptance criteria explicit: include approved evidence, exclude unapproved findings, and omit empty reviewer-note labels.
Steering and tests
Kiro read .kiro/steering/product.md, evidence.md, and verification.md. These guided source traceability, human review, and preservation of local settings and saved data.

Kiro added three behavioral tests in tests/test_brief_evidence.py:
- Approved PDFs include the reviewer note, supporting quotation text, source titles and locators, while excluding unapproved findings for the same role.
- Draft PDFs are labeled and include unapproved findings.
- Findings without a reviewer note do not show an empty note label.
The full suite passed with 37 tests, compared with the 34-test baseline. The suite includes existing Hypothesis properties for chunk coverage and citation validation. These check text handling and traceability, not LLM accuracy. Kiro also ran the credential-pattern scanner manually; no configured credential patterns were detected.
Agent hook
Kiro recreated .kiro/hooks/backend-tests.json using its native createHook tool. The PostFileSave hook targets backend and test Python files and runs:
.venv/bin/python -m pytest tests -q
After a new session and a test-file docstring edit, Kiro's interface recorded “1 hook triggered” and “Run Command Hook — Backend regression and property checks.” The captured log does not include that hook run's stdout or exit status, so successful completion of the hook-run tests is unconfirmed. The 37-test result above was obtained separately.
MCP documentation check
After installing uv and enabling the configured server, Kiro successfully used public-docs-fetch::fetch to retrieve:

https://ai.google.dev/gemini-api/docs/structured-output

Kiro compared the retrieved Pydantic schema example with backend/llm.py. Both derive a JSON schema using model_json_schema(). The retrieved SDK example uses the interactions API, while this application uses generateContent; the comparison confirms the schema-generation approach, not full API compliance or live-model correctness.
Final cleanup and limits
Kiro removed four obsolete starter/update guides and updated their README references. The root .kiro/ folder, tests, setup instructions, third-party notices, and submission checklist were retained.

The PDF change was checked through automated PDF text extraction. These Kiro sessions did not perform browser visual verification or a live Gemini evaluation. No Kiro CLI, Web, Crew, or Powers usage is claimed. Hook-trigger observation and successful MCP retrieval are distinguished from unverified execution outcomes.