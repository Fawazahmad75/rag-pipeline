import streamlit as st
import requests
from datetime import datetime

API_URL = "https://rag-pipeline-production-ccb0.up.railway.app"

st.set_page_config(
    page_title="DocPal Finance",
    page_icon="assets/logo.png" if False else "D",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #111827 !important;
    color: #E8EAF0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Geometric background pattern ── */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
}

/* ── Subtle radial glow top-left ── */
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    top: -200px; left: -200px;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(99,140,255,0.08) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none !important; }

/* ── Main content ── */
[data-testid="stMainBlockContainer"] {
    max-width: 1200px !important;
    margin: 0 auto !important;
    padding: 3rem 2rem !important;
    position: relative;
    z-index: 1;
}

/* ── Typography ── */
h1, h2, h3 {
    font-family: 'DM Serif Display', serif !important;
    letter-spacing: -0.02em;
}

/* ── Header bar ── */
.header-bar {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    padding-bottom: 2rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 3rem;
}

.header-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    color: #FFFFFF;
    letter-spacing: -0.03em;
    line-height: 1;
}

.header-subtitle {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.35);
    font-weight: 300;
    margin-top: 0.4rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.header-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: rgba(99,140,255,0.8);
    border: 1px solid rgba(99,140,255,0.2);
    padding: 0.3rem 0.8rem;
    border-radius: 2px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Cards ── */
.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 4px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.card-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: rgba(255,255,255,0.3);
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.card-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    color: #FFFFFF;
    font-weight: 500;
}

.card-unit {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.3);
    margin-left: 0.3rem;
}

/* ── Answer box ── */
.answer-box {
    background: rgba(255,255,255,0.03);
    border-left: 2px solid #638CFF;
    border-radius: 0 4px 4px 0;
    padding: 1.5rem 2rem;
    margin: 1.5rem 0;
    font-size: 0.95rem;
    line-height: 1.7;
    color: #D0D4E0;
}

.answer-box.declined {
    border-left-color: rgba(255,255,255,0.2);
    color: rgba(255,255,255,0.4);
}

/* ── Query type tag ── */
.query-tag {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.25rem 0.6rem;
    border-radius: 2px;
    margin-right: 0.5rem;
}

.tag-factual { background: rgba(99,140,255,0.1); color: #638CFF; border: 1px solid rgba(99,140,255,0.2); }
.tag-comparison { background: rgba(140,99,255,0.1); color: #8C63FF; border: 1px solid rgba(140,99,255,0.2); }
.tag-out_of_scope { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.3); border: 1px solid rgba(255,255,255,0.1); }

/* ── Meta row ── */
.meta-row {
    display: flex;
    gap: 2rem;
    margin: 1rem 0;
    align-items: center;
}

.meta-item {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: rgba(255,255,255,0.3);
}

.meta-item span {
    color: rgba(255,255,255,0.6);
    margin-left: 0.3rem;
}

/* ── Trace link ── */
.trace-link {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: rgba(99,140,255,0.6);
    text-decoration: none;
    letter-spacing: 0.05em;
    border-bottom: 1px solid rgba(99,140,255,0.2);
    padding-bottom: 1px;
    transition: color 0.2s;
}

/* ── Divider ── */
.section-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 2.5rem 0;
}

/* ── Tab styling ── */
[data-testid="stTabs"] button {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,0.35) !important;
    font-weight: 500 !important;
    border: none !important;
    background: transparent !important;
    padding: 0.5rem 0 !important;
    margin-right: 2rem !important;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: #FFFFFF !important;
    border-bottom: 1px solid #638CFF !important;
}

/* ── Input ── */
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 4px !important;
    color: #A8B4D0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.8rem 1rem !important;
    transition: border-color 0.2s !important;
}

[data-testid="stTextInput"] input:focus {
    border-color: rgba(99,140,255,0.4) !important;
    box-shadow: none !important;
}

[data-testid="stTextInput"] input::placeholder {
    color: rgba(255,255,255,0.2) !important;
}

/* ── Button ── */
[data-testid="stButton"] button {
    background: rgba(99,140,255,0.1) !important;
    border: 1px solid rgba(99,140,255,0.3) !important;
    color: #638CFF !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    font-weight: 500 !important;
    border-radius: 2px !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s !important;
}

[data-testid="stButton"] button:hover {
    background: rgba(99,140,255,0.2) !important;
    border-color: rgba(99,140,255,0.5) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px dashed rgba(255,255,255,0.1) !important;
    border-radius: 4px !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 4px !important;
    padding: 1rem !important;
}

[data-testid="stMetricLabel"] {
    font-size: 0.65rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: rgba(255,255,255,0.3) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.4rem !important;
    color: #FFFFFF !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 4px !important;
}

[data-testid="stExpander"] summary {
    font-size: 0.8rem !important;
    letter-spacing: 0.05em !important;
    color: rgba(255,255,255,0.4) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Success/warning ── */
[data-testid="stSuccess"] {
    background: rgba(99,140,255,0.05) !important;
    border: 1px solid rgba(99,140,255,0.15) !important;
    color: rgba(255,255,255,0.7) !important;
    border-radius: 4px !important;
}

[data-testid="stWarning"] {
    background: rgba(255,200,100,0.05) !important;
    border: 1px solid rgba(255,200,100,0.15) !important;
    color: rgba(255,200,100,0.7) !important;
    border-radius: 4px !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: rgba(99,140,255,0.6) !important; }

/* ── Line chart ── */
[data-testid="stVegaLiteChart"] {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 4px !important;
    padding: 1rem !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

/* ── Section label ── */
.section-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: rgba(255,255,255,0.25);
    font-weight: 500;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

.source-item {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: rgba(255,255,255,0.35);
    padding: 0.4rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "query_history" not in st.session_state:
    st.session_state.query_history = []

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-bar">
    <div>
        <div class="header-title">DocPal Finance</div>
        <div class="header-subtitle">Canadian Securities Course — Intelligent Document Assistant</div>
    </div>
    <div class="header-badge">v1.0.0 — Production</div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Query", "Dashboard", "Ingest"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — QUERY
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    query = st.text_input(
        "",
        placeholder="Ask a question about the Canadian Securities Course material...",
        label_visibility="collapsed"
    )

    if query:
        with st.spinner("Processing..."):
            response = requests.post(f"{API_URL}/ask", params={"query": query})

            if response.status_code == 200:
                result = response.json()

                query_type = result.get("query_type", "unknown")
                tag_class = f"tag-{query_type}"
                declined = result.get("declined", False)
                answer = result.get("answer", "")
                trace_url = result.get("trace_url")
                prompt_version = result.get("prompt_version", "N/A")
                retrieval_ms = result.get("retrieval_ms", 0)
                generation_ms = result.get("generation_ms", 0)
                cited = result.get("cited", False)

                # Query type tag + meta
                trace_html = f'<a class="trace-link" href="{trace_url}" target="_blank">View trace</a>' if trace_url else '<span class="meta-item">Trace unavailable</span>'

                st.markdown(f"""
                <div style="margin-bottom: 1rem;">
                    <span class="query-tag {tag_class}">{query_type}</span>
                    <span class="query-tag" style="background:rgba(255,255,255,0.03);color:rgba(255,255,255,0.25);border:1px solid rgba(255,255,255,0.08);">
                        {"cited" if cited else "no citation"}
                    </span>
                </div>
                <div class="meta-row">
                    <div class="meta-item">Retrieval <span>{retrieval_ms}ms</span></div>
                    <div class="meta-item">Generation <span>{generation_ms}ms</span></div>
                    <div class="meta-item">Prompt <span>{prompt_version}</span></div>
                    <div class="meta-item">{trace_html}</div>
                </div>
                """, unsafe_allow_html=True)

                # Answer
                box_class = "answer-box declined" if declined else "answer-box"
                st.markdown(f'<div class="{box_class}">{answer}</div>', unsafe_allow_html=True)

                # Sources
                sources = result.get("sources", [])
                if sources:
                    with st.expander("Sources"):
                        seen = set()
                        for s in sources:
                            src = s.get("source", "Unknown")
                            if src not in seen:
                                st.markdown(f'<div class="source-item">{src}</div>', unsafe_allow_html=True)
                                seen.add(src)

                # Save to history
                st.session_state.query_history.append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "query": query,
                    "query_type": query_type,
                    "retrieval_ms": retrieval_ms,
                    "generation_ms": generation_ms,
                    "cited": cited,
                    "declined": declined,
                    "prompt_version": prompt_version
                })

            else:
                st.error("Backend error — check Railway logs")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-label">System Metrics</div>', unsafe_allow_html=True)

    try:
        metrics_response = requests.get(f"{API_URL}/metrics")
        if metrics_response.ok:
            data = metrics_response.json()
            summary = data.get("summary", {})
            metrics = data.get("metrics", [])

            if not summary:
                st.markdown('<div class="answer-box declined">No queries recorded yet. Ask a question to populate metrics.</div>', unsafe_allow_html=True)
            else:
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Total Queries", summary.get("total_queries", 0))
                col2.metric("Citation Rate", f"{summary.get('citation_rate', 0)}%")
                col3.metric("Decline Rate", f"{summary.get('decline_rate', 0)}%")
                col4.metric("P50 Latency", f"{summary.get('p50_latency_ms', 0)}ms")
                col5.metric("P95 Latency", f"{summary.get('p95_latency_ms', 0)}ms")

                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

                col_a, col_b = st.columns(2)

                with col_a:
                    st.markdown('<div class="section-label">Avg Latency Breakdown</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    c1.metric("Retrieval", f"{summary.get('avg_retrieval_ms', 0)}ms")
                    c2.metric("Generation", f"{summary.get('avg_generation_ms', 0)}ms")

                with col_b:
                    st.markdown('<div class="section-label">Query Type Distribution</div>', unsafe_allow_html=True)
                    type_counts = {}
                    for m in metrics:
                        t = m.get("query_type", "unknown")
                        type_counts[t] = type_counts.get(t, 0) + 1
                    for qtype, count in type_counts.items():
                        st.markdown(f"""
                        <div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">
                            <span class="query-tag tag-{qtype}">{qtype}</span>
                            <span style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:rgba(255,255,255,0.4);">{count}</span>
                        </div>
                        """, unsafe_allow_html=True)

                if metrics:
                    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                    st.markdown('<div class="section-label">Latency Over Time — Last 20 Queries</div>', unsafe_allow_html=True)
                    st.line_chart({
                        "Retrieval (ms)": [m["retrieval_ms"] for m in metrics],
                        "Generation (ms)": [m["generation_ms"] for m in metrics]
                    })

                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                st.markdown('<div class="section-label">Recent Query History</div>', unsafe_allow_html=True)
                for m in reversed(metrics):
                    with st.expander(f"{m['timestamp'][:19]}  —  {m['query'][:70]}"):
                        c1, c2, c3, c4 = st.columns(4)
                        c1.write(f"**Type:** {m.get('query_type', 'N/A')}")
                        c2.write(f"**Total:** {m.get('total_ms', 0)}ms")
                        c3.write(f"**Cited:** {'Yes' if m.get('cited') else 'No'}")
                        c4.write(f"**Declined:** {'Yes' if m.get('declined') else 'No'}")

    except Exception as e:
        st.error(f"Could not load metrics: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — INGEST
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="section-label">Upload Document</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("PDF or TXT", type=["pdf", "txt"], label_visibility="collapsed")
        if uploaded_file:
            with st.spinner("Ingesting..."):
                response = requests.post(
                    f"{API_URL}/upload",
                    files={"file": (uploaded_file.name, uploaded_file, "application/octet-stream")}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"{data['filename']} — {data['chunks']} chunks indexed")
                else:
                    st.error("Upload failed")

    with col_right:
        st.markdown('<div class="section-label">Ingest URL</div>', unsafe_allow_html=True)
        url_input = st.text_input("URL", placeholder="https://...", label_visibility="collapsed")
        if st.button("Ingest") and url_input:
            with st.spinner("Fetching..."):
                response = requests.post(f"{API_URL}/ingest-url", json={"url": url_input})
                if response.ok:
                    data = response.json()
                    st.success(f"{data['chunks']} chunks ingested")
                else:
                    st.error("Failed to ingest URL")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">System Status</div>', unsafe_allow_html=True)

    if st.button("Refresh"):
        try:
            stats = requests.get(f"{API_URL}/stats").json()
            c1, c2 = st.columns(2)
            c1.metric("Total Chunks", stats["total_chunks"])
            c2.metric("Model", "Llama 3.1 8B")
            if stats.get("ingested_sources"):
                st.markdown('<div class="section-label" style="margin-top:1.5rem;">Ingested Sources</div>', unsafe_allow_html=True)
                for source, info in stats["ingested_sources"].items():
                    st.markdown(f'<div class="source-item">{source} — {info["chunks"]} chunks — {info["ingested_at"]}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Could not fetch stats: {e}")