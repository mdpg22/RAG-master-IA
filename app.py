"""
app.py — Interfaz Streamlit para el RAG del Máster.
Diseño Apple-inspired: minimal, limpio, tipografía precisa.

Uso:
  streamlit run app.py
"""
import os
import datetime
import streamlit as st

from config import LLM_PROVIDER, VECTORSTORE_DIR, COLLECTION_NAME
from rag_engine import RAGEngine


# ── Configuración de página ────────────────────────────────────
st.set_page_config(
    page_title="Máster IA · Asistente",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Apple-inspired CSS ─────────────────────────────────────────
st.markdown("""
<style>
    /* ── Import SF Pro-like font ────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Global resets ──────────────────────────── */
    *, *::before, *::after { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', sans-serif !important; }

    .stApp {
        background: #fafafa;
    }

    /* ── Hide Streamlit defaults ────────────────── */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* ── Main container ─────────────────────────── */
    .block-container {
        max-width: 860px !important;
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
    }

    /* ── Hero header ────────────────────────────── */
    .hero-container {
        text-align: center;
        padding: 3rem 0 2rem 0;
        margin-bottom: 1rem;
    }
    .hero-icon {
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, #007AFF, #5856D6);
        border-radius: 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 16px rgba(0, 122, 255, 0.2);
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1d1d1f;
        letter-spacing: -0.03em;
        margin: 0 0 0.4rem 0;
        line-height: 1.15;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        font-weight: 400;
        color: #86868b;
        letter-spacing: -0.01em;
        margin: 0;
    }

    /* ── Chat messages ──────────────────────────── */
    .stChatMessage {
        background: transparent !important;
        border: none !important;
        padding: 0.6rem 0 !important;
    }

    /* User message bubble */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: transparent !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"] {
        background: #007AFF;
        color: white !important;
        padding: 10px 16px;
        border-radius: 18px 18px 4px 18px;
        display: inline-block;
        max-width: 85%;
        font-size: 0.92rem;
        line-height: 1.5;
        font-weight: 400;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"] p {
        color: white !important;
    }

    /* Assistant message bubble */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stMarkdownContainer"] {
        background: #f5f5f7;
        color: #1d1d1f;
        padding: 14px 18px;
        border-radius: 18px 18px 18px 4px;
        display: inline-block;
        max-width: 90%;
        font-size: 0.92rem;
        line-height: 1.6;
        font-weight: 400;
        border: 1px solid #e8e8ed;
    }

    /* Chat input */
    .stChatInput {
        border-top: none !important;
    }
    .stChatInput > div {
        background: white !important;
        border: 1px solid #d2d2d7 !important;
        border-radius: 22px !important;
        padding: 4px 8px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .stChatInput > div:focus-within {
        border-color: #007AFF !important;
        box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.12) !important;
    }
    .stChatInput textarea {
        font-size: 0.92rem !important;
        font-weight: 400 !important;
        color: #1d1d1f !important;
    }
    .stChatInput textarea::placeholder {
        color: #86868b !important;
        font-weight: 400 !important;
    }

    /* ── Source tags ─────────────────────────────── */
    .source-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: white;
        color: #1d1d1f;
        padding: 4px 12px;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 500;
        margin: 3px 4px 3px 0;
        border: 1px solid #e8e8ed;
        letter-spacing: -0.01em;
        transition: all 0.2s ease;
    }
    .source-pill:hover {
        background: #f5f5f7;
        border-color: #d2d2d7;
    }
    .source-pill .pill-icon {
        font-size: 0.7rem;
        opacity: 0.5;
    }
    .sources-row {
        margin-top: 8px;
        display: flex;
        flex-wrap: wrap;
        gap: 0;
    }

    /* ── Sidebar ─────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e8e8ed !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem !important;
    }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 0 1.5rem 0;
        border-bottom: 1px solid #f0f0f5;
        margin-bottom: 1.5rem;
    }
    .sidebar-brand-icon {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #007AFF, #5856D6);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        flex-shrink: 0;
    }
    .sidebar-brand-text {
        font-size: 0.85rem;
        font-weight: 600;
        color: #1d1d1f;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .sidebar-brand-sub {
        font-size: 0.72rem;
        color: #86868b;
        font-weight: 400;
    }

    .sidebar-section-title {
        font-size: 0.7rem;
        font-weight: 600;
        color: #86868b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 1.2rem 0 0.6rem 0;
    }

    /* ── Stats cards (sidebar) ──────────────────── */
    .stat-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin: 0.5rem 0;
    }
    .stat-card {
        background: #f5f5f7;
        border-radius: 12px;
        padding: 14px 12px;
        text-align: center;
        border: 1px solid #e8e8ed;
        transition: all 0.2s ease;
    }
    .stat-card:hover {
        background: #efeff4;
    }
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1d1d1f;
        letter-spacing: -0.03em;
        line-height: 1;
    }
    .stat-label {
        font-size: 0.68rem;
        font-weight: 500;
        color: #86868b;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-top: 4px;
    }

    /* ── Provider badge ─────────────────────────── */
    .provider-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #f5f5f7;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 500;
        color: #1d1d1f;
        border: 1px solid #e8e8ed;
    }
    .provider-dot {
        width: 7px;
        height: 7px;
        background: #34C759;
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }

    /* ── Slider styling ─────────────────────────── */
    .stSlider > div > div > div {
        background: #e8e8ed !important;
    }
    .stSlider [data-testid="stThumbValue"] {
        font-weight: 600 !important;
        color: #007AFF !important;
    }

    /* ── Toggle styling ─────────────────────────── */
    .stCheckbox label span {
        font-size: 0.85rem !important;
        font-weight: 400 !important;
        color: #1d1d1f !important;
    }

    /* ── Button styling ─────────────────────────── */
    .stButton > button {
        background: #f5f5f7 !important;
        color: #1d1d1f !important;
        border: 1px solid #e8e8ed !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }
    .stButton > button:hover {
        background: #efeff4 !important;
        border-color: #d2d2d7 !important;
    }

    /* ── Expander ────────────────────────────────── */
    .streamlit-expanderHeader {
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        color: #86868b !important;
        background: transparent !important;
        border: none !important;
    }

    /* ── Welcome card ───────────────────────────── */
    .welcome-card {
        background: white;
        border: 1px solid #e8e8ed;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0 2rem 0;
    }
    .welcome-text {
        font-size: 0.88rem;
        color: #86868b;
        line-height: 1.6;
        margin: 0;
    }
    .welcome-suggestions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        margin-top: 1.2rem;
    }
    .suggestion-chip {
        background: #f5f5f7;
        color: #1d1d1f;
        padding: 8px 16px;
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 450;
        border: 1px solid #e8e8ed;
        cursor: default;
        transition: all 0.2s ease;
        letter-spacing: -0.01em;
    }
    .suggestion-chip:hover {
        background: #efeff4;
        border-color: #d2d2d7;
    }

    /* ── Spinner ─────────────────────────────────── */
    .stSpinner > div {
        border-top-color: #007AFF !important;
    }

    /* ── Error ───────────────────────────────────── */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }

    /* ── Divider ─────────────────────────────────── */
    hr {
        border-color: #f0f0f5 !important;
    }

    /* ── Footer ──────────────────────────────────── */
    .sidebar-footer {
        font-size: 0.7rem;
        color: #aeaeb2;
        text-align: center;
        padding-top: 1rem;
        border-top: 1px solid #f0f0f5;
        margin-top: 1.5rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)


# ── Verificar vectorstore ──────────────────────────────────────
def check_vectorstore():
    """Verifica si la base de datos vectorial existe."""
    return os.path.exists(VECTORSTORE_DIR) and any(
        f.endswith(".sqlite3") or f.endswith(".bin")
        for f in os.listdir(VECTORSTORE_DIR)
    ) if os.path.exists(VECTORSTORE_DIR) else False


# ── Motor RAG (cacheado) ──────────────────────────────────────
@st.cache_resource(show_spinner="Inicializando modelo...")
def init_engine():
    return RAGEngine()


# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">🎓</div>
        <div>
            <div class="sidebar-brand-text">Máster IA & Data</div>
            <div class="sidebar-brand-sub">Asistente de conocimiento</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Provider
    st.markdown('<div class="sidebar-section-title">Modelo</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="provider-badge">
        <span class="provider-dot"></span>
        {LLM_PROVIDER.capitalize()} · Local
    </div>
    """, unsafe_allow_html=True)

    # Ajustes
    st.markdown('<div class="sidebar-section-title">Ajustes de búsqueda</div>', unsafe_allow_html=True)

    top_k = st.slider(
        "Fragmentos de contexto",
        min_value=1,
        max_value=15,
        value=5,
        help="Número de fragmentos del material que se envían como contexto al modelo.",
    )

    show_context = st.toggle(
        "Mostrar contexto",
        value=False,
        help="Muestra los fragmentos exactos que el modelo usa para responder.",
    )

    show_sources = st.toggle(
        "Mostrar fuentes",
        value=True,
        help="Muestra los archivos de los que se extrajo la información.",
    )

    # Stats
    if check_vectorstore():
        try:
            engine = init_engine()
            stats = engine.get_collection_stats()

            st.markdown('<div class="sidebar-section-title">Base de conocimiento</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-value">{stats["total_chunks"]}</div>
                    <div class="stat-label">Chunks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{top_k}</div>
                    <div class="stat-label">Top-K</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass

    st.markdown("", unsafe_allow_html=True)

    if st.button("Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()

    # Footer
    year = datetime.datetime.now().year
    st.markdown(f"""
    <div class="sidebar-footer">
        Máster en Análisis de Datos e IA<br>
        RAG Assistant · {year}
    </div>
    """, unsafe_allow_html=True)


# ── Pantalla principal ─────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-icon">🎓</div>
    <div class="hero-title">Asistente del Máster</div>
    <div class="hero-subtitle">Pregunta lo que necesites sobre el material del programa</div>
</div>
""", unsafe_allow_html=True)


# Verificar vectorstore
if not check_vectorstore():
    st.error(
        "**Base de datos no encontrada.**\n\n"
        "1. Deposita los archivos en `docs/`\n"
        "2. Ejecuta `python ingest.py`\n"
        "3. Relanza `streamlit run app.py`"
    )
    st.stop()

engine = init_engine()

# ── Chat ───────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Welcome card si no hay mensajes
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <p class="welcome-text">
            Consulta cualquier aspecto del máster: temario, conceptos,
            metodologías, herramientas o ejercicios.
        </p>
        <div class="welcome-suggestions">
            <span class="suggestion-chip">¿Qué temas cubre el máster?</span>
            <span class="suggestion-chip">Explícame qué es un Random Forest</span>
            <span class="suggestion-chip">¿Qué herramientas se usan?</span>
            <span class="suggestion-chip">Resume el temario del día 1</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Historial
for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🎓"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

        if msg["role"] == "assistant" and "sources" in msg and show_sources:
            if msg["sources"]:
                pills = "".join(
                    f'<span class="source-pill"><span class="pill-icon">◉</span>{s["file"]}</span>'
                    for s in msg["sources"]
                )
                st.markdown(f'<div class="sources-row">{pills}</div>', unsafe_allow_html=True)

# Input
if prompt := st.chat_input("Pregunta algo sobre el máster..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🎓"):
        with st.spinner("Buscando..."):
            try:
                result = engine.query(prompt, top_k=top_k)

                st.markdown(result["answer"])

                if show_sources and result["sources"]:
                    pills = "".join(
                        f'<span class="source-pill"><span class="pill-icon">◉</span>{s["file"]}</span>'
                        for s in result["sources"]
                    )
                    st.markdown(f'<div class="sources-row">{pills}</div>', unsafe_allow_html=True)

                if show_context and result["context"]:
                    with st.expander(f"Contexto recuperado · {result['num_chunks']} fragmentos"):
                        st.text(result["context"])

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"],
                })

            except Exception as e:
                error_msg = f"Error al procesar la consulta: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"⚠️ {error_msg}",
                    "sources": [],
                })