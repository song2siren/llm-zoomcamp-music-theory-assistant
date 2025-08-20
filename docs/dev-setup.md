# Developer Setup

## Development without Docker (*Optional*)

If you prefer running locally (not recommended for reviewers), you can use [Pipenv](https://pipenv.pypa.io/en/latest/).

1. Install dependencies:

    ```bash
    pip install pipenv
    pipenv install --dev
    ```

2. Add your OpenAI API key in .envrc or export it:

    ```bash
    export OPENAI_API_KEY=sk-...
    ```

3. Ingest the dataset:

    ```bash
    pipenv run python music-theory-assistant/ingest.py
    ```

4. Run the Streamlit app:

    ```bash
    pipenv run streamlit run music-theory-assistant/app.py
    ```

5. Or run the API:

    ```bash
    pipenv run uvicorn music-theory-assistant.api:app --reload --port 8000
    ```
## Interacting with the API

To ping the API (using [HTTPie](https://httpie.io/)):

```bash
http GET :8000/health
```
Expected: `{"ok": true}`

To ask the RAG a question via the API:

```bash
http POST :8000/rag question="Which songs use deceptive cadences?"
```

To then verify this has been saved to Postgres:

```bash
docker compose exec postgres psql -U your_username -d music_theory_assistant -c \
"SELECT id, left(question,60)||'…' AS q, model_used, response_time, relevance, openai_cost, timestamp
 FROM conversations ORDER BY timestamp DESC LIMIT 5;"
```

To send feedback via the API:

```bash
http POST :8000/feedback conversation_id=<YOUR_CONVERSATION_ID> feedback:=1
# or thumbs down
http POST :8000/feedback conversation_id=<YOUR_CONVERSATION_ID> feedback:=-1
```

And then verify it saved:

```bash
docker compose exec postgres psql -U your_username -d music_theory_assistant -c \
"SELECT conversation_id, feedback, timestamp FROM feedback ORDER BY timestamp DESC LIMIT 5;"
```
Alternatively there is a small [generate_events.sh](/generate_events.sh) file at the project root. Run this:

```bash
bash generate_events.sh
```
And check...

```bash
curl -s http://localhost:8000/metrics | grep -E 'feedback_(up|down)_total'
```