# DOU Crawler & Dashboard

Automated daily monitoring of Diário Oficial da União (DOU) with a built-in visualization dashboard.

##  Features

- **Automated Scraping**: Fetches daily editions of DOU (Sections 1, 2, and 3) directly from `in.gov.br`.
- **Smart Matching**: configurably searches for keywords in article titles and bodies, extracting relevant context (~150 chars).
- **Rule-Based Configuration**: Define complex search rules targeting specific sections (e.g., "Look for 'Licitação' only in Section 3").
- **Visual Dashboard**: A **Streamlit** app to browse, filter, and analyze the captured data.
- **CI/CD Automation**: A **GitHub Actions** workflow runs the scraper daily at **07:00 AM (BRT)** and commits results back to the repo.
- **Robustness**: Handles network retries, pagination, and "No Edition" scenarios gracefully.

##  Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/loboferreira1/DOUcrawler.git
   cd DOUcrawler
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

##  Configuration (`config.yaml`)

The behavior of the scraper is controlled by `config.yaml`. You can define multiple rules:

```yaml
rules:
  - name: "Nomeações na Força Nacional"
    title_terms:
      - "PORTARIA MJSP"
    body_terms:
      - "força nacional"
    sections: ["dou1"]  # Only look in Section 2

  - name: "Avisos e Editais Recentes"
    title_terms: []     # Empty means match any title
    body_terms:
      - "aviso de licitação"
      - "edital de notificação"
    sections: ["dou3"]  # Only look in Section 3

logging:
  level: "INFO"
```
##  Usage
### 1. Manual Scraper Run
To trigger an immediate run for the current date (useful for testing or local updates):

```bash
python -m src.main --run-now
```

### 2. Launch Dashboard
To view the collected data in the interactive dashboard:

```bash
streamlit run src/app.py
```
Access in your browser at `http://localhost:8501`.

##  Automation (GitHub Actions)

This repository includes a workflow `.github/workflows/scrape_daily.yml` that:
1.  **Triggers** every day at 10:00 UTC (07:00 AM Brasília Time).
2.  **Runs** the scraper inside a GitHub runner.
3.  **Commits** specific results (`data/*.jsonl`) back to the branch.

This ensures your dataset is always up-to-date without needing a dedicated server.

##  Deployment (Streamlit Cloud)

1.  Push this code to GitHub.
2.  Go to [share.streamlit.io](https://share.streamlit.io/).
3.  Deploy a new app pointing to `src/app.py`.
4.  **Done!** Streamlit Cloud will automatically pull the daily data updates pushed by the GitHub Action.

##  Project Structure

- `src/main.py`: Scraper orchestrator and CLI entry point.
- `src/app.py`: Streamlit dashboard application.
- `src/config.py`: Configuration loader and validation.
- `src/parser.py`: HTML parsing and text normalization logic.
- `src/downloader.py`: Network handling and DOU API interaction.
- `data/`: Storage for JSONL files (database).
- `.github/workflows/`: Automation scripts.
