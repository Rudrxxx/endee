"""
ingest_codebase.py
------------------
CLI tool to process a repository and store its embeddings in the Endee vector database.

Usage:
    python3 backend/ingest_codebase.py --repo_path ./data/sample_repo
"""

import sys
import os
import argparse

# Ensure the project root is on the path so backend.* imports resolve correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.code_loader import load_codebase
from backend.code_chunker import chunk_code_files
from backend.embedder import generate_embeddings
from backend.vector_store import connect_to_endee, insert_embeddings


def ingest(repo_path: str) -> None:
    """
    Full ingestion pipeline: load -> chunk -> embed -> insert into Endee.

    Args:
        repo_path (str): Path to the repository directory to process.
    """

    # ─── Stage 1: Connect to Endee ────────────────────────────────────────────
    print("\n[1/4] Connecting to Endee and ensuring index exists...")
    connect_to_endee()

    # ─── Stage 2: Load Files ─────────────────────────────────────────────────
    print(f"\n[2/4] Loading code files from: {repo_path}")
    code_files = load_codebase(repo_path)
    print(f"      ✔ Files loaded: {len(code_files)}")

    if not code_files:
        print("      No supported code files found. Exiting.")
        return

    # ─── Stage 3: Chunk Files ─────────────────────────────────────────────────
    print("\n[3/4] Chunking files into segments...")
    chunks = chunk_code_files(code_files)
    print(f"      ✔ Chunks created: {len(chunks)}")

    if not chunks:
        print("      No chunks generated. Exiting.")
        return

    # ─── Stage 4: Generate Embeddings ────────────────────────────────────────
    print("\n[4/4] Generating semantic embeddings...")
    embeddings = generate_embeddings(chunks)
    print(f"      ✔ Embeddings generated: {len(embeddings)}")

    # ─── Stage 5: Insert into Endee ──────────────────────────────────────────
    print("\n[5/5] Inserting vectors into Endee...")
    insert_embeddings(embeddings)
    print(f"      ✔ Vectors inserted: {len(embeddings)}")

    print("\n✅ Ingestion complete! The codebase is now searchable.")


def main():
    parser = argparse.ArgumentParser(
        description="Ingest a codebase into the Endee vector database."
    )
    parser.add_argument(
        "--repo_path",
        type=str,
        required=True,
        help="Path to the repository directory to ingest.",
    )
    args = parser.parse_args()

    repo_path = os.path.abspath(args.repo_path)

    if not os.path.isdir(repo_path):
        print(f"Error: '{repo_path}' is not a valid directory.")
        sys.exit(1)

    ingest(repo_path)


if __name__ == "__main__":
    main()
