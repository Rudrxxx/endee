# AI Codebase Assistant using Endee Vector Database

A developer tool that lets you ask **natural language questions about any codebase** and instantly retrieve the most semantically relevant code snippets — powered by the [Endee](https://endee.io) high-performance vector database.

---

## Problem Statement

Modern codebases can span hundreds of files and thousands of functions. Traditional keyword search falls short because it can't understand *meaning* — searching for "authentication" won't find a function called `verify_token()` unless both words appear together.

Semantic search solves this by converting code into dense vector embeddings that capture conceptual similarity, not just textual overlap. This lets developers ask questions like *"How is the database connection managed?"* and get back the exact relevant code — even if none of those words appear verbatim in the source.

---

## System Architecture

```
Your Codebase
     │
     ▼
┌─────────────────────────────────────────────┐
│  Ingestion Pipeline (ingest_codebase.py)    │
│                                             │
│  1. Load     – Scan for .py .js .ts ...     │
│  2. Chunk    – Split into ~400-char segments │
│  3. Embed    – all-MiniLM-L6-v2 (384-dim)  │
│  4. Insert   – Push vectors into Endee      │
└─────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────┐
│  Endee Vector Database │  ← stores vectors + metadata
└────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│  Query Pipeline (rag_pipeline.py)           │
│                                             │
│  1. Embed query  – same model for alignment │
│  2. Search Endee – top-k cosine similarity  │
│  3. Return chunks with file name + score    │
└─────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────┐
│  Streamlit UI (app.py) │  ← developer chat interface
└────────────────────────┘
```

---

## How Endee is Used

**Endee** is an open-source, high-performance vector database optimised for Approximate Nearest Neighbour (ANN) search.

| Feature | How it's used |
|---|---|
| **Vector Storage** | Code chunk embeddings (384-dim float32) are stored via `POST /api/v1/index/<name>/vector/insert` along with JSON metadata (`file_name`, `chunk_id`, `chunk_text`). |
| **Similarity Search** | At query time, `POST /api/v1/index/<name>/search` accepts a query vector and returns the top-k closest chunks by cosine distance. |
| **Index Management** | A `codebase_index` is created automatically on first run via `POST /api/v1/index/create`. All calls go through `backend/vector_store.py`. |

---

## Project Structure

```
ai-codebase-assistant/
├── backend/
│   ├── code_loader.py       # Recursively scan and read source files
│   ├── code_chunker.py      # Split files into overlapping chunks
│   ├── embedder.py          # Generate embeddings (sentence-transformers)
│   ├── query_processor.py   # Embed a user query
│   ├── vector_store.py      # Endee connection, insert, and search
│   ├── rag_pipeline.py      # End-to-end retrieval pipeline
│   └── ingest_codebase.py   # CLI tool to ingest a repository
├── frontend/
│   └── app.py               # Streamlit UI
├── tests/                   # Verification scripts for each module
├── data/                    # Sample data and indexed repos
├── utils/                   # Shared utilities
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Rudrxxx/endee.git
cd endee/ai-codebase-assistant
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Build and Start Endee

From the repository root:

```bash
cd ..              # endee/
mkdir build && cd build
cmake .. -DUSE_NEON=ON   # macOS Apple Silicon; use -DUSE_AVX2=ON for x86
make -j$(nproc)
cd ..
./run.sh
```

Endee will start on **`http://localhost:8080`**.

### 4. Ingest Your Codebase

Point the ingestion script at any directory containing source files:

```bash
python3 backend/ingest_codebase.py --repo_path ./data/sample_repo
```

This will load, chunk, embed, and insert all code into Endee automatically.

### 5. Launch the UI

```bash
streamlit run frontend/app.py
```

Then open **`http://localhost:8501`** in your browser.

---

## Example Usage

| Question | What it finds |
|---|---|
| `How is user authentication handled?` | Functions related to login, tokens, sessions |
| `Where are database connections managed?` | DB init code, connection pooling |
| `How does the chunking algorithm work?` | The `chunk_code_files` logic |
| `What endpoints does the API expose?` | Route definitions and handlers |

---

## Tech Stack

| Component | Technology |
|---|---|
| Embedding model | [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) |
| Vector database | [Endee](https://endee.io) (open-source, Apache 2.0) |
| API communication | Python `requests` + `msgpack` |
| Frontend | [Streamlit](https://streamlit.io) |
| Language | Python 3.10+ |

---

## License

[MIT](../LICENSE)
