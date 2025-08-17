# music-theory-assistant/db.py
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, List, Any, Dict

import psycopg2
from psycopg2.extras import DictCursor

# --- Config ---
RUN_TIMEZONE_CHECK = os.getenv("RUN_TIMEZONE_CHECK", "1") == "1"

# Default to London unless overridden via env
TZ_INFO = os.getenv("TZ", "Europe/London")
tz = ZoneInfo(TZ_INFO)

# --- Connection ---
def get_db_connection():
    """
    Returns a new psycopg2 connection using env vars:
      POSTGRES_HOST (default: 'postgres' for Docker; 'localhost' for local)
      POSTGRES_DB   (default: 'course_assistant')
      POSTGRES_USER (default: 'your_username')
      POSTGRES_PASSWORD (default: 'your_password')
    """
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        database=os.getenv("POSTGRES_DB", "course_assistant"),
        user=os.getenv("POSTGRES_USER", "your_username"),
        password=os.getenv("POSTGRES_PASSWORD", "your_password"),
    )


# --- Schema management ---
def init_db(drop_existing: bool = True):
    """
    Initializes the database schema.
    By default drops and recreates the 'conversations' and 'feedback' tables
    for a clean start. Set drop_existing=False to keep existing data.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if drop_existing:
                cur.execute("DROP TABLE IF EXISTS feedback")
                cur.execute("DROP TABLE IF EXISTS conversations")

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    model_used TEXT NOT NULL,
                    response_time FLOAT NOT NULL,
                    relevance TEXT NOT NULL,
                    relevance_explanation TEXT NOT NULL,
                    prompt_tokens INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    eval_prompt_tokens INTEGER NOT NULL,
                    eval_completion_tokens INTEGER NOT NULL,
                    eval_total_tokens INTEGER NOT NULL,
                    openai_cost FLOAT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT REFERENCES conversations(id) ON DELETE CASCADE,
                    feedback INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
                """
            )
        conn.commit()
    finally:
        conn.close()


# --- Writes ---
def save_conversation(conversation_id: str, question: str, answer_data: Dict[str, Any], timestamp: Optional[datetime] = None):
    """
    Persists a single conversation.
    'answer_data' must contain keys:
      answer, model_used, response_time, relevance, relevance_explanation,
      prompt_tokens, completion_tokens, total_tokens,
      eval_prompt_tokens, eval_completion_tokens, eval_total_tokens, openai_cost
    """
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations 
                (id, question, answer, model_used, response_time, relevance, 
                 relevance_explanation, prompt_tokens, completion_tokens, total_tokens, 
                 eval_prompt_tokens, eval_completion_tokens, eval_total_tokens, openai_cost, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    conversation_id,
                    question,
                    answer_data["answer"],
                    answer_data["model_used"],
                    float(answer_data["response_time"]),
                    str(answer_data.get("relevance", "unknown")),
                    str(answer_data.get("relevance_explanation", "")),
                    int(answer_data.get("prompt_tokens", 0)),
                    int(answer_data.get("completion_tokens", 0)),
                    int(answer_data.get("total_tokens", 0)),
                    int(answer_data.get("eval_prompt_tokens", 0)),
                    int(answer_data.get("eval_completion_tokens", 0)),
                    int(answer_data.get("eval_total_tokens", 0)),
                    float(answer_data.get("openai_cost", 0.0)),
                    timestamp,
                ),
            )
        conn.commit()
    finally:
        conn.close()


def save_feedback(conversation_id: str, feedback: int, timestamp: Optional[datetime] = None):
    """
    Persists feedback for a conversation. feedback: 1 (thumbs up) or -1 (thumbs down).
    """
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO feedback (conversation_id, feedback, timestamp) 
                VALUES (%s, %s, %s)
                """,
                (conversation_id, int(feedback), timestamp),
            )
        conn.commit()
    finally:
        conn.close()


# --- Reads ---
def get_recent_conversations(limit: int = 5, relevance: Optional[str] = None):
    """
    Returns the most recent conversations (optionally filtered by relevance).
    Includes a joined 'feedback' value if available (may be NULL).
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            base = """
                SELECT c.*, f.feedback
                FROM conversations c
                LEFT JOIN feedback f ON c.id = f.conversation_id
            """
            params: List[Any] = []
            if relevance:
                base += " WHERE c.relevance = %s"
                params.append(relevance)
            base += " ORDER BY c.timestamp DESC LIMIT %s"
            params.append(limit)

            cur.execute(base, params)
            return cur.fetchall()
    finally:
        conn.close()


def get_feedback_stats():
    """
    Returns a dict-like row with 'thumbs_up' and 'thumbs_down' counts.
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                """
                SELECT 
                    SUM(CASE WHEN feedback > 0 THEN 1 ELSE 0 END) AS thumbs_up,
                    SUM(CASE WHEN feedback < 0 THEN 1 ELSE 0 END) AS thumbs_down
                FROM feedback
                """
            )
            return cur.fetchone()
    finally:
        conn.close()


# --- Optional debugging: timezone sanity check ---
def check_timezone():
    """
    Debug helper to compare DB timezone vs Python tz and verify TIMESTAMPTZ I/O.
    Inserts a test row and prints times in UTC and local TZ.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Show DB timezone & current timestamp
            cur.execute("SHOW timezone;")
            db_timezone = cur.fetchone()[0]
            print(f"Database timezone: {db_timezone}")

            cur.execute("SELECT current_timestamp;")
            db_now = cur.fetchone()[0]
            print(f"Database current time (UTC): {db_now}")
            print(f"Database current time ({TZ_INFO}): {db_now.astimezone(tz)}")

            py_now = datetime.now(tz)
            print(f"Python current time ({TZ_INFO}): {py_now}")

            # Insert test row using Python-localized time
            cur.execute(
                """
                INSERT INTO conversations 
                (id, question, answer, model_used, response_time, relevance, 
                 relevance_explanation, prompt_tokens, completion_tokens, total_tokens, 
                 eval_prompt_tokens, eval_completion_tokens, eval_total_tokens, openai_cost, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING timestamp;
                """,
                (
                    "test",
                    "test question",
                    "test answer",
                    "test model",
                    0.0,
                    "test",
                    "test explanation",
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0.0,
                    py_now,
                ),
            )
            inserted_ts = cur.fetchone()[0]
            print(f"Inserted time (UTC): {inserted_ts}")
            print(f"Inserted time ({TZ_INFO}): {inserted_ts.astimezone(tz)}")

            cur.execute("SELECT timestamp FROM conversations WHERE id = 'test';")
            selected_ts = cur.fetchone()[0]
            print(f"Selected time (UTC): {selected_ts}")
            print(f"Selected time ({TZ_INFO}): {selected_ts.astimezone(tz)}")

            # Cleanup
            cur.execute("DELETE FROM conversations WHERE id = 'test';")
            conn.commit()
    except Exception as e:
        print(f"[Timezone check] Error: {e}")
        conn.rollback()
    finally:
        conn.close()


if RUN_TIMEZONE_CHECK:
    check_timezone()
