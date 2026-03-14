# 🎓 RAG — Data Analytics & AI Master's Degree

A Retrieval-Augmented Generation (RAG) system that turns the entire material from a master's degree into a searchable knowledge base using natural language queries.

![RAG Pipeline](assets/rag_pipeline.png)

## The problem

After completing the coursework of a master's program with hundreds of files — PDFs, slides, notebooks, Python and R scripts — accessing accumulated knowledge was slow and inefficient. This project solves that problem by centralizing all course material into a local vector database queryable through a conversational interface.

## How it works

The system operates in two phases:

**Ingestion (offline, one-time):** Documents are loaded, split into overlapping chunks, transformed into vector embeddings using a local model, and stored in a persistent vector database.

**Query (real-time):** The user types a question in natural language. The system retrieves the most relevant chunks from the vector store, sends them as context to an LLM, and generates a precise answer citing the sources.

## Tech stack

| Component | Technology |
|---|---|
| Embeddings | `all-MiniLM-L6-v2` (sentence-transformers, local) |
| Vector store | ChromaDB (persistent on disk) |
| LLM | Groq API — Llama 3.3 70B (free tier) |
| Interface | Streamlit |
| Orchestration | LangChain |
| Language | Python 3.11+ |

The system supports multiple interchangeable LLM providers without code changes: **Ollama** (local), **Groq**, **Google Gemini**, and **HuggingFace**.

## Project structure

```
rag-master-ai/
├── app.py                 # Streamlit interface
├── ingest.py              # Document ingestion pipeline
├── rag_engine.py          # RAG engine (retrieval + generation)
├── config.py              # Centralized configuration
├── organizar_docs.py      # Automatic file classification script
├── requirements.txt
├── .env.example           # Environment variables template
├── docs/                  # Directory for source documents
│   └── LEEME.txt
└── utils/
    ├── __init__.py
    └── loaders.py         # File type loaders
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/rag-master-ai.git
cd rag-master-ai
```

### 2. Create virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### 3. Configure the LLM provider

```bash
cp .env.example .env
```

Edit `.env` with your chosen provider and API key. Example with Groq (recommended):

```
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

For fully offline usage, configure Ollama:

```
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
```

### 4. Add your documents

Copy the files you want to index into `docs/`. Subdirectories are supported. Accepted formats: PDF, DOCX, PPTX, TXT, MD, CSV, HTML, EPUB.

For large collections, the `organizar_docs.py` script automatically classifies files by type and filters out non-ingestible ones:

```bash
python organizar_docs.py --origen /path/to/your/files --destino ./docs --ejecutar
```

### 5. Run the ingestion

```bash
python ingest.py
```

### 6. Launch the app

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

## Free LLM options

| Provider | Model | Free tier | Requires internet |
|---|---|---|---|
| **Ollama** | llama3.1:8b | Unlimited | No (local) |
| **Groq** | llama-3.3-70b-versatile | 6,000 req/day | Yes |
| **Google Gemini** | gemini-2.0-flash | 1,500 req/day | Yes |
| **HuggingFace** | Mistral-7B-Instruct | Rate-limited | Yes |

## Original project stats

In the original implementation on a full master's degree course material:

- **22,662** files scanned
- **~500** ingestible files after automatic filtering
- **9,108** chunks generated
- **Full ingestion** in ~10 minutes (MacBook, CPU only)
- **Embeddings** generated locally without GPU

## Notes

- Course documents are not included in this repository for copyright reasons.
- The vector database (`vectorstore/`) is generated locally and not tracked in version control.
- The `.env` file containing API keys is excluded from the repository for security.

## License

MIT
 
