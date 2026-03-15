"""
vector_store.py
---------------
Integrates with the Endee vector database for storing and searching code embeddings.
"""

import json
import requests
from typing import List, Dict, Optional

# Configuration
ENDEE_URL = "http://localhost:8080"
INDEX_NAME = "codebase_index"
DENSE_DIM = 384  # Dimensionality of all-MiniLM-L6-v2

def connect_to_endee() -> str:
    """
    Ensures connection to Endee and verifies that the index exists.
    Returns the base URL.
    """
    try:
        # Check health
        resp = requests.get(f"{ENDEE_URL}/api/v1/health")
        resp.raise_for_status()
        print(f"[vector_store] Connected to Endee: {resp.json().get('status')}")
        
        # Ensure index exists
        ensure_index_exists()
        
    except Exception as e:
        print(f"[vector_store] Error connecting to Endee: {e}")
        raise
    
    return ENDEE_URL

def ensure_index_exists():
    """Checks if the codebase index exists, and creates it if not."""
    try:
        # List indices
        resp = requests.get(f"{ENDEE_URL}/api/v1/index/list")
        resp.raise_for_status()
        indices = resp.json().get("indexes", [])
        
        if not any(idx["name"] == INDEX_NAME for idx in indices):
            print(f"[vector_store] Creating index: {INDEX_NAME}")
            create_resp = requests.post(
                f"{ENDEE_URL}/api/v1/index/create",
                json={
                    "index_name": INDEX_NAME,
                    "dim": DENSE_DIM,
                    "space_type": "cosine",
                    "precision": "int16"
                }
            )
            create_resp.raise_for_status()
        else:
            print(f"[vector_store] Index {INDEX_NAME} already exists.")
            
    except Exception as e:
        print(f"[vector_store] Error ensuring index exists: {e}")
        raise

def insert_embeddings(embeddings_data: List[Dict]):
    """
    Inserts embeddings into the Endee vector store.
    
    Args:
        embeddings_data (List[Dict]): List of dicts each containing:
            - "embedding" (numpy array)
            - "chunk_text" (str)
            - "metadata" (Dict: file_name, chunk_id, etc.)
    """
    url = f"{ENDEE_URL}/api/v1/index/{INDEX_NAME}/vector/insert"
    
    payload = []
    for item in embeddings_data:
        # Endee expects a string for metadata
        metadata = item["metadata"].copy()
        metadata["chunk_text"] = item["chunk_text"]
        
        payload.append({
            "id": metadata["chunk_id"],
            "vector": item["embedding"].tolist(), # Convert numpy to list
            "meta": json.dumps(metadata) # Storing metadata as JSON string
        })
    
    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        print(f"[vector_store] Successfully inserted {len(payload)} vectors.")
    except Exception as e:
        print(f"[vector_store] Error inserting embeddings: {e}")
        raise

def search_similar(query_vector: List[float], top_k: int = 5) -> List[Dict]:
    """
    Performs similarity search in the Endee vector store.
    
    Args:
        query_vector (List[float]): The vector to search for.
        top_k (int): Number of similar items to return.
        
    Returns:
        List[Dict]: List of results with chunk text and metadata.
    """
    url = f"{ENDEE_URL}/api/v1/index/{INDEX_NAME}/search"
    
    payload = {
        "vector": query_vector,
        "k": top_k
    }
    
    try:
        # Note: The search endpoint might return application/msgpack 
        # based on the C++ code, but Crow usually handles JSON if requested.
        # Let's try JSON first as it's easier to debug here.
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        
        # The C++ code uses msgpack for search results, so we might need a msgpack library
        # if the server doesn't fallback to JSON.
        # Let's check the Content-Type of the response.
        if resp.headers.get("Content-Type") == "application/msgpack":
            import msgpack
            results = msgpack.unpackb(resp.content)
        else:
            results = resp.json()
            
        final_results = []
        for res in results:
            # Parse the metadata string back to dict
            metadata = json.loads(res.get("meta", "{}"))
            final_results.append({
                "score": res.get("score"),
                "chunk_text": metadata.get("chunk_text", ""),
                "file_name": metadata.get("file_name", ""),
                "chunk_id": metadata.get("chunk_id", ""),
                "metadata": metadata
            })
            
        return final_results
        
    except Exception as e:
        print(f"[vector_store] Error searching similar: {e}")
        # If msgpack is missing, let's suggest it
        if "msgpack" in str(e):
             print("[vector_store] Hint: run 'pip install msgpack'")
        raise
