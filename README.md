# wp2hugo

A modular Python migration tool to convert WordPress SQL dumps into Hugo Page Bundles, optimized for the **Blowfish** theme.

## 📁 Project Structure

### Source Code
- **`main.py`**: Application entry point and orchestrator.
- **`config.py`**: Central configuration and environment settings.
- **`src/`**: Modular logic for SQL ingestion, manifest generation, and content creation.
- **`src/utils/html_cleaner.py`**: Surgical HTML cleaning and shortcode transformation.

### Output (Generated)
- **`output/content/`**: Your new Hugo content folder.
- **`output/assets/i/`**: Downloaded images and media.
- **`output/meta/`**: Database, manifest, logs, asset queue, and download history.

## Version Log

- **v1.6.1**: Aligned front matter with official Blowfish schema (using `featureimage` and adding `summary`).
- **v1.6.0**: Implemented Stage 5: Link Transformation.
- **v1.5.2**: Security update. Moved `SITE_DOMAIN` and `WP_PREFIX` to `.env` file to protect site identity.
- **v1.5.1**: Documentation overhaul. Updated README and Specs with all CLI flags and workflow details.
- **v1.5.0**: Added `download_history.json` to track successes/failures. Asset downloader now has persistent resume memory.
- **v1.4.0**: Added fail-safe asset downloading. Script now stops on HTTP errors by default. Added `--force-continue` and `--skip-codes`.
- **v1.3.0**: Consolidated asset downloading into `main.py` using the `--assets-only` flag.
- **v1.2.0**: Architectural refactor. Logic moved to `src/` package.
- **v1.1.0**: Major structural refactor. Moved all generated files into `output/`.

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment:**
   Copy `.env.example` to `.env` and enter your site domain:
   ```bash
   cp .env.example .env
   ```

## Usage

### Full Migration
Runs the entire 7-stage workflow (SQL ingestion, manifest generation, content creation, etc.).
```bash
python main.py
```

### Asset Download Only
Downloads featured images and content media using an *existing* manifest.
```bash
python main.py --assets-only
```

### Advanced Asset Flags
- `--force-continue`: Ignore all HTTP errors and keep downloading.
- `--skip-codes=404,403`: Skip specific error codes but stop on others.

## Configuration (`config.py`)

- **RESET_FRESH**: Wipes the `output/` folder for a clean start.
- **DOWNLOAD_ASSETS**: Set to `True` to fetch remote images during full migration.
- **ADD_FOOTER_SHORTCODE**: Inject a specific Hugo shortcode into every page.
