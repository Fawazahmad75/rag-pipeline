import streamlit as st
import requests

API_URL = "https://rag-pipeline-production-ccb0.up.railway.app"

st.set_page_config(page_title="RAG Document Assistant", page_icon="📄", layout="wide")
st.title("📄 Document Intelligence Assistant")
st.caption("Upload documents and ask questions — powered by Hybrid Search + Groq LLM")

with st.sidebar:
    st.header("📁 Upload Documents")
    uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])
    if uploaded_file:
        with st.spinner("Processing document..."):
            response = requests.post(
                f"{API_URL}/upload",
                files={"file": (uploaded_file.name, uploaded_file, "application/octet-stream")}
            )
            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ {data['filename']} — {data['chunks']} chunks indexed")
            else:
                st.error("Failed to process document")

    st.divider()
    st.header("📊 System Stats")
    if st.button("Refresh Stats"):
        stats = requests.get(f"{API_URL}/stats").json()
        st.metric("Total Chunks", stats["total_chunks"])
        st.write(f"**Model:** {stats['llm']}")
        st.write(f"**Search:** {stats['search']}")

st.header("💬 Ask a Question")
query = st.text_input("Ask anything about your uploaded documents:")
if query:
    with st.spinner("Searching and generating answer..."):
        response = requests.post(f"{API_URL}/ask", params={"query": query})
        if response.status_code == 200:
            result = response.json()
            st.write(result['answer'])
            col1, col2 = st.columns(2)
            col1.metric("Retrieval", f"{result['retrieval_ms']}ms")
            col2.metric("Generation", f"{result['generation_ms']}ms")
            with st.expander("📚 Sources"):
                seen = set()
                for s in result['sources']:
                    src = s.get('source', 'Unknown')
                    if src not in seen:
                        st.write(f"- {src}")
                        seen.add(src)
        else:
            st.error("Something went wrong")