---
description: "Task list for Feature 001: Automated Daily DOU Monitor"
---

# Tasks: Automated Daily DOU Monitor (MVP)

**Prerequisites**: plan.md, spec.md, research.md, data-model.md
**Tests**: Strict TDD is enforced. Write tests before implementation for every task.

## Phase 1: Setup & Foundations

**Purpose**: Initialize project, dependencies, and core data structures.

- [x] T001 Create `pyproject.toml` with `uv` or `pip` (Python 3.11+, requests, bs4, lxml, tenacity, etc.).
- [x] T002 Create project directory structure (`src/`, `tests/`, `data/`, `logs/`).
- [x] T003 Create `config.yaml` with default settings and `src/models.py` for `MatchEntry`/`Config` dataclasses.
- [x] T004 Implement `src/config.py` to load YAML and setup basic `structlog` logging.
- [x] T005 Create tests for configuration loading in `tests/test_config.py`.

## Phase 2: User Story 2 - Search & Extraction (The Brain)

**Goal**: Accurately find keywords in text and extract context (Case/Accent Insensitive).
**Independent Test**: Feed raw HTML/Text -> Verify Match Objects.

- [x] T006 [US2] Create `tests/test_parser.py` (HTML cleaning, title extraction).
- [x] T007 [P] [US2] Implement `src/parser.py` (HTML -> Clean Text, NFD normalization).
- [x] T008 [US2] Create `tests/test_matcher.py` (Keyword matching, context extraction windows).
- [x] T009 [P] [US2] Implement `src/matcher.py` (Find keywords, slice context ~150 chars).

## Phase 3: User Story 3 - Persistence (The Memory)

**Goal**: Save matches to JSONL files without data loss.
**Independent Test**: Save object -> Check File Content.

- [x] T010 [US3] Create `tests/test_storage.py` (File creation, append, data integrity).
- [x] T011 [US3] Implement `src/storage.py` (JSONL handler, unique directory management).

## Phase 4: User Story 1 - Daily Monitor & Fetching (The Body)

**Goal**: Fetch actual DOU pages and orchestrate the pipeline.
**Independent Test**: Mock Network -> Run Pipeline -> Verify calls.

- [X] T012 [US1] Create `tests/test_downloader.py` (Mock HTML pages, pagination, 404s, retries).
- [X] T013 [P] [US1] Implement `src/downloader.py` (Requests, Tenacity, URL manipulation for `secao`/`data`).
- [X] T014 [US1] Create `tests/test_scheduler.py` (Job trigger logic).
- [X] T015 [US1] Implement `src/scheduler.py` (APScheduler configuration).
- [X] T016 [US1] Create `tests/test_main.py` (Integration flow).
- [X] T017 [US1] Implement `src/main.py` (CLI entry point, orchestrator loop).

## Phase 5: Polish & Integration

- [X] T018 Run full integration test suite and verify 100% coverage.
- [X] T019 Implement graceful exit for "No Edition Today" (404 on `leiturajornal`).
- [X] T020 Dockerfile (optional) or README instructions for running as a service.

## Dependencies

- Phase 1 blocks all.
- Phase 2 & 3 are parallelizable.
- Phase 4 depends on P2 & P3 components (imports).

## Parallel Execution Examples

- Developer A: T007 (`parser.py`)
- Developer B: T009 (`matcher.py`)
- Developer C: T011 (`storage.py`)
