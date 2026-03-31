# Project Specifications: wp2hugo

This document details the modular scripts, directory structure, and the 7-stage technical execution plan.

## 📁 Directory Structure

```text
wp2hugo/
├── main.py              # Central orchestrator & CLI entry point
├── config.py            # User configuration hub
├── src/                 # Logic package
│   ├── utils/           # Shared utilities (HTML cleaning, etc.)
│   ├── ingest_sql.py    # MySQL -> SQLite Parser
│   ├── ...              # Other modular stages
├── output/              # Generated Migration Data
│   ├── content/         # Hugo Page Bundles
│   ├── assets/i/        # Downloaded media
│   └── meta/            # Logs, Database, Manifest, and History
```

## 🛠️ CLI Flags & Usage

### Full Migration
Runs Stages 0 through 6.
```bash
python main.py
```

### Asset Recovery
Triggers Stage 4 only using the existing manifest.
```bash
python main.py --assets-only
```

### Fail-Safe Controls (Asset Stage)
- `--force-continue`: Ignore all HTTP errors and attempt every download in the queue.
- `--skip-codes=404,403`: Resume downloading, skipping specific errors but stopping on others (like 500).

## ⚙️ The 7-Stage Workflow

### 0. Pre-flight & Reset
- **Cleanup:** Wipes the `output/` directory if `RESET_FRESH` is enabled.
- **Validation:** Confirms `export.sql` exists and Python dependencies are met.

### 1. Data Ingestion (`ingest_sql.py`)
- Parses raw `.sql` line-by-line, converting MySQL syntax to SQLite.
- Audits total rows vs. published content to ensure a clean source.

### 2. Manifest Generation (`generate_manifest.py`)
- Builds the "Source of Truth" JSON.
- Resolves recursive category hierarchies and maps featured image IDs to actual URLs.

### 3. Content Generation (`build_content.py`)
- **Cleaning:** Uses `src/utils/html_cleaner.py` to strip Gutenberg noise and map shortcodes.
- **Front Matter:** Follows official [Blowfish Front Matter](https://blowfish.page/docs/front-matter/) schema.
- **Bundling:** Creates `index.md` files in nested folders matching the category path.
- **Shortcodes:** (Optional) Injects a custom footer shortcode via `ADD_FOOTER_SHORTCODE`.

### 4. Asset Acquisition (`fetch_assets.py`)
- **Memory:** Checks `download_history.json` to skip previously successful (200) downloads.
- **Formatting:** Renames featured images to `featured.[ext]` per Blowfish spec.
- **Security:** Uses browser-mimicking `USER_AGENT` and `DOWNLOAD_DELAY` to mitigate WAF blocks.

### 5. Link Transformation (Pending)
- Post-processes Markdown to swap absolute WP links for Hugo `{{< ref >}}`.

### 6. Validation & Audit (Pending)
- Final integrity check of file counts and media availability.
