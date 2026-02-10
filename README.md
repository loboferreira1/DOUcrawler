# DOU Scrapper (MVP)

Automated daily monitoring of Diário Oficial da União (DOU).

## Description
This tool scrapes the daily edition of the DOU for specific keywords, extracts the context, and saves the results in organized JSON Lines files.

## Features
- **Daily Monitoring**: Automatically fetches DOU (sections 1, 2, 3) at a scheduled time.
- **Robustness**: Retries on network failures, logs all actions.
- **Precision**: Extracts clean text and matches keywords (accent/case insensitive).
- **Storage**: Appends matches to JSONL files partitioned by keyword.

## Setup

1. **Install uv** (recommended):
   ```bash
   pip install uv
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -e .[dev]
   ```

3. **Configuration**:
   Edit `config.yaml` to set your target keywords and schedule.
   ```yaml
   keywords:
     - "licitação"
     - "portaria"
   schedule:
     time: "08:00"
   ```

## Running

### Service Mode (Default)
Start the daily monitor service:

```bash
uv run python -m src.main
```

The service will run indefinitely, waking up at the scheduled time to process the daily edition.

### Manual Run
To trigger an immediate run for the current date (useful for testing or ad-hoc updates):

```bash
uv run python -m src.main --run-now
```

## Data

Matches are saved to the `data/` directory (configurable) as `{keyword-slug}.jsonl`.

## Development

See `specs/001-dou-scrapper-mvp/plan.md` for architecture details.

Run tests:
```bash
uv run pytest
```
