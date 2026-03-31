import logging
import os
from dotenv import load_dotenv

# Load variables from .env file if it exists
load_dotenv()

# --- General Settings ---
VERSION = "1.5.2"
# resets everything for a clean slate or attempts to skip existing asset download.
RESET_FRESH = True
SQL_INPUT_FILE = "export.sql"

# --- Output Path Configuration ---
OUTPUT_DIR = "output"
HUGO_CONTENT_DIR = os.path.join(OUTPUT_DIR, "content")
META_DIR = os.path.join(OUTPUT_DIR, "meta")
GLOBAL_ASSET_DIR = os.path.join(OUTPUT_DIR, "assets", "i")

# Meta Files
SQLITE_DB_FILE = os.path.join(META_DIR, "wp_dump.db")
MANIFEST_FILE = os.path.join(META_DIR, "manifest.json")
LOG_FILE = os.path.join(META_DIR, "migration.log")
ASSETS_QUEUE_FILE = os.path.join(META_DIR, "assets_queue.txt")
DOWNLOAD_HISTORY_FILE = os.path.join(META_DIR, "download_history.json")

# Sensitive Site Data (Loaded from .env)
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "https://example.com")
WP_PREFIX = os.getenv("WP_PREFIX", "wp_")

# --- WordPress Database Configuration ---
TABLE_MAPPING = {
    "posts": f"{WP_PREFIX}posts",
    "postmeta": f"{WP_PREFIX}postmeta",
    "terms": f"{WP_PREFIX}terms",
    "term_taxonomy": f"{WP_PREFIX}term_taxonomy",
    "term_relationships": f"{WP_PREFIX}term_relationships",
    "users": f"{WP_PREFIX}users"
}

# --- Conversion Strategy ---
ADD_FOOTER_SHORTCODE = True
FOOTER_SHORTCODE_NAME = "footer-add"
MIGRATE_STATUSES = ['publish', 'draft', 'private']
USE_CATEGORY_FOLDERS = True
USE_PAGE_BUNDLES = True

# --- Hugo / Blowfish Front Matter Defaults ---
BLOWFISH_DEFAULTS = {
    "showTableOfContents": True,
    "showTaxonomies": True,
    "showDate": True,
    "showAuthor": True,
    "showReadingTime": True,
    "showWordCount": False,
    "showComments": False,
}

# --- Asset Management ---
DOWNLOAD_ASSETS = False
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
DOWNLOAD_DELAY = 1.0
RENAME_FEATURED_IMAGE = True
DOWNLOAD_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".svg", ".webp"]

# --- Debugging & Logging ---
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEBUG_MODE = False

# --- Path Management ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
