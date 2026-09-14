# CLAUDE.md — Instructions for Claude Code

## Project
SMMS-Agent — multi-agent GenAI extension of Chandigarh Admin's meeting management system.
Full spec: @docs/PROJECT_SPEC.md

**This is a production project.** It deploys to Azure (Central India) and every change ships
through GitHub Actions CI/CD. No throwaway scripts, no manual deploys, no "we'll add tests later."

## Non-negotiables
- Everything runs on Azure Container Apps, provisioned by Bicep in `infra/`. No hand-created resources.
- Every merge to `main` goes through CI (lint + typecheck + test + security scan) and `cd-dev`.
- Secrets live in Azure Key Vault, accessed via Managed Identity. Never in code, never in `.env` committed.
- Data residency: India regions only (DPDP Act 2023). See @docs/PROJECT_SPEC.md §13.

## Code conventions
- Python 3.12, Ruff + Mypy strict
- FastAPI async everywhere, Pydantic v2 models
- SQLAlchemy 2.0 async style — no sync sessions
- React Native TypeScript, Zustand for state, Tailwind (nativewind)
- Every new endpoint: add unit test + integration test
- Every prompt: version it in `src/prompts/` and add a promptfoo case
- Structured JSON logs; every agent action emits an `audit_log` row (FR-22)

## Never do
- Generate synchronous DB code
- Introduce a new dependency without asking
- Skip the eval gate in CI
- Give an MCP server a write tool that fires without explicit human approval
  (FR-19 — no autonomous side effects. Read tools are free; `create_event`,
  `send_email`, `create_task` must be approval-gated at the API layer.)
- Let unredacted PII reach an LLM (NFR-07)

## Ask before
- Adding new npm/pip dependencies
- Changing schema (Alembic migration required)
- Editing any file under `infra/` (Bicep infra changes)
- Anything that increases Azure spend (budget ceiling: @docs/PROJECT_SPEC.md §7)

## Layout
```
apps/api/        FastAPI backend + LangGraph agents
apps/mobile/     React Native / Expo app
services/mcp-*/  4 custom MCP servers (calendar, transcription, email, tasks)
infra/           Bicep IaC
docs/            PROJECT_SPEC.md
.github/workflows/  ci, cd-dev, cd-staging, cd-prod, security-scan, expo-mobile-build
```

## Reference
- Architecture + agent contracts: @docs/PROJECT_SPEC.md §9
- Functional requirements (FR-01..FR-22): @docs/PROJECT_SPEC.md §5
- Non-functional / SLOs: @docs/PROJECT_SPEC.md §6, §15
- Data model: @docs/PROJECT_SPEC.md §11
- Azure topology: @docs/PROJECT_SPEC.md §12
- Security: @docs/PROJECT_SPEC.md §13
- Testing strategy: @docs/PROJECT_SPEC.md §14
- Build plan: @docs/PROJECT_SPEC.md §16
