# api.py — FastAPI for Music Theory Assistant
import os
from fastapi import FastAPI
from pydantic import BaseModel
from qdrant_client import QdrantClient, models
from dotenv import load_dotenv
from openai import OpenAI

# Load env vars from .envrc/.env if available
load_dotenv()

QD_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "zoomcamp-music-theory")
EMBED_MODEL = os.getenv("EMBED_MODEL", "jinaai/jina-embeddings-v2-small-en")
TOP_K = int(os.getenv("TOP_K", "5"))

qd = QdrantClient(QD_URL)
app = FastAPI(title="Music Theory Assistant API")

class Query(BaseModel):
    question: str

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

@app.post("/rag")
def rag(q: Query):
    hits = qd.query_points(
        collection_name=COLLECTION,
        query=models.Document(text=q.question, model=EMBED_MODEL),
        limit=TOP_K,
        with_payload=True
    ).points
    prompt = build_prompt(q.question, hits)
    answer = llm(prompt)
    return {
        "answer": answer,
        "sources": [h.payload for h in hits]
    }
