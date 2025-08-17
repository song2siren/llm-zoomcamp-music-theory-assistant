import uuid
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from dotenv import load_dotenv

from rag import rag # shared RAG flow
from db import save_conversation, save_feedback

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

REQUESTS = Counter("rag_requests_total", "Total RAG requests")
ERRORS = Counter("rag_errors_total", "Total RAG request errors")
LATENCY = Histogram("rag_latency_seconds", "RAG end-to-end latency (seconds)")
TOKENS = Histogram("rag_total_tokens", "Total tokens per call", buckets=(0, 250, 500, 1000, 2000, 4000, 8000))
HEALTH = Gauge("app_healthy", "1 if app considers itself healthy")

load_dotenv()

app = FastAPI(title="Music Theory Assistant API")

class Query(BaseModel):
    question: str

class Feedback(BaseModel):
    conversation_id: str
    feedback: int  # 1 or -1

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health():
    HEALTH.set(1.0)
    return {"ok": True}    

@app.post("/rag")
@LATENCY.time()
def rag_endpoint(q: Query):
    REQUESTS.inc()
    try:
        answer_data, hits = rag(q.question)
        TOKENS.observe(answer_data["total_tokens"])
    except Exception as e:
        ERRORS.inc()
        raise HTTPException(status_code=500, detail=f"RAG error: {e}")

    conv_id = str(uuid.uuid4())
    try:
        save_conversation(conv_id, q.question, answer_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB save failed: {e}")

    return {
        "conversation_id": conv_id,
        "answer": answer_data["answer"],
        "model": answer_data["model_used"],
        "response_time": answer_data["response_time"],
        "usage": {
            "prompt_tokens": answer_data["prompt_tokens"],
            "completion_tokens": answer_data["completion_tokens"],
            "total_tokens": answer_data["total_tokens"],
            "eval_prompt_tokens": answer_data["eval_prompt_tokens"],
            "eval_completion_tokens": answer_data["eval_completion_tokens"],
            "eval_total_tokens": answer_data["eval_total_tokens"],
        },
        "relevance": {
            "label": answer_data["relevance"],
            "explanation": answer_data["relevance_explanation"],
        },
        "openai_cost": answer_data["openai_cost"],
        "sources": [h.payload for h in hits],
    }

@app.post("/feedback")
def feedback_endpoint(fb: Feedback):
    if fb.feedback not in (1, -1):
        raise HTTPException(status_code=400, detail="feedback must be 1 or -1")
    try:
        save_feedback(fb.conversation_id, fb.feedback)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB save failed: {e}")
    return {"ok": True}
