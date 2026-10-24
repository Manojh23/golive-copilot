Kiro Usage — GoLive Copilot
How I used Kiro

I used Kiro's AI coding agent as a development assistant for GoLive Copilot. Kiro helped generate and refine implementation code from my requirements, work through development tasks, review changes, and add tests. I guided the development, reviewed the generated changes, and remained responsible for the final application.

Kiro's contribution included hands-on code implementation, specification work, automated testing, external documentation review through MCP, and documentation cleanup. The sections below describe the concrete work and verification outcomes captured in the development notes.

One concrete example of Kiro's implementation work is the approved role-brief export. Kiro updated the backend code so each included finding can show the reviewer's note, all supporting source quotations, and the source title and page or section locator for each quotation. This carries the evidence from the application into the exported report.
Specifications and implementation
Kiro created a dedicated specification in .kiro/specs/role-brief-evidence/, organized into:
- requirements.md: the required report behavior and acceptance criteria.
- design.md: how to render evidence using the existing finding and citation data.
- tasks.md: implementation and verification steps.
Kiro then updated export_brief in backend/app.py and added three regression tests in tests/test_brief_evidence.py. The change removed the previous two-citation display limit and reused the existing paragraph helper to escape and wrap report text.

The spec provided a concrete target for implementation and testing. Compared with an open-ended coding prompt, this made the expected behavior easier to review: the report needed to preserve evidence details while retaining existing approval and role filtering.
Steering strategy
The repository includes three steering documents that Kiro read during the feature session:
- .kiro/steering/product.md: product scope and workflow context.
- .kiro/steering/evidence.md: evidence handling and attribution expectations.
- .kiro/steering/verification.md: verification expectations.
These documents supplied project context alongside the feature specification. The implementation retained source quotations and locators in the report, supporting the project's emphasis on traceable evidence.
Agent hooks
Two hooks are configured in .kiro/hooks/ with these intended actions:
- backend-tests.json: runs the Python test suite after matching backend or test file saves.
- credential-pattern-check.json: runs a credential-pattern check when the agent stops.
Kiro configured the backend test hook and attempted to trigger it. No automatic hook execution was observed during the recorded agent-tool edits, so I do not count the manually executed tests as hook runs. The hook configurations are included for inspection; successful automatic execution remains unverified.
MCP use
I used the public-docs-fetch MCP server configured in .kiro/settings/mcp.json. In the recorded verification session, Kiro successfully fetched Google's Gemini structured-output documentation and compared its Pydantic schema approach with backend/llm.py.

The comparison identified the use of model_json_schema() in the application. This was a documentation-based review, not a live Gemini API test or verification of every API field.
Testing and property-based tests
The recorded Kiro implementation session ran:
.venv/bin/python -m pytest tests -q
The baseline result was 34 passed, 1 warning. After the feature implementation, the result was 37 passed, 1 warning, including the three new report regression tests. These are results from that session, not a new test run for this write-up.

The report tests checked extracted PDF text for the evidence details, including source titles and locators. Visual PDF review was not performed in that session.

The project also includes Hypothesis property-based tests in tests/test_retrieval_upgrade.py. Property-based testing complements fixed examples by checking behavior across generated inputs. The recorded Kiro feature session added the three report regression tests described above; it does not establish authorship of the existing Hypothesis tests.
Powers
No Kiro Powers were used in the recorded sessions.
Scope and verification limits
The concrete session evidence covers the role-brief feature specification, backend implementation, regression tests, MCP documentation review, and documentation cleanup. Existing repository files alone do not establish which tool authored them, so this write-up does not assign every component to Kiro based only on its presence in the package.