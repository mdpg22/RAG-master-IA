"""
utils/loaders.py — Cargadores de documentos por tipo de archivo.
Recorre recursivamente el directorio y carga cada archivo según su extensión.
"""
import os
import glob
from typing import List
from langchain_core.documents import Document


# Mapeo extensión → loader
SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".txt", ".md",
    ".pptx", ".csv", ".html", ".htm", ".epub"
}


def load_single_file(filepath: str) -> List[Document]:
    """Carga un archivo individual y devuelve lista de Documents."""
    ext = os.path.splitext(filepath)[1].lower()
    docs = []

    try:
        if ext == ".pdf":
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(filepath)
            docs = loader.load()

        elif ext in (".docx", ".doc"):
            from langchain_community.document_loaders import Docx2txtLoader
            loader = Docx2txtLoader(filepath)
            docs = loader.load()

        elif ext == ".pptx":
            from langchain_community.document_loaders import UnstructuredPowerPointLoader
            loader = UnstructuredPowerPointLoader(filepath)
            docs = loader.load()

        elif ext in (".txt", ".md"):
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(filepath, encoding="utf-8")
            docs = loader.load()

        elif ext == ".csv":
            from langchain_community.document_loaders import CSVLoader
            loader = CSVLoader(filepath, encoding="utf-8")
            docs = loader.load()

        elif ext in (".html", ".htm"):
            from langchain_community.document_loaders import BSHTMLLoader
            loader = BSHTMLLoader(filepath, open_encoding="utf-8")
            docs = loader.load()

        elif ext == ".epub":
            from langchain_community.document_loaders import UnstructuredEPubLoader
            loader = UnstructuredEPubLoader(filepath)
            docs = loader.load()

        else:
            print(f"  ⚠  Extensión no soportada: {ext} → {filepath}")
            return []

        # Enriquecer metadata con nombre de archivo
        for doc in docs:
            doc.metadata["source_file"] = os.path.basename(filepath)
            doc.metadata["full_path"] = filepath

    except Exception as e:
        print(f"  ✗  Error cargando {filepath}: {e}")
        return []

    return docs


def load_all_documents(docs_dir: str) -> List[Document]:
    """Recorre recursivamente docs_dir y carga todos los archivos soportados."""
    all_docs = []
    file_count = 0

    for root, dirs, files in os.walk(docs_dir):
        for filename in sorted(files):
            ext = os.path.splitext(filename)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                continue

            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, docs_dir)
            print(f"  📄 Cargando: {rel_path}")

            docs = load_single_file(filepath)
            if docs:
                # Añadir ruta relativa como metadata
                for doc in docs:
                    doc.metadata["relative_path"] = rel_path
                all_docs.extend(docs)
                file_count += 1

    print(f"\n  ✓ {file_count} archivos cargados → {len(all_docs)} documentos extraídos")
    return all_docs
