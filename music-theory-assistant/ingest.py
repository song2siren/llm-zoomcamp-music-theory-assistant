# ingest.py — Automated ingestion into Qdrant
import os
import pandas as pd
from qdrant_client import QdrantClient, models
from dotenv import load_dotenv

# Load env vars from .envrc/.env if available
load_dotenv()

# ---- Config ----
CSV_PATH = os.getenv("CSV_PATH", "../data/music-theory-dataset-100.csv")
QD_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "zoomcamp-music-theory-assistant")
EMBED_MODEL = os.getenv("EMBED_MODEL", "jinaai/jina-embeddings-v2-small-en")
EMBED_DIM = int(os.getenv("EMBED_DIM", "512"))

def build_text(row):
    return " | ".join([
        str(row["title"]),
        str(row["artist"]),
        f"Genre: {row['genre']}",
        f"Key: {row['key']}",
        f"Tempo: {row['tempo_bpm']} BPM",
        f"Time: {row['time_signature']}",
        f"Chords: {row['chord_progression']}",
        f"Roman: {row['roman_numerals']}",
        f"Cadence: {row['cadence']}",
        f"Notes: {row['theory_notes']}",
    ])

def main():
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    docs = df.to_dict(orient="records")

    qd = QdrantClient(QD_URL)

    # recreate collection
    try:
        qd.delete_collection(collection_name=COLLECTION)
    except Exception:
        pass

    qd.create_collection(
        collection_name=COLLECTION,
        vectors_config=models.VectorParams(size=EMBED_DIM, distance=models.Distance.COSINE),
    )

    vectors = [models.Document(text=build_text(d), model=EMBED_MODEL) for d in docs]
    ids = [int(d["id"]) for d in docs]

    qd.upload_collection(
        collection_name=COLLECTION,
        vectors=vectors,
        payload=docs,
        ids=ids
    )

    print(f"Ingested {len(ids)} items into '{COLLECTION}' at {QD_URL}")

if __name__ == "__main__":
    main()
