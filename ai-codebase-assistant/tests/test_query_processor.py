"""
test_query_processor.py
-----------------------
Verifies that natural language queries are correctly converted into 
the target semantic vector space.
"""

import numpy as np
from backend.query_processor import embed_query

def run_query_processor_test():
    query = "How do I implement user authentication in this codebase?"
    
    print(f"--- Embedding query: {query!r} ---")
    
    try:
        embedding = embed_query(query)
        
        print(f"Embedding generated: Yes")
        print(f"Vector dimension: {embedding.shape[0]}")
        print(f"Vector type: {type(embedding)}")
        
        # Verify dimension
        if embedding.shape[0] == 384:
            print("Verification: Dimension is correct (384).")
        else:
            print(f"Warning: Unexpected dimension ({embedding.shape[0]}).")
            
        # Preview vector
        print(f"Vector preview: {embedding[:5]}...")
        
    except Exception as e:
        print(f"Error during query processor test: {e}")

if __name__ == "__main__":
    run_query_processor_test()
