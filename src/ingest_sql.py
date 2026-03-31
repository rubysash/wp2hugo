import sqlite3
import os
import re
import logging
import config
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def ingest_wp_sql(sql_file_path, sqlite_db_path):
    """
    Reads a raw WordPress .sql dump and populates a local SQLite database.
    Handles basic MySQL to SQLite syntax conversion.
    """
    logger = logging.getLogger(__name__)
    print(f"{Fore.CYAN}Stage 1: Ingesting SQL dump into SQLite...{Style.RESET_ALL}")
    
    if os.path.exists(sqlite_db_path):
        logger.info(f"Removing existing SQLite database: {sqlite_db_path}")
        os.remove(sqlite_db_path)

    conn = sqlite3.connect(sqlite_db_path)
    cursor = conn.cursor()

    statement = ""
    count_statements = 0
    
    try:
        with open(sql_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Skip comments and empty lines
                if line.startswith('--') or line.startswith('/*') or not line.strip():
                    continue
                
                statement += line
                
                # If the line ends with a semicolon, we have a complete statement
                if line.strip().endswith(';'):
                    stmt = statement.strip()
                    
                    # Clean up MySQL-specific syntax for SQLite
                    if stmt.upper().startswith('CREATE TABLE'):
                        # Remove ENGINE, CHARSET, etc.
                        stmt = re.sub(r'ENGINE=.*?;', ';', stmt, flags=re.IGNORECASE | re.DOTALL)
                        stmt = re.sub(r'CHARSET=.*?;', ';', stmt, flags=re.IGNORECASE | re.DOTALL)
                        stmt = re.sub(r'COLLATE=.*?;', ';', stmt, flags=re.IGNORECASE | re.DOTALL)
                        # Remove backticks in column names if needed, though SQLite supports them
                        # Handle specific MySQL types like bigint(20) -> INTEGER
                        stmt = re.sub(r'bigint\(\d+\)', 'INTEGER', stmt, flags=re.IGNORECASE)
                        stmt = re.sub(r'int\(\d+\)', 'INTEGER', stmt, flags=re.IGNORECASE)
                        stmt = re.sub(r'tinyint\(\d+\)', 'INTEGER', stmt, flags=re.IGNORECASE)
                        stmt = re.sub(r'unsigned', '', stmt, flags=re.IGNORECASE)
                        stmt = re.sub(r'AUTO_INCREMENT', 'PRIMARY KEY AUTOINCREMENT', stmt, flags=re.IGNORECASE)
                        # SQLite doesn't support AFTER column_name
                        stmt = re.sub(r'AFTER `.*?`', '', stmt, flags=re.IGNORECASE)

                    if stmt.upper().startswith('INSERT INTO') or stmt.upper().startswith('CREATE TABLE'):
                        try:
                            # Final cleanup: ensure single semicolon at the end
                            if not stmt.endswith(';'):
                                stmt += ';'
                            cursor.execute(stmt)
                            count_statements += 1
                            if count_statements % 500 == 0:
                                print(f"{Fore.YELLOW}  Processed {count_statements} statements...{Style.RESET_ALL}", end='\r')
                        except sqlite3.Error as e:
                            # Log but don't stop for every insert error (e.g. duplicate keys)
                            logger.debug(f"SQLite error: {e} | Statement: {stmt[:100]}...")
                    
                    statement = ""

        conn.commit()
        print(f"\n{Fore.GREEN}Successfully ingested {count_statements} SQL statements into SQLite.{Style.RESET_ALL}")
        
        # Verify basic data integrity
        verify_data_integrity(cursor)
        
    except Exception as e:
        logger.error(f"Failed to ingest SQL: {e}")
        print(f"{Fore.RED}Error during SQL ingestion: {e}{Style.RESET_ALL}")
    finally:
        conn.close()

def verify_data_integrity(cursor):
    """
    Runs detailed counts to verify the ingestion and content status.
    """
    print(f"\n{Fore.CYAN}--- Data Integrity Check ---{Style.RESET_ALL}")
    
    # General Table Counts
    tables = [
        ("Total Rows in Posts", config.TABLE_MAPPING['posts']),
        ("Total Post Meta", config.TABLE_MAPPING['postmeta']),
        ("Total Terms/Cats", config.TABLE_MAPPING['terms']),
        ("Total Users", config.TABLE_MAPPING['users'])
    ]
    
    for label, table_name in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            count = cursor.fetchone()[0]
            print(f"{Fore.WHITE}{label.ljust(25)}: {Fore.GREEN}{count}")
        except sqlite3.OperationalError:
            print(f"{Fore.WHITE}{label.ljust(25)}: {Fore.RED}Table not found")

    # Content Status Breakdown
    print(f"\n{Fore.WHITE}Post Status Breakdown (All Types):")
    try:
        cursor.execute(f"SELECT post_status, COUNT(*) FROM `{config.TABLE_MAPPING['posts']}` GROUP BY post_status")
        for status, count in cursor.fetchall():
            display_status = status
            if status == 'inherit':
                display_status = "old versions/revisions"
            
            if status in config.MIGRATE_STATUSES:
                color = Fore.GREEN
                tag = "(Will Migrate)"
            else:
                color = Fore.YELLOW
                tag = ""
            print(f"  {Fore.WHITE}{display_status.ljust(25)}: {color}{str(count).ljust(10)} {tag}")
    except Exception:
        pass

    # Content to Migrate by Type
    status_placeholders = ', '.join(['?'] * len(config.MIGRATE_STATUSES))
    print(f"\n{Fore.WHITE}Content to Migrate by Type ({', '.join(config.MIGRATE_STATUSES)}):")
    try:
        cursor.execute(f"SELECT post_type, COUNT(*) FROM `{config.TABLE_MAPPING['posts']}` WHERE post_status IN ({status_placeholders}) GROUP BY post_type", config.MIGRATE_STATUSES)
        results = cursor.fetchall()
        for ptype, count in results:
            print(f"  {Fore.WHITE}{ptype.ljust(15)}: {Fore.CYAN}{count}")
    except Exception:
        pass
    
    print(f"{Fore.CYAN}----------------------------{Style.RESET_ALL}\n")
