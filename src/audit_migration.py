import os
import json
import csv
import re
import requests
import logging
import config
from colorama import Fore, Style

def verify_migration(manifest, hugo_content_dir, remote_check=False):
    """
    Comprehensive audit of the migration.
    Generates a high-level report (JSON) and a detailed row-by-row checklist (CSV).
    """
    logger = logging.getLogger(__name__)
    print(f"{Fore.CYAN}Stage 6: Auditing Migration Integrity...{Style.RESET_ALL}")

    report = {
        "local_posts_found": 0,
        "local_pages_found": 0,
        "total_assets_found": 0,
        "total_links_found": 0
    }

    # Prepare detailed CSV data
    csv_data = []
    csv_headers = [
        "ID", "Type", "Title", "WP URL", "Hugo Path", 
        "File Exists", "Featured Img", "Assets (Found/Target)", 
        "Link Count", "Remote Status"
    ]

    all_items = manifest.get("posts", []) + manifest.get("pages", [])
    
    print(f"{Fore.WHITE}  Analyzing {len(all_items)} items for detailed audit...")

    for item in all_items:
        is_post = item["post_type"] == 'post'
        path = get_item_local_folder(item, hugo_content_dir)
        index_path = os.path.join(path, "index.md")
        
        # 1. Local File Check
        file_exists = os.path.exists(index_path)
        if file_exists:
            if is_post: report["local_posts_found"] += 1
            else: report["local_pages_found"] += 1

        # 2. Featured Image Check
        fimg_status = "N/A"
        if item.get("featured_image"):
            ext = os.path.splitext(item["featured_image"])[1]
            fimg_path = os.path.join(path, f"featured{ext}")
            fimg_status = "Yes" if os.path.exists(fimg_path) else "MISSING"

        # 3. Asset Count Check
        assets_found = 0
        assets_target = len(item.get("local_assets", []))
        for asset_url in item.get("local_assets", []):
            filename = os.path.basename(asset_url)
            # Check for featured rename or regular filename
            if asset_url == item.get("featured_image"):
                ext = os.path.splitext(asset_url)[1]
                if os.path.exists(os.path.join(path, f"featured{ext}")): assets_found += 1
            else:
                if os.path.exists(os.path.join(path, filename)): assets_found += 1
        
        report["total_assets_found"] += assets_found

        # 4. Link Count Check (Scan the generated Markdown)
        link_count = 0
        if file_exists:
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Count Hugo ref shortcodes
                link_count = len(re.findall(r'{{< ref', content))
        report["total_links_found"] += link_count

        # 5. Remote Check
        remote_status = "Skipped"
        wp_url = f"{config.SITE_DOMAIN}/{item['post_name']}/"
        if remote_check:
            try:
                resp = requests.head(wp_url, headers={'User-Agent': config.USER_AGENT}, timeout=5, allow_redirects=True)
                remote_status = str(resp.status_code)
            except Exception:
                remote_status = "ERROR"

        # Build CSV Row
        hugo_rel_path = path.replace(config.HUGO_CONTENT_DIR, "").replace("\\", "/")
        csv_data.append({
            "ID": item["ID"],
            "Type": item["post_type"],
            "Title": item["post_title"],
            "WP URL": wp_url,
            "Hugo Path": hugo_rel_path,
            "File Exists": "Yes" if file_exists else "NO",
            "Featured Img": fimg_status,
            "Assets (Found/Target)": f"{assets_found}/{assets_target}",
            "Link Count": link_count,
            "Remote Status": remote_status
        })

    # --- SAVE OUTPUTS ---
    
    # Save CSV Details
    csv_file = os.path.join(config.META_DIR, "audit_details.csv")
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()
        writer.writerows(csv_data)

    # Save JSON Report
    report_file = os.path.join(config.META_DIR, "audit_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Print Summary
    print_summary(report, len(manifest['posts']), len(manifest['pages']), remote_check)
    print(f"{Fore.GREEN}Audit complete.{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  Detailed checklist saved to: {Fore.YELLOW}{csv_file}{Style.RESET_ALL}")

def get_item_local_folder(item, content_dir):
    if item["post_type"] == 'post':
        if config.USE_CATEGORY_FOLDERS and item.get("category_path"):
            return os.path.join(content_dir, "posts", item["category_path"], item["post_name"])
        return os.path.join(content_dir, "posts", item["post_name"])
    return os.path.join(content_dir, item["post_name"])

def print_summary(report, total_posts, total_pages, remote_check):
    print(f"\n{Fore.CYAN}--- Audit Summary ---{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Posts Found        : {report['local_posts_found']}/{total_posts}")
    print(f"{Fore.WHITE}Pages Found        : {report['local_pages_found']}/{total_pages}")
    print(f"{Fore.WHITE}Total Assets Local : {report['total_assets_found']}")
    print(f"{Fore.WHITE}Total Internal Refs: {report['total_links_found']}")
    print(f"{Fore.CYAN}----------------------{Style.RESET_ALL}\n")
