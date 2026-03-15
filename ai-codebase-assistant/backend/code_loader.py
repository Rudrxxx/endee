"""
code_loader.py
--------------
Utility module to recursively scan a directory for source code files
and load their contents into a structured list of dictionaries.
"""

import os
from typing import Dict, List

# Supported source code file extensions
SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".java", ".cpp"}

# Maximum allowed file size (1 MB)
MAX_FILE_SIZE_BYTES = 1 * 1024 * 1024  # 1 MB


def load_codebase(directory_path: str) -> List[Dict]:
    """
    Recursively scan a directory for supported code files and return their contents.

    Only files with extensions in SUPPORTED_EXTENSIONS are included.
    Files larger than 1 MB are silently skipped.

    Args:
        directory_path (str): Absolute or relative path to the root directory to scan.

    Returns:
        List[Dict]: A list of dictionaries, each containing:
            - "file_path"    (str): The absolute path to the file.
            - "file_name"    (str): The base name of the file (e.g. "main.py").
            - "code_content" (str): The full text content of the file.

    Raises:
        ValueError: If the provided path does not exist or is not a directory.
        PermissionError: If the directory or a file cannot be accessed due to OS permissions.
    """
    if not os.path.exists(directory_path):
        raise ValueError(f"Path does not exist: {directory_path!r}")

    if not os.path.isdir(directory_path):
        raise ValueError(f"Path is not a directory: {directory_path!r}")

    results: List[Dict] = []

    for root, _dirs, files in os.walk(directory_path):
        for file_name in files:
            _, ext = os.path.splitext(file_name)

            # Skip unsupported file types
            if ext.lower() not in SUPPORTED_EXTENSIONS:
                continue

            file_path = os.path.abspath(os.path.join(root, file_name))

            # Skip files larger than 1 MB
            try:
                file_size = os.path.getsize(file_path)
            except OSError as e:
                print(f"[code_loader] Warning: could not stat file {file_path!r}: {e}")
                continue

            if file_size > MAX_FILE_SIZE_BYTES:
                print(f"[code_loader] Skipping large file ({file_size} bytes): {file_path!r}")
                continue

            # Read file contents
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    code_content = f.read()
            except OSError as e:
                print(f"[code_loader] Warning: could not read file {file_path!r}: {e}")
                continue

            results.append(
                {
                    "file_path": file_path,
                    "file_name": file_name,
                    "code_content": code_content,
                }
            )

    return results
