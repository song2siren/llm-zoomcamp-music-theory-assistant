# app.py — Streamlit UI for Music Theory Assistant
import os
import streamlit as st
from qdrant_client import QdrantClient, models
from dotenv import load_dotenv
from openai import OpenAI

# Load env vars from .envrc/.env if available
load_dotenv()

# ---- Config ----
QD_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "zoomcamp-music-theory-assistant")
EMBED_MODEL = os.getenv("EMBED_MODEL", "jinaai/jina-embeddings-v2-small-en")
TOP_K = int(os.getenv("TOP_K", "5"))

qd = QdrantClient(QD_URL)

# ---- Helper functions ----
def vector_search(question: str, top_k: int = TOP_K):
    res = qd.query_points(
        collection_name=COLLECTION,
        query=models.Document(text=question, model=EMBED_MODEL),
        limit=top_k,
        with_payload=True
    )
    return res.points

def build_prompt(question: str, hits):
    contexts = []
    for h in hits:
        p = h.payload
        contexts.append(
            f"{p.get('title')} — {p.get('artist')} | Key: {p.get('key')} | Cadence: {p.get('cadence')} | "
            f"Roman: {p.get('roman_numerals')} | Notes: {p.get('theory_notes')}"
        )
    context_block = "\n".join(f"- {c}" for c in contexts)
    return f"""You are a music theory assistant. Answer the QUESTION based on the CONTEXT from our music theory database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT:
{context_block}

Answer clearly and cite the most relevant song titles if applicable."""

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def llm(prompt: str, model: str = "gpt-4o-mini") -> str:
    """Send a prompt to the LLM and return the text answer."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful music theory assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def rag(question: str):
    hits = vector_search(question, TOP_K)
    if not hits:
        return "⚠️ No results found. Did you run `ingest.py`?", []
    prompt = build_prompt(question, hits)
    answer = llm(prompt)
    return answer, hits

# ---- Streamlit UI ----
st.set_page_config(page_title="Music Theory Assistant", page_icon="🎵")
st.title("🎵 Music Theory Assistant")
st.caption("Ask about cadences, chord functions, keys, progressions, and more.")

question = st.text_input("Your question", placeholder="Which songs use deceptive cadences?")
if st.button("Ask") and question.strip():
    with st.spinner("Thinking…"):
        answer, hits = rag(question)
    st.subheader("Answer")
    st.write(answer)

    if hits:
        st.subheader("Top sources")
        for h in hits:
            p = h.payload
            st.markdown(
                f"**{p.get('title')}** — {p.get('artist')} "
                f"(Key: {p.get('key')}, Cadence: {p.get('cadence')})  \n"
                f"Roman: {p.get('roman_numerals')}  \n"
                f"Notes: {p.get('theory_notes')}"
            )
