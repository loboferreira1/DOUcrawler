# Implementation Plan: Automated Daily DOU Monitor (MVP)

**Branch**: `001-dou-scrapper-mvp` | **Date**: 2026-02-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-dou-scrapper-mvp/spec.md`

## Summary

This tool will automate the daily monitoring of the Diário Oficial da União (DOU). It will run on a schedule (or manual trigger), attempt to fetch the latest edition from official sources (prioritizing XML, falling back to HTML), search for user-defined keywords (case/accent insensitive), extract surrounding context, and save matches to append-only JSONL files. The implementation will be strictly in Python 3.11+ using a modular architecture (downloader, parser, storage) and adhering to strict TDD.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- `requests` (HTTP)
- `beautifulsoup4`, `lxml` (Parsing)
- `tenacity` (Retries)
- `pyyaml` (Config)
- `python-dateutil`, `pytz` (Time/Dates)
- `structlog` (Logging)
- `APScheduler` (Scheduling)
**Storage**: Local File System (JSON Lines `.jsonl`)
**Testing**: `pytest`, `pytest-mock`, `responses` (Strict TDD)
**Target Platform**: CLI / Background Service (Cross-platform Python)
**Project Type**: Single Python Project (CLI)
**Performance Goals**: Complete daily scan < 5 mins; handle ~10 keywords against ~500 pages.
**Constraints**: No UI, no external API wrappers, strictly defined libs.
**Scale/Scope**: MVP scope (Daily inputs, limited keywords).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle I (Quality)**: Senior mindset, no vibe coding.
- [x] **Principle II (MVP)**: No UI, CLI only, daily scrape.
- [x] **Principle III (TDD)**: "Test-First" workflow is acknowledged.
- [x] **Principle IV (Quality)**: Files <300 lines, extensive linting/typing.
- [x] **Principle VII (Locale)**: Date/Timezone settings correctly identified.
- [x] **Stack Lock**: Only permitted libraries listed in Technical Context.

## Project Structure

### Documentation (this feature)

```text
specs/001-dou-scrapper-mvp/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── config.py         # Config loading
├── main.py           # Entry point
├── scheduler.py      # Job runner
├── downloader.py     # INLABS/HTML fetcher
├── parser.py         # Text extraction & normalization
├── matcher.py        # Keyword search logic
└── storage.py        # File system persistence
tests/                # Mirror src structure
```
