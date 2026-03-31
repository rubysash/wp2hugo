import os
import sys
import shutil
import logging
import config
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def run_preflight_checks():
    """
    Validates the environment, configuration, and input files before migration starts.
    Returns True if all checks pass, otherwise False.
    """
    logger = logging.getLogger(__name__)
    print(f"{Fore.CYAN}Stage 0: Running pre-flight checks...{Style.RESET_ALL}")

    # 1. Check for SQL Input File

    if not os.path.exists(config.SQL_INPUT_FILE):
        print(f"{Fore.RED}CRITICAL: SQL input file '{config.SQL_INPUT_FILE}' not found.{Style.RESET_ALL}")
        logger.error(f"SQL input file '{config.SQL_INPUT_FILE}' not found.")
        return False

    # 2. Check SQL Content (Basic Validation)
    try:
        with open(config.SQL_INPUT_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            head = [next(f) for _ in range(100)]
            content = "".join(head)
            if "INSERT INTO" not in content and "CREATE TABLE" not in content:
                print(f"{Fore.RED}CRITICAL: '{config.SQL_INPUT_FILE}' does not appear to be a valid SQL dump.{Style.RESET_ALL}")
                logger.error(f"'{config.SQL_INPUT_FILE}' does not appear to be a valid SQL dump.")
                return False
            if config.WP_PREFIX not in content:
                print(f"{Fore.YELLOW}WARNING: Table prefix '{config.WP_PREFIX}' not found in the first 100 lines.{Style.RESET_ALL}")
                logger.warning(f"Table prefix '{config.WP_PREFIX}' not found in the first 100 lines.")
    except Exception as e:
        print(f"{Fore.RED}CRITICAL: Could not read SQL file: {e}{Style.RESET_ALL}")
        logger.error(f"Could not read SQL file: {e}")
        return False

    # 3. Check Dependencies
    required_libs = ["yaml", "markdownify", "requests", "sqlite3", "colorama"]
    for lib in required_libs:
        try:
            __import__(lib)
        except ImportError:
            print(f"{Fore.RED}CRITICAL: Missing required library '{lib}'. Run 'pip install -r requirements.txt'.{Style.RESET_ALL}")
            logger.error(f"Missing required library '{lib}'.")
            return False

    # 4. Check Permissions/Directories
    try:
        test_file = "test_perm.tmp"
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
    except Exception:
        print(f"{Fore.RED}CRITICAL: No write permissions in the current directory.{Style.RESET_ALL}")
        logger.error("No write permissions in the current directory.")
        return False

    print(f"{Fore.GREEN}Pre-flight checks passed.{Style.RESET_ALL}")
    return True
