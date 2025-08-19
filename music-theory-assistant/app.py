# --- at the top of app.py ---
import os, time, uuid
import streamlit as st
from dotenv import load_dotenv

from rag import rag
from db import save_conversation, save_feedback

# Prometheus (UI-side)
from prometheus_client import (
    Counter,
    Histogram,
    CollectorRegistry,
    start_http_server,
)

load_dotenv()

# ---------- UI metrics singleton ----------
UI_METRICS_PORT = int(os.getenv("UI_METRICS_PORT", "8001"))

def _init_ui_metrics():
    """Create a single CollectorRegistry + metrics + HTTP server, store in session_state."""
    reg = CollectorRegistry()
    # start the tiny HTTP server for this registry
    start_http_server(UI_METRICS_PORT, registry=reg)

    metrics = {
        "UI_QUERIES": Counter("ui_queries_total", "Queries submitted from Streamlit UI", registry=reg),
        "UI_FEEDBACK_UP": Counter("ui_feedback_up_total", "Thumbs-up clicked in UI", registry=reg),
        "UI_FEEDBACK_DOWN": Counter("ui_feedback_down_total", "Thumbs-down clicked in UI", registry=reg),
        "UI_LATENCY": Histogram("ui_latency_seconds", "UI-perceived latency (submit→answer)", registry=reg),
    }
    return reg, metrics

# Initialize once per process/session
if "ui_prom_registry" not in st.session_state:
    reg, metrics = _init_ui_metrics()
    st.session_state["ui_prom_registry"] = reg
    st.session_state["ui_metrics"] = metrics

# convenient handles
UI_QUERIES = st.session_state["ui_metrics"]["UI_QUERIES"]
UI_FEEDBACK_UP = st.session_state["ui_metrics"]["UI_FEEDBACK_UP"]
UI_FEEDBACK_DOWN = st.session_state["ui_metrics"]["UI_FEEDBACK_DOWN"]
UI_LATENCY = st.session_state["ui_metrics"]["UI_LATENCY"]

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Music Theory Assistant", page_icon="🎵")
st.title("🎵 Music Theory Assistant")
st.caption("Ask about cadences, chord functions, keys, progressions, and more.")

question = st.text_input("Your question", placeholder="Which songs use deceptive cadences?")

if st.button("Ask") and question.strip():
    t0 = time.time()
    UI_QUERIES.inc()

    with st.spinner("Thinking…"):
        answer_data, hits = rag(question)

    UI_LATENCY.observe(time.time() - t0)

    st.subheader("Answer")
    st.write(answer_data["answer"])

    st.subheader("Sources")
    if not hits:
        st.info("No results found. Did you run the ingestion step?")
    else:
        for h in hits:
            p = h.payload
            st.markdown(
                f"**{p.get('title')}** — {p.get('artist')}  \n"
                f"Key: {p.get('key')}, Cadence: {p.get('cadence')}  \n"
                f"Roman: {p.get('roman_numerals')}  \n"
                f"Notes: {p.get('theory_notes')}"
            )

    conv_id = str(uuid.uuid4())
    try:
        save_conversation(conv_id, question, answer_data)
        st.caption(f"Saved conversation id: `{conv_id}`")
    except Exception as e:
        st.error(f"Failed to save conversation: {e}")

    c1, c2 = st.columns(2)
    if c1.button("👍 Helpful"):
        try:
            UI_FEEDBACK_UP.inc()          # UI metric
            save_feedback(conv_id, 1)     # persist to DB
            st.success("Thanks for the feedback!")
        except Exception as e:
            st.error(f"Failed to save feedback: {e}")

    if c2.button("👎 Not helpful"):
        try:
            UI_FEEDBACK_DOWN.inc()        # UI metric
            save_feedback(conv_id, -1)
            st.success("Thanks for the feedback!")
        except Exception as e:
            st.error(f"Failed to save feedback: {e}")
