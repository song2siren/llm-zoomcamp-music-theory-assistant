# LLM Zoomcamp - Music Theory Assistant
This is a RAG application project for the DataTalksClub [LLM Zoomcamp 2025](https://github.com/DataTalksClub/llm-zoomcamp).

<p align="center">
  <img src="images/banner.png">
</p>

## Problem Description

Understanding music theory can be overwhelming, especially when analysing harmonic functions and cadences across different songs. Traditional resources are often scattered and difficult to search effectively.

The Music Theory Assistant provides a conversational AI that helps users explore songs through a theoretical lens—answering questions about cadences, chord functions, and harmonic context in a natural and intuitive way.

This is based upon a musically accurate dataset that can answer music theory questions like:

  *"Which songs use deceptive cadences?"*

  *"Which have authentic cadences?"*

  *"What is the function of G in Let It Be?"*

## Project Overview
The Music Theory Assistant is a RAG application designed to help users analyse and understand songs through the lens of music theory.

The main use cases include:

**Cadence Identification**: Discovering songs that use specific cadences such as deceptive or authentic cadences.

**Chord Function Analysis**: Understanding the harmonic function of specific chords within a song’s context.

**Song-Based Querying**: Asking theory-related questions about well-known songs in a conversational way.

**Conversational Interaction**: Making music theory more approachable without digging through textbooks, disparate online resources or dense analyses.

## Dataset

The dataset used in this project contains detailed music theory annotations for various well-known songs, including:

- **Title:** The name of the song (e.g., *Let It Be*, *Smells Like Teen Spirit*).  
- **Artist:** The performing artist or band (e.g., The Beatles, Nirvana).  
- **Genre:** The musical style or category (e.g., Pop, Rock, Jazz).  
- **Key:** The key signature of the song (e.g., C major, A minor).  
- **Tempo (BPM):** The tempo in beats per minute (e.g., 76, 120).  
- **Time Signature:** The time signature used in the song (e.g., 4/4, 3/4).  
- **Chord Progression:** The main chord sequence in Roman and/or letter notation (e.g., C – G – Am – F).  
- **Roman Numerals:** The chord progression translated into Roman numeral analysis (e.g., I – V – vi – IV).  
- **Cadence:** Identified cadences within the song (e.g., Authentic, Deceptive, Plagal).  
- **Theory Notes:** Additional commentary on harmonic features, chord functions, or interesting theoretical elements.

The dataset currently contains 100 curated, musically accurate and unique records. It serves as the foundation for the Music Theory Assistant's ability to answer questions about harmonic analysis, cadences, and chord functions.

You can find the data in [`data/music-theory-dataset-100.csv`](data/music-theory-dataset-100.csv).

## Technologies

- [Python 3.12](https://www.python.org/downloads/release/python-3120/)
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) for containerisation
- [Minsearch](https://github.com/alexeygrigorev/minsearch) for full-text search
- [Qdrant](https://qdrant.tech/) for vector search
- [Streamlit](https://streamlit.io/) for the application
- [FastAPI](https://fastapi.tiangolo.com/) for the API
- [Grafana](https://grafana.com/) and [Prometheus](https://prometheus.io/) for monitoring and [PostgreSQL](https://www.postgresql.org/) as the backend
- [OpenAI](https://openai.com/) as an LLM

## Setup
The Python project has been developed in [GitHub Codespaces](https://github.com/features/codespaces). As such, it is preferable to use Codespaces to run this application.

The project uses [OpenAI](https://openai.com/), so you need to provide the API key:

1. OpenAI keys can be generated here: [OpenAI Platform](https://platform.openai.com/api-keys). The key is then stored as an evironment variable associated with this project.
2. For OpenAI, it is recommended that you create a new project and use a separate key.
3. Install `direnv`. This is a shell extension that automatically manages environment variables necessary to run the project.

```bash
sudo apt update
sudo apt install direnv
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
source ~/.bashrc
```
4. Run `direnv allow` to load the key into your environment.
5. Copy `.envrc_template` into `.envrc` and insert your OpenAI key there.
6. Install pipenv (for dependency management):

```bash
pip install pipenv
```
7. Once installed, you can install the virtual environment and app dependencies:

```bash
pipenv install --dev
```
8. Now install remaining dependencies:

```bash
pipenv install \
  openai \
  scikit-learn \
  pandas \
  minsearch \
  "qdrant-client[fastembed]>=1.14.2" \
  sentence-transformers \
  streamlit \
  httpie \
  python-dotenv \
  psycopg2-binary \
  prometheus-client
```

9. Now install developer tools

```bash
pipenv install --dev tqdm notebook==7.1.2 ipywidgets
```

## Evaluation

For each of the evaluation criteria, see the following sections:

- [Problem description](#problem-description)
- [Retrieval flow](#retrieval-flow)
- [Retrieval evaluation](#retrieval-evaluation)
- [LLM evaluation](#llm-evaluation)
- [Interface](#interface)
- [Ingestion pipeline](#ingestion-pipeline)
- [Monitoring](#monitoring)
- [Containerization](#containerization)
- [Reproducibility](#reproducibility) TODO
- [Best practices](#best-practices) TODO

The score criteria (with self-evaluation and additional commentary) can be found in the [docs/project-evaluation.ipynb](notebooks/docs/project-evaluation.ipynb) notebook.

The code for evaluating the system can be found in the [notebooks/rag-test.ipynb](notebooks/rag-test.ipynb) notebook.

To launch [Jupyter Notebook](https://jupyter.org/) from inside Pipenv, do the following:

```bash
pipenv run jupyter notebook
```

This code requires Qdrant and FastEmbed to be installed and running. If it is not available, do the following:

Install Qdrant and FastEmbed (if not already installed during project setup):

```bash
pipenv install "qdrant-client[fastembed]>=1.14.2"
```

Run in Docker:

```bash
docker pull qdrant/qdrant

docker run -p 6333:6333 -p 6334:6334 \
   -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
   qdrant/qdrant
```
### Retrieval Flow

The knowledgebase is based upon a [ChatGPT](https://chatgpt.com/) generated [data/music-theory-dataset-100.csv](data/music-theory-dataset-100.csv) CSV file. This is used together with the [ChatGPT 4o LLM](https://chatgpt.com/?model=gpt-4o).

### Retrieval Evaluation

Multiple retrieval approaches are evaluated:

#### minsearch

The first approach uses [minsearch](https://github.com/alexeygrigorev/minsearch/blob/main/minsearch.py) text search without any boosting and returns the following results:

* hit_rate: 91%
* MRR: 63%

#### minsearch boosted

After the boosting is improved, the following results are returned:

* hit_rate: 93%
* MRR: 91%

The best boosting parameters:
```python
boost = {
    'title': 2.83,
    'artist': 0.58,
    'genre': 0.75,
    'key': 1.52,
    'tempo_bpm': 1.02,
    'time_signature': 0.80,
    'chord_progression': 2.69,
    'roman_numerals': 1.92,
    'cadence': 1.06,
    'theory_notes': 0.15
}
```
Note that the routine to generate these parameters will likely return different results each time it is run.

#### Qdrant vector search

The second approach uses [Qdrant](https://qdrant.tech/) vector search and returns the following results:

* hit_rate: 91%
* MRR: 87%

#### Qdrant hybrid vector search

The third approach uses [Qdrant](https://qdrant.tech/) hybrid vector search (dense and sparse vectors) and returns the following results:

* hit_rate: 91%
* MRR: 87%

Note that these results are the same as the regular vector search above which suggests the hybrid could be falling back to the dense side and behaving the same.

#### Qdrant hybrid vector search (re-ranked)

Finally, the fourth approach uses [Qdrant](https://qdrant.tech/) hybrid vector search (dense and sparse vectors) but also with document re-ranking and returns the following results:

* hit_rate: 91%
* MRR: 55%

Note that here the MRR is lower, possibly because the first correct document is still within the top results but pushed lower on average.

**Conclusion**: The **minsearch text search with boosted parameters** seems to perform the best and is therefore used in the LLM evaluation below.

### LLM Evaluation

Two approaches are taken to evaluate the quality of the RAG flow:

* Cosine similarity (with [gpt-4o-mini](https://chatgpt.com/?model=gpt-4o-mini))
* LLM-as-a-Judge (with [gpt-4o-mini](https://chatgpt.com/?model=gpt-4o-mini) and [gpt-4o](https://chatgpt.com/?model=gpt-4o))

#### Cosine Similarity

For cosine similarity with a single test record, the following result was returned:

* Cosine similarity: 0.47456914

For cosine similarity when comparing the [gpt-4o-mini](https://chatgpt.com/?model=gpt-4o-mini) answer for each question in the [ground truth data set](data/ground-truth-retrieval.csv) with the answer in the original [music theory dataset](data/music-theory-dataset-100.csv), the following results were returned:

| Metric   | Value   | Meaning                                 |
| -------- | ------- | --------------------------------------- |
| count    | 500     | Number of comparisons made.             |
| mean     | 0.57    | Avg cosine similarity across all pairs. |
| std      | 0.12    | Standard deviation.                     |
| min      | 0.21    | Lowest similarity.                      |
| 25%      | 0.51    | First quartile (poor matches).          |
| 50%      | 0.58    | Median.                                 |
| 75%      | 0.65    | Third quartile (good matches).          |
| max      | 0.88    | Best similarity.                        |

Just a single model was used for cosine similarity, but for LLM-as-a-Judge multiple models were evaluated.

#### LLM-as-a-Judge

For the LLM-as-a-Judge (with [gpt-4o-mini](https://chatgpt.com/?model=gpt-4o-mini)), among 200 records, the following results were returned:

* RELEVANT - 195 (97.5%)
* PARTLY_RELEVANT - 4 (2%)
* NON_RELEVANT - 1 (0.5%)

For the LLM-as-a-Judge (with [gpt-4o](https://chatgpt.com/?model=gpt-4o)), among 200 records, the following results were returned:

* RELEVANT - 193 (96.5%)
* PARTLY_RELEVANT - 6 (3%)
* NON_RELEVANT - 1 (0.5%)

**Conclusion**: Using LLM-as-a-Judge [gpt-4o-mini](https://chatgpt.com/?model=gpt-4o-mini) is marginally better and will be used for developiing the music theory assistant application.

### Interface

Before running either interface it is necessary to run the Python data ingestion script into Qdrant as noted in the [Ingestion Pipeline section](#ingestion-pipeline) below.

This project provides **two ways to interact with the Music Theory Assistant**:

- **Streamlit UI** 🎵

  A web-based interface where users can type in natural-language questions (e.g., "Which songs use deceptive cadences?") and receive answers enhanced with contextual information from the knowledge base.

  To start the app:

  ```bash
  streamlit run music-theory-assistant/app.py
  ```
  The UI is interactive, lightweight, and requires no coding from the user.

- **FastAPI** ⚡

  A REST API that exposes the same RAG functionality programmatically. This allows other applications or scripts to integrate with the assistant.

  To start the API server:

  ```bash
  # Option 1: Run from inside the application folder
  cd music-theory-assistant
  uvicorn api:app --reload --port 8000

  # Option 2: Run from project root
  uvicorn music-theory-assistant.api:app --reload --port 8000
  ```

  Example query from the terminal (using [httpie](https://httpie.io/)):

  ```bash
  http POST :8000/rag question="Which songs use deceptive cadences?"
  ```

  Or open the interactive docs at: http://127.0.0.1:8000/docs

### Ingestion Pipeline

The dataset (of musical theory–annotated songs) is loaded into a Qdrant vector database via a dedicated ingestion script. This ensures that the retrieval layer is always backed by fresh and structured embeddings.

The script reads from [data/music-theory-dataset-100.csv](data/music-theory-dataset-100.csv).

It generates embeddings for each record (title, artist, genre, chords, cadences, etc.) using jinaai/jina-embeddings-v2-small-en.

The embeddings and payloads are stored in a Qdrant collection (zoomcamp-music-theory-assistant).

Run the ingestion step once before starting the app:

```bash
python music-theory-assistant/ingest.py
```

After ingestion, Qdrant persists the collection, so the app and API can be restarted without re-ingesting.

## Monitoring ##

To Ping the API (using HTTPie installed earlier in Pipenv):

```bash
http GET :8000/health
```
Expected: {"ok": true}

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

### Prometheus

To check Prometheus is running open http://localhost:9090 in your browser.

To run a quick query, go to the Graph tab and execute this in the query box:

```promql
up
```
To check the Postgres exporter is running:

```promql
pg_database_size_bytes
```

### Grafana

To check Grafana is running open http://localhost:3000 in your browser. Login with default credentials (admin / admin unless you changed them).

Go to Connections → Data sources and check Prometheus is already added.

From Connections → Data sources → Prometheus:

- Click Build a dashboard
- Add visualization
- Select Prometheus as the data source
- Toggle the query builder to code and run the following:

```bash
rate(pg_stat_activity_count[1m])
```
You should see a graph.

Alternatively, there is a [preconfigured Grafana dashboard](/dashboard.json) at the project root which you can load into Grafana.

![Grafana](/images/grafana.png)

This shows 8 key panels or charts.

- **RAG Request Rate** – how many user queries are being processed per second.
- **Latency (P95)** – the 95th percentile response time for end-to-end RAG requests, showing how fast answers are returned under load.
- **Average Tokens per Call** – the average number of LLM tokens consumed per request (prompt + completion).
- **Feedback Trends** – counts of 👍 thumbs-up and 👎 thumbs-down feedback submitted by users.
- **Feedback Approval Rate** – the percentage of positive feedback, indicating answer quality.
- **Error Rate** – the number of failed RAG calls per second.
- **Conversations Saved** – how many conversations are being persisted to the database.
- **App Health** – a simple 1/0 indicator showing if the API is reporting itself healthy.

### Containerization

[Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) have also been used for the application and API setup.

To get started:

**Prerequisites**

- Docker and Docker Compose installed (should be already if running in Codespaces)
- An OpenAI API key

**Project layout (expected)**

```kotlin
project-root/
├── data/
│   └── music-theory-dataset-100.csv
├── docker-compose.yml
└── music-theory-assistant/
    ├── api.py
    ├── app.py
    ├── ingest.py
    ├── wait_for_qdrant.py
    ├── requirements.txt
    └── (other project files…)
```

**Environment**

Set your OpenAI key so the containers can access it. The simplest thing to do is export it before running Compose:

```bash
export OPENAI_API_KEY=sk-...
```

(You can also put this in a .env file next to docker-compose.yml with OPENAI_API_KEY=....)

**One-command run**

From the **project root**, run:

```bash
docker compose up --build
```

What happens:

- **Qdrant** starts and persists data in a named volume.
- **Ingest** waits until Qdrant is ready, then loads [data/music-theory-dataset-100.csv](data/music-theory-dataset-100.csv) into the zoomcamp-music-theory collection (and exits).
- **App** (Streamlit UI) starts on http://localhost:8501.
- **API** (FastAPI) starts on http://localhost:8000.
- **Monitoring** Prometheus starts on http://localhost:9090 and Grafana starts on http://localhost:3000.

Visit:

- UI: http://localhost:8501
- API docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

**Re-ingesting data**

If you change the CSV, re-run only the ingestion:

```bash
docker compose run --rm ingest
```

**Stopping everything**

```bash
docker compose down
```
## Reproducibility

TODO

## Best Practices

TODO

## Acknowledgements

Many thanks to [DataTalksClub](https://github.com/DataTalksClub) for the `llm-zoomcamp` resources and to Alexey Grigorev and others for providing clear and comprehensive project instructions.