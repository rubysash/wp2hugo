import os
import re
import logging
import config
from colorama import Fore, Style

def post_process_links(hugo_content_dir, manifest):
    """
    Transforms internal WP links to Hugo refs and maps images to relative paths.
    """
    logger = logging.getLogger(__name__)
    print(f"{Fore.CYAN}Stage 5: Transforming links and asset paths...{Style.RESET_ALL}")

    url_map = build_url_map(manifest)
    
    count_files = 0
    count_links = 0
    count_images = 0

    items = manifest.get("posts", []) + manifest.get("pages", [])
    for item in items:
        file_path = get_item_index_md(item, hugo_content_dir)
        if not os.path.exists(file_path):
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # A. Replace Internal Links (Absolute WP -> Hugo ref)
        for old_url, new_path in url_map.items():
            if old_url in content:
                content = content.replace(old_url, f'{{{{< ref "{new_path}" >}}}}')
                count_links += 1

        # B. Replace Image URLs (Absolute WP -> Relative Filename)
        # For Page Bundles, the image is now in the same folder.
        for asset_url in item.get("local_assets", []):
            if asset_url in content:
                filename = os.path.basename(asset_url)
                # Just the filename, as it's now in the same folder
                content = content.replace(asset_url, filename)
                count_images += 1

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            count_files += 1

    print(f"{Fore.GREEN}Link transformation complete.{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  Updated {count_links} links and {count_images} images in {count_files} files.")

def build_url_map(manifest):
    url_map = {}
    for post in manifest.get("posts", []):
        path = f"/posts/{post['category_path']}/{post['post_name']}/" if config.USE_CATEGORY_FOLDERS and post.get("category_path") else f"/posts/{post['post_name']}/"
        url_map[f"{config.SITE_DOMAIN}/?p={post['ID']}"] = path
        url_map[f"{config.SITE_DOMAIN}/{post['post_name']}/"] = path
    
    for page in manifest.get("pages", []):
        path = f"/{page['post_name']}/"
        url_map[f"{config.SITE_DOMAIN}/?p={page['ID']}"] = path
        url_map[f"{config.SITE_DOMAIN}/{page['post_name']}/"] = path
    return url_map

def get_item_index_md(item, content_dir):
    if item["post_type"] == 'post':
        if config.USE_CATEGORY_FOLDERS and item.get("category_path"):
            folder = os.path.join(content_dir, "posts", item["category_path"], item["post_name"])
        else:
            folder = os.path.join(content_dir, "posts", item["post_name"])
    else:
        folder = os.path.join(content_dir, item["post_name"])
    return os.path.join(folder, "index.md")
