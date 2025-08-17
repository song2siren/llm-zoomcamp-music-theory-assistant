import os
import json
from time import time
from typing import Dict, Tuple, List, Any

from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient, models

load_dotenv()

# --------- Config (env-overridable) ----------
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "zoomcamp-music-theory-assistant")
EMBEDDING_MODEL = os.getenv("EMBED_MODEL", "jinaai/jina-embeddings-v2-small-en")
TOP_K = int(os.getenv("TOP_K", "5"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # used for both answer + eval

# --------- Clients ----------
qd_client = QdrantClient(QDRANT_URL)
client = OpenAI(api_key=OPENAI_API_KEY)

# ---------- Prompt templates ----------
prompt_template = """
You're a music teacher. Answer the QUESTION based on the CONTEXT from our music theory database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT:
{context}
""".strip()

entry_template = """
title: {title}
artist: {artist}
genre: {genre}
key: {key}
tempo_bpm: {tempo_bpm}
time_signature: {time_signature}
chord_progression: {chord_progression}
roman_numerals: {roman_numerals}
cadence: {cadence}
theory_notes: {theory_notes}
""".strip()


def build_prompt(query, search_results):
    context = ""

    for doc in search_results:
        # Qdrant returns ScoredPoint with .payload; allow dicts too (tests)
        payload = doc.payload if hasattr(doc, "payload") else doc
        context = context + entry_template.format(**payload) + "\n\n"

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt


# --------- Retrieval ---------
def vector_search(question: str, top_k: int = TOP_K):
    """
    Retrieve top-k hits from Qdrant. Returns a list of ScoredPoint (with .payload).
    """
    query_points = qd_client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=models.Document(
            model=EMBEDDING_MODEL,
            text=question
        ),
        limit=top_k,
        with_payload=True
    )
    return query_points.points


# --------- LLM wrapper ---------
def llm(prompt: str, model: str = OPENAI_MODEL):
    """
    Returns (answer_text, token_stats) where token_stats has:
      prompt_tokens, completion_tokens, total_tokens
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content.strip()

    token_stats = {
        "prompt_tokens": getattr(response.usage, "prompt_tokens", 0) or 0,
        "completion_tokens": getattr(response.usage, "completion_tokens", 0) or 0,
        "total_tokens": getattr(response.usage, "total_tokens", 0)
            or ((getattr(response.usage, "prompt_tokens", 0) or 0)
                + (getattr(response.usage, "completion_tokens", 0) or 0))
    }
    return answer, token_stats


# --------- Relevance evaluator ---------
prompt_template_evaluation = """
You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks. Return ONLY valid JSON
with double quotes, no comments, and no trailing commas. For example:

{{
  "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
  "Explanation": "[Provide a brief explanation for your evaluation]"
}}
""".strip()

def evaluate_relevance(question: str, answer: str):
    prompt = prompt_template_evaluation.format(question=question, answer=answer)
    evaluation, tokens = llm(prompt, model=OPENAI_MODEL)

    try:
        json_eval = json.loads(evaluation)
        return json_eval, tokens
    except json.JSONDecodeError:
        result = {"Relevance": "UNKNOWN", "Explanation": "Failed to parse evaluation"}
        return result, tokens


# --------- Cost calculation ---------
def calculate_openai_cost(model: str, tokens: Dict[str, int]) -> float:
    """
    Estimate OpenAI API cost (USD) based on model + token usage.
    tokens must include 'prompt_tokens' and 'completion_tokens'.
    """
    openai_cost = 0.0

    if model == "gpt-4o-mini":
        openai_cost = (
            tokens.get("prompt_tokens", 0) * 0.00015
            + tokens.get("completion_tokens", 0) * 0.0006
        ) / 1000
    else:
        print("Model not recognized. OpenAI cost calculation failed.")

    return openai_cost


# --------- Full RAG pipeline ---------
def rag(query: str, model: str = OPENAI_MODEL):
    """
    Runs the full RAG flow:
      1) retrieve from Qdrant
      2) build grounded prompt (exact template)
      3) call LLM to answer
      4) call LLM to evaluate relevance
      5) compute total OpenAI cost

    Returns:
      answer_data (dict) — ready to persist to DB
      hits (list) — retrieval results to display as sources
    """
    t0 = time()

    # 1–2) retrieval + prompt
    hits = vector_search(query, TOP_K)
    prompt = build_prompt(query, hits)

    # 3) answer
    answer, token_stats = llm(prompt, model=model)

    # 4) evaluate relevance
    relevance, rel_token_stats = evaluate_relevance(query, answer)

    t1 = time()
    took = t1 - t0

    # 5) costs
    openai_cost_rag = calculate_openai_cost(model, token_stats)
    openai_cost_eval = calculate_openai_cost(model, rel_token_stats)
    openai_cost = openai_cost_rag + openai_cost_eval

    # 6) pack answer_data 
    answer_data = {
        "answer": answer,
        "model_used": model,
        "response_time": took,
        "relevance": relevance.get("Relevance", "UNKNOWN"),
        "relevance_explanation": relevance.get("Explanation", "Failed to parse evaluation"),
        "prompt_tokens": token_stats["prompt_tokens"],
        "completion_tokens": token_stats["completion_tokens"],
        "total_tokens": token_stats["total_tokens"],
        "eval_prompt_tokens": rel_token_stats["prompt_tokens"],
        "eval_completion_tokens": rel_token_stats["completion_tokens"],
        "eval_total_tokens": rel_token_stats["total_tokens"],
        "openai_cost": openai_cost,
    }

    return answer_data, hits
