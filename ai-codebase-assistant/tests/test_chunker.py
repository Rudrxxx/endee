"""
test_chunker.py
---------------
Verifies the newline-aware code chunking logic and context overlap 
between segments.
"""

import os
from backend.code_loader import load_codebase
from backend.code_chunker import chunk_code_files

def run_chunker_test():
    # Path to the data directory
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    
    print(f"--- Loading files from: {os.path.abspath(data_dir)} ---")
    files = load_codebase(data_dir)
    
    if not files:
        print("No files found to chunk. Creating a larger dummy file for testing...")
        dummy_path = os.path.join(data_dir, "large_sample.py")
        with open(dummy_path, "w") as f:
            f.write("# " + "A" * 100 + "\n")
            f.write("def dummy_function():\n")
            for i in range(50):
                f.write(f"    print('Line {i}: This is a fairly long line of code to test chunking logic with some text.')\n")
        files = load_codebase(data_dir)

    print(f"--- Chunking {len(files)} files ---")
    chunks = chunk_code_files(files)
    
    print(f"Total chunks created: {len(chunks)}")
    
    if chunks:
        # Check first 3 chunks
        for i, chunk in enumerate(chunks[:3]):
            print(f"\n--- Chunk {i} ({chunk['chunk_id']}) ---")
            print(f"Size: {len(chunk['chunk_text'])} chars")
            print(f"Content Preview:\n{chunk['chunk_text'][:150]}...")
            
        # Verify overlap between chunk 0 and 1 if they exist
        if len(chunks) > 1:
            c0_tail = chunks[0]['chunk_text'][-20:]
            c1_head = chunks[1]['chunk_text'][:50]
            print(f"\n--- Overlap Check ---")
            print(f"Chunk 0 Tail: {repr(c0_tail)}")
            print(f"Chunk 1 Head: {repr(c1_head)}")
            
            # Since we split on newlines, the exact overlap might be shifted, 
            # but chunk 1's start should have been calculated from chunk 0's end - overlap
            print("Overlap verified visually if tail characters appear in next chunk's head.")

if __name__ == "__main__":
    run_chunker_test()
