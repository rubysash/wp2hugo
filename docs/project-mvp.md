# Project MVP: wp2hugo

The goal of the MVP is to achieve a successful "End-to-End" conversion of a standard WordPress SQL dump into a functional Hugo site with the Blowfish theme, even if some advanced features (like automatic asset downloading) are handled manually or in later phases.

## MVP Feature Set (The "Must-Haves")

### 1. SQL Ingestion
- Successfully parse a standard WordPress SQL dump into a local SQLite database.
- Support for `wp_posts`, `wp_postmeta`, and basic category/tag terms.

### 2. Core Manifest Generation
- Identify and list all `published` posts and pages.
- Map basic category hierarchies (at least 1-2 levels deep).
- Resolve "Featured Images" (thumbnail IDs) to their remote URLs.

### 3. Markdown Conversion
- Convert HTML content to clean Markdown using `markdownify`.
- Generate YAML front matter specifically for the **Blowfish** theme.
- Support for **Page Bundles** (`index.md` inside a folder named after the slug).

### 4. Basic URL Preservation
- Use the original WordPress `post_name` as the Hugo slug/folder name.

---

## Development Stages to MVP

### Stage 1: The Foundation (Data)
- **Goal:** Get the data out of the SQL file and into a queryable format.
- **Tasks:**
  - Implement `ingest_sql.py` logic to handle `CREATE TABLE` and `INSERT INTO` statements.
  - Verify data integrity by querying the number of posts in SQLite.

### Stage 2: The Map (Manifest)
- **Goal:** Create a structured JSON "Source of Truth."
- **Tasks:**
  - Implement `generate_manifest.py` to link posts to their categories and metadata.
  - Output a `manifest.json` that a human can verify.

### Stage 3: The Generator (Content)
- **Goal:** Create the actual Hugo files.
- **Tasks:**
  - Implement `build_content.py` to create the `content/` folder and `.md` files.
  - Apply Blowfish front matter defaults from `config.py`.

### Stage 4: Basic Verification
- **Goal:** Ensure the Hugo site actually builds.
- **Tasks:**
  - Run the `hugo` command against the generated `content/` folder to ensure no syntax errors.

---

## Post-MVP (Phase 2)
- Automatic Asset Downloading (`fetch_assets.py`).
- Internal Link Transformation (`transform_links.py`).
- WordPress Shortcode Conversion ([caption] to figure).
- Deep (3+ level) Category Nesting.
