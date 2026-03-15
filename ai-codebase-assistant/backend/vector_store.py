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
                    "precision": "float32"
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
    Inserts embeddings into the Endee vector store using msgpack format.

    The Endee JSON insert path silently discards vectors (returns 200 but
    stores nothing). The correct path is application/msgpack, which maps
    to the ndd::HybridVectorObject struct layout:

        MSGPACK_DEFINE(id, meta, filter, norm, vector, sparse_ids, sparse_values)

    Where:
      - id           : str
      - meta         : bytes  (metadata serialised to utf-8 bytes)
      - filter       : str    (empty string if unused)
      - norm         : float  (0.0 for cosine, computed server-side)
      - vector       : list[float]
      - sparse_ids   : list[uint32]  (empty for dense-only)
      - sparse_values: list[float]   (empty for dense-only)

    Serialised as a msgpack array-of-arrays (list of objects).
    """
    import msgpack

    url = f"{ENDEE_URL}/api/v1/index/{INDEX_NAME}/vector/insert"

    # Build list of HybridVectorObjects as msgpack arrays in field order
    objects = []
    for item in embeddings_data:
        metadata = item["metadata"].copy()
        metadata["chunk_text"] = item["chunk_text"]

        # meta is stored as raw bytes
        meta_bytes = json.dumps(metadata).encode("utf-8")

        objects.append([
            metadata["chunk_id"],          # id  (str)
            meta_bytes,                     # meta (bytes)
            "",                             # filter (str, unused)
            0.0,                            # norm (float, 0 = auto)
            item["embedding"].tolist(),     # vector (list[float])
            [],                             # sparse_ids (empty)
            [],                             # sparse_values (empty)
        ])

    body = msgpack.packb(objects, use_bin_type=True)

    try:
        resp = requests.post(
            url,
            data=body,
            headers={"Content-Type": "application/msgpack"},
        )
        resp.raise_for_status()
        print(f"[vector_store] Successfully inserted {len(objects)} vectors.")
    except Exception as e:
        print(f"[vector_store] Error inserting embeddings: {e}")
        print(f"[vector_store] Server response: {resp.text}")
        raise



def search_similar(query_vector: List[float], top_k: int = 5) -> List[Dict]:
    """
    Performs similarity search in the Endee vector store.

    Endee returns results as msgpack-encoded ResultSet:
        ResultSet { results: [VectorResult] }
        MSGPACK_DEFINE(results)   → serialised as [[results_list]]

    Each VectorResult:
        MSGPACK_DEFINE(similarity, id, meta, filter, norm, vector)
        → [similarity(float), id(str), meta(bytes), filter(str), norm(float), vector(list)]

    Args:
        query_vector (List[float]): The vector to search for.
        top_k (int): Number of similar items to return.

    Returns:
        List[Dict]: List of results. Empty if no matches or on error.
    """
    import msgpack

    url = f"{ENDEE_URL}/api/v1/index/{INDEX_NAME}/search"
    payload = {"vector": query_vector, "k": top_k}

    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type", "")

        if "msgpack" in content_type:
            raw = msgpack.unpackb(resp.content, raw=False)
        else:
            # Fallback: JSON (rarely used by Endee for search)
            raw = resp.json()

        # ── Decode ResultSet ──────────────────────────────────────────────
        # The msgpack search response is a flat list of VectorResult arrays:
        #   [ [similarity, id, meta_bytes, filter, norm, vector?], ... ]
        # (NOT nested inside a ResultSet wrapper)
        if isinstance(raw, list):
            result_items = raw
        elif isinstance(raw, dict):
            result_items = raw.get("results", raw.get("data", []))
        else:
            result_items = []

        if not result_items:
            return []

        final_results = []
        for item in result_items:
            # VectorResult as msgpack array: [similarity, id, meta_bytes, filter, norm, vector]
            if isinstance(item, (list, tuple)) and len(item) >= 3:
                similarity  = item[0]
                chunk_id    = item[1] if isinstance(item[1], str) else str(item[1])
                meta_raw    = item[2]
                # fields 3+ are filter, norm, vector (optional)
            elif isinstance(item, dict):
                # JSON / dict fallback path
                similarity = item.get("similarity") or item.get("score") or item.get("distance")
                chunk_id   = item.get("id", "")
                meta_raw   = item.get("meta") or item.get("metadata") or b"{}"
            else:
                continue

            # Decode meta bytes → JSON dict
            if isinstance(meta_raw, (bytes, bytearray)):
                try:
                    metadata = json.loads(meta_raw.decode("utf-8"))
                except Exception:
                    metadata = {}
            elif isinstance(meta_raw, str):
                try:
                    metadata = json.loads(meta_raw)
                except Exception:
                    metadata = {}
            elif isinstance(meta_raw, dict):
                metadata = meta_raw
            else:
                metadata = {}

            final_results.append({
                "score":      similarity,
                "chunk_text": metadata.get("chunk_text", ""),
                "file_name":  metadata.get("file_name", ""),
                "chunk_id":   metadata.get("chunk_id", chunk_id),
                "metadata":   metadata,
            })

        return final_results

    except Exception as e:
        print(f"[vector_store] Error searching similar: {e}")
        if "msgpack" in str(e):
            print("[vector_store] Hint: run 'pip install msgpack'")
        raise
