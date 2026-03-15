# AI Codebase Assistant using Endee

A developer tool that uses semantic search and AI to help you understand, navigate, and query your codebase using natural language — powered by **Endee**.

---

## Architecture

> _Placeholder: Describe the high-level architecture here (e.g., embedding pipeline, vector store, API layer, frontend UI)._

```
ai-codebase-assistant/
├── backend/    # FastAPI server — handles embedding, retrieval, and LLM responses
├── frontend/   # Streamlit UI — user-facing chat interface
├── data/       # Indexed codebase chunks and vector stores
├── utils/      # Shared utilities (chunking, embedding helpers, etc.)
```

---

## Setup

> _Placeholder: Add setup instructions here._

1. Clone the repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in the required values.

---

## Usage

> _Placeholder: Add usage instructions here._

**Start the backend:**
```bash
uvicorn backend.main:app --reload
```

**Start the frontend:**
```bash
streamlit run frontend/app.py
```

Then open your browser and navigate to `http://localhost:8501` to interact with the assistant.

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss what you'd like to change.

---

## License

[MIT](LICENSE)
