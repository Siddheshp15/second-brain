import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Second Brain", page_icon="🧠", layout="wide")
st.title("🧠 Second Brain")
st.caption("Upload documents, then ask questions. Answers come only from your files, with sources.")

# Streamlit reruns this whole script on every click, so we keep data in session_state
if "messages" not in st.session_state:
    st.session_state.messages = []      # chat history
if "processed" not in st.session_state:
    st.session_state.processed = set()  # files already uploaded this session


def show_sources(sources):
    """Show source chunks in an expandable section."""
    if not sources:
        return
    with st.expander(f"Sources ({len(sources)})"):
        for i, s in enumerate(sources, start=1):
            st.markdown(f"**[{i}] {s['file']}, page {s['page']}**")
            st.caption(s["text"][:400] + "...")


# ---------- Sidebar: upload + document list ----------
with st.sidebar:
    st.header("📄 Documents")

    uploaded = st.file_uploader(
        "Upload PDF or TXT", type=["pdf", "txt"], accept_multiple_files=True
    )
    for f in uploaded or []:
        if f.name in st.session_state.processed:
            continue
        with st.spinner(f"Processing {f.name}..."):
            try:
                r = requests.post(
                    f"{API_URL}/upload",
                    files={"file": (f.name, f.getvalue())},
                    timeout=300,
                )
                if r.status_code == 200:
                    info = r.json()
                    st.success(f"{f.name}: {info['pages']} pages, {info['chunks']} chunks")
                    st.session_state.processed.add(f.name)
                else:
                    st.error(f"{f.name}: {r.json().get('detail', 'Upload failed')}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach the API. Is uvicorn running?")

    st.divider()
    st.subheader("In your library")
    try:
        docs = requests.get(f"{API_URL}/documents", timeout=10).json()
        if docs:
            for d in docs:
                st.write(f"• **{d['file']}** ({d['pages']} pages)")
        else:
            st.caption("No documents yet.")
    except requests.exceptions.ConnectionError:
        st.warning("API not running. Start it with uvicorn.")

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ---------- Main: chat ----------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        show_sources(m.get("sources"))

question = st.chat_input("Ask a question about your documents...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                r = requests.post(
                    f"{API_URL}/ask", json={"question": question, "k": 4}, timeout=120
                )
                if r.status_code == 200:
                    data = r.json()
                    answer, sources = data["answer"], data["sources"]
                else:
                    answer, sources = f"Error: {r.json().get('detail', 'Something went wrong')}", []
            except requests.exceptions.ConnectionError:
                answer, sources = "Cannot reach the API. Is uvicorn running?", []
        st.markdown(answer)
        show_sources(sources)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )