"""
config.py — Configuración centralizada del RAG
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# RUTAS
# ─────────────────────────────────────────────
DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
VECTORSTORE_DIR = os.path.join(os.path.dirname(__file__), "vectorstore")

# ─────────────────────────────────────────────
# CHUNKING
# ─────────────────────────────────────────────
CHUNK_SIZE = 1000          # caracteres por chunk
CHUNK_OVERLAP = 200        # solapamiento entre chunks
SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

# ─────────────────────────────────────────────
# EMBEDDINGS (local, gratuito)
# ─────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ─────────────────────────────────────────────
# CHROMADB
# ─────────────────────────────────────────────
COLLECTION_NAME = "master_ia_docs"
TOP_K = 5                  # documentos a recuperar por consulta

# ─────────────────────────────────────────────
# LLM — Seleccionar proveedor
# Opciones: "ollama", "groq", "gemini", "huggingface"
# ─────────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

# Ollama (local)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Groq (gratuito con API key)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

# Google Gemini (gratuito con API key)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# HuggingFace (gratuito con token)
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")

# ─────────────────────────────────────────────
# PROMPT DEL SISTEMA
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """Eres un asistente académico experto en el Máster de Análisis de Datos e Inteligencia Artificial.
Tu función es responder preguntas EXCLUSIVAMENTE con base en el material del máster proporcionado como contexto.

Reglas:
1. Responde siempre en español.
2. Si la respuesta no se encuentra en el contexto proporcionado, indica claramente:
   "No he encontrado información sobre esto en el material del máster."
3. Cita las fuentes (nombre del archivo y sección) cuando sea posible.
4. Sé preciso, estructurado y didáctico en tus respuestas.
5. Si la pregunta es ambigua, pide aclaración antes de responder.
"""
