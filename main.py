import logging
import sys
import os
import shutil
import json
import argparse
import config
from colorama import Fore, Style

# Import from the src package
from src.preflight import run_preflight_checks
from src.ingest_sql import ingest_wp_sql
from src.generate_manifest import create_site_manifest
from src.build_content import generate_hugo_content
from src.fetch_assets import download_assets
from src.transform_links import post_process_links
from src.audit_migration import verify_migration

def main():
    """
    Main entry point for the wp2hugo migration tool.
    """
    parser = argparse.ArgumentParser(description="wp2hugo migration tool")
    parser.add_argument("--assets-only", action="store_true", help="Only download assets using existing manifest")
    parser.add_argument("--force-continue", action="store_true", help="Don't stop on HTTP errors (404, 403, etc)")
    parser.add_argument("--skip-codes", type=str, help="Comma-separated list of HTTP codes to ignore (e.g. 404,403)")
    args = parser.parse_args()

    # Parse skip codes if provided
    skip_codes = []
    if args.skip_codes:
        try:
            skip_codes = [int(c.strip()) for f in args.skip_codes.split(',') for c in [f] if c.strip()]
        except ValueError:
            print(f"{Fore.RED}Error: --skip-codes must be a comma-separated list of integers.{Style.RESET_ALL}")
            sys.exit(1)

    if args.assets_only:
        run_assets_only(args.force_continue, skip_codes)
        return

    # Stage 0a: Fresh Reset
    if config.RESET_FRESH:
        if os.path.exists(config.OUTPUT_DIR):
            print(f"{Fore.YELLOW}Resetting environment (Removing {config.OUTPUT_DIR})...{Style.RESET_ALL}")
            try:
                shutil.rmtree(config.OUTPUT_DIR)
            except Exception as e:
                print(f"{Fore.RED}  Warning: Could not remove output directory: {e}{Style.RESET_ALL}")

    # Ensure meta directory exists for logging and database
    if not os.path.exists(config.META_DIR):
        os.makedirs(config.META_DIR, exist_ok=True)

    # Initialize logging (Console + File)
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)

    logger.info(f"Starting wp2hugo migration v{config.VERSION}...")
    print(f"{Fore.MAGENTA}wp2hugo v{config.VERSION}{Style.RESET_ALL}")

    # Stage 0: Pre-flight Checks
    if not run_preflight_checks():
        logger.error("Pre-flight checks failed. Aborting migration.")
        sys.exit(1)

    # Stage 1: Ingest SQL dump into local SQLite for easier querying
    ingest_wp_sql(config.SQL_INPUT_FILE, config.SQLITE_DB_FILE)

    # Stage 2: Analyze the DB and create a Source of Truth manifest
    manifest = create_site_manifest(config.SQLITE_DB_FILE)

    # Stage 3: Build the Hugo content directory and Page Bundles
    generate_hugo_content(manifest, config.HUGO_CONTENT_DIR)

    # Stage 4: Fetch remote assets (images/PDFs) and place in Page Bundles
    download_assets(manifest, force_continue=args.force_continue, skip_codes=skip_codes)

    # Stage 5: Fix internal links and update remote image paths to local ones
    # post_process_links(config.HUGO_CONTENT_DIR, manifest)

    # Stage 6: Final audit to ensure everything was migrated correctly
    # verify_migration(manifest, config.HUGO_CONTENT_DIR)

    logger.info("Migration process complete.")
    
    # Next Steps Reminder
    print(f"\n{Fore.CYAN}--- Next Steps ---{Style.RESET_ALL}")
    if not config.DOWNLOAD_ASSETS:
        print(f"{Fore.WHITE}1. Review the generated content in {Fore.YELLOW}'{config.HUGO_CONTENT_DIR}'{Style.RESET_ALL}")
        print(f"{Fore.WHITE}2. To download images only, run: {Fore.GREEN}python main.py --assets-only{Style.RESET_ALL}")
        print(f"{Fore.WHITE}3. See {Fore.YELLOW}'{config.ASSETS_QUEUE_FILE}'{Fore.WHITE} for all detected asset URLs.")
    else:
        print(f"{Fore.WHITE}1. Assets downloaded to {Fore.YELLOW}'{config.GLOBAL_ASSET_DIR}'{Fore.WHITE} and Page Bundles.")
        print(f"{Fore.WHITE}2. Proceed to Stage 5: Link Transformation.")
    print(f"{Fore.CYAN}------------------{Style.RESET_ALL}\n")

def run_assets_only(force_continue, skip_codes):
    """Logic for the --assets-only flag."""
    if not os.path.exists(config.META_DIR):
        os.makedirs(config.META_DIR, exist_ok=True)

    logging.basicConfig(
        level=config.LOG_LEVEL,
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)

    print(f"{Fore.MAGENTA}wp2hugo Asset Downloader v{config.VERSION}{Style.RESET_ALL}")

    if not os.path.exists(config.MANIFEST_FILE):
        print(f"{Fore.RED}Error: Manifest file '{config.MANIFEST_FILE}' not found.{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Please run 'python main.py' first to generate the manifest.{Style.RESET_ALL}")
        return

    # Load the existing manifest
    try:
        with open(config.MANIFEST_FILE, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Error loading manifest: {e}{Style.RESET_ALL}")
        return

    logger.info(f"Loaded manifest with {len(manifest['assets'])} assets.")
    
    # Run the download stage (forcing it to run)
    download_assets(manifest, force=True, force_continue=force_continue, skip_codes=skip_codes)

    print(f"\n{Fore.GREEN}Asset download process finished.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
