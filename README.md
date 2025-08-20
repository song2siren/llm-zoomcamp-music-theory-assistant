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

The [dataset used in this project]((data/music-theory-dataset-100.csv)) contains detailed music theory annotations for various well-known songs, including:

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

You can find the data in [`data/music-theory-dataset-100.csv`](/data/music-theory-dataset-100.csv).

There is a list of example questions you could ask the Music Theory Assistant in [`data/ground-truth-retrieval.csv`](/data/ground-truth-retrieval.csv).

## Technologies

- [Python 3.12](https://www.python.org/downloads/release/python-3120/)
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) for containerisation
- [Minsearch](https://github.com/alexeygrigorev/minsearch) for full-text search
- [Qdrant](https://qdrant.tech/) for vector search and hybrid vector search
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

For each of the evaluation criteria, see the following sections of the README below:

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

The score criteria (with self-evaluation and additional commentary) can be found in the [Project Evaluation](/docs/project-evaluation.md) notebook.

The code for evaluating the system can be found in the [RAG Test](/notebooks/rag-test.ipynb) notebook.

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

The knowledgebase is based upon a [ChatGPT](https://chatgpt.com/) generated [Music Theory Dataset CSV file](/data/music-theory-dataset-100.csv).

### Retrieval Evaluation

Multiple retrieval approaches are evaluated:

- [minsearch (text search non-boosted)](#minsearch)
- [minsearch (text search boosted)](#minsearch-boosted)
- [Qdrant (vector search)](#qdrant-vector-search)
- [Qdrant (vector search hybrid)](#qdrant-hybrid-vector-search)
- [Qdrant (vector search hybrid re-ranked)](#qdrant-hybrid-vector-search-re-ranked)

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

**Conclusion**: The [**minsearch text search with boosted parameters**](#minsearch-boosted) seems to perform the best and is therefore used moving forward in the LLM evaluation below.

### LLM Evaluation

Two approaches are taken to evaluate the quality of the RAG flow:

* [Cosine similarity](#cosine-similarity) (with [gpt-4o-mini](https://chatgpt.com/?model=gpt-4o-mini))
* [LLM-as-a-Judge](#llm-as-a-judge) (with [gpt-4o-mini](https://chatgpt.com/?model=gpt-4o-mini) and [gpt-4o](https://chatgpt.com/?model=gpt-4o))

#### Cosine Similarity

For cosine similarity with a single test record, the following result was returned:

* Cosine similarity: 0.47456914

For cosine similarity when comparing the [gpt-4o-mini](https://chatgpt.com/?model=gpt-4o-mini) answer for each question in the [Ground Truth Dataset](data/ground-truth-retrieval.csv) with the answer in the original [Music Theory Dataset](/data/music-theory-dataset-100.csv), the following results were returned:

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

Just a single model was used for cosine similarity, but for [LLM-as-a-Judge](#llm-as-a-judge) multiple models were evaluated.

#### LLM-as-a-Judge

For the LLM-as-a-Judge (with [gpt-4o-mini](https://chatgpt.com/?model=gpt-4o-mini)), among 200 records, the following results were returned:

* RELEVANT - 195 (97.5%)
* PARTLY_RELEVANT - 4 (2%)
* NON_RELEVANT - 1 (0.5%)

For the LLM-as-a-Judge (with [gpt-4o](https://chatgpt.com/?model=gpt-4o)), among 200 records, the following results were returned:

* RELEVANT - 193 (96.5%)
* PARTLY_RELEVANT - 6 (3%)
* NON_RELEVANT - 1 (0.5%)

**Conclusion**: Using LLM-as-a-Judge [gpt-4o-mini](https://chatgpt.com/?model=gpt-4o-mini) is marginally better and will be used for developiing the Music Theory Assistant application.

### Interface

This project provides **two ways** to interact with the Music Theory Assistant:

- **Streamlit UI** 🎵

  A web-based interface where users can type in natural-language questions (e.g., *"Which songs use deceptive cadences?"*) and receive answers enhanced with contextual information from the knowledge base.

- **FastAPI** ⚡

  A REST API that exposes the same RAG functionality programmatically. This allows other applications or scripts to integrate with the assistant.

  An example of a query from the terminal (using [httpie](https://httpie.io/)):

  ```bash
  http POST :8000/rag question="Which songs use deceptive cadences?"
  ```

  More information about interacting with the API can be found [here](/docs/dev-setup.md#interacting-with-the-api).

  Both of these interfaces implement [Qdrant](https://qdrant.tech/) vector search as the search technology.

#### 🚀 Quickstart (Recommended)

The fastest way to run the Music Theory Assistant is with [Docker Compose](https://docs.docker.com/compose/). This will launch the Streamlit UI, FastAPI backend, Qdrant, Postgres, Prometheus, and Grafana in one command.

1. Prerequisites
    - [Docker](https://www.docker.com/)
    - [Docker Compose](https://docs.docker.com/compose/)
    - An [OpenAI API](https://platform.openai.com/api-keys) key

2. Set your API key

    Export your OpenAI API key so the containers can access it:

    ```bash
    export OPENAI_API_KEY=sk-...
    ```

    (Alternatively, create a `.env` file next to [docker-compose.yml](/docker-compose.yml) with OPENAI_API_KEY=sk-... inside.)

3. Run everything

    From the project root:

    ```bash
    docker compose up --build
    ```

    That’s it 🎉 — everything is started at once.

4. Open the services

    - Streamlit App (UI) → http://localhost:8501
    - FastAPI Docs → http://localhost:8000/docs
    - Prometheus → http://localhost:9090
    - Grafana → http://localhost:3000 (login: admin / admin)

    The dataset ingestion step runs automatically on startup as a [Python script](/music-theory-assistant/ingest.py), so the app is ready to query.

5. Re-ingest data (if you change the CSV)

    If you update the dataset, reload it into Qdrant with:

    ```bash
    docker compose run --rm ingest
    ```

6. Stop everything

    ```bash
    docker compose down
    ```

🔧 Development without Docker (*Optional*)

If you prefer running locally (not recommended for reviewers), see [these instructions](/docs/dev-setup.md).

### Ingestion Pipeline

The [dataset (of musical theory–annotated songs)](/data/music-theory-dataset-100.csv) is loaded into a Qdrant vector database via a dedicated [Python ingestion script](/music-theory-assistant/ingest.py). This ensures that the retrieval layer is always backed by fresh and structured embeddings.

It generates embeddings for each record (title, artist, genre, chords, cadences, etc.) using jinaai/jina-embeddings-v2-small-en.

The embeddings and payloads are stored in a Qdrant collection (zoomcamp-music-theory-assistant).

The data ingestion is performed automatically as part of the [Quickstart](#-quickstart-recommended) process described above.

## Monitoring

Monitoring is performed using [Prometheus](https://prometheus.io/) and [Grafana](https://grafana.com/). These services are launched automatically with Docker Compose.

### Access the UIs

- Prometheus → http://localhost:9090
- Grafana → http://localhost:3000 (login: admin / admin)

### Metrics

The API and UI expose Prometheus metrics (via `/metrics`), including:

- `rag_requests_total` – number of RAG requests processed
- `rag_latency_seconds` – request latency distribution
- `rag_errors_total` – failed requests
- `rag_total_tokens` – token usage per request
- `feedback_up_total` / `feedback_down_total` – user feedback counts
- `conversation_saved_total` – persisted conversations
- `app_healthy` – API health flag (1/0)

### Preconfigured Grafana Dashboard

A ready-to-use dashboard is provided at [dashboard.json](/dashboard.json).

To import it:

1. Open Grafana → http://localhost:3000 (login: admin / admin)
2. Left menu → Dashboards → New → Import
3. Upload dashboard.json (from the project root).
4. Select Prometheus as the data source.
5. Click Import.

### Dashboard Overview

The dashboard shows **8 panels** to cover the evaluation criteria:

- **RAG Request Rate** – queries processed per second
- **Latency (P95)** – 95th percentile response time
- **Average Tokens per Call** – LLM usage per query
- **Feedback Trends** – 👍 thumbs-up vs 👎 thumbs-down feedback
- **Feedback Approval Rate** – percentage of positive feedback
- **Error Rate** – failed RAG calls per second
- **Conversations Saved** – successful DB persistence
- **App Health** – 1/0 flag showing if API reports healthy

![Grafana](/images/grafana.png)

### Containerization

[Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) have been used to launch the Streamlit UI, FastAPI backend, Qdrant, Postgres, Prometheus, and Grafana in one command. Instructions are provide in the [Quickstart guide](#-quickstart-recommended) above.

## Reproducibility

Full instructions on how to run the code and all dependencies are provided in this README file.

## Best Practices

Hybrid vector search and document re-ranking have been evaluated in the [Rag Test](/notebooks/rag-test.ipynb) file. User query re-ranking has not been implemented on this project. 

## Bonus Points

Deployment to the cloud has not been implemented for this project.

## Acknowledgements

Many thanks to [DataTalksClub](https://github.com/DataTalksClub) for the `llm-zoomcamp` resources and to Alexey Grigorev and others for providing clear and comprehensive project instructions.