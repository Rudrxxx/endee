# test_search.py

from backend.vector_store import search_vectors
from backend.query_processor import embed_query

query = "embedding generation"
vector = embed_query(query)

results = search_vectors(vector, k=5)

print("RAW RESULTS:")
print(results)