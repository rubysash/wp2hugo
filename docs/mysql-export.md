# Preparing your WordPress SQL Dump

The `wp2hugo` tool requires a raw `.sql` file named `export.sql` in the project root. If you do not have access to phpMyAdmin, you can generate this using the MySQL command line.

## Using `mysqldump`

We recommend using the `--skip-extended-insert` flag. This ensures every database row is on its own line, making the ingestion process much more reliable and easier to debug.

### Recommended Command:
```bash
mysqldump --no-autocommit --single-transaction --skip-extended-insert -u [YOUR_USERNAME] -p [YOUR_DATABASE_NAME] > export.sql
```

### Just the Core Tables:
If your database is very large and contains log or cache tables you don't need, you can dump only the essential WordPress tables (assuming the default `wp_` prefix):

```bash
mysqldump -u [USER] -p [DB] wp_posts wp_postmeta wp_terms wp_term_taxonomy wp_term_relationships wp_users > export.sql
```

## Troubleshooting
- **Prefixes:** If your site uses a custom prefix (e.g., `wp_site1_`), ensure you update the `WP_PREFIX` in your `.env` file before running the migration.
- **Encoding:** Ensure your terminal/CLI is set to UTF-8 to prevent character corruption during the dump.
