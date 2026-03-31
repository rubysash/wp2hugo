# Gemini Project Mandates: wp2hugo

This project is a migration utility designed to convert WordPress SQL dumps into a Hugo-compatible directory structure, specifically optimized for the **Blowfish** theme.

## Core Architectural Principles

- **Modular Python (PEP8):** All logic is encapsulated in the `src/` package. The root contains only execution entry points (`main.py`) and configuration (`config.py`).
- **Surgical SQL Parsing:** Processes raw WordPress SQL dumps into a local SQLite database for relational mapping.
- **Output Isolation:** All generated data (content, media, logs, DBs) must be stored within an `output/` directory, sub-divided into `content/`, `assets/`, and `meta/`.
- **Source of Truth (Manifest):** A `manifest.json` is generated to map all site relationships (categories, authors, assets) before content generation.
- **Blowfish Integration:** Automatically configures front matter and Page Bundle structures matching Blowfish conventions (`featured.[ext]`).

## Versioning & Change Management
- **Version Log:** Every time code logic is modified or a new feature is added, the `VERSION` in `config.py` must be incremented (Semantic Versioning), and a corresponding entry must be added to the **Version Log** in `README.md`.
- **Traceability:** Ensure the version log briefly describes the technical impact of the change.

## Media & Asset Mandates
- **Fail-Safe Downloading:** The script must default to stopping on HTTP errors (403, 404, 500) to protect IP reputation and data integrity.
- **Persistent Resume:** Successes and failures must be tracked in `download_history.json` to allow reliable resumption without re-downloading existing files.
- **CLI Overrides:** Support for `--force-continue` and `--skip-codes` is mandatory for flexible asset acquisition.

## Workflow Mandates
- **Idempotency & Cleanup:** `RESET_FRESH` toggle allows for a clean environment wipe before each run.
- **Fail-Fast:** Stage 0 (Pre-flight) validates environment, SQL integrity, and dependencies.
