import os
import requests
import time
import json
import logging
import config
from colorama import Fore, Style

def download_assets(manifest, force=False, force_continue=False, skip_codes=None):
    """
    Downloads featured images and content assets.
    Tracks success/failure in download_history.json for reliable resume.
    """
    logger = logging.getLogger(__name__)
    skip_codes = skip_codes or []
    
    # Always generate the queue file for the user
    os.makedirs(os.path.dirname(config.ASSETS_QUEUE_FILE), exist_ok=True)
    with open(config.ASSETS_QUEUE_FILE, "w", encoding="utf-8") as f:
        for asset in sorted(manifest["assets"]):
            f.write(f"{asset}\n")
    logger.info(f"Generated {config.ASSETS_QUEUE_FILE}")

    if not config.DOWNLOAD_ASSETS and not force:
        print(f"{Fore.YELLOW}Stage 4: Asset download is DISABLED in config.py.{Style.RESET_ALL}")
        return

    # Load download history
    history = load_history()
    
    print(f"{Fore.CYAN}Stage 4: Downloading assets (Images/PDFs)...{Style.RESET_ALL}")
    if force_continue:
        print(f"{Fore.YELLOW}  Warning: --force-continue is enabled.{Style.RESET_ALL}")

    if not os.path.exists(config.GLOBAL_ASSET_DIR):
        os.makedirs(config.GLOBAL_ASSET_DIR, exist_ok=True)

    headers = {'User-Agent': config.USER_AGENT}
    
    # 1. Process Featured Images
    for item in manifest["posts"] + manifest["pages"]:
        if item.get("featured_image"):
            url = item["featured_image"]
            
            # Skip if already successfully downloaded (200)
            if history.get(url) == 200 and os.path.exists(get_featured_path(item)):
                continue

            post_dir = get_post_dir(item)
            if os.path.exists(post_dir):
                ext = os.path.splitext(url)[1]
                dest_path = os.path.join(post_dir, f"featured{ext}")
                
                success, code = download_file(url, dest_path, headers)
                history[url] = code
                save_history(history)
                
                if not success and not should_continue(code, force_continue, skip_codes):
                    handle_stop(url, code)
                    return

    # 2. Process General Assets
    for url in manifest["assets"]:
        # Skip if already successfully downloaded
        filename = os.path.basename(url)
        dest_path = os.path.join(config.GLOBAL_ASSET_DIR, filename)
        
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
    """Loads the download history from JSON."""
    if os.path.exists(config.DOWNLOAD_HISTORY_FILE):
        try:
            with open(config.DOWNLOAD_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_history(history):
    """Saves the current download history to JSON."""
    try:
        with open(config.DOWNLOAD_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception:
        pass

def should_continue(code, force_continue, skip_codes):
    if force_continue:
        return True
    if code in skip_codes:
        return True
    return False

def handle_stop(url, code):
    print(f"\n{Fore.RED}CRITICAL ERROR: Asset download stopped.{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Failed URL: {url}")
    print(f"{Fore.WHITE}HTTP Code: {code}")
    print(f"{Fore.YELLOW}Progress saved to history. Use {Fore.GREEN}--force-continue{Fore.YELLOW} or {Fore.GREEN}--skip-codes={code}{Fore.YELLOW} to resume.{Style.RESET_ALL}\n")

def get_post_dir(item):
    if item["post_type"] == 'post':
        if config.USE_CATEGORY_FOLDERS and item.get("category_path"):
            return os.path.join(config.HUGO_CONTENT_DIR, "posts", item["category_path"], item["post_name"])
        return os.path.join(config.HUGO_CONTENT_DIR, "posts", item["post_name"])
    return os.path.join(config.HUGO_CONTENT_DIR, item["post_name"])

def get_featured_path(item):
    """Helper to get the expected local path of a featured image."""
    url = item.get("featured_image")
    if not url: return ""
    ext = os.path.splitext(url)[1]
    return os.path.join(get_post_dir(item), f"featured{ext}")

def download_file(url, destination, headers):
    logger = logging.getLogger(__name__)
    try:
        if config.DOWNLOAD_DELAY > 0:
            time.sleep(config.DOWNLOAD_DELAY)
            
        # requests follows redirects by default (301, 302)
        response = requests.get(url, headers=headers, timeout=15, stream=True)
        if response.status_code == 200:
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            logger.info(f"Downloaded: {url}")
            return True, 200
        else:
            logger.warning(f"Failed (HTTP {response.status_code}): {url}")
            return False, response.status_code
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        return False, "CONNECTION_ERROR"
