import sqlite3
import json
import re
import logging
import config
from colorama import Fore, Style

def create_site_manifest(sqlite_db_path):
    """
    Queries the SQLite DB to build a comprehensive map of the site.
    """
    logger = logging.getLogger(__name__)
    print(f"{Fore.CYAN}Stage 2: Generating site manifest from SQLite...{Style.RESET_ALL}")
    
    conn = sqlite3.connect(sqlite_db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    manifest = {
        "authors": {},
        "categories": {},
        "tags": {},
        "posts": [],
        "pages": [],
        "assets": set()
    }

    # 1. Map Authors
    cursor.execute(f"SELECT ID, user_login, display_name FROM `{config.TABLE_MAPPING['users']}`")
    for row in cursor.fetchall():
        manifest["authors"][row["ID"]] = {
            "login": row["user_login"],
            "name": row["display_name"]
        }

    # 2. Map Categories and Tags (Terms)
    # This query gets terms and their taxonomy (category vs post_tag) and parent info
    cursor.execute(f"""
        SELECT t.term_id, t.name, t.slug, tt.taxonomy, tt.parent
        FROM `{config.TABLE_MAPPING['terms']}` t
        JOIN `{config.TABLE_MAPPING['term_taxonomy']}` tt ON t.term_id = tt.term_id
    """)
    terms = cursor.fetchall()
    
    # First pass: build flat map
    temp_terms = {row["term_id"]: dict(row) for row in terms}
    
    # Second pass: resolve full paths for categories
    for tid, term in temp_terms.items():
        if term["taxonomy"] == 'category':
            path = [term["slug"]]
            parent_id = term["parent"]
            while parent_id != 0 and parent_id in temp_terms:
                parent = temp_terms[parent_id]
                path.insert(0, parent["slug"])
                parent_id = parent["parent"]
            term["full_path"] = "/".join(path)
            manifest["categories"][tid] = term
        elif term["taxonomy"] == 'post_tag':
            manifest["tags"][tid] = term

    # 3. Extract Posts and Pages
    status_placeholders = ', '.join(['?'] * len(config.MIGRATE_STATUSES))
    cursor.execute(f"""
        SELECT ID, post_author, post_date, post_content, post_title, post_excerpt, post_status, post_name, post_type, post_parent
        FROM `{config.TABLE_MAPPING['posts']}`
        WHERE post_status IN ({status_placeholders})
        AND post_type IN ('post', 'page')
    """, config.MIGRATE_STATUSES)
    
    content_rows = cursor.fetchall()
    
    for row in content_rows:
        item = dict(row)
        item_id = item["ID"]
        
        # Resolve Author
        author_info = manifest["authors"].get(item["post_author"], {"name": "Admin", "login": "admin"})
        item["author_name"] = author_info["name"]
        
        # Resolve Categories and Tags for this item
        cursor.execute(f"""
            SELECT term_taxonomy_id FROM `{config.TABLE_MAPPING['term_relationships']}`
            WHERE object_id = ?
        """, (item_id,))
        term_ids = [r[0] for r in cursor.fetchall()]
        
        item["item_categories"] = [manifest["categories"][tid]["name"] for tid in term_ids if tid in manifest["categories"]]
        item["item_tags"] = [manifest["tags"][tid]["name"] for tid in term_ids if tid in manifest["tags"]]
        
        # Get category path (use the first category found as primary for folder structure)
        primary_cat_path = ""
        for tid in term_ids:
            if tid in manifest["categories"]:
                primary_cat_path = manifest["categories"][tid]["full_path"]
                break
        item["category_path"] = primary_cat_path

        # Resolve Featured Image (Post Meta _thumbnail_id)
        cursor.execute(f"""
            SELECT meta_value FROM `{config.TABLE_MAPPING['postmeta']}`
            WHERE post_id = ? AND meta_key = '_thumbnail_id'
        """, (item_id,))
        thumb_id_row = cursor.fetchone()
        if thumb_id_row:
            thumb_id = thumb_id_row[0]
            cursor.execute(f"SELECT guid FROM `{config.TABLE_MAPPING['posts']}` WHERE ID = ?", (thumb_id,))
            img_row = cursor.fetchone()
            if img_row:
                item["featured_image"] = img_row[0]
                manifest["assets"].add(img_row[0])

        # Find other assets in content
        found_assets = re.findall(r'src=["\'](https?://[^"\']+\.(?:jpg|jpeg|png|gif|pdf|svg|webp))["\']', item["post_content"], re.IGNORECASE)
        for asset in found_assets:
            manifest["assets"].add(asset)

        if item["post_type"] == 'post':
            manifest["posts"].append(item)
        else:
            manifest["pages"].append(item)

    # Convert assets set to list for JSON serialization
    manifest["assets"] = list(manifest["assets"])
    
    conn.close()
    
    # Save manifest
    with open(config.MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"{Fore.GREEN}Manifest generated with {len(manifest['posts'])} posts and {len(manifest['pages'])} pages.{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Found {len(manifest['assets'])} unique assets to download.{Style.RESET_ALL}")
    
    return manifest
