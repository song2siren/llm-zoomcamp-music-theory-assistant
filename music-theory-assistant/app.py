import os
import uuid
import streamlit as st
from dotenv import load_dotenv

from rag import rag   # shared RAG flow
from db import save_conversation, save_feedback

load_dotenv()

st.set_page_config(page_title="Music Theory Assistant", page_icon="🎵")
st.title("🎵 Music Theory Assistant")
st.caption("Ask about cadences, chord functions, keys, progressions, and more.")

question = st.text_input("Your question", placeholder="Which songs use deceptive cadences?")

if st.button("Ask") and question.strip():
    with st.spinner("Thinking…"):
        answer_data, hits = rag(question)

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

    # Save conversation to Postgres
    conv_id = str(uuid.uuid4())
    try:
        save_conversation(conv_id, question, answer_data)
        st.caption(f"Saved conversation id: `{conv_id}`")
    except Exception as e:
        st.error(f"Failed to save conversation: {e}")

    # Feedback buttons
    c1, c2 = st.columns(2)
    if c1.button("👍 Helpful"):
        try:
            save_feedback(conv_id, 1)
            st.success("Thanks for the feedback!")
        except Exception as e:
            st.error(f"Failed to save feedback: {e}")
    if c2.button("👎 Not helpful"):
        try:
            save_feedback(conv_id, -1)
            st.success("Thanks for the feedback!")
        except Exception as e:
            st.error(f"Failed to save feedback: {e}")
