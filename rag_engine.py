"""
rag_engine.py — Motor RAG: recuperación de contexto + generación de respuesta.

Soporta múltiples proveedores LLM gratuitos:
  - Ollama  (local, sin límite)
  - Groq    (API gratuita, muy rápido)
  - Gemini  (API gratuita de Google)
  - HuggingFace (API gratuita, más lento)
"""
import os
from typing import List, Dict, Optional, Tuple

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from config import (
    VECTORSTORE_DIR,
    EMBEDDING_MODEL,
    COLLECTION_NAME,
    TOP_K,
    LLM_PROVIDER,
    OLLAMA_MODEL, OLLAMA_BASE_URL,
    GROQ_API_KEY, GROQ_MODEL,
    GEMINI_API_KEY, GEMINI_MODEL,
    HF_API_TOKEN, HF_MODEL,
    SYSTEM_PROMPT,
)


class RAGEngine:
    """Motor de Retrieval-Augmented Generation."""

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        self.vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=VECTORSTORE_DIR,
        )
        self.llm = self._init_llm()

    # ── Inicialización del LLM ─────────────────────────────────

    def _init_llm(self):
        """Inicializa el LLM según el proveedor configurado."""
        provider = LLM_PROVIDER.lower()

        if provider == "ollama":
            return self._init_ollama()
        elif provider == "groq":
            return self._init_groq()
        elif provider == "gemini":
            return self._init_gemini()
        elif provider == "huggingface":
            return self._init_huggingface()
        else:
            raise ValueError(
                f"Proveedor LLM no reconocido: '{provider}'. "
                "Opciones: ollama, groq, gemini, huggingface"
            )

    def _init_ollama(self):
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1,
        )

    def _init_groq(self):
        from langchain_groq import ChatGroq
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY no configurada en .env")
        return ChatGroq(
            api_key=GROQ_API_KEY,
            model_name=GROQ_MODEL,
            temperature=0.1,
        )

    def _init_gemini(self):
        from langchain_google_genai import ChatGoogleGenerativeAI
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY no configurada en .env")
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0.1,
        )

    def _init_huggingface(self):
        from langchain_huggingface import HuggingFaceEndpoint
        if not HF_API_TOKEN:
            raise ValueError("HF_API_TOKEN no configurado en .env")
        return HuggingFaceEndpoint(
            repo_id=HF_MODEL,
            huggingfacehub_api_token=HF_API_TOKEN,
            temperature=0.1,
            max_new_tokens=1024,
        )

    # ── Recuperación ───────────────────────────────────────────

    def retrieve(self, query: str, top_k: int = TOP_K) -> List[Document]:
        """Recupera los chunks más relevantes para la consulta."""
        results = self.vectorstore.similarity_search(query, k=top_k)
        return results

    def _format_context(self, docs: List[Document]) -> str:
        """Formatea los documentos recuperados como contexto para el LLM."""
        if not docs:
            return "No se encontró contexto relevante en la base de datos."

        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("relative_path", doc.metadata.get("source_file", "desconocido"))
            page = doc.metadata.get("page", "")
            page_info = f" (pág. {page + 1})" if page != "" else ""

            context_parts.append(
                f"--- Fuente {i}: {source}{page_info} ---\n{doc.page_content}"
            )

        return "\n\n".join(context_parts)

    # ── Generación ─────────────────────────────────────────────

    def query(self, question: str, top_k: int = TOP_K) -> Dict:
        """
        Pipeline completo: recuperar contexto → generar respuesta.

        Returns:
            {
                "answer": str,
                "sources": List[Dict],     # fuentes utilizadas
                "context": str,            # contexto enviado al LLM
                "num_chunks": int,
            }
        """
        # 1. Recuperar contexto
        docs = self.retrieve(question, top_k=top_k)
        context = self._format_context(docs)

        # 2. Construir prompt
        user_prompt = f"""Contexto del material del máster:
{context}

Pregunta del estudiante:
{question}

Responde de forma precisa y estructurada basándote únicamente en el contexto proporcionado."""

        # 3. Generar respuesta
        from langchain_core.messages import SystemMessage, HumanMessage
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        response = self.llm.invoke(messages)

        # Extraer texto de la respuesta
        answer = response.content if hasattr(response, "content") else str(response)

        # 4. Preparar fuentes
        sources = []
        seen = set()
        for doc in docs:
            source_file = doc.metadata.get("source_file", "desconocido")
            if source_file not in seen:
                seen.add(source_file)
                sources.append({
                    "file": source_file,
                    "path": doc.metadata.get("relative_path", ""),
                    "page": doc.metadata.get("page", None),
                })

        return {
            "answer": answer,
            "sources": sources,
            "context": context,
            "num_chunks": len(docs),
        }

    # ── Utilidades ─────────────────────────────────────────────

    def get_collection_stats(self) -> Dict:
        """Devuelve estadísticas de la colección vectorial."""
        collection = self.vectorstore._collection
        count = collection.count()
        return {
            "total_chunks": count,
            "collection_name": COLLECTION_NAME,
            "embedding_model": EMBEDDING_MODEL,
            "vectorstore_path": VECTORSTORE_DIR,
        }
