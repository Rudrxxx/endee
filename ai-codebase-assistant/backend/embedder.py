"""
embedder.py
-----------
Handles generating semantic embeddings for code chunks using sentence-transformers.
"""

from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer

# Singleton model instance
_MODEL = None

def get_model():
    """Lazy-load the transformer model single time."""
    global _MODEL
    if _MODEL is None:
        print("[embedder] Loading semantic model (all-MiniLM-L6-v2)...")
        _MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    return _MODEL

def generate_embeddings(chunks: List[Dict]) -> List[Dict]:
    """
    Generate embedding vectors for each code chunk.

    Args:
        chunks (List[Dict]): Chunks with "chunk_text", "file_name", "chunk_id", etc.

    Returns:
        List[Dict]: Enhanced chunks with "embedding" (numpy array) and core metadata.
    """
    if not chunks:
        return []

    model = get_model()
    
    # Extract only the text for batch processing
    texts = [c["chunk_text"] for c in chunks]
    
    # Generate embeddings in batch
    embeddings = model.encode(texts)
    
    results: List[Dict] = []
    for i, chunk in enumerate(chunks):
        results.append({
            "embedding": embeddings[i],
            "chunk_text": chunk["chunk_text"],
            "metadata": {
                "file_name": chunk["file_name"],
                "chunk_id": chunk["chunk_id"],
                "file_path": chunk.get("file_path", "")
            }
        })
        
    return results
