# Kiro Usage — GoLive Copilot

## Development approach

I provided the product requirements and instructions, and used Kiro’s AI coding agent to rebuild and implement the prototype. Kiro generated and refined code, assisted with testing, and helped prepare documentation. I reviewed the results and requested revisions.

## Implementation

Kiro helped implement:

- React frontend and FastAPI backend.
- SQLite storage and application APIs.
- Document ingestion, evidence retrieval, and clinical synonym support.
- Gemini integration with structured outputs and citation validation.
- Impact reviews, reviewer assignments, and approval workflows.
- Staff-feedback grouping and links to earlier findings.
- Role briefs and PDF, CSV, and JSON exports.
- Regression tests and property-based tests.

The application includes a disclosed deterministic demo mode that works without an LLM API key.

## Specifications

I organized development around requirements, design, and task documents in `.kiro/specs/`.

These documents helped turn feature requests into clear implementation steps. Compared with open-ended coding prompts, specifications made expected behavior and verification easier to follow.

For example, Kiro created the role-brief evidence specification and implemented exports containing reviewer notes, supporting quotations, source titles, and page or section references.

## Steering

I supplied product, evidence, and verification instructions to guide Kiro. These covered application scope, source attribution, credential handling, and testing expectations.

## MCP

Kiro used the `public-docs-fetch` MCP server to retrieve Gemini structured-output documentation and compare it with the application’s Pydantic schema approach.

## Testing

Kiro helped develop regression tests and Hypothesis property-based tests for retrieval and evidence handling.

The role-brief feature also included three regression tests checking evidence details in exported PDFs.

Verification commands:

    npm run build
    .venv/bin/python -m pytest tests -q
    python3 scripts/check_secrets.py

## Hooks and Powers

Test hooks were explored, but automatic execution was not confirmed. Tests were run manually.

No Kiro Powers were used.