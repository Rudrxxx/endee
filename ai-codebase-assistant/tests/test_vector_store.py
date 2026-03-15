"""
test_vector_store.py
--------------------
Verifies connectivity, data insertion, and similarity search 
functionality with the Endee vector database.
"""

import numpy as np
from backend.vector_store import connect_to_endee, insert_embeddings, search_similar

def run_vector_store_test():
    print("--- Connecting to Endee ---")
    try:
        connect_to_endee()
        
        # 1. Prepare sample data
        sample_embeddings = [
            {
                "embedding": np.random.rand(384).astype(np.float32),
                "chunk_text": "First sample chunk of code for testing Endee.",
                "metadata": {"file_name": "test_1.py", "chunk_id": "test_1_0"}
            },
            {
                "embedding": np.random.rand(384).astype(np.float32),
                "chunk_text": "Second sample chunk of code for testing Endee search.",
                "metadata": {"file_name": "test_2.py", "chunk_id": "test_2_0"}
            }
        ]
        
        # 2. Insert embeddings
        print("\n--- Inserting 2 sample embeddings ---")
        insert_embeddings(sample_embeddings)
        
        # 3. Perform similarity search
        print("\n--- Performing similarity search ---")
        # Use the first vector as query for a guaranteed match
        query_vector = sample_embeddings[0]["embedding"].tolist()
        results = search_similar(query_vector, top_k=2)
        
        print(f"Retrieved {len(results)} chunks:")
        for i, res in enumerate(results):
            print(f"\nResult {i+1} (Score: {res['score']:.4f}):")
            print(f"File: {res['file_name']}")
            print(f"Content: {res['chunk_text']}")
            
    except Exception as e:
        print(f"Error during vector store test: {e}")
        print("\nNote: Make sure the Endee server is running (port 8080).")

if __name__ == "__main__":
    run_vector_store_test()
