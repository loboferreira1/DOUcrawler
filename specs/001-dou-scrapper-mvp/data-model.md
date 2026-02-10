# Data Model

## Entities

### Match Entry (Storage Unit)
Represents a single discovery of a keyword in an article.
Append-only to `.jsonl` files.

```json
{
  "keyword": "indígena",        // The configured keyword that matched
  "context": "...texto da portaria onde cita a terra indígena do xingu...", // ~150 chars padding
  "date": "10/02/2026",         // Publication date (DD/MM/YYYY)
  "section": "dou1",            // Source section slug
  "url": "https://www.in.gov.br/web/dou/-/at-123", // Direct link
  "title": "Portaria nº 123",   // Article title (if available)
  "capture_timestamp": "2026-02-10T08:31:00-03:00" // ISO 8601 with timezone
}
```

### Configuration (`config.yaml`)
User settings.

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
  format: "jsonl" // fixed for MVP

logging:
  level: "INFO"
  file: "logs/scrapper.log"
```
