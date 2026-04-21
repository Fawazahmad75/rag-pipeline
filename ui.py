import streamlit as st
import requests
import json
import os
from datetime import datetime

API_URL = "https://rag-pipeline-production-ccb0.up.railway.app"

st.set_page_config(page_title="DocPal Finance", page_icon="💼", layout="wide")

# ── Session state for metrics tracking ────────────────────────────────────────
if "query_history" not in st.session_state:
    st.session_state.query_history = []

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("💼 DocPal Finance")
st.caption("Production-grade RAG assistant for financial advisors — CSC powered")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["💬 Ask", "📊 Dashboard"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ASK
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_main, col_sidebar = st.columns([3, 1])

    with col_sidebar:
        st.header("📁 Ingest Documents")

        uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
        if uploaded_file:
            with st.spinner("Processing..."):
                response = requests.post(
                    f"{API_URL}/upload",
                    files={"file": (uploaded_file.name, uploaded_file, "application/octet-stream")}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"✅ {data['filename']} — {data['chunks']} chunks")
                else:
                    st.error("Upload failed")

        st.divider()

        st.subheader("🌐 Ingest URL")
        url_input = st.text_input("Paste a URL")
        if st.button("Ingest URL") and url_input:
            with st.spinner("Fetching..."):
                response = requests.post(
                    f"{API_URL}/ingest-url",
                    json={"url": url_input}
                )
                if response.ok:
                    data = response.json()
                    st.success(f"✅ {data['chunks']} chunks from URL")
                else:
                    st.error("Failed to ingest URL")

        st.divider()

        st.subheader("📊 System Stats")
        if st.button("Refresh Stats"):
            try:
                stats = requests.get(f"{API_URL}/stats").json()
                st.metric("Total Chunks", stats["total_chunks"])
                st.write(f"**Model:** {stats['llm']}")
                st.write(f"**Search:** {stats['search']}")
                if stats.get("ingested_sources"):
                    st.write("**Ingested Sources:**")
                    for source, info in stats["ingested_sources"].items():
                        st.write(f"- {source} ({info['chunks']} chunks)")
            except Exception as e:
                st.error(f"Could not fetch stats: {e}")

    with col_main:
        st.header("💬 Ask a Question")
        query = st.text_input("Ask anything about your financial documents:")

        if query:
            with st.spinner("Routing → Retrieving → Generating..."):
                response = requests.post(f"{API_URL}/ask", params={"query": query})

                if response.status_code == 200:
                    result = response.json()

                    # ── Query type badge ───────────────────────────────────────
                    query_type = result.get("query_type", "unknown")
                    badge_color = {
                        "factual": "🔵",
                        "comparison": "🟣",
                        "out_of_scope": "🔴"
                    }.get(query_type, "⚪")

                    st.markdown(f"**Query Type:** {badge_color} `{query_type.upper()}`")
                    st.markdown(f"**Prompt Version:** `{result.get('prompt_version', 'N/A')}`")

                    # ── Answer ─────────────────────────────────────────────────
                    if result.get("declined"):
                        st.warning(result["answer"])
                    else:
                        st.success(result["answer"])

                    # ── Metrics row ────────────────────────────────────────────
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Retrieval", f"{result.get('retrieval_ms', 0)}ms")
                    col2.metric("Generation", f"{result.get('generation_ms', 0)}ms")
                    col3.metric("Cited", "✅" if result.get("cited") else "❌")
                    col4.metric("Declined", "Yes" if result.get("declined") else "No")

                    # ── LangSmith trace link ───────────────────────────────────
                    trace_url = result.get("trace_url")
                    if trace_url:
                        st.markdown(f"🔍 [View LangSmith Trace]({trace_url})")

                    # ── Sources ────────────────────────────────────────────────
                    with st.expander("📚 Sources"):
                        seen = set()
                        for s in result.get("sources", []):
                            src = s.get("source", "Unknown")
                            if src not in seen:
                                st.write(f"- {src}")
                                seen.add(src)

                    # ── Save to session history ────────────────────────────────
                    st.session_state.query_history.append({
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "query": query,
                        "query_type": query_type,
                        "retrieval_ms": result.get("retrieval_ms", 0),
                        "generation_ms": result.get("generation_ms", 0),
                        "cited": result.get("cited", False),
                        "declined": result.get("declined", False),
                        "prompt_version": result.get("prompt_version", "N/A")
                    })

                else:
                    st.error("Something went wrong — check the backend")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("📊 Session Dashboard")

    history = st.session_state.query_history

    if not history:
        st.info("No queries yet — ask a question in the Ask tab to see metrics here.")
    else:
        total = len(history)
        cited = sum(1 for h in history if h["cited"])
        declined = sum(1 for h in history if h["declined"])
        avg_retrieval = sum(h["retrieval_ms"] for h in history) / total
        avg_generation = sum(h["generation_ms"] for h in history) / total
        citation_rate = cited / total * 100
        decline_rate = declined / total * 100

        # ── KPI metrics ───────────────────────────────────────────────────────
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Queries", total)
        col2.metric("Citation Coverage", f"{citation_rate:.0f}%")
        col3.metric("Decline Rate", f"{decline_rate:.0f}%")
        col4.metric("Avg Retrieval", f"{avg_retrieval:.0f}ms")
        col5.metric("Avg Generation", f"{avg_generation:.0f}ms")

        st.divider()

        # ── Query type breakdown ──────────────────────────────────────────────
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("Query Type Breakdown")
            type_counts = {}
            for h in history:
                t = h["query_type"]
                type_counts[t] = type_counts.get(t, 0) + 1
            for qtype, count in type_counts.items():
                st.write(f"**{qtype.upper()}:** {count} queries")

        with col_b:
            st.subheader("Latency Over Time")
            retrieval_data = [h["retrieval_ms"] for h in history]
            generation_data = [h["generation_ms"] for h in history]
            st.line_chart({
                "Retrieval (ms)": retrieval_data,
                "Generation (ms)": generation_data
            })

        st.divider()

        # ── Query history table ───────────────────────────────────────────────
        st.subheader("Query History")
        for i, h in enumerate(reversed(history)):
            with st.expander(f"[{h['timestamp']}] {h['query'][:60]}..."):
                c1, c2, c3, c4 = st.columns(4)
                c1.write(f"**Type:** {h['query_type']}")
                c2.write(f"**Retrieval:** {h['retrieval_ms']}ms")
                c3.write(f"**Cited:** {'✅' if h['cited'] else '❌'}")
                c4.write(f"**Declined:** {'Yes' if h['declined'] else 'No'}")