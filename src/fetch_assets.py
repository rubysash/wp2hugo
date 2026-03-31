import os
import requests
import time
import json
import logging
import config
from colorama import Fore, Style

def download_assets(manifest, force=False, force_continue=False, skip_codes=None):
    """
    Downloads images and PDFs into Page Bundles.
    """
    logger = logging.getLogger(__name__)
    skip_codes = skip_codes or []
    
    # 1. Update the Assets Queue for user reference
    all_assets = set()
    for item in manifest["posts"] + manifest["pages"]:
        for asset in item.get("local_assets", []):
            all_assets.add(asset)
    
    os.makedirs(os.path.dirname(config.ASSETS_QUEUE_FILE), exist_ok=True)
    with open(config.ASSETS_QUEUE_FILE, "w", encoding="utf-8") as f:
        for asset in sorted(list(all_assets)):
            f.write(f"{asset}\n")

    if not config.DOWNLOAD_ASSETS and not force:
        print(f"{Fore.YELLOW}Stage 4: Asset download is DISABLED in config.py.{Style.RESET_ALL}")
        return

    history = load_history()
    print(f"{Fore.CYAN}Stage 4: Downloading assets into Page Bundles...{Style.RESET_ALL}")

    headers = {'User-Agent': config.USER_AGENT}
    
    # Process each post/page
    items = manifest["posts"] + manifest["pages"]
    for item in items:
        post_dir = get_post_dir(item)
        if not os.path.exists(post_dir):
            continue

        for url in item.get("local_assets", []):
            filename = os.path.basename(url)
            
            # Special handling for Featured Image (renaming to featured.ext)
            if url == item.get("featured_image"):
                ext = os.path.splitext(url)[1]
                dest_path = os.path.join(post_dir, f"featured{ext}")
            else:
                dest_path = os.path.join(post_dir, filename)

            # Skip if already success
            if history.get(url) == 200 and os.path.exists(dest_path):
                continue

            success, code = download_file(url, dest_path, headers)
            history[url] = code
            save_history(history)
            
            if not success and not should_continue(code, force_continue, skip_codes):
                handle_stop(url, code)
                return

    print(f"{Fore.GREEN}Asset download complete.{Style.RESET_ALL}")

def load_history():
    if os.path.exists(config.DOWNLOAD_HISTORY_FILE):
        try:
            with open(config.DOWNLOAD_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_history(history):
    try:
        with open(config.DOWNLOAD_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception:
        pass

def should_continue(code, force_continue, skip_codes):
    if force_continue: return True
    if code in skip_codes: return True
    return False

def handle_stop(url, code):
    print(f"\n{Fore.RED}CRITICAL ERROR: Asset download stopped.{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Failed URL: {url}")
    print(f"{Fore.WHITE}HTTP Code: {code}")
    print(f"{Fore.YELLOW}Use {Fore.GREEN}--force-continue{Fore.YELLOW} to resume.{Style.RESET_ALL}\n")

def get_post_dir(item):
    if item["post_type"] == 'post':
        if config.USE_CATEGORY_FOLDERS and item.get("category_path"):
            return os.path.join(config.HUGO_CONTENT_DIR, "posts", item["category_path"], item["post_name"])
        return os.path.join(config.HUGO_CONTENT_DIR, "posts", item["post_name"])
    return os.path.join(config.HUGO_CONTENT_DIR, item["post_name"])

def download_file(url, destination, headers):
    try:
        if config.DOWNLOAD_DELAY > 0:
            time.sleep(config.DOWNLOAD_DELAY)
        response = requests.get(url, headers=headers, timeout=15, stream=True)
        if response.status_code == 200:
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True, 200
        else:
            return False, response.status_code
    except Exception as e:
        return False, "CONNECTION_ERROR"
