import logging
import os
from dotenv import load_dotenv

# Load site-specific variables (SITE_DOMAIN, WP_PREFIX) from a local .env file.
# This keeps your sensitive site identity out of version control.
load_dotenv()

# --- General Project Settings ---
# Current version of the migration tool.
VERSION = "1.9.0"

# If True, the script deletes the entire 'output/' directory before starting.
# Why: Ensures a clean slate so old files from previous runs don't mix with new data.
RESET_FRESH = True

# The name of your WordPress SQL export file.
# Why: This file must be placed in the project root for the parser to find it.
SQL_INPUT_FILE = "export.sql"

# --- Output Path Configuration ---
# Root directory where all generated data will be stored.
OUTPUT_DIR = "output"

# Hugo Content path: Where your Markdown files and Page Bundles will be created.
HUGO_CONTENT_DIR = os.path.join(OUTPUT_DIR, "content")

# Meta path: Where internal project data (logs, database, manifest) is stored.
META_DIR = os.path.join(OUTPUT_DIR, "meta")

# Global Assets: Used ONLY for site-wide static files (headers, backgrounds).
# Content-specific images are automatically placed in Page Bundles (Stage 4).
GLOBAL_ASSET_DIR = os.path.join(OUTPUT_DIR, "assets", "i")

# --- Meta File Definitions ---
# The local SQLite database generated from your raw SQL dump.
SQLITE_DB_FILE = os.path.join(META_DIR, "wp_dump.db")
# The JSON 'Source of Truth' mapping all site relationships.
MANIFEST_FILE = os.path.join(META_DIR, "manifest.json")
# The main activity log for tracking the migration process.
LOG_FILE = os.path.join(META_DIR, "migration.log")
# A simple text list of every unique asset URL found in your content.
ASSETS_QUEUE_FILE = os.path.join(META_DIR, "assets_queue.txt")
# Tracks which downloads succeeded or failed so you can resume later.
DOWNLOAD_HISTORY_FILE = os.path.join(META_DIR, "download_history.json")

# --- Sensitive Site Data (Loaded from .env) ---
# Your live site URL (e.g., https://mysite.com).
# Why: Used to resolve remote image paths and fix internal absolute links.
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "https://example.com")

# Your WordPress table prefix (default is 'wp_').
# Why: The parser needs this to identify the correct tables in your SQL dump.
WP_PREFIX = os.getenv("WP_PREFIX", "wp_")

# --- WordPress Database Table Mapping ---
# Maps internal logic to your specific database table names.
TABLE_MAPPING = {
    "posts": f"{WP_PREFIX}posts",
    "postmeta": f"{WP_PREFIX}postmeta",
    "terms": f"{WP_PREFIX}terms",
    "term_taxonomy": f"{WP_PREFIX}term_taxonomy",
    "term_relationships": f"{WP_PREFIX}term_relationships",
    "users": f"{WP_PREFIX}users"
}

# --- Conversion & Structure Strategy ---
# If True, appends a specific shortcode to the end of every generated file.
# Why: Useful for injecting site-wide footers, CTAs, or scripts in Hugo.
ADD_FOOTER_SHORTCODE = True
FOOTER_SHORTCODE_NAME = "footer-add"

# List of WordPress post statuses to include in the migration.
# Why: Hugo supports drafts and private pages, so we can capture them here.
MIGRATE_STATUSES = ['publish', 'draft', 'private']

# If True, nesting is based on categories (e.g., /posts/news/my-post/).
# Why: Preserves your existing URL structure and SEO hierarchy.
USE_CATEGORY_FOLDERS = True

# If True, every post is its own folder with an index.md file.
# Why: Required for Blowfish 'Page Bundles' to keep featured images with their posts.
USE_PAGE_BUNDLES = True

# --- Blowfish Theme Defaults ---
# These are injected into the YAML front matter of every Markdown file.
# Why: Configures theme behavior (TOC, author display, etc.) automatically.
BLOWFISH_DEFAULTS = {
    "showTableOfContents": True,
    "showTaxonomies": True,
    "showDate": True,
    "showAuthor": True,
    "showReadingTime": True,
    "showWordCount": False,
    "showComments": False,
}

# --- Asset Management & Security ---
# If True, the script will attempt to download images during a full migration.
DOWNLOAD_ASSETS = False

# Mimics a real web browser to avoid being blocked by security plugins like Wordfence.
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

# Number of seconds to wait between each download.
# Why: Prevents triggering Rate Limits or WAF blocks on the live server.
DOWNLOAD_DELAY = 1.0

# If True, renames featured images to 'featured.[ext]' per Blowfish requirements.
RENAME_FEATURED_IMAGE = True

# Only files with these extensions will be identified as assets to download.
DOWNLOAD_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".svg", ".webp"]

# --- Debugging & Logging ---
# LOG_LEVEL controls how much info is saved (DEBUG, INFO, WARNING, ERROR).
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# Set to True if you want to see detailed SQL queries or transformation steps.
DEBUG_MODE = False

# --- Path Management ---
# Automatically determines the root path of the project.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
