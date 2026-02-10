# Quickstart: DOU Scrapper MVP

## Prerequisites
- Python 3.11+
- `uv` (recommended) or `pip`

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   uv sync
   # OR
   pip install -r requirements.txt
   ```

## Configuration

Create a `config.yaml` in the root:
```yaml
schedule:
  time: "08:30"
  timezone: "America/Sao_Paulo"

keywords:
  - "indígena"
  - "funai"
  - "ibama"

storage:
  output_dir: "data"

logging:
  level: "INFO"
```

## Running

**Manual Run (Once)**:
```bash
python -m src.main --run-now
```

**Scheduled Mode (Daemon)**:
```bash
python -m src.main
```

## Testing

```bash
pytest tests/
```
