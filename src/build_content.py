import os
import json
import yaml
import logging
import re
import config
from markdownify import markdownify as md
from colorama import Fore, Style
from src.utils.html_cleaner import clean_wp_html

def generate_hugo_content(manifest, output_dir):
    """
    Converts manifest entries into Hugo Markdown files with Blowfish front matter.
    """
    logger = logging.getLogger(__name__)
    print(f"{Fore.CYAN}Stage 3: Generating Hugo content in '{output_dir}'...{Style.RESET_ALL}")
    
    # Prompt for overwrite if directory exists and is not empty
    if os.path.exists(output_dir) and os.listdir(output_dir):
        print(f"{Fore.YELLOW}Target directory '{output_dir}' already exists and is not empty.{Style.RESET_ALL}")
        confirm = input(f"{Fore.WHITE}Do you want to overwrite all existing content? (y/n): ").lower()
        if confirm != 'y':
            print(f"{Fore.RED}Aborting content generation.{Style.RESET_ALL}")
            return
        logger.info(f"User confirmed overwrite of {output_dir}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Process Pages
    print(f"{Fore.WHITE}  Processing {len(manifest['pages'])} pages...")
    for page in manifest["pages"]:
        create_hugo_item(page, output_dir, is_post=False)

    # Process Posts
    print(f"{Fore.WHITE}  Processing {len(manifest['posts'])} posts...")
    for post in manifest["posts"]:
        create_hugo_item(post, output_dir, is_post=True)

    print(f"{Fore.GREEN}Content generation complete.{Style.RESET_ALL}")

def create_hugo_item(item, base_output_dir, is_post=True):
    """
    Creates a single Hugo Page Bundle.
    """
    # Determine directory path
    if is_post:
        # Posts go into 'posts' or category folders
        if config.USE_CATEGORY_FOLDERS and item.get("category_path"):
            target_dir = os.path.join(base_output_dir, "posts", item["category_path"], item["post_name"])
        else:
            target_dir = os.path.join(base_output_dir, "posts", item["post_name"])
    else:
        target_dir = os.path.join(base_output_dir, item["post_name"])

    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    # Build Front Matter
    front_matter = {
        "title": item["post_title"],
        "date": item["post_date"],
        "draft": item["post_status"] == "draft",
        "description": item["post_excerpt"] if item["post_excerpt"] else "",
        "categories": item["item_categories"],
        "tags": item["item_tags"],
        "authors": [item["author_name"]],
    }

    # Add Blowfish defaults
    front_matter.update(config.BLOWFISH_DEFAULTS)

    # Handle Featured Image
    if item.get("featured_image"):
        ext = os.path.splitext(item["featured_image"])[1]
        front_matter["featureImage"] = f"featured{ext}"

    # Convert Content to Markdown
    content = item["post_content"]
    
    # Replace literal \n, \r, \t with actual characters if they were double-escaped in the dump
    content = content.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')
    
    # Use regex to strip Gutenberg comments without deleting the lines
    content = re.sub(r'<!-- /?wp:.*? -->', '', content)
    
    # Convert HTML to Markdown
    markdown_content = md(content, heading_style="ATX")
    
    # Clean up excessive newlines (3+ becomes 2)
    markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)

    # Write index.md
    file_path = os.path.join(target_dir, "index.md")
    
    # Optional Footer Shortcode Injection
    if config.ADD_FOOTER_SHORTCODE:
        markdown_content += f"\n\n{{{{< {config.FOOTER_SHORTCODE_NAME} >}}}}"

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("---\n")
            # Using yaml.dump with sort_keys=False to keep order nice
            yaml.dump(front_matter, f, allow_unicode=True, sort_keys=False)
            f.write("---\n\n")
            f.write(markdown_content)
    except Exception as e:
        print(f"{Fore.RED}Error writing {file_path}: {e}{Style.RESET_ALL}")

def build_front_matter(post_data, manifest):
    """
    Helper to construct YAML front matter from manifest data.
    """
    pass
