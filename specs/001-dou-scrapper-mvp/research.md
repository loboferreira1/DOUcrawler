# Research: Data Access Strategy for DOU

**Status**: Complete
**Date**: 2026-02-10

## Unknown 1: Data Source (XML vs HTML)
- **Decision**: HTML Scraping via `in.gov.br`.
- **Rationale**: Official XML/Dados Abertos are updated monthly, not daily. The MVP requires same-day monitoring.
- **Alternatives**: INLABS legacy FTP (deprecated/inaccessible).

## Unknown 2: URL Structure
- **Pattern**: `https://www.in.gov.br/leiturajornal`
- **Parameters**: `?secao={slug}&data={dd-mm-yyyy}`
- **Section Slugs**:
  - Seção 1: `dou1`
  - Seção 2: `dou2`
  - Seção 3: `dou3`
  - Extras: `do1e`, `do2e`, `do3e`

## Unknown 3: Pagination & Crawling
- **Discovery**: The `leiturajornal` page lists articles with "Next" pagination.
- **Strategy**:
  1. Determine date (today).
  2. For each section [dou1, dou2, dou3]:
     a. Fetch `leiturajornal` page 1.
     b. Parse article links (hrefs to `/web/dou/-/title-id`).
     c. Extract text snippets from list view OR visit individual pages if full text needed (MVP decision: Visit individual pages for reliable context).
     d. Follow "Próximo" link if exists.
