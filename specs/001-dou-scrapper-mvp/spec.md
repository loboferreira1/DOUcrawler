# Feature Specification: Automated Daily DOU Monitor (MVP)

**Feature Branch**: `001-dou-scrapper-mvp`
**Created**: 2026-02-10
**Status**: Draft
**Input**: User description: "Automated daily tool that monitors the Diário Oficial da União (DOU)..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Daily Automated Monitoring (Priority: P1)

As a user, I want the tool to wake up daily, find the latest DOU edition, and determine if there are new matches for my keywords, so that I don't have to manually check the website.

**Why this priority**: Core value proposition. Without automation and fetching, there is no product.

**Independent Test**:
- Can be tested by mocking the scheduler trigger and the generic "fetch today's edition" function.
- Verify logging of "Execution started", "Edition found/not found", and "Execution finished".

**Acceptance Scenarios**:
1. **Given** the scheduler triggers at 08:30, **When** the script runs, **Then** it logs the attempt and checks for the current date's edition.
2. **Given** today's edition is not yet available, **When** the script runs, **Then** it logs "No edition found", does not crash, and exits clean (or retries if configured).
3. **Given** the script was already run today successfully, **When** it runs again, **Then** it avoids processing the same edition/matches again (idempotency).

---

### User Story 2 - Keyword Search & Context Extraction (Priority: P1)

As a user, I want the system to scan the full text of the edition for my specific keywords (e.g., "indígena", "funai") and extract the surrounding context, so that I can quickly judge if the mention is relevant.

**Why this priority**: This is the functional "brain" of the tool.

**Independent Test**:
- Feed sample text with known keywords.
- Verify that matches are found regardless of case or accents.
- Verify that extracted context includes ~100-200 chars around the keyword.

**Acceptance Scenarios**:
1. **Given** a text containing "Fundação Nacional dos Povos Indígenas", **When** searching for "fundação nacional dos povos indígenas", **Then** a match is recorded.
2. **Given** a text with "Ação da Funai em...", **When** searching for "FUNAI", **Then** it matches (case-insensitive).
3. **Given** a text with "fôrça nacional", **When** searching for "forca nacional", **Then** it matches (accent-insensitive).
4. **Given** a match is found, **When** data is extracted, **Then** it includes the keyword, ~150 chars of context, source URL, and section.

---

### User Story 3 - Persistent Data Storage (Priority: P1)

As a user, I want all matches to be saved to a structured file system (JSONL), organized by keyword, so that I can consume the data later without it being overwritten.

**Why this priority**: Data loss or overwrite would render the tool useless.

**Independent Test**:
- Mock the file system.
- Save a match.
- Verify file existence and content format.
- Verify append behavior on subsequent saves.

**Acceptance Scenarios**:
1. **Given** a new match is found, **When** saving, **Then** it is appended to `data/{keyword}.jsonl` (or similar structure).
2. **Given** the file does not exist, **When** saving, **Then** the file is created.
3. **Given** invalid characters in content, **When** saving, **Then** data is valid JSON (properly escaped).

---

## Functional Requirements

1. **Scheduling & Execution**:
   - Run daily on a configurable schedule (default 08:30).
   - Timezone: `America/Sao_Paulo`.

2. **Data Acquisition (Fetch)**:
   - **Primary**: Attempt to download XML from official sources (e.g., INLABS) if accessible.
   - **Fallback**: Scrape HTML from the official website (e.g., `www.in.gov.br`).
   - Must handle network timeouts with a retry mechanism.

3. **Search Engine**:
   - Input: List of keywords from configuration.
   - Logic: Exact match but Case-Insensitive and Accent-Insensitive.
   - Normalization: NFD/NFC for consistent comparison.

4. **Extraction**:
   - For every match: capture Keyword, Context (~100-200 chars before/after), Date, Edition Number/Section, Source URL.

5. **Storage**:
   - Format: JSON Lines (`.jsonl`).
   - Strategy: Append-only.
   - Organization: Categorized files (e.g., per keyword/category).

6. **Configuration**:
   - External configuration file (e.g., YAML) to define:
     - Keywords list.
     - Output directory path.
     - Schedule time.
     - Log level.

## Non-Functional Requirements

- **Idempotency**: Preventing duplicate entries for the same match (Key: Date + URL + Keyword + Snippet match).
- **Resilience**: 
  - Retry on network failures (e.g., 3 attempts).
  - Silent exit on "No Edition" available for the day.
- **Observability**: Structured logs for all major events (Start, Match Found, Error, End).
- **Constraints**: 
  - Implementation must follow project strict tech stack (Python 3.11+, specific libraries).
  - No User Interface (CLI/Background process only).

## Success Criteria

- The system runs automatically on the defined schedule.
- When run against a published edition:
  - Expected keywords are identified correctly.
  - Output files are created/updated with correct JSON structure.
  - Matches contain accurate context and metadata.
- System handles "page not found" or "no internet" without crashing (logs error and retries/exits).
- All functional requirements are verified by automated tests.

## Assumptions

- We can deduce the URL pattern for today's DOU or find a main "latest" page to scrape.
- Keywords are provided in Portuguese.
- "Context" extraction does not need NLP, just string slicing.
- "Categories" in the prompt are simple mappings (e.g., "funai" -> "indigena"). If mapping is not provided, use keyword as category.
