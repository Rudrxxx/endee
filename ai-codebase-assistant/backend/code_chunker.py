"""
code_chunker.py
---------------
Splits source code files into manageable chunks for semantic search and LLM context.
"""

from typing import List, Dict

def chunk_code_files(code_files: List[Dict], chunk_size: int = 400, overlap: int = 50) -> List[Dict]:
    """
    Split a list of code file dictionaries into smaller chunks.

    Each chunk aims to be between 300-500 characters. By default, we use 400 
    characters as the target window.

    Args:
        code_files (List[Dict]): List of dicts from code_loader, each with:
                                 "file_path", "file_name", "code_content".
        chunk_size (int): Target number of characters per chunk.
        overlap (int): Number of characters to overlap between consecutive chunks 
                       to maintain context.

    Returns:
        List[Dict]: A list of chunks, each with:
                    - "file_name" (str)
                    - "file_path" (str)
                    - "chunk_id" (str) - formatted as "filename_index"
                    - "chunk_text" (str)
    """
    all_chunks: List[Dict] = []

    for file_data in code_files:
        content = file_data["code_content"]
        file_name = file_data["file_name"]
        file_path = file_data["file_path"]
        
        # If the file is empty, we skip it or create one empty chunk
        if not content.strip():
            continue

        start = 0
        chunk_index = 0
        
        while start < len(content):
            # Calculate end of chunk
            end = start + chunk_size
            
            # If we're not at the very end, try to find the nearest newline 
            # to avoid splitting in the middle of a line. 
            # We look in the range [end-50, end+50] to keep it around 300-500.
            if end < len(content):
                # Try to find a newline within a reasonable range to make the cut cleaner
                newline_pos = content.find('\n', end - 50, end + 50)
                if newline_pos != -1:
                    end = newline_pos + 1 # Include the newline

            chunk_text = content[start:end].strip()
            
            if chunk_text:
                all_chunks.append({
                    "file_name": file_name,
                    "file_path": file_path,
                    "chunk_id": f"{file_name}_{chunk_index}",
                    "chunk_text": chunk_text
                })
                chunk_index += 1
            
            # Move start pointer forward, considering overlap
            start = end - overlap
            
            # Safety break to avoid infinite loop if progress isn't made
            if start >= len(content) or (end >= len(content)):
                break
            if start < 0: start = 0 # sanity check

    return all_chunks
