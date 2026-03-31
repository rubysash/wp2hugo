import os
import re
import json
import logging
import config
from colorama import Fore, Style

def post_process_links(hugo_content_dir, manifest):
    """
    Scans Markdown files to transform internal WordPress links to Hugo relative paths.
    Converts remote image URLs to local paths.
    """
    logger = logging.getLogger(__name__)
    print(f"{Fore.CYAN}Stage 5: Transforming links and asset paths...{Style.RESET_ALL}")

    # 1. Build the Mapping
    # Map old WP URLs/IDs to new Hugo paths
    url_map = {}
    
    # Handle Posts
    for post in manifest.get("posts", []):
        old_url = f"{config.SITE_DOMAIN}/?p={post['ID']}"
        # Hugo path: /posts/category/slug/
        if config.USE_CATEGORY_FOLDERS and post.get("category_path"):
            new_path = f"/posts/{post['category_path']}/{post['post_name']}/"
        else:
            new_path = f"/posts/{post['post_name']}/"
        url_map[old_url] = new_path
        # Also map slug-based URL if possible
        url_map[f"{config.SITE_DOMAIN}/{post['post_name']}/"] = new_path

    # Handle Pages
    for page in manifest.get("pages", []):
        old_url = f"{config.SITE_DOMAIN}/?p={page['ID']}"
        new_path = f"/{page['post_name']}/"
        url_map[old_url] = new_path
        url_map[f"{config.SITE_DOMAIN}/{page['post_name']}/"] = new_path

    # 2. Iterate through Markdown files
    count_files = 0
    count_links = 0
    count_images = 0

    for root, dirs, files in os.walk(hugo_content_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                # A. Replace Internal Links
                # Look for patterns matching the site domain
                for old_url, new_path in url_map.items():
                    # Check for standard Markdown links [text](url)
                    link_pattern = re.escape(old_url)
                    if old_url in content:
                        content = content.replace(old_url, f'{{{{< ref "{new_path}" >}}}}')
                        count_links += 1

                # B. Replace Image URLs
                # Remote images were downloaded to output/assets/i/
                # We want them to point to /i/filename.ext (assuming they move to Hugo static/i)
                for asset_url in manifest.get("assets", []):
                    if asset_url in content:
                        filename = os.path.basename(asset_url)
                        # Point to the global assets directory structure
                        new_img_path = f"/i/{filename}"
                        content = content.replace(asset_url, new_img_path)
                        count_images += 1

                # 3. Save if changed
                if content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    count_files += 1

    print(f"{Fore.GREEN}Link transformation complete.{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  Updated {count_links} internal links and {count_images} image paths across {count_files} files.")
    logger.info(f"Transformed {count_links} links and {count_images} images in {count_files} files.")
