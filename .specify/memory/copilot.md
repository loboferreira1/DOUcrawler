# DOU Scrapper Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-10

## Active Technologies

- **Language**: Python 3.11+
- **Core Libs**: `requests`, `beautifulsoup4`, `lxml`, `tenacity`, `pyyaml`, `python-dateutil`, `structlog`
- **Infrastructure**: `APScheduler`
- **Testing**: `pytest`, `pytest-mock`, `responses`

## Project Structure

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

## Commands

- **Install**: `uv sync` or `pip install -r requirements.txt`
- **Run**: `python -m src.main`
- **Run Once**: `python -m src.main --run-now`
- **Test**: `pytest tests/`

## Code Style

- **Python**:
  - Max file size: 300 lines.
  - Max function size: 50 lines.
  - **Mypy strict** mandatory.
  - **Ruff** for linting/formatting.
  - Case-insensitive, accent-insensitive string handling.
  - TDD: Red-Green-Refactor.

## Recent Changes

- **001-dou-scrapper-mvp**: Initial MVP (Daily Monitor). HTML scraping strategy for `in.gov.br`.

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
