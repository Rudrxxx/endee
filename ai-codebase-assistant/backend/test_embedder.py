import numpy as np
from embedder import generate_embeddings

def run_embedder_test():
    # Define some sample chunks for testing
    sample_chunks = [
        {
            "chunk_text": "def hello_world():\n    print('Hello World!')",
            "file_name": "test.py",
            "chunk_id": "test.py_0"
        },
        {
            "chunk_text": "class Assistant:\n    def __init__(self):\n        pass",
            "file_name": "assistant.py",
            "chunk_id": "assistant.py_0"
        }
    ]

    print(f"--- Generating embeddings for {len(sample_chunks)} chunks ---")
    
    try:
        results = generate_embeddings(sample_chunks)
        
        print(f"Number of embeddings generated: {len(results)}")
        
        if results:
            first_vector = results[0]["embedding"]
            print(f"Length of first embedding vector: {len(first_vector)}")
            print(f"Type of embedding: {type(first_vector)}")
            
            # Verify it's a numpy array
            if isinstance(first_vector, np.ndarray):
                print("Verification: Embedding is a numpy array.")
            else:
                print("Warning: Embedding is NOT a numpy array.")
                
            # Print metadata check
            print(f"Metadata check: {results[0]['metadata']}")
            
    except Exception as e:
        print(f"Error during embedding test: {e}")
        print("\nNote: Make sure 'sentence-transformers' is installed: pip install sentence-transformers")

if __name__ == "__main__":
    run_embedder_test()
