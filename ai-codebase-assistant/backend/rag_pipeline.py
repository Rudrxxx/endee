"""
rag_pipeline.py
---------------
Retrieval-Augmented Generation (RAG) pipeline for the AI Codebase Assistant.
Connects the query processor to the Endee vector store to retrieve code chunks.
"""

from typing import List, Dict
from backend.query_processor import embed_query
from backend.vector_store import connect_to_endee, search_similar


def retrieve_relevant_chunks(query: str, top_k: int = 5) -> List[Dict]:
    """
    Full end-to-end retrieval pipeline.
    
    1. Embeds the user's natural language query.
    2. Searches Endee for the most semantically similar code chunks.
    3. Returns the top results with their metadata.

    Args:
        query (str): A natural language question about the codebase.
        top_k (int): Number of top results to retrieve.

    Returns:
        List[Dict]: List of results, each containing:
            - "chunk_text"  (str): The code chunk content.
            - "file_name"   (str): The source file name.
            - "chunk_id"    (str): The unique chunk identifier.
            - "score"       (float): Cosine similarity score.
            
    Raises:
        ConnectionError: If the Endee server is unreachable.
        ValueError: If the query string is empty.
    """
    if not query or not query.strip():
        raise ValueError("Query must not be empty.")

    # Step 1: Connect to Endee and verify index exists
    connect_to_endee()

    # Step 2: Embed the query into a vector
    query_vector = embed_query(query).tolist()

    # Step 3: Retrieve top-k similar chunks from Endee
    results = search_similar(query_vector, top_k=top_k)

    return results
