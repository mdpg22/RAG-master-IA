"""
organizar_docs.py — Organiza automáticamente los archivos del máster.

FASE 1: Clasifica por tipo de archivo en carpetas temporales.
FASE 2: Genera un informe para facilitar la reorganización manual por módulos.

Uso:
  python organizar_docs.py --origen /ruta/a/carpeta/desordenada --destino ./docs

  ⚠️ IMPORTANTE: Ejecutar primero en modo preview (por defecto) para ver
  qué haría sin mover nada. Luego confirmar con --ejecutar.
"""
import os
import sys
import shutil
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ── Extensiones a EXCLUIR (binarios, sin valor textual) ────────
EXCLUIR = {
    # Imágenes
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".bmp", ".tiff", ".ico", ".webp",
    # Pesos de modelos
    ".h5", ".pt", ".pth", ".onnx", ".pb", ".tflite", ".safetensors",
    # Binarios Python/R
    ".pickle", ".pkl", ".pyc", ".pyo", ".rdata", ".rhistory", ".rds",
    # Comprimidos
    ".zip", ".tar", ".gz", ".rar", ".7z", ".bz2",
    # Source maps y compilados
    ".map", ".o", ".so", ".dll", ".exe", ".class",
    # Otros sin valor
    ".sample", ".pper", ".conf", ".log", ".lock", ".env",
    # Multimedia
    ".mp3", ".mp4", ".wav", ".avi", ".mov",
}

# ── Mapeo extensión → categoría (solo ingestables) ─────────────
CATEGORIAS = {
    # Teoría y documentación
    ".pdf":  "teoria",
    ".docx": "teoria",
    ".doc":  "teoria",
    ".pptx": "teoria",
    ".ppt":  "teoria",
    ".odt":  "teoria",
    ".odp":  "teoria",
    ".epub": "teoria",

    # Apuntes y texto
    ".txt":  "apuntes",
    ".md":   "apuntes",
    ".rst":  "apuntes",

    # Código Python
    ".py":    "codigo_python",
    ".ipynb": "codigo_python",

    # Código R
    ".r":    "codigo_r",
    ".rmd":  "codigo_r",

    # Código otros
    ".swift": "codigo_otros",
    ".ino":   "codigo_otros",
    ".toml":  "codigo_otros",

    # Datos
    ".csv":     "datos",
    ".tsv":     "datos",
    ".xlsx":    "datos",
    ".xls":     "datos",
    ".json":    "datos",
    ".xml":     "datos",
    ".parquet": "datos",
    ".sql":     "datos",
    ".db":      "datos",
    ".sqlite":  "datos",

    # Web
    ".html": "web",
    ".htm":  "web",
    ".css":  "web",
    ".js":   "web",
}

# Extensiones que el RAG puede ingestar
INGESTABLES = set(CATEGORIAS.keys())


def escanear_directorio(ruta_origen: str) -> dict:
    """Escanea recursivamente y clasifica todos los archivos."""
    archivos_por_categoria = defaultdict(list)
    archivos_excluidos = defaultdict(int)
    archivos_no_clasificados = []
    total = 0
    total_excluidos = 0

    for root, dirs, files in os.walk(ruta_origen):
        # Ignorar carpetas ocultas, __pycache__, venv, node_modules
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".")
            and d not in ("__pycache__", "venv", ".venv", "node_modules", ".git")
        ]

        for filename in sorted(files):
            if filename.startswith("."):
                continue

            filepath = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1].lower()
            rel_path = os.path.relpath(filepath, ruta_origen)

            try:
                size_kb = os.path.getsize(filepath) / 1024
            except OSError:
                continue

            total += 1

            # Excluir binarios y archivos sin valor
            if ext in EXCLUIR:
                archivos_excluidos[ext] += 1
                total_excluidos += 1
                continue

            info = {
                "nombre": filename,
                "ruta_relativa": rel_path,
                "ruta_completa": filepath,
                "extension": ext,
                "tamano_kb": round(size_kb, 1),
                "ingestable": ext in INGESTABLES,
            }

            if ext in CATEGORIAS:
                archivos_por_categoria[CATEGORIAS[ext]].append(info)
            else:
                archivos_no_clasificados.append(info)

    return {
        "por_categoria": dict(archivos_por_categoria),
        "sin_clasificar": archivos_no_clasificados,
        "excluidos": dict(archivos_excluidos),
        "total": total,
        "total_excluidos": total_excluidos,
    }


def generar_informe(resultado: dict, ruta_destino: str) -> str:
    """Genera un informe detallado en Markdown."""
    lineas = []
    lineas.append("# Informe de organización — Archivos del Máster\n")
    lineas.append(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    lineas.append(f"**Total archivos escaneados:** {resultado['total']}")
    lineas.append(f"**Archivos excluidos (binarios/imágenes):** {resultado['total_excluidos']}")

    total_ingestables = sum(
        sum(1 for a in archivos if a["ingestable"])
        for archivos in resultado["por_categoria"].values()
    )
    lineas.append(f"**Archivos ingestables para RAG:** {total_ingestables}\n")

    # Resumen por categoría
    lineas.append("## Archivos a incluir en el RAG\n")
    lineas.append("| Categoría | Archivos | Ingestables RAG |")
    lineas.append("|-----------|----------|-----------------|")

    for cat, archivos in sorted(resultado["por_categoria"].items()):
        n_ingestables = sum(1 for a in archivos if a["ingestable"])
        lineas.append(f"| {cat} | {len(archivos)} | {n_ingestables} |")

    if resultado["sin_clasificar"]:
        lineas.append(f"| ⚠️ sin clasificar | {len(resultado['sin_clasificar'])} | — |")

    lineas.append(f"| **TOTAL** | **{total_ingestables}** | **{total_ingestables}** |\n")

    # Archivos excluidos
    lineas.append("## Archivos excluidos\n")
    lineas.append("| Extensión | Cantidad | Motivo |")
    lineas.append("|-----------|----------|--------|")
    for ext, count in sorted(resultado["excluidos"].items(), key=lambda x: -x[1]):
        motivo = "Imagen" if ext in {".jpg", ".jpeg", ".png", ".gif", ".svg", ".bmp", ".tiff", ".ico", ".webp"} \
            else "Pesos modelo" if ext in {".h5", ".pt", ".pth", ".onnx", ".pb", ".safetensors"} \
            else "Binario" if ext in {".pickle", ".pkl", ".pyc", ".pyo", ".rdata", ".rhistory"} \
            else "Comprimido" if ext in {".zip", ".tar", ".gz", ".rar"} \
            else "Otro"
        lineas.append(f"| {ext} | {count} | {motivo} |")
    lineas.append(f"| **TOTAL** | **{resultado['total_excluidos']}** | |\n")

    # Detalle por categoría
    lineas.append("## Detalle de archivos ingestables\n")
    for cat, archivos in sorted(resultado["por_categoria"].items()):
        lineas.append(f"### {cat.upper()} ({len(archivos)} archivos)\n")
        for a in archivos:
            lineas.append(f"- `{a['ruta_relativa']}` ({a['tamano_kb']} KB)")
        lineas.append("")

    if resultado["sin_clasificar"]:
        lineas.append(f"### SIN CLASIFICAR ({len(resultado['sin_clasificar'])} archivos)\n")
        for a in resultado["sin_clasificar"]:
            lineas.append(f"- `{a['ruta_relativa']}` ({a['extension']}, {a['tamano_kb']} KB)")
        lineas.append("")

    # Siguiente paso
    lineas.append("## Siguiente paso: reorganización por módulos\n")
    lineas.append("Revisa el detalle anterior y reorganiza en estructura de módulos:")
    lineas.append("```")
    lineas.append("docs/")
    lineas.append("├── 00_programa/")
    lineas.append("├── 01_modulo_nombre/")
    lineas.append("│   ├── teoria/")
    lineas.append("│   ├── ejercicios/")
    lineas.append("│   ├── codigo/")
    lineas.append("│   └── datos/")
    lineas.append("├── 02_modulo_nombre/")
    lineas.append("└── ...")
    lineas.append("```")
    lineas.append("\nDespués de organizar, ejecuta `python ingest.py` para regenerar el RAG.\n")

    # Guardar informe
    informe_path = os.path.join(ruta_destino, "_INFORME_ORGANIZACION.md")
    contenido = "\n".join(lineas)
    with open(informe_path, "w", encoding="utf-8") as f:
        f.write(contenido)

    return informe_path


def organizar_archivos(resultado: dict, ruta_destino: str, ejecutar: bool = False):
    """Copia SOLO los archivos ingestables organizados por categoría al destino."""
    acciones = []

    for cat, archivos in resultado["por_categoria"].items():
        carpeta_destino = os.path.join(ruta_destino, f"_{cat}")

        for archivo in archivos:
            if not archivo["ingestable"]:
                continue

            origen = archivo["ruta_completa"]
            destino = os.path.join(carpeta_destino, archivo["nombre"])

            # Resolver conflictos de nombre
            counter = 1
            base, ext = os.path.splitext(archivo["nombre"])
            while os.path.exists(destino):
                destino = os.path.join(carpeta_destino, f"{base}_{counter}{ext}")
                counter += 1

            acciones.append((origen, destino, carpeta_destino))

    if not ejecutar:
        # Solo preview
        print(f"\n  📋 PREVIEW — {len(acciones)} archivos ingestables se copiarían:\n")
        carpetas_vistas = set()
        for origen, destino, carpeta in acciones:
            if carpeta not in carpetas_vistas:
                carpetas_vistas.add(carpeta)
                cat_name = os.path.basename(carpeta)
                count = sum(1 for _, _, c in acciones if c == carpeta)
                print(f"\n  📁 {cat_name}/ ({count} archivos)")
            print(f"     ← {os.path.basename(origen)}")

        print(f"\n  ─────────────────────────────────────────")
        print(f"  Total: {len(acciones)} archivos ingestables")
        print(f"  Excluidos: {resultado['total_excluidos']} archivos (binarios/imágenes)")
        print(f"\n  ⚠️  Esto es solo una preview. Para ejecutar, añade --ejecutar")
        return

    # Ejecutar copia
    # Ejecutar copia
    print(f"\n  🚀 Copiando {len(acciones)} archivos ingestables...\n")
    errores = []
    copiados = 0
    for origen, destino, carpeta in acciones:
        os.makedirs(carpeta, exist_ok=True)
        try:
            shutil.copy2(origen, destino)
            copiados += 1
        except Exception as e:
            errores.append((os.path.basename(origen), str(e)))
            print(f"  ⚠️  Error copiando {os.path.basename(origen)}: {e}")

    # Resumen por carpeta
    carpetas = defaultdict(int)
    for _, _, carpeta in acciones:
        carpetas[os.path.basename(carpeta)] += 1

    for cat, count in sorted(carpetas.items()):
        print(f"  ✓ {cat:25s} → {count} archivos")

    print(f"\n  ✅ {copiados} archivos copiados en {ruta_destino}")
    if errores:
        print(f"  ⚠️  {len(errores)} archivos fallidos (timeout o permisos)")
    print(f"  🚫 {resultado['total_excluidos']} archivos excluidos (imágenes, binarios, pesos)")
    print(f"\n  → Siguiente paso: reorganizar por módulos y ejecutar 'python ingest.py'")


def main():
    parser = argparse.ArgumentParser(
        description="Organiza automáticamente los archivos del máster por categoría."
    )
    parser.add_argument(
        "--origen",
        required=True,
        help="Ruta a la carpeta con los archivos desordenados del máster.",
    )
    parser.add_argument(
        "--destino",
        default="./docs",
        help="Ruta destino donde se organizarán (por defecto: ./docs).",
    )
    parser.add_argument(
        "--ejecutar",
        action="store_true",
        help="Ejecutar la copia. Sin este flag, solo muestra preview.",
    )
    parser.add_argument(
        "--solo-informe",
        action="store_true",
        help="Solo genera el informe sin organizar archivos.",
    )

    args = parser.parse_args()

    if not os.path.exists(args.origen):
        print(f"  ✗ No existe la ruta: {args.origen}")
        sys.exit(1)

    print("=" * 60)
    print("  ORGANIZADOR DE ARCHIVOS — MÁSTER IA & DATA")
    print("=" * 60)
    print(f"\n  📂 Origen:  {os.path.abspath(args.origen)}")
    print(f"  📁 Destino: {os.path.abspath(args.destino)}")

    # Escanear
    print(f"\n{'─' * 60}")
    print("  Escaneando archivos...")
    resultado = escanear_directorio(args.origen)
    print(f"  ✓ {resultado['total']} archivos escaneados")
    print(f"  🚫 {resultado['total_excluidos']} excluidos (binarios/imágenes)")

    total_ingestables = sum(
        sum(1 for a in archivos if a["ingestable"])
        for archivos in resultado["por_categoria"].values()
    )
    print(f"  ✅ {total_ingestables} ingestables para el RAG")

    # Resumen rápido
    print(f"\n{'─' * 60}")
    print("  RESUMEN INGESTABLES:")
    for cat, archivos in sorted(resultado["por_categoria"].items()):
        n_rag = sum(1 for a in archivos if a["ingestable"])
        if n_rag > 0:
            print(f"    {cat:25s} → {n_rag:3d} archivos")

    if resultado["sin_clasificar"]:
        print(f"    {'sin clasificar':25s} → {len(resultado['sin_clasificar']):3d} archivos")

    # Generar informe
    os.makedirs(args.destino, exist_ok=True)
    informe_path = generar_informe(resultado, args.destino)
    print(f"\n  📄 Informe generado: {informe_path}")

    # Organizar
    if not args.solo_informe:
        print(f"\n{'─' * 60}")
        organizar_archivos(resultado, args.destino, ejecutar=args.ejecutar)

    print()


if __name__ == "__main__":
    main()