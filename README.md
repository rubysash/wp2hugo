# wp2hugo

A modular Python migration tool to convert WordPress SQL dumps into Hugo Page Bundles, optimized for the **Blowfish** theme.

## Why?

Hugo is faster, more secure, and costs less to host with nearly zero maintenance.   Wordpress is full of security and management nightmares.   This script allows you to convert wordpress data with the same structure into hugo so you do not lose any SEO juice.

## Overview

You will need to modify the blowfish theme to look the way you want.   This script only converts the text into markdown for use with Hugo.

1. Export your wordpress database as SQL using either phpmyadmin or via cli (see [MySQL Export instructions](docs/mysql-export.md)).   Save that export as "export.sql".  It should be a plain text file, not compressed.

2. Edit the .env  and config.py files as needed.   

3. Run `python main.py` and the script will create the files needed for copy into your hugo installation (you still need to install hugo as normal, this just converts wordress to markdown).   

**note*** Very large sites will take several minutes to an hour to download the images, because they are throttled at 1 image per second to get around wordfence and other types of WAF.


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

- **v1.6.3**: Added detailed comments to `config.py` explaining each setting and rationale.
- **v1.6.2**: Fixed documentation link to MySQL Export instructions.
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
