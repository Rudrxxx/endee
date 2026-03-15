"""
query_processor.py
------------------
Processes user natural language queries into semantic embeddings.
"""

import numpy as np
from backend.embedder import get_model

def embed_query(query: str) -> np.ndarray:
    """
    Convert a user query string into a semantic embedding vector.
    
    Uses the same SentenceTransformer model ('all-MiniLM-L6-v2') as the 
    chunk embedder to ensure that queries and code chunks live in the 
    same vector space.

    Args:
        query (str): The natural language query from the user.

    Returns:
        np.ndarray: The 384-dimensional semantic vector.
    """
    model = get_model()
    
    # Generate embedding for a single string
    # sentence-transformers returns a numpy array by default
    embedding = model.encode(query)
    
    return np.array(embedding)
