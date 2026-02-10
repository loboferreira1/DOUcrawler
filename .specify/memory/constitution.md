<!--
Sync Impact Report:
- Version change: Initial (1.0.0)
- List of modified principles: Defined Principles I through VII covering Workflow, Scope, TDD, Code Quality, Architecture, Git, and Localization.
- Added sections: Technology Stack (Locked Down).
- Templates requiring updates:
  - `templates/plan-template.md`: ✅ Checked (Generality ok)
  - `templates/spec-template.md`: ✅ Checked (Generality ok)
  - `templates/tasks-template.md`: ⚠ pending (Contradiction: "Tests are OPTIONAL". Needs update to reflect Strict TDD).
- Follow-up TODOs: None.
-->

# DOU Scrapper Constitution

## Core Principles

### I. Senior Engineering & Workflow
Senior software engineer quality is expected from day one: clean, maintainable, robust, and production-ready code. No vibe coding allowed. Development MUST strictly follow the Spec Kit workflow: `/specify` → `/plan` → `/tasks` → `/implement`, ensuring one task is completed at a time.

### II. MVP Scope & Resilience
Scope is strictly limiting to a daily automated scrape of the latest Diário Oficial da União (DOU) editions. Implementation does keyword search, extracts surrounding text context and source URL, and saves structured data categorized by keyword.
- **No UI/Dashboard**: Pure CLI script + data files/DB only. No Streamlit or web servers.
- **Fail-safe & Idempotent**: Must handle "no new edition", "no matches", network issues, and duplicates gracefully.
- **Observability**: Process must log everything using structured JSON.

### III. Strict Test-Driven Development (TDD)
Red → Green → Refactor cycle is mandatory. Write failing tests **before** any production code in every task.
- **Coverage**: 100% unit test coverage on logic (matching, extraction, normalization, storage).
- **Integration**: Mock HTTP/XML responses to test full pipeline on sample data.
- **Tools**: `pytest` only. Tests reside in `tests/` mirroring `src/`.
- **Validation**: Agent must show test pass output before considering implementation done.
- **Edge Cases**: Must cover empty results, malformed XML/HTML, encoding issues, and repeated runs.

### IV. Clean Code & Quality Standards
- **File Limits**: Maximum 300 lines per file — split mercilessly by responsibility (e.g., config, downloader, parser).
- **Functions**: Small (<50 lines), single responsibility, descriptive names.
- **Typing**: Mandatory type hints enforced with `mypy --strict`.
- **Linting**: `ruff` for formatting and linting (black-compatible).
- **Error Handling**: Custom exceptions, explicit handling, no silent fails, retries on transient errors.
- **Text Handling**: Case-insensitive + accent-insensitive keyword search (`unicodedata.normalize`).
- **Config**: External YAML file for keywords, paths, timezone, log levels.

### V. Spec / Plan / Tasks Architecture
Detailed separation of concerns is non-negotiable:
- **spec.md**: Defines WHAT + WHY, user acceptance criteria, example keywords, and output schema. Zero tech choices.
- **plan.md**: Defines architecture, module breakdown, chosen endpoints/libs, data flow, and error strategy.
- **tasks/**: Defines atomic changes/features per `.md` file. Rules: One logical change per task.
- **Constraint**: NEVER write code outside of explicit `/implement` on a task file. No jumping ahead.

### VI. Git & Commit Discipline
- **Atomic Commits**: One logical change, using Conventional Commits (`feat:`, `fix:`, `test:`, `refactor:`, `chore:`).
- **Branching**: `feat/xxx`, `fix/yyy`, `chore/zzz` per task.
- **Rule**: Main branch must always pass tests.
- **Messages**: English, clear, and in imperative mood.

### VII. Locale & Brazil-Specific Rules
- **Dates**: Parse, store, and log as `dd/mm/yyyy`.
- **Timezone**: `America/Sao_Paulo` for scheduling and timestamps.
- **Text**: Preserve Portuguese accents in storage, normalize only for search (NFD/NFC).

## Technology Stack (Locked Down)

**Language**: Python 3.11+ exclusively. No Node.js or other languages.

**Core Libraries**:
- `requests`, `beautifulsoup4`, `lxml` (Parsing)
- `tenacity` (Retries)
- `pyyaml` (Config)
- `python-dateutil`, `pytz` (Time/Dates)
- `structlog` or `logging` (Structured Logs)
- `pytest`, `pytest-mock`, `responses` or `vcrpy` (Testing)

**Data Access Priority**:
1. Official INLABS XML downloads (if active).
2. Fallback: Structured scrape from `https://www.in.gov.br` (Seções 1, 2, 3).
3. **Prohibited**: Reliance on third-party/unofficial APIs or scrapers.

**Storage**:
- MVP: Append-only JSON Lines (`.jsonl`) files.
- Optional: SQLite (single file).

**Scheduling**: APScheduler (in-process) or document native cron/Task Scheduler setup.

**Dependency Management**: `uv` (preferred), `pdm`, or `rye`. Use `venv`.

## Governance

This Constitution supersedes all other practices or defaults.
- **Amendments**: Any deviation (new library, UI addition, stack change) requires:
  1. A new task justifying the change.
  2. Explicit update to this file (version bump).
  3. Re-approval via `/constitution`.
- **Compliance**: All PRs and code reviews must verify compliance with these principles.

**Version**: 1.0.0 | **Ratified**: 2026-02-10 | **Last Amended**: 2026-02-10
