"""
ingest.py — Pipeline de ingesta de documentos.

Flujo:
  1. Carga todos los archivos de docs/
  2. Divide en chunks con solapamiento
  3. Genera embeddings con sentence-transformers (local, gratuito)
  4. Almacena en ChromaDB (persistente en disco)

Uso:
  python ingest.py
"""
import os
import sys
import time
import shutil

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from config import (
    DOCS_DIR,
    VECTORSTORE_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    SEPARATORS,
    EMBEDDING_MODEL,
    COLLECTION_NAME,
)
from utils.loaders import load_all_documents


def main():
    print("=" * 60)
    print("  RAG MÁSTER — INGESTA DE DOCUMENTOS")
    print("=" * 60)

    # ── 1. Verificar que existen documentos ────────────────────
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        print(f"\n  ✗ Carpeta '{DOCS_DIR}' creada pero vacía.")
        print("    Deposita los archivos del máster en esa carpeta y vuelve a ejecutar.")
        sys.exit(1)

    files_in_docs = [
        f for f in os.listdir(DOCS_DIR)
        if os.path.isfile(os.path.join(DOCS_DIR, f)) and not f.startswith(".")
    ]
    # También contar archivos en subcarpetas
    total_files = sum(
        len([f for f in files if not f.startswith(".")])
        for _, _, files in os.walk(DOCS_DIR)
    )

    if total_files == 0:
        print(f"\n  ✗ No se encontraron archivos en '{DOCS_DIR}'.")
        print("    Deposita los archivos del máster y vuelve a ejecutar.")
        sys.exit(1)

    print(f"\n  📁 Directorio de documentos: {DOCS_DIR}")
    print(f"  📊 Archivos encontrados: {total_files}")

    # ── 2. Cargar documentos ───────────────────────────────────
    print(f"\n{'─' * 60}")
    print("  FASE 1: Carga de documentos")
    print(f"{'─' * 60}")
    t0 = time.time()

    documents = load_all_documents(DOCS_DIR)

    if not documents:
        print("\n  ✗ No se pudo extraer contenido de ningún archivo.")
        sys.exit(1)

    print(f"  ⏱  Tiempo de carga: {time.time() - t0:.1f}s")

    # ── 3. Chunking ────────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print("  FASE 2: División en chunks")
    print(f"{'─' * 60}")
    t1 = time.time()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SEPARATORS,
        length_function=len,
    )

    chunks = splitter.split_documents(documents)
    print(f"  ✓ {len(documents)} documentos → {len(chunks)} chunks")
    print(f"    Tamaño chunk: {CHUNK_SIZE} | Overlap: {CHUNK_OVERLAP}")
    print(f"  ⏱  Tiempo de chunking: {time.time() - t1:.1f}s")

    # ── 4. Embeddings + ChromaDB ───────────────────────────────
    print(f"\n{'─' * 60}")
    print("  FASE 3: Generación de embeddings y almacenamiento")
    print(f"{'─' * 60}")
    t2 = time.time()

    print(f"  🧠 Modelo de embeddings: {EMBEDDING_MODEL}")
    print("     (primera ejecución descarga el modelo, ~90MB)")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    # Limpiar vectorstore anterior si existe
    if os.path.exists(VECTORSTORE_DIR):
        shutil.rmtree(VECTORSTORE_DIR)
        print("  🗑  Vectorstore anterior eliminado")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=VECTORSTORE_DIR,
    )

    print(f"  ✓ {len(chunks)} chunks almacenados en ChromaDB")
    print(f"  📂 Vectorstore en: {VECTORSTORE_DIR}")
    print(f"  ⏱  Tiempo de embeddings: {time.time() - t2:.1f}s")

    # ── Resumen ────────────────────────────────────────────────
    total_time = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"  ✅ INGESTA COMPLETADA en {total_time:.1f}s")
    print(f"     Archivos procesados:  {total_files}")
    print(f"     Documentos extraídos: {len(documents)}")
    print(f"     Chunks generados:     {len(chunks)}")
    print(f"     Modelo embeddings:    {EMBEDDING_MODEL}")
    print(f"{'=' * 60}")
    print(f"\n  → Ejecuta 'streamlit run app.py' para lanzar la interfaz.\n")


if __name__ == "__main__":
    main()
